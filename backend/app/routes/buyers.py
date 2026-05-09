from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.buyer import Buyer
from app.auth import create_access_token
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

class BuyerCreate(BaseModel):
    name: str
    type: str
    phone: str
    location_lat: float
    location_lng: float
    district: str

class BuyerResponse(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    phone: str
    district: str
    location_lat: float
    location_lng: float


class BuyerLogin(BaseModel):
    phone: str


@router.get("/check-phone")
async def check_buyer_phone(number: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer).where(Buyer.phone == number))
    exists = result.scalar_one_or_none() is not None
    return {"exists": exists}


@router.post("/", response_model=BuyerResponse)
async def create_buyer(buyer: BuyerCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Buyer).where(Buyer.phone == buyer.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Phone number already registered as buyer")
    try:
        new_buyer = Buyer(**buyer.model_dump())
        db.add(new_buyer)
        await db.commit()
        await db.refresh(new_buyer)
        return new_buyer
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Phone number already registered")

@router.post("/login")
async def buyer_login(body: BuyerLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate a buyer by phone and return a signed JWT."""
    result = await db.execute(select(Buyer).where(Buyer.phone == body.phone))
    buyer = result.scalar_one_or_none()
    if not buyer:
        raise HTTPException(status_code=401, detail="Invalid phone number")
    access_token = create_access_token(user_id=str(buyer.id), role="buyer")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "buyer_id": str(buyer.id),
        "name": buyer.name,
        "role": "buyer",
    }


@router.get("/", response_model=List[BuyerResponse])
async def get_all_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer))
    return result.scalars().all()

@router.get("/{buyer_id}")
async def get_buyer(buyer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer).where(Buyer.id == buyer_id))
    buyer = result.scalar_one_or_none()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
        
    from app.models.deal import Deal
    from sqlalchemy import func as sqlfunc
    
    completed = await db.execute(
        select(sqlfunc.count(Deal.id)).where(Deal.buyer_id == buyer_id, Deal.deal_status == 'completed')
    )
    completed_deals = completed.scalar_one()
    
    attempted = await db.execute(
        select(sqlfunc.count(Deal.id)).where(Deal.buyer_id == buyer_id, Deal.deal_status.in_(['completed', 'failed', 'locked', 'accepted']))
    )
    attempted_deals = attempted.scalar_one()
    
    score = 100.0
    if attempted_deals > 0:
        score = round((completed_deals / attempted_deals) * 100, 1)
        
    buyer_data = {c.name: getattr(buyer, c.name) for c in buyer.__table__.columns}
    buyer_data["fulfillment_reliability_score"] = score
    return buyer_data
