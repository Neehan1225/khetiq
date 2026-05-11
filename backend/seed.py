import asyncio
import httpx

BASE_URL = "http://13.49.74.167:8000/api"

async def seed():
    async with httpx.AsyncClient() as client:

        # Create farmers
        farmers_data = [
            {"name": "Raju Patil", "phone": "9876543210", "location_lat": 15.8497, "location_lng": 74.4977, "district": "Belagavi", "state": "Karnataka", "language": "kn"},
            {"name": "Suresh Gowda", "phone": "9845123456", "location_lat": 15.3647, "location_lng": 75.1240, "district": "Dharwad", "state": "Karnataka", "language": "kn"},
            {"name": "Meera Desai", "phone": "9731234567", "location_lat": 14.4673, "location_lng": 75.9199, "district": "Davanagere", "state": "Karnataka", "language": "kn"},
        ]

        farmer_ids = []
        for f in farmers_data:
            res = await client.post(f"{BASE_URL}/farmers/", json=f)
            farmer_ids.append(res.json()["id"])
            print(f"Created farmer: {f['name']}")

        # Create buyers
        buyers_data = [
            {"name": "Hubli Fresh Mart", "type": "supermarket", "phone": "9900112233", "location_lat": 15.3647, "location_lng": 75.1240, "district": "Dharwad"},
            {"name": "Bengaluru Organic Hub", "type": "trader", "phone": "9900445566", "location_lat": 12.9716, "location_lng": 77.5946, "district": "Bengaluru"},
            {"name": "Hotel Nisarga Kitchen", "type": "restaurant", "phone": "9900778899", "location_lat": 15.8497, "location_lng": 74.4977, "district": "Belagavi"},
        ]

        buyer_ids = []
        for b in buyers_data:
            res = await client.post(f"{BASE_URL}/buyers/", json=b)
            buyer_ids.append(res.json()["id"])
            print(f"Created buyer: {b['name']}")

        # Create crops
        crops_data = [
            {"farmer_id": farmer_ids[0], "crop_type": "tomato", "quantity_kg": 800, "field_size_acres": 2.5, "sowing_date": "2026-03-01", "expected_harvest_date": "2026-05-02"},
            {"farmer_id": farmer_ids[1], "crop_type": "onion", "quantity_kg": 1200, "field_size_acres": 3.0, "sowing_date": "2026-02-15", "expected_harvest_date": "2026-04-30"},
            {"farmer_id": farmer_ids[2], "crop_type": "potato", "quantity_kg": 600, "field_size_acres": 1.8, "sowing_date": "2026-03-10", "expected_harvest_date": "2026-05-05"},
        ]

        crop_ids = []
        for c in crops_data:
            res = await client.post(f"{BASE_URL}/crops/", json=c)
            crop_ids.append(res.json()["id"])
            print(f"Created crop: {c['crop_type']}")

        print("\n✅ Seed complete. Database has real Karnataka farmer data.")
        print(f"Farmer IDs: {farmer_ids}")
        print(f"Buyer IDs: {buyer_ids}")
        print(f"Crop IDs: {crop_ids}")

if __name__ == "__main__":
    asyncio.run(seed())