import asyncio
import httpx

BASE_URL = "http://localhost:8000/api"

async def check():
    async with httpx.AsyncClient() as client:
        try:
            farmers = await client.get(f"{BASE_URL}/farmers/")
            buyers = await client.get(f"{BASE_URL}/buyers/")
            crops = await client.get(f"{BASE_URL}/crops/")
            deals = await client.get(f"{BASE_URL}/deals/")
            
            print(f"Farmers: {len(farmers.json())}")
            for f in farmers.json():
                print(f" - {f['name']} ({f['phone']})")
                
            print(f"Buyers: {len(buyers.json())}")
            for b in buyers.json():
                print(f" - {b['name']} ({b['phone']})")
                
            print(f"Crops: {len(crops.json())}")
            print(f"Deals: {len(deals.json())}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
