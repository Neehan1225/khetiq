import os
import json
import re
import time
import tempfile
import urllib.request
from pathlib import Path
from json import JSONDecodeError, JSONDecoder
from google import genai
from app.config import settings

# #region agent log


def _debug_log_file_paths():
    resolved = Path(__file__).resolve()
    out = []
    for d in [resolved.parent, *resolved.parents]:
        front, back = d / "frontend", d / "backend"
        try:
            if front.is_dir() and back.is_dir():
                out.append(d / "debug-e1ee78.log")
                break
        except OSError:
            continue
    try:
        out.append(resolved.parents[3] / "debug-e1ee78.log")
    except IndexError:
        pass
    out.append(Path.cwd() / "debug-e1ee78.log")
    out.append(Path(tempfile.gettempdir()) / "debug-e1ee78.log")
    env_path = os.environ.get("KHETIQ_DEBUG_LOG")
    if env_path:
        out.append(Path(env_path))
    seen = set()
    unique = []
    for p in out:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def _debug_ingest_post(payload: dict) -> None:
    """Cursor debug-mode NDJSON ingest (writes session log when ingest server is up)."""
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:7808/ingest/f172c522-7f69-46bc-b775-75436f2e6389",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Debug-Session-Id": "e1ee78",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=0.6)
    except Exception:
        pass


def _agent_debug_log(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    payload = {
        "sessionId": "e1ee78",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    last_exc = None
    file_written = False
    for path in _debug_log_file_paths():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)
            file_written = True
            break
        except Exception as ex:
            last_exc = repr(ex)
            continue
    if not file_written:
        try:
            fb = Path(tempfile.gettempdir()) / "debug-e1ee78-agent-fallback.log"
            with open(fb, "a", encoding="utf-8") as f:
                f.write(
                    json.dumps({"message": "_agent_debug_log_all_paths_failed", "last_exc": last_exc, **payload})
                    + "\n"
                )
        except Exception:
            pass
    _debug_ingest_post(payload)
# #endregion


def _strip_model_json_markup(raw: str) -> str:
    text = raw.strip()
    text = re.sub(r"^\s*```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s*```\s*$", "", text).strip().rstrip("`").strip()
    return text


def _parse_gemini_json_object(raw: str) -> tuple[dict, str]:
    """Parse first JSON object from model output; Gemini often adds preamble after JSON instructions."""
    text = _strip_model_json_markup(raw)
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj, "direct"
    except JSONDecodeError:
        pass
    decoder = JSONDecoder()
    last_err = None
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _end = decoder.raw_decode(text, i)
            if isinstance(obj, dict):
                return obj, "raw_decode"
        except JSONDecodeError as e:
            last_err = e
            continue
    if last_err:
        raise last_err
    raise JSONDecodeError("No JSON object in model response", text, 0)

LANG_NAMES = {
    "kn": "Kannada",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "en": "English",
}


_COPILOT_LANGUAGE_INSTRUCTION = (
    "Detect the language of the user's question. If Hindi respond in Hindi. "
    "If Kannada respond in Kannada. If Telugu respond in Telugu. "
    "If English respond in English. Always match the user's language exactly. "
    "Never respond in a different language than what the user asked in."
)

_COPILOT_USER_QUESTION_WRAPPER_TAIL = (
    "Answer specifically using the farm data provided. If they ask what to do next — give step by step recommendation "
    "based on their crops, deals, and market conditions. If they ask about demand — reference actual supply vs demand numbers. "
    "If they ask about buyers — give specific buyer names, distances, and net profit figures. If they ask about price — "
    "give exact APMC rate and net profit after transport."
)


def _format_copilot_user_question_block(question_text: str) -> str:
    return f"User question: {question_text}. {_COPILOT_USER_QUESTION_WRAPPER_TAIL}"


def _copilot_user_contents_after_system(task_and_question: str) -> str:
    """Language rule first (after system_instruction), then task and user prompt."""
    return f"{_COPILOT_LANGUAGE_INSTRUCTION}\n\n{task_and_question}"


def _copilot_system_instruction(full_context: dict) -> str:
    ctx_json = json.dumps(full_context, ensure_ascii=False)
    return (
        "You are KhetIQ, an expert Indian agricultural supply chain advisor helping farmers maximize profit. "
        f"You have access to real-time farm and market data: {ctx_json}. "
        "Use this data to answer every question with specific numbers, buyer names, distances, and actionable advice. "
        "Never give generic responses. Keep answers under 4 sentences but make every sentence count. "
        "Net profit discipline: Whenever analysis_data.copilot_derived_financials is present, use its "
        "gross_revenue, transport_cost, and computed_net_profit (formula (price_per_kg × quantity_kg) − transport_cost "
        "using those numeric fields)—do not trust net_profit_estimate or stale per-buyer net_profit literals if they disagree. "
        "Never quote a headline net-profit figure as ₹0; if computed_net_profit is negative, state the negative rupee amount "
        "and prepend the correct-language string from negative_margin_warning_text matching the farmer's script (⚠️ transport exceeds crop value). "
        "If computed_net_profit equals zero because revenue equals transport (break-even), say surplus is absorbed by transport "
        "instead of saying ₹0 net profit."
    )


async def get_profit_recommendation(
    farmer_name=None,
    district=None,
    language=None,
    crop_type=None,
    quantity_kg=None,
    expected_harvest_date=None,
    weather_summary=None,
    apmc_price=None,
    buyers=None,
    field_data=None,
    **kwargs
):
    lang_name = LANG_NAMES.get(language, "Kannada")

    try:
        client = genai.Client(api_key=settings.gemini_api_key)

        buyers_summary = json.dumps(
            [{"index": i, "name": b["name"], "district": b["district"],
              "distance_km": round(b["distance_km"], 1),
              "transport_cost": round(b["transport_cost"], 0),
              "net_profit": round(b["net_profit"], 0)}
             for i, b in enumerate(buyers or [])],
            indent=2
        )

        field_info = ""
        if field_data:
            field_info = f"\nField Data: stage={field_data.get('crop_stage')}, health={field_data.get('field_health')}, source={field_data.get('source')}"

        prompt = f"""You are KhetIQ, an expert agricultural AI advisor for Indian farmers.

Farmer: {farmer_name} | District: {district} | Crop: {crop_type}
Quantity: {quantity_kg} kg | Expected Harvest: {expected_harvest_date}
Weather (7-day forecast): {weather_summary}
APMC Mandi Price: ₹{apmc_price}/kg{field_info}

Available Buyers (ranked by distance):
{buyers_summary}

Analyze this data and return ONLY valid JSON (no markdown fences, no extra text):
{{
  "resilience_index": <integer 0-100, crop viability score>,
  "risk_level": "<low|medium|high>",
  "best_buyer_index": <integer, index of best buyer from array above>,
  "net_profit_best": <number, net profit in INR for best buyer>,
  "harvest_urgency": "<normal|urgent>",
  "urgency_reason": <string or null, reason if urgent>,
  "reasoning_local": "<Detailed 3-4 sentence analysis written in {lang_name} language. Explain exactly WHY the recommended buyer is the best choice (factoring in transport cost vs APMC price), how the current weather impacts the crop, and what the farmer should do right now. Use simple, conversational language suitable for a farmer.>",
  "price_tip": "<Actionable pricing advice in {lang_name} language. E.g., 'Hold for 3 days due to rain' or 'Lock deal today to save ₹200 on transport'.>"
}}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?", "", text).strip()
        return json.loads(text)

    except Exception as e:
        print(f"Gemini API error: {e}, using fallback")
        return _fallback(buyers, weather_summary, apmc_price, lang_name)


def _fallback(buyers, weather_summary, apmc_price, lang_name="Kannada"):
    if not buyers:
        return {
            "resilience_index": 75,
            "risk_level": "low",
            "best_buyer_index": -1,
            "net_profit_best": 0,
            "harvest_urgency": "normal",
            "urgency_reason": None,
            "reasoning_local": "No buyers available in the system.",
            "price_tip": "Check local APMC market rates.",
        }

    best_idx, best_profit = 0, 0
    for i, b in enumerate(buyers):
        if b.get("net_profit", 0) > best_profit:
            best_profit = b["net_profit"]
            best_idx = i

    weather_text = (weather_summary or "").lower()
    has_rain = any(k in weather_text for k in ["heavy rain", "moderate rain"])
    resilience = 50 if has_rain else 75
    buyer_name = buyers[best_idx].get("name", "Unknown")

    # Simple local-language fallback strings
    # Detailed local-language fallback strings
    if lang_name == "Kannada":
        reasoning = f"ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಬೆಳೆ ವಿಶ್ಲೇಷಣೆ ಇಲ್ಲಿದೆ: {'ಮುಂಬರುವ ದಿನಗಳಲ್ಲಿ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಇರುವುದರಿಂದ ದಯವಿಟ್ಟು ಬೇಗನೆ ಮಾರಾಟ ಮಾಡಿ.' if has_rain else 'ಹವಾಮಾನವು ಪ್ರಸ್ತುತ ಉತ್ತಮವಾಗಿದೆ, ಆದ್ದರಿಂದ ನೀವು ಸುರಕ್ಷಿತವಾಗಿದ್ದೀರಿ.'} ನಾವು {buyer_name} ಅನ್ನು ಆಯ್ಕೆ ಮಾಡಿದ್ದೇವೆ ಏಕೆಂದರೆ ಸಾರಿಗೆ ವೆಚ್ಚದ ನಂತರ ಇದು ನಿಮಗೆ ಗರಿಷ್ಠ ₹{best_profit:.0f} ನಿವ್ವಳ ಲಾಭವನ್ನು ನೀಡುತ್ತದೆ. ಇದು ನಿಮ್ಮ ಹತ್ತಿರವಿರುವ ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ ಆಯ್ಕೆಯಾಗಿದೆ."
        tip = f"ಸಲಹೆ: ಮಾರುಕಟ್ಟೆ ದರವು ಪ್ರಸ್ತುತ ₹{apmc_price}/kg ಇದೆ. ಸಾರಿಗೆ ವೆಚ್ಚವನ್ನು ಉಳಿಸಲು {buyers[best_idx]['district']} ನ ಖರೀದಿದಾರರಿಗೆ ನೀಡಿ."
    elif lang_name == "Hindi":
        reasoning = f"नमस्ते! यहाँ आपका फसल विश्लेषण है: {'आने वाले दिनों में बारिश की संभावना है, इसलिए कृपया अपनी फसल जल्दी बेचें।' if has_rain else 'मौसम वर्तमान में अनुकूल है, इसलिए आपकी फसल सुरक्षित है।'} हमने {buyer_name} को चुना है क्योंकि परिवहन लागत के बाद यह आपको अधिकतम ₹{best_profit:.0f} का शुद्ध लाभ देता है। यह आपके आस-पास सबसे अच्छा बाजार विकल्प है।"
        tip = f"सलाह: बाजार भाव अभी ₹{apmc_price}/kg है। परिवहन लागत बचाने के लिए {buyers[best_idx]['district']} में खरीदार को चुनें।"
    else:
        reasoning = f"Hello! Here is your crop analysis: {'Due to the upcoming rain forecast, I strongly advise selling your crop urgently to prevent damage.' if has_rain else 'The weather conditions are currently favorable, so your harvest is safe.'} I have selected {buyer_name} as your best buyer because, even after transport costs, they provide the highest net profit of ₹{best_profit:.0f}. This ensures you get the absolute best return for your hard work."
        tip = f"Tip: The current APMC market rate is ₹{apmc_price}/kg. Locking the deal with the buyer in {buyers[best_idx]['district']} minimizes your transport expenses."

    return {
        "resilience_index": resilience,
        "risk_level": "low" if resilience > 70 else "medium",
        "best_buyer_index": best_idx,
        "net_profit_best": best_profit,
        "harvest_urgency": "urgent" if has_rain else "normal",
        "urgency_reason": "Heavy rain forecast may damage unharvested crop." if has_rain else None,
        "reasoning_local": reasoning,
        "price_tip": tip,
    }


async def get_copilot_response(
    user_type: str,
    user_name: str,
    language: str,
    context: dict,
    message: str,
    apmc_prices: dict = None,
) -> dict:
    """
    KhetIQ AI Copilot — conversational advisor for farmers and buyers.
    Returns response text + 3 quick-reply suggestions in the farmer's language.
    """
    full_context = context or {}

    task_prompt = f"""{_format_copilot_user_question_block(message)}

Respond for participant: {user_name} ({user_type}).

Then provide EXACTLY 3 short follow-up questions the user might want to ask next (in the detected language, max 8 words each).

Return ONLY valid JSON (no markdown fences):
{{
  "response": "<your advice>",
  "suggestions": ["<question 1>", "<question 2>", "<question 3>"]
}}"""
    prompt = _copilot_user_contents_after_system(task_prompt)

    try:
        sys_ins = _copilot_system_instruction(full_context)
        # #region agent log
        _agent_debug_log(
            "H4",
            "gemini_service.py:get_copilot_response",
            "pre_request",
            {
                "language": language,
                "context_key_count": len(full_context),
                "context_keys": list(full_context.keys())[:40],
                "message_len": len(message),
                "system_instruction_len": len(sys_ins),
                "user_prompt_len": len(prompt),
            },
        )
        # #endregion
        copilot_key = settings.copilot_api_key or settings.gemini_api_key
        if not copilot_key or "your_gemini_api_key" in copilot_key:
            raise ValueError("Invalid API key. Please set COPILOT_API_KEY in .env")

        client = genai.Client(api_key=copilot_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=sys_ins,
            ),
        )
        if not resp or not resp.text:
            # #region agent log
            _agent_debug_log("H2", "gemini_service.py:get_copilot_response", "empty_gemini_text", {"has_resp": resp is not None})
            # #endregion
            raise ValueError("Empty response from Gemini")
        text = resp.text.strip()
        # #region agent log
        _agent_debug_log(
            "H1",
            "gemini_service.py:get_copilot_response",
            "raw_model_text",
            {"text_len": len(text), "prefix": text[:500]},
        )
        # #endregion
        data, parse_mode = _parse_gemini_json_object(text)
        # #region agent log
        _agent_debug_log(
            "H1",
            "gemini_service.py:get_copilot_response",
            "parse_ok",
            {
                "parse_mode": parse_mode,
                "has_response": bool(data.get("response")),
                "suggestion_n": len(data.get("suggestions") or []),
            },
        )
        # #endregion
        return {
            "response": data.get("response", ""),
            "suggestions": data.get("suggestions", [])[:3],
        }
    except Exception as e:
        # #region agent log
        _agent_debug_log(
            "H3",
            "gemini_service.py:get_copilot_response",
            "copilot_error",
            {"exc_type": type(e).__name__, "exc": str(e)[:800], "language": language},
        )
        # #endregion
        print(f"Copilot error: {e}")
        if language == "kn":
            fallback = "ನಾನು ಈಗ ಉತ್ತರಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
            sugg = ["ಈ ಬೆಲೆ ಸರಿಯಾಗಿದೆಯೇ?", "ಯಾವ ಬೆಳೆ ಉತ್ತಮ?", "ಸಾರಿಗೆ ವೆಚ್ಚ ಎಷ್ಟು?"]
        elif language == "hi":
            fallback = "अभी उत्तर नहीं दे सकता। कृपया फिर से प्रयास करें।"
            sugg = ["क्या यह दाम सही है?", "कौन सी फसल बेहतर?", "ट्रांसपोर्ट लागत कितनी?"]
        else:
            fallback = "I'm unable to respond right now. Please try again."
            sugg = ["Is this price fair?", "Which crop is best now?", "What is transport cost?"]
        return {"response": fallback, "suggestions": sugg}


async def get_copilot_voice_response(
    user_type: str,
    language: str,
    audio_bytes: bytes,
    context: dict,
    apmc_prices: dict
):
    """Processes audio and returns an AI response in JSON format."""
    
    full_context = context or {}
    voice_example = _format_copilot_user_question_block(
        "[REPLACE THIS BRACKETED TEXT WITH THE VERBATIM TRANSCRIPTION FROM STEP 1]"
    )
    task_prompt = f"""The user ({user_type}) sent a voice message.
1. Transcribe it exactly.
2. Answer as if they typed the following line verbatim (substitute only the bracketed segment with step 1's transcription — keep everything else unchanged):
{voice_example}
3. Provide EXACTLY 3 short follow-up questions the user might want to ask next (in the detected language, max 8 words each).

Return ONLY valid JSON (no markdown fences):
{{
  "transcription": "<what the user said>",
  "response": "<your advice>",
  "suggestions": ["<q1>", "<q2>", "<q3>"]
}}"""
    prompt = _copilot_user_contents_after_system(task_prompt)

    try:
        sys_ins = _copilot_system_instruction(full_context)
        # #region agent log
        _agent_debug_log(
            "H4",
            "gemini_service.py:get_copilot_voice_response",
            "pre_request",
            {
                "language": language,
                "context_key_count": len(full_context),
                "audio_bytes": len(audio_bytes),
                "system_instruction_len": len(sys_ins),
            },
        )
        # #endregion
        copilot_key = settings.copilot_api_key or settings.gemini_api_key
        client = genai.Client(api_key=copilot_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
            ],
            config=genai.types.GenerateContentConfig(
                system_instruction=sys_ins,
            ),
        )
        if not resp or not resp.text:
            # #region agent log
            _agent_debug_log("H2", "gemini_service.py:get_copilot_voice_response", "empty_gemini_text", {})
            # #endregion
            raise ValueError("Empty response from Gemini")
            
        text = resp.text.strip()
        # #region agent log
        _agent_debug_log(
            "H1",
            "gemini_service.py:get_copilot_voice_response",
            "raw_model_text",
            {"text_len": len(text), "prefix": text[:500]},
        )
        # #endregion
        data, parse_mode = _parse_gemini_json_object(text)
        # #region agent log
        _agent_debug_log(
            "H1",
            "gemini_service.py:get_copilot_voice_response",
            "parse_ok",
            {"parse_mode": parse_mode, "keys": list(data.keys())},
        )
        # #endregion
        return data
    except Exception as e:
        # #region agent log
        _agent_debug_log(
            "H3",
            "gemini_service.py:get_copilot_voice_response",
            "voice_copilot_error",
            {"exc_type": type(e).__name__, "exc": str(e)[:800], "language": language},
        )
        # #endregion
        print(f"Voice Copilot error: {e}")
        return {
            "transcription": "Unable to transcribe audio.",
            "response": "I'm unable to process your voice message right now. Please try typing your question.",
            "suggestions": ["Is this price fair?", "Which crop is best now?", "What is transport cost?"]
        }


async def transcribe_audio_with_gemini(audio_bytes: bytes, language: str):
    """Transcribes short audio clips to text."""
    lang_name = LANG_NAMES.get(language, "English")
    prompt = f"Transcribe this voice message exactly as spoken in {lang_name}. If it's a number, return it as digits. Return ONLY the transcribed text."

    try:
        copilot_key = settings.copilot_api_key or settings.gemini_api_key
        client = genai.Client(api_key=copilot_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
            ]
        )
        return resp.text.strip() if resp.text else ""
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
