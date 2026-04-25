import httpx
from datetime import date, timedelta
from app.config import settings

async def get_field_data(lat: float, lng: float, crop_type: str) -> dict:
    """
    Call Google AMED API to get crop monitoring data.
    Falls back to intelligent estimation if API key not available.
    """

    if settings.amed_api_key and settings.amed_api_key != "your_amed_api_key_here":
        try:
            url = "https://agrimonitoring.googleapis.com/v1/fields:query"
            headers = {"Authorization": f"Bearer {settings.amed_api_key}"}
            payload = {
                "location": {"latitude": lat, "longitude": lng},
                "cropType": crop_type,
                "requestedData": ["HARVEST_DATE", "CROP_STAGE", "FIELD_HEALTH"]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "amed_confirmed": True,
                        "crop_stage": data.get("cropStage", "unknown"),
                        "field_health": data.get("fieldHealth", "good"),
                        "predicted_harvest": data.get("harvestDate"),
                        "source": "AMED_API"
                    }
        except Exception:
            pass

    # Intelligent fallback based on crop type
    harvest_days = {
        "tomato": 75, "onion": 90, "potato": 80,
        "brinjal": 70, "cabbage": 65, "cauliflower": 70,
        "beans": 55, "carrot": 75, "chilli": 90,
        "maize": 110, "wheat": 120, "rice": 130,
        "banana": 180, "mango": 120, "grapes": 150,
    }

    days = harvest_days.get(crop_type.lower(), 80)
    predicted = date.today() + timedelta(days=days // 3)

    return {
        "amed_confirmed": False,
        "crop_stage": "mid_season",
        "field_health": "good",
        "predicted_harvest": predicted.isoformat(),
        "source": "KhetIQ_ESTIMATE"
    }