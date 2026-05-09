import os
import json
import re
from google import genai
from app.config import settings

LANG_NAMES = {
    "kn": "Kannada",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "mr": "Marathi",
    "en": "English",
}


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
            model="gemini-2.0-flash-lite",
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
    lang_name = LANG_NAMES.get(language, "Kannada")
    apmc_prices = apmc_prices or {}

    recent_deals_str = ""
    if context.get("recent_deals"):
        recent_deals_str = "Recent deals: " + "; ".join(
            f"{d['crop']} ₹{d['price']}/kg {d['qty']}kg [{d['status']}]"
            for d in context["recent_deals"][:3]
        )

    crop_ctx = ""
    if context.get("crop_type"):
        apmc = apmc_prices.get(context["crop_type"].lower(), "unknown")
        crop_ctx = f"Current crop: {context['crop_type']}, quantity: {context.get('quantity_kg','?')}kg, APMC rate: ₹{apmc}/kg"

    role = "farmer selling crops" if user_type == "farmer" else "agricultural buyer sourcing crops"

    prompt = f"""You are KhetIQ Copilot, an expert AI advisor for Indian agriculture.
You are helping {user_name}, a {role} in Karnataka.
{crop_ctx}
{recent_deals_str}

The user asks (in their words): "{message}"

Respond in {lang_name} language with practical, concise advice (2-3 sentences max).
Then provide EXACTLY 3 short follow-up questions the user might want to ask next (in {lang_name}, max 8 words each).

Return ONLY valid JSON (no markdown fences):
{{
  "response": "<your advice in {lang_name}>",
  "suggestions": ["<question 1>", "<question 2>", "<question 3>"]
}}"""

    try:
        copilot_key = settings.copilot_api_key or settings.gemini_api_key
        if not copilot_key or "your_gemini_api_key" in copilot_key:
            raise ValueError("Invalid API key. Please set COPILOT_API_KEY in .env")

        client = genai.Client(api_key=copilot_key)
        resp = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        if not resp or not resp.text:
            raise ValueError("Empty response from Gemini")
        text = resp.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`")
        data = json.loads(text)
        return {
            "response": data.get("response", ""),
            "suggestions": data.get("suggestions", [])[:3],
        }
    except Exception as e:
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
    lang_name = LANG_NAMES.get(language, "English")
    role = "farmer selling crops" if user_type == "farmer" else "agricultural buyer sourcing crops"
    
    prompt = f"""You are KhetIQ Copilot, an expert AI advisor for Indian agriculture.
You are helping a {role} in Karnataka.

The user has sent a voice message.
1. Transcribe the voice message.
2. Based on the transcription, provide practical advice in {lang_name} (2-3 sentences max).
3. Provide 3 short follow-up questions in {lang_name}.

Return ONLY valid JSON:
{{
  "transcription": "<what the user said>",
  "response": "<your advice in {lang_name}>",
  "suggestions": ["<q1>", "<q2>", "<q3>"]
}}"""

    try:
        copilot_key = settings.copilot_api_key or settings.gemini_api_key
        client = genai.Client(api_key=copilot_key)
        resp = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
            ]
        )
        if not resp or not resp.text:
            raise ValueError("Empty response from Gemini")
            
        text = resp.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`")
        data = json.loads(text)
        return data
    except Exception as e:
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
            model="gemini-2.0-flash-lite",
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm")
            ]
        )
        return resp.text.strip() if resp.text else ""
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""