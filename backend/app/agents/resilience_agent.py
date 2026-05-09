from app.services.gemini_service import get_profit_recommendation
from app.services.weather_service import get_weather_data
from app.services.maps_service import get_distance_and_cost
from app.services.apmc_service import get_apmc_price
from app.services.amed_service import get_field_data


async def run_resilience_agent(farmer, crop, buyers, lang=None):
    """
    Core KhetIQ agent. Takes farmer, crop, and nearby buyers.
    Returns full AI recommendation with resilience index + weather days + buyer coords.
    """

    # Step 1: Get real weather for farmer's location (structured + summary)
    weather_data = await get_weather_data(farmer.location_lat, farmer.location_lng)
    weather = weather_data["summary"]
    weather_days = weather_data["days"]

    # Step 2: Get real APMC mandi price
    apmc_price = get_apmc_price(crop.crop_type)

    # Step 3: Get satellite/field data from AMED (falls back to estimate if no API key)
    field_data = await get_field_data(farmer.location_lat, farmer.location_lng, crop.crop_type)

    # Step 4: Calculate transport cost and net profit for each buyer
    enriched_buyers = []
    for buyer in buyers:
        transport_data = await get_distance_and_cost(
            farmer.location_lat, farmer.location_lng,
            buyer.location_lat, buyer.location_lng,
            crop.quantity_kg
        )

        gross_revenue = apmc_price * crop.quantity_kg
        net_profit = gross_revenue - transport_data["transport_cost"]

        enriched_buyers.append({
            "name": buyer.name,
            "type": buyer.type,
            "district": buyer.district,
            "distance_km": transport_data["distance_km"],
            "transport_cost": transport_data["transport_cost"],
            "net_profit": net_profit,
            "buyer_id": str(buyer.id),
            "location_lat": buyer.location_lat,
            "location_lng": buyer.location_lng,
        })

    # Step 5: Send everything to Gemini for reasoning
    harvest_date = str(crop.expected_harvest_date) if crop.expected_harvest_date else "unknown"

    ai_result = await get_profit_recommendation(
        farmer_name=farmer.name,
        district=farmer.district,
        language=lang or farmer.language,
        crop_type=crop.crop_type,
        quantity_kg=crop.quantity_kg,
        expected_harvest_date=harvest_date,
        weather_summary=weather,
        apmc_price=apmc_price,
        buyers=enriched_buyers,
        field_data=field_data,
    )

    # Step 6: Build final response
    best_idx = ai_result.get("best_buyer_index", 0)
    if not enriched_buyers:
        best_buyer = None
    elif best_idx < 0 or best_idx >= len(enriched_buyers):
        best_idx = 0
        best_buyer = enriched_buyers[0]
    else:
        best_buyer = enriched_buyers[best_idx]

    return {
        "farmer": farmer.name,
        "farmer_lat": farmer.location_lat,
        "farmer_lng": farmer.location_lng,
        "crop": crop.crop_type,
        "quantity_kg": crop.quantity_kg,
        "apmc_price_per_kg": apmc_price,
        "weather": weather,
        "weather_days": weather_days,
        "field_data": field_data,
        "resilience_index": ai_result.get("resilience_index", 0),
        "risk_level": ai_result.get("risk_level", "medium"),
        "harvest_urgency": ai_result.get("harvest_urgency", "normal"),
        "urgency_reason": ai_result.get("urgency_reason"),
        "best_buyer": best_buyer,
        "net_profit_estimate": ai_result.get("net_profit_best", 0),
        "reasoning": ai_result.get("reasoning_local", ""),
        "price_tip": ai_result.get("price_tip", ""),
        "all_buyers": enriched_buyers,
    }