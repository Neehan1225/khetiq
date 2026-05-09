import httpx
from datetime import date, timedelta

WMO_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

def wmo_icon(code):
    for k in sorted(WMO_ICONS.keys(), reverse=True):
        if code >= k:
            return WMO_ICONS[k]
    return "🌡️"

async def get_weather_data(lat: float, lng: float) -> dict:
    """Returns structured 7-day weather data + summary string."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,weathercode"
        f"&forecast_days=7&timezone=Asia/Kolkata"
    )
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            data = res.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        precip = daily.get("precipitation_sum", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        codes = daily.get("weathercode", [])

        days = []
        for i in range(len(dates)):
            code = int(codes[i]) if i < len(codes) else 0
            days.append({
                "date": dates[i],
                "icon": wmo_icon(code),
                "max_temp": round(temps_max[i], 1) if i < len(temps_max) else 30,
                "min_temp": round(temps_min[i], 1) if i < len(temps_min) else 22,
                "rain_mm": round(precip[i], 1) if i < len(precip) else 0,
            })

        total_rain = sum(precip) if precip else 0
        avg_temp = sum(temps_max) / len(temps_max) if temps_max else 30

        if total_rain > 50:
            condition = "heavy rain expected"
        elif total_rain > 20:
            condition = "moderate rain expected"
        elif total_rain > 5:
            condition = "light rain possible"
        else:
            condition = "dry and clear"

        summary = f"{condition}, avg max temp {avg_temp:.1f}°C, total rainfall {total_rain:.1f}mm over 7 days"
        return {"summary": summary, "days": days}

    except Exception:
        days_fallback = []
        for i in range(7):
            d = date.today() + timedelta(days=i)
            days_fallback.append({
                "date": d.isoformat(), "icon": "🌡️",
                "max_temp": 30, "min_temp": 22, "rain_mm": 0,
            })
        return {
            "summary": "weather data unavailable, assume normal conditions",
            "days": days_fallback,
        }

async def get_weather_summary(lat: float, lng: float) -> str:
    """Backward-compatible: returns just the summary string."""
    data = await get_weather_data(lat, lng)
    return data["summary"]