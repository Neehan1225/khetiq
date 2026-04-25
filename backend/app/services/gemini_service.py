import os
import json
import re
from google import genai

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
    **kwargs
):
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        prompt = f"""Analyze crop {crop_type} for farmer {farmer_name} in {district}.
Weather: {weather_summary}
APMC Price: ₹{apmc_price}/kg
Quantity: {quantity_kg}kg
Buyers: {buyers}
Return JSON with resilience_index, risk_level, best_buyer_index, net_profit_best, harvest_urgency, urgency_reason, reasoning_local, price_tip"""
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except Exception as e:
        print(f"Gemini API error: {e}, using fallback")
        
        if not buyers:
            return {
                "resilience_index": 75,
                "risk_level": "low",
                "best_buyer_index": -1,
                "net_profit_best": 0,
                "harvest_urgency": "normal",
                "urgency_reason": None,
                "reasoning_local": "No buyers available",
                "price_tip": "Check local market rates"
            }
        
        best_idx = 0
        best_profit = 0
        for i, b in enumerate(buyers):
            profit = b.get("net_profit", 0)
            if profit > best_profit:
                best_profit = profit
                best_idx = i

        weather_text = weather_summary if weather_summary else ""
        rain_keywords = ["heavy rain", "moderate rain"]
        has_rain = any(k in weather_text.lower() for k in rain_keywords)
        resilience = 75 if not has_rain else 50

        buyer_name = buyers[best_idx].get('name', 'Unknown') if buyers else 'Unknown'

        return {
            "resilience_index": resilience,
            "risk_level": "low" if resilience > 70 else "medium",
            "best_buyer_index": best_idx,
            "net_profit_best": best_profit,
            "harvest_urgency": "urgent" if has_rain else "normal",
            "urgency_reason": "Rain forecast may damage crop" if has_rain else None,
            "reasoning_local": f"{'ಮಳೆ ಅಪಾಯವಿದೆ, ಬೇಗ ಮಾರಾಟ ಮಾಡಿ.' if has_rain else 'ಹವಾಮಾನ ಉತ್ತಮವಾಗಿದೆ, ಉತ್ತಮ ಬೆಲೆಗೆ ಮಾರಾಟ ಮಾಡಿ.'} Best buyer: {buyer_name} at ₹{best_profit:.0f} net profit.",
            "price_tip": f"Current APMC rate is ₹{apmc_price}/kg. Transport to {buyers[best_idx]['district']} recommended."
        }