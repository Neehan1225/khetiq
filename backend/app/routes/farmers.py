from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.farmer import Farmer
from pydantic import BaseModel
from typing import Optional
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

@router.get("/")
async def get_farmers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer))
    return result.scalars().all()

@router.get("/{farmer_id}")
async def get_farmer(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer