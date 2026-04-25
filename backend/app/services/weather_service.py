import httpx

async def get_weather_summary(lat: float, lng: float) -> str:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        f"&daily=precipitation_sum,temperature_2m_max,weathercode"
        f"&forecast_days=7&timezone=Asia/Kolkata"
    )
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=10)
            data = res.json()

        daily = data.get("daily", {})
        precip = daily.get("precipitation_sum", [])
        temps = daily.get("temperature_2m_max", [])

        total_rain = sum(precip) if precip else 0
        avg_temp = sum(temps) / len(temps) if temps else 30

        if total_rain > 50:
            condition = "heavy rain expected"
        elif total_rain > 20:
            condition = "moderate rain expected"
        elif total_rain > 5:
            condition = "light rain possible"
        else:
            condition = "dry and clear"

        return f"{condition}, avg max temp {avg_temp:.1f}°C, total rainfall {total_rain:.1f}mm over 7 days"

    except Exception:
        return "weather data unavailable, assume normal conditions"