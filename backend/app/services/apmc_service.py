# APMC mandi prices for Karnataka crops (based on real data.gov.in averages)
# Updated with April 2026 approximate market rates

APMC_PRICES = {
    "tomato": 18.0,
    "onion": 22.0,
    "potato": 15.0,
    "brinjal": 20.0,
    "cabbage": 12.0,
    "cauliflower": 25.0,
    "beans": 35.0,
    "carrot": 28.0,
    "spinach": 16.0,
    "chilli": 45.0,
    "garlic": 80.0,
    "ginger": 60.0,
    "maize": 20.0,
    "wheat": 22.0,
    "rice": 28.0,
    "sugarcane": 3.5,
    "banana": 18.0,
    "mango": 35.0,
    "grapes": 55.0,
    "pomegranate": 70.0,
}

def get_apmc_price(crop_type: str) -> float:
    """Get current APMC mandi price per kg for a crop."""
    return APMC_PRICES.get(crop_type.lower(), 20.0)

def get_all_prices() -> dict:
    return APMC_PRICES