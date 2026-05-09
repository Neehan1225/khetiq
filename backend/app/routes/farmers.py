from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.farmer import Farmer
from app.auth import create_access_token
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter()

class FarmerCreate(BaseModel):
    name: str
    phone: str
    location_lat: float
    location_lng: float
    district: str
    state: str = "Karnataka"
    language: str = "kn"


class FarmerLogin(BaseModel):
    phone: str


@router.get("/check-phone")
async def check_farmer_phone(number: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.phone == number))
    exists = result.scalar_one_or_none() is not None
    return {"exists": exists}


@router.post("/")
async def create_farmer(farmer: FarmerCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate phone first
    existing = await db.execute(select(Farmer).where(Farmer.phone == farmer.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Phone number already registered as farmer")
    try:
        db_farmer = Farmer(**farmer.model_dump())
        db.add(db_farmer)
        await db.commit()
        await db.refresh(db_farmer)
        return db_farmer
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Phone number already registered")

@router.post("/login")
async def farmer_login(body: FarmerLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate a farmer by phone and return a signed JWT."""
    result = await db.execute(select(Farmer).where(Farmer.phone == body.phone))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid phone number")
    access_token = create_access_token(user_id=str(farmer.id), role="farmer")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "farmer_id": str(farmer.id),
        "name": farmer.name,
        "role": "farmer",
    }


@router.get("/")
async def get_farmers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer))
    return result.scalars().all()

@router.get("/districts", response_model=List[str])
async def get_farmer_districts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer.district).distinct())
    return [d for d in result.scalars().all() if d]

@router.get("/{farmer_id}")
async def get_farmer(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
        
    from app.models.deal import Deal
    from sqlalchemy import func as sqlfunc
    
    completed = await db.execute(
        select(sqlfunc.count(Deal.id)).where(Deal.farmer_id == farmer_id, Deal.deal_status == 'completed')
    )
    completed_deals = completed.scalar_one()
    
    attempted = await db.execute(
        select(sqlfunc.count(Deal.id)).where(Deal.farmer_id == farmer_id, Deal.deal_status.in_(['completed', 'failed', 'locked', 'accepted']))
    )
    attempted_deals = attempted.scalar_one()
    
    score = 100.0
    if attempted_deals > 0:
        score = round((completed_deals / attempted_deals) * 100, 1)
        
    farmer_data = {c.name: getattr(farmer, c.name) for c in farmer.__table__.columns}
    farmer_data["fulfillment_reliability_score"] = score
    return farmer_data