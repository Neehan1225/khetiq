import asyncio
import uuid
import random
from datetime import date, datetime, timedelta
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.farmer import Farmer
from app.models.buyer import Buyer
from app.models.crop import Crop
from app.models.deal import Deal
from app.models.review import Review
from app.models.recommendations import Recommendation

async def seed_demo():
    async with AsyncSessionLocal() as session:
        print("Starting Demo Seeding...")

        # 1. Fetch or create Raju Patil (9876543210)
        res = await session.execute(select(Farmer).where(Farmer.phone == "9876543210"))
        raju = res.scalar_one_or_none()
        if not raju:
            raju = Farmer(
                id=uuid.uuid4(),
                name="Raju Patil",
                phone="9876543210",
                location_lat=15.8497,
                location_lng=74.4977,
                village="Kakkanatti",
                district="Belagavi",
                state="Karnataka",
                language="kn"
            )
            session.add(raju)
            await session.flush()
            print("Created Raju Patil (Farmer)")
        else:
            print("Raju Patil already exists")

        # 2. Fetch other demo farmers
        res = await session.execute(select(Farmer).where(Farmer.phone == "9900000000"))
        bhimappa = res.scalar_one_or_none()
        
        res = await session.execute(select(Farmer).where(Farmer.phone == "9900000001"))
        mallikarjun = res.scalar_one_or_none()

        res = await session.execute(select(Farmer).where(Farmer.phone == "9900000021"))
        prashant = res.scalar_one_or_none()

        farmers = [raju]
        if bhimappa: farmers.append(bhimappa)
        if mallikarjun: farmers.append(mallikarjun)
        if prashant: farmers.append(prashant)

        # 3. Fetch or create Hotel Nisarga Kitchen (9900778899)
        res = await session.execute(select(Buyer).where(Buyer.phone == "9900778899"))
        nisarga = res.scalar_one_or_none()
        if not nisarga:
            nisarga = Buyer(
                id=uuid.uuid4(),
                name="Hotel Nisarga Kitchen",
                type="restaurant",
                phone="9900778899",
                location_lat=15.8497,
                location_lng=74.4977,
                district="Belagavi",
                gstin="29NSRG1234F1ZA"
            )
            session.add(nisarga)
            await session.flush()
            print("Created Hotel Nisarga Kitchen (Buyer)")
        else:
            print("Hotel Nisarga Kitchen already exists")

        # 4. Fetch other demo buyers
        res = await session.execute(select(Buyer).where(Buyer.phone == "9900000040"))
        greenbasket = res.scalar_one_or_none()

        res = await session.execute(select(Buyer).where(Buyer.phone == "9900000041"))
        agriexports = res.scalar_one_or_none()

        res = await session.execute(select(Buyer).where(Buyer.phone == "9900000042"))
        agrofreeze = res.scalar_one_or_none()

        buyers = [nisarga]
        if greenbasket: buyers.append(greenbasket)
        if agriexports: buyers.append(agriexports)
        if agrofreeze: buyers.append(agrofreeze)

        # 5. Clear old crops/deals/reviews for these specific demo users to have clean states
        farmer_ids = [f.id for f in farmers]
        buyer_ids = [b.id for b in buyers]

        # Get deals for these users
        res = await session.execute(
            select(Deal).where((Deal.farmer_id.in_(farmer_ids)) | (Deal.buyer_id.in_(buyer_ids)))
        )
        deal_ids = [d.id for d in res.scalars().all()]

        if deal_ids:
            await session.execute(delete(Review).where(Review.deal_id.in_(deal_ids)))
            await session.execute(delete(Deal).where(Deal.id.in_(deal_ids)))
        
        # Delete recommendations referencing these farmer crops
        res_crops = await session.execute(select(Crop.id).where(Crop.farmer_id.in_(farmer_ids)))
        farmer_crop_ids = [c for c in res_crops.scalars().all()]
        if farmer_crop_ids:
            await session.execute(delete(Recommendation).where(Recommendation.crop_id.in_(farmer_crop_ids)))

        await session.execute(delete(Crop).where(Crop.farmer_id.in_(farmer_ids)))
        await session.commit()
        print("Cleared previous demo transactions")

        # 6. Add some Crops for these Farmers
        crops = []
        crop_types = ["Tomato", "Onion", "Chilli", "Pomegranate", "Banana"]
        for f in farmers:
            # 2 crops per farmer
            for ct in random.sample(crop_types, 2):
                c = Crop(
                    id=uuid.uuid4(),
                    farmer_id=f.id,
                    crop_type=ct,
                    quantity_kg=float(random.randint(1000, 5000)),
                    field_size_acres=round(random.uniform(1.5, 4.0), 1),
                    sowing_date=date.today() - timedelta(days=90),
                    expected_harvest_date=date.today() + timedelta(days=30)
                )
                crops.append(c)
                session.add(c)
        await session.flush()
        print(f"Added {len(crops)} crops for demo farmers")

        # 7. Add Deals & Reviews
        # Let's add specific deals for Raju Patil (9876543210)
        # We need completed deals to have reviews, failed/rejected ones for feedback, and negotiating ones for bargaining.
        
        # A. Completed Deals with positive verified reviews
        d1 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=nisarga.id,
            crop_type="Tomato",
            quantity_kg=1500.0,
            agreed_price_per_kg=22.0,
            total_value=33000.0,
            deal_status="completed",
            payment_status="completed",
            expected_delivery_date=date.today() - timedelta(days=5),
            initiated_by="buyer"
        )
        session.add(d1)

        d2 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=greenbasket.id if greenbasket else nisarga.id,
            crop_type="Onion",
            quantity_kg=2000.0,
            agreed_price_per_kg=25.0,
            total_value=50000.0,
            deal_status="completed",
            payment_status="completed",
            expected_delivery_date=date.today() - timedelta(days=12),
            initiated_by="farmer"
        )
        session.add(d2)

        # B. Completed Deal with 3-star rating
        d3 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=agrofreeze.id if agrofreeze else nisarga.id,
            crop_type="Chilli",
            quantity_kg=800.0,
            agreed_price_per_kg=110.0,
            total_value=88000.0,
            deal_status="completed",
            payment_status="completed",
            expected_delivery_date=date.today() - timedelta(days=20),
            initiated_by="buyer"
        )
        session.add(d3)

        # C. Failed Deal (with feedback review)
        d4 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=agriexports.id if agriexports else nisarga.id,
            crop_type="Pomegranate",
            quantity_kg=1000.0,
            agreed_price_per_kg=85.0,
            total_value=85000.0,
            deal_status="failed",
            payment_status="pending",
            expected_delivery_date=date.today() - timedelta(days=8),
            initiated_by="buyer"
        )
        session.add(d4)

        # D. Bargaining / Counter-offered Deal (ongoing)
        # Buyer counter-offered Raju Patil
        d5 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=nisarga.id,
            crop_type="Tomato",
            quantity_kg=1200.0,
            agreed_price_per_kg=20.0,
            counter_price_per_kg=18.5,
            counter_quantity_kg=1200.0,
            counter_by="buyer",
            total_value=24000.0,
            deal_status="counter_offered",
            initiated_by="farmer",
            expected_delivery_date=date.today() + timedelta(days=10)
        )
        session.add(d5)

        # E. Fresh pending offer from Raju Patil to a Buyer
        d6 = Deal(
            id=uuid.uuid4(),
            farmer_id=raju.id,
            buyer_id=greenbasket.id if greenbasket else nisarga.id,
            crop_type="Banana",
            quantity_kg=3000.0,
            agreed_price_per_kg=15.0,
            total_value=45000.0,
            deal_status="pending",
            initiated_by="farmer",
            expected_delivery_date=date.today() + timedelta(days=15)
        )
        session.add(d6)

        # Let's flush so deals get IDs
        await session.flush()

        # Add corresponding Reviews
        # 1. 5-star verified review from Nisarga for Raju Patil
        r1 = Review(
            id=uuid.uuid4(),
            deal_id=d1.id,
            reviewer_type="buyer",
            reviewer_id=nisarga.id,
            reviewee_type="farmer",
            reviewee_id=raju.id,
            rating=5,
            comment="Excellent quality tomatoes. Very polite farmer, delivered exactly on time. Highly recommended!",
            review_type="verified"
        )
        session.add(r1)

        # 2. 4-star verified review from GreenBasket for Raju Patil
        r2 = Review(
            id=uuid.uuid4(),
            deal_id=d2.id,
            reviewer_type="buyer",
            reviewer_id=greenbasket.id if greenbasket else nisarga.id,
            reviewee_type="farmer",
            reviewee_id=raju.id,
            rating=4,
            comment="Onions were well-packed. Quality is good. Payment was done quickly.",
            review_type="verified"
        )
        session.add(r2)

        # 3. 3-star verified review from AgroFreeze for Raju Patil
        r3 = Review(
            id=uuid.uuid4(),
            deal_id=d3.id,
            reviewer_type="buyer",
            reviewer_id=agrofreeze.id if agrofreeze else nisarga.id,
            reviewee_type="farmer",
            reviewee_id=raju.id,
            rating=3,
            comment="Delivery was delayed by a couple of days. Product quality is acceptable.",
            review_type="verified"
        )
        session.add(r3)

        # 4. 2-star feedback review from AgriExports for Raju Patil (due to quality_concern or price_disagreement)
        r4 = Review(
            id=uuid.uuid4(),
            deal_id=d4.id,
            reviewer_type="buyer",
            reviewer_id=agriexports.id if agriexports else nisarga.id,
            reviewee_type="farmer",
            reviewee_id=raju.id,
            rating=2,
            comment="The crop quality did not match the initial specifications agreed upon.",
            review_type="feedback",
            reason="quality_concern"
        )
        session.add(r4)

        # Let's add some reciprocal reviews (Farmer reviews Buyer) so that the buyers also have ratings
        r5 = Review(
            id=uuid.uuid4(),
            deal_id=d1.id,
            reviewer_type="farmer",
            reviewer_id=raju.id,
            reviewee_type="buyer",
            reviewee_id=nisarga.id,
            rating=5,
            comment="Prompt payment on delivery. Very professional team.",
            review_type="verified"
        )
        session.add(r5)

        r6 = Review(
            id=uuid.uuid4(),
            deal_id=d2.id,
            reviewer_type="farmer",
            reviewer_id=raju.id,
            reviewee_type="buyer",
            reviewee_id=greenbasket.id if greenbasket else nisarga.id,
            rating=5,
            comment="Fair pricing and quick confirmation. Will trade again.",
            review_type="verified"
        )
        session.add(r6)

        # 5. Let's add a couple of deals/reviews for other farmers to make the database look rich too
        for other_f in [bhimappa, mallikarjun, prashant]:
            if other_f:
                # Add 1 completed deal
                o_deal = Deal(
                    id=uuid.uuid4(),
                    farmer_id=other_f.id,
                    buyer_id=nisarga.id,
                    crop_type="Onion",
                    quantity_kg=1000.0,
                    agreed_price_per_kg=24.0,
                    total_value=24000.0,
                    deal_status="completed",
                    payment_status="completed",
                    expected_delivery_date=date.today() - timedelta(days=10),
                    initiated_by="buyer"
                )
                session.add(o_deal)
                await session.flush()

                # Add review
                o_rev = Review(
                    id=uuid.uuid4(),
                    deal_id=o_deal.id,
                    reviewer_type="buyer",
                    reviewer_id=nisarga.id,
                    reviewee_type="farmer",
                    reviewee_id=other_f.id,
                    rating=random.choice([4, 5]),
                    comment="Good transaction. Reliable farmer.",
                    review_type="verified"
                )
                session.add(o_rev)

        await session.commit()
        print("✅ Demo seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_demo())
