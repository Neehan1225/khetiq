import httpx
import math
from app.config import settings

def haversine_distance(lat1, lng1, lat2, lng2) -> float:
    """Calculate distance in km between two GPS coordinates."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def calculate_transport_cost(distance_km: float, quantity_kg: float) -> float:
    """Estimate transport cost based on distance and quantity."""
    base_rate_per_km = 12
    if quantity_kg > 500:
        base_rate_per_km = 10
    return round(distance_km * base_rate_per_km, 2)

async def get_distance_and_cost(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
    quantity_kg: float
) -> dict:
    distance_km = haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng)
    transport_cost = calculate_transport_cost(distance_km, quantity_kg)

    # Try Google Maps API if key exists
    if settings.google_maps_api_key and settings.google_maps_api_key != "your_maps_api_key_here":
        try:
            url = (
                f"https://maps.googleapis.com/maps/api/distancematrix/json"
                f"?origins={origin_lat},{origin_lng}"
                f"&destinations={dest_lat},{dest_lng}"
                f"&key={settings.google_maps_api_key}"
            )
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=10)
                data = res.json()
            actual_km = data["rows"][0]["elements"][0]["distance"]["value"] / 1000
            distance_km = actual_km
            transport_cost = calculate_transport_cost(actual_km, quantity_kg)
        except Exception:
            pass  # Fall back to haversine

    return {
        "distance_km": distance_km,
        "transport_cost": transport_cost
    }