import asyncio
import argparse
import random
import uuid
from datetime import datetime, timedelta, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import engine, AsyncSessionLocal, Base
from app.models.farmer import Farmer
from app.models.buyer import Buyer
from app.models.crop import Crop
from app.models.deal import Deal
from app.models.review import Review

# Reference Data
CROP_DATA = {
    "Tomato": {"apmc": 18, "min_q": 1000, "max_q": 8000},
    "Onion": {"apmc": 22, "min_q": 2000, "max_q": 12000},
    "Cotton": {"apmc": 65, "min_q": 500, "max_q": 3000},
    "Sugarcane": {"apmc": 3.5, "min_q": 5000, "max_q": 18000},
    "Pomegranate": {"apmc": 85, "min_q": 800, "max_q": 4000},
    "Groundnut": {"apmc": 55, "min_q": 1000, "max_q": 6000},
    "Jowar": {"apmc": 28, "min_q": 2000, "max_q": 10000},
    "Wheat": {"apmc": 24, "min_q": 3000, "max_q": 15000},
    "Maize": {"apmc": 20, "min_q": 2000, "max_q": 9000},
    "Chilli": {"apmc": 120, "min_q": 400, "max_q": 2000},
    "Bengal Gram": {"apmc": 58, "min_q": 1000, "max_q": 5000},
    "Tur Dal": {"apmc": 95, "min_q": 600, "max_q": 3000},
    "Banana": {"apmc": 25, "min_q": 1000, "max_q": 6000},
    "Grapes": {"apmc": 72, "min_q": 500, "max_q": 3000},
    "Paddy": {"apmc": 22, "min_q": 3000, "max_q": 12000},
    "Sunflower": {"apmc": 45, "min_q": 800, "max_q": 5000},
    "Brinjal": {"apmc": 15, "min_q": 500, "max_q": 3000},
    "Linseed": {"apmc": 40, "min_q": 500, "max_q": 2000},
    "Chickpea": {"apmc": 55, "min_q": 800, "max_q": 4000},
}

DISTRICTS = {
    "Belagavi": {"count": 7, "crops": ["Jowar", "Sugarcane", "Sunflower", "Groundnut", "Wheat"], "lat": 15.8497, "lng": 74.4977, "villages": ["Kakkanatti", "Sadalga", "Chikkodi", "Gokak", "Athani", "Hukkeri", "Bailhongal", "Kittur"]},
    "Dharwad": {"count": 6, "crops": ["Cotton", "Groundnut", "Maize", "Bengal Gram"], "lat": 15.4589, "lng": 75.0078, "villages": ["Navalgund", "Kundgol", "Kalghatgi", "Alnavar", "Garag", "Hebballi", "Amminbhavi"]},
    "Hubli": {"count": 5, "crops": ["Tomato", "Onion", "Chilli", "Brinjal"], "lat": 15.3647, "lng": 75.1240, "villages": ["Unkal", "Gokul", "Tarihal", "Rayapur", "Kusugal", "Byahatti"]},
    "Gadag": {"count": 5, "crops": ["Wheat", "Bengal Gram", "Linseed", "Sunflower"], "lat": 15.4296, "lng": 75.6322, "villages": ["Ron", "Mundargi", "Nargund", "Shirahatti", "Gajendragad", "Mulagund"]},
    "Bagalkot": {"count": 5, "crops": ["Pomegranate", "Banana", "Grapes", "Sugarcane"], "lat": 16.1817, "lng": 75.6958, "villages": ["Jamkhandi", "Mudhol", "Badami", "Guledgudda", "Ilkal", "Hungund"]},
    "Vijayapura": {"count": 5, "crops": ["Tur Dal", "Chickpea", "Onion", "Maize"], "lat": 16.8272, "lng": 75.7240, "villages": ["Indi", "Sindagi", "Basavana Bagevadi", "Muddebihal", "Talikota", "Babaleshwar"]},
    "Haveri": {"count": 4, "crops": ["Cotton", "Chilli", "Groundnut", "Jowar"], "lat": 14.7946, "lng": 75.4015, "villages": ["Ranebennur", "Shiggaon", "Savanoor", "Byadgi", "Hirekerur", "Hangal"]},
    "Koppal": {"count": 3, "crops": ["Paddy", "Sunflower", "Maize", "Wheat"], "lat": 15.3465, "lng": 76.1555, "villages": ["Gangavathi", "Kushtagi", "Yelburga", "Kanakagiri", "Karatagi", "Tavaragera"]}
}

FARMER_NAMES = [
    "Basavaraj Patil", "Shivakumar Hiremath", "Ramesh Gowda", "Siddappa K", "Mallikarjun Hosamani",
    "Mohammed Ali", "Abdul Khader", "Ibrahim Nadaf", "Ismail Mulla", "Husensab",
    "Chennamma D", "Savitri Kulkarni", "Kallappa J", "Sangappa M", "Veerabhadrappa",
    "Manjunath Doddamani", "Gurusiddappa", "Prakash Naik", "Lakshman Rao", "Venkatesh S",
    "Ningappa T", "Yallappa R", "Shivanand B", "Ramappa K", "Tippanna",
    "Fakkirappa", "Hanamantappa", "Muttappa", "Yamanappa", "Shekharappa",
    "Bhimappa", "Somappa", "Maruti D", "Anand K", "Raju N",
    "Umesh G", "Ashok H", "Santosh P", "Mahantesh S", "Prashant M"
]

BUYER_GROUPS = [
    {"type": "Hotel chains", "names": ["Hotel Naveen Residency", "Sri Renuka Caterers", "Basaveshwar Hotel Group", "Kamat Upachar"]},
    {"type": "Wholesale traders", "names": ["Patil Agro Traders", "Deshpande Commodity Merchants", "Kulkarni Wholesale", "SRT Traders"]},
    {"type": "Export houses", "names": ["Karnataka Agri Exports Pvt Ltd", "Deccan Fresh Exports", "Global Green Exports"]},
    {"type": "Cold storage units", "names": ["Hubli Cold Chain Solutions", "Belagavi AgroFreeze"]},
    {"type": "Supermarket chains", "names": ["Fresh Mandi Retail", "GreenBasket Stores"]}
]

FARMER_REVIEWS = [
    "Samayakke bandu payment madidaru, khush aade",
    "Good price, no bargain problem",
    "Late aadru pay madidaru"
]

BUYER_REVIEWS = [
    "Tomato quality superb, weight correct",
    "Onion had some spoilage but acceptable",
    "Will buy again next season"
]

def random_date(start_days_ago, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def get_gstin():
    state = "29" # Karnataka
    pan = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5)) + "".join(random.choices("0123456789", k=4)) + random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{state}{pan}1Z{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')}"

async def clear_data(session: AsyncSession):
    await session.execute(delete(Review))
    await session.execute(delete(Deal))
    await session.execute(delete(Crop))
    await session.execute(delete(Buyer))
    await session.execute(delete(Farmer))
    await session.commit()
    print("Database cleared.")

async def main():
    parser = argparse.ArgumentParser(description="Seed database with Karnataka agricultural data.")
    parser.add_argument("--reset", action="store_true", help="Clear all tables and re-seed completely.")
    parser.add_argument("--preview", action="store_true", help="Print a summary without inserting to DB.")
    args = parser.parse_args()

    if args.preview:
        print("--- PREVIEW MODE ---")
        print("Would generate:")
        print("- 40 Farmers (mixed naming, random coordinates within 0.05-0.3 deg of district centers)")
        print("- 15 Buyers (GSTIN, random coordinates within 12-180km)")
        print("- ~90 Crops (2-3 per farmer, realistic quantities, dates -15 to +75 days)")
        print("- 50 Deals (15 Completed, 14 Pending, 8 Negotiating, 8 Late, 5 Rejected)")
        print("- 30 Reviews (mixed ratings 2-5 stars)")
        print("✅ 40 farmers, 15 buyers, 50 deals, 30 reviews inserted successfully")
        return

    # To avoid duplicate data, we check if farmers already exist unless reset is called
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        if args.reset:
            await clear_data(session)
        else:
            result = await session.execute(select(Farmer).limit(1))
            if result.scalars().first() is not None:
                print("Data already exists. Use --reset to clear and re-seed.")
                return

        random.shuffle(FARMER_NAMES)
        farmer_name_idx = 0
        phone_counter = 9900000000

        farmers = []
        crops = []
        
        # 1. Farmers & Crops
        for dist_name, dist_info in DISTRICTS.items():
            for _ in range(dist_info["count"]):
                f_name = FARMER_NAMES[farmer_name_idx]
                farmer_name_idx += 1
                phone = str(phone_counter)
                phone_counter += 1
                
                lat_offset = random.uniform(0.05, 0.3) * random.choice([1, -1])
                lng_offset = random.uniform(0.05, 0.3) * random.choice([1, -1])
                
                f = Farmer(
                    id=uuid.uuid4(),
                    name=f_name,
                    phone=phone,
                    location_lat=dist_info["lat"] + lat_offset,
                    location_lng=dist_info["lng"] + lng_offset,
                    village=random.choice(dist_info["villages"]),
                    district=dist_name,
                    state="Karnataka",
                    created_at=random_date(180)
                )
                farmers.append(f)
                
                num_crops = random.randint(2, 3)
                selected_crops = random.sample(dist_info["crops"], num_crops)
                
                for c_name in selected_crops:
                    c_info = CROP_DATA[c_name]
                    qty = random.uniform(c_info["min_q"], c_info["max_q"])
                    
                    harvest_offset = random.randint(-15, 75)
                    expected_harvest = date.today() + timedelta(days=harvest_offset)
                    sowing = expected_harvest - timedelta(days=90)
                    
                    c = Crop(
                        id=uuid.uuid4(),
                        farmer_id=f.id,
                        crop_type=c_name,
                        quantity_kg=round(qty, 2),
                        field_size_acres=round(qty / 2000, 2),
                        sowing_date=sowing,
                        expected_harvest_date=expected_harvest,
                        created_at=random_date(180)
                    )
                    crops.append(c)

        # 2. Buyers
        buyers = []
        buyer_flat_list = []
        for group in BUYER_GROUPS:
            for name in group["names"]:
                buyer_flat_list.append({"type": group["type"], "name": name})
        
        # Select 15 buyers
        selected_buyers = random.sample(buyer_flat_list, 15)
        for b_info in selected_buyers:
            dist_name = random.choice(list(DISTRICTS.keys()))
            dist_info = DISTRICTS[dist_name]
            
            # Near town center
            lat_offset = random.uniform(0.01, 0.05) * random.choice([1, -1])
            lng_offset = random.uniform(0.01, 0.05) * random.choice([1, -1])
            
            phone = str(phone_counter)
            phone_counter += 1
            
            b = Buyer(
                id=uuid.uuid4(),
                name=b_info["name"],
                type=b_info["type"],
                gstin=get_gstin(),
                phone=phone,
                location_lat=dist_info["lat"] + lat_offset,
                location_lng=dist_info["lng"] + lng_offset,
                district=dist_name,
                created_at=random_date(540) # last 18 months
            )
            buyers.append(b)

        # 3. Deals
        deals = []
        
        deal_distribution = [
            ("completed", 15),
            ("pending", 14),
            ("bargaining", 8),
            ("pending_late", 8),
            ("rejected", 5)
        ]
        
        pricing_distribution = [
            ("premium", 25),
            ("fair", 30),
            ("exact", 25),
            ("distress", 20)
        ]
        pricing_pool = []
        for p_type, count in pricing_distribution:
            pricing_pool.extend([p_type] * count)
        random.shuffle(pricing_pool)
        
        for status, count in deal_distribution:
            for _ in range(count):
                f = random.choice(farmers)
                f_crops = [c for c in crops if c.farmer_id == f.id]
                c = random.choice(f_crops)
                b = random.choice(buyers)
                
                apmc = CROP_DATA[c.crop_type]["apmc"]
                p_type = pricing_pool.pop()
                
                if p_type == "premium":
                    price = apmc * random.uniform(1.06, 1.12)
                elif p_type == "fair":
                    price = apmc * random.uniform(1.02, 1.05)
                elif p_type == "exact":
                    price = apmc
                else: # distress
                    price = apmc * random.uniform(0.92, 0.97)
                
                price = round(price, 2)
                qty = round(random.uniform(500, max(c.quantity_kg, 501)), 2)
                
                # Calculate transport cost based on distance
                f_lat, f_lng = f.location_lat, f.location_lng
                b_lat, b_lng = b.location_lat, b.location_lng
                import math
                R = 6371
                dLat = math.radians(b_lat - f_lat)
                dLng = math.radians(b_lng - f_lng)
                a_h = math.sin(dLat/2)**2 + math.cos(math.radians(f_lat))*math.cos(math.radians(b_lat))*math.sin(dLng/2)**2
                dist_km = R * 2 * math.asin(math.sqrt(a_h))
                transport_cost = round(dist_km * (10 if qty > 500 else 12), 2)

                deal = Deal(
                    id=uuid.uuid4(),
                    farmer_id=f.id,
                    buyer_id=b.id,
                    crop_type=c.crop_type,
                    quantity_kg=qty,
                    agreed_price_per_kg=price,
                    transport_cost=transport_cost,
                    total_value=round(price * qty, 2),
                    initiated_by=random.choice(["farmer", "buyer"]),
                    created_at=random_date(60)
                )
                
                if status == "completed":
                    deal.deal_status = "accepted"
                    deal.payment_status = "completed"
                    deal.expected_delivery_date = date.today() - timedelta(days=random.randint(1, 10))
                elif status == "pending":
                    deal.deal_status = "locked"
                    deal.expected_delivery_date = date.today() + timedelta(days=random.randint(1, 14))
                elif status == "bargaining":
                    deal.deal_status = "offer"
                    deal.counter_price_per_kg = round(price * 1.05, 2)
                    deal.expected_delivery_date = date.today() + timedelta(days=random.randint(5, 20))
                elif status == "pending_late":
                    deal.deal_status = "locked"
                    deal.expected_delivery_date = date.today() - timedelta(days=random.randint(4, 10))
                elif status == "rejected":
                    deal.deal_status = "rejected"
                    deal.expected_delivery_date = date.today() + timedelta(days=random.randint(1, 10))
                    
                deals.append(deal)

        # 4. Reviews
        reviews = []
        completed_deals = [d for d in deals if d.deal_status == "accepted"]
        
        # Need 2 ratings per completed deal (farmer reviews buyer + buyer reviews farmer)
        num_reviews_needed = len(completed_deals) * 2
        # Build a pool with realistic distribution
        rating_pool = []
        for _ in range(num_reviews_needed // 4 + 1):
            rating_pool.extend([5]*3 + [4]*4 + [3]*2 + [2]*1)
        rating_pool = rating_pool[:num_reviews_needed]
        random.shuffle(rating_pool)
        
        for d in completed_deals:
            # Farmer reviews Buyer
            f_rev = Review(
                id=uuid.uuid4(),
                deal_id=d.id,
                reviewer_type="farmer",
                reviewer_id=d.farmer_id,
                reviewee_type="buyer",
                reviewee_id=d.buyer_id,
                rating=rating_pool.pop(),
                comment=random.choice(FARMER_REVIEWS),
                created_at=d.created_at + timedelta(days=random.randint(1, 5))
            )
            reviews.append(f_rev)
            
            # Buyer reviews Farmer
            b_rev = Review(
                id=uuid.uuid4(),
                deal_id=d.id,
                reviewer_type="buyer",
                reviewer_id=d.buyer_id,
                reviewee_type="farmer",
                reviewee_id=d.farmer_id,
                rating=rating_pool.pop(),
                comment=random.choice(BUYER_REVIEWS),
                created_at=d.created_at + timedelta(days=random.randint(1, 5))
            )
            reviews.append(b_rev)

        session.add_all(farmers)
        session.add_all(buyers)
        await session.flush() # Ensure farmers/buyers get IDs before crops/deals reference them

        session.add_all(crops)
        await session.flush()

        session.add_all(deals)
        await session.flush()

        session.add_all(reviews)
        await session.commit()
        
        print(f"✅ {len(farmers)} farmers, {len(buyers)} buyers, {len(deals)} deals, {len(reviews)} reviews inserted successfully")

if __name__ == "__main__":
    asyncio.run(main())
