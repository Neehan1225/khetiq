from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.buyer import Buyer
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

@router.get("/", response_model=List[BuyerResponse])
async def get_all_buyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Buyer))
    return result.scalars().all()
