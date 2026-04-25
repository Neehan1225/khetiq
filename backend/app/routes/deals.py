from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models.deal import Deal
from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid

router = APIRouter()

class DealCreate(BaseModel):
    farmer_id: uuid.UUID
    buyer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    agreed_price_per_kg: float
    expected_delivery_date: datetime

class DealResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    buyer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    total_value: float
    payment_status: str
    deal_status: str

@router.post("/", response_model=DealResponse)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_db)):
    total_value = deal.quantity_kg * deal.agreed_price_per_kg
    new_deal = Deal(**deal.model_dump(), total_value=total_value)
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return new_deal

@router.get("/farmer/{farmer_id}", response_model=List[DealResponse])
async def get_farmer_deals(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.farmer_id == farmer_id))
    return result.scalars().all()
