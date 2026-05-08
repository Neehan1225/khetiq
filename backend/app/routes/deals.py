from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.deal import Deal
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
import uuid

router = APIRouter()


class DealCreate(BaseModel):
    farmer_id: uuid.UUID
    buyer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    agreed_price_per_kg: float
    transport_cost: float = 0.0
    expected_delivery_date: date
    initiated_by: str = "buyer"   # "buyer" or "farmer"
    deal_status: str = "offer"


class DealStatusUpdate(BaseModel):
    deal_status: str             # accepted | rejected | bargaining | locked
    counter_price_per_kg: Optional[float] = None


class DealResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    buyer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    agreed_price_per_kg: float
    counter_price_per_kg: Optional[float] = None
    transport_cost: float
    total_value: float
    payment_status: str
    deal_status: str
    initiated_by: str = "buyer"
    expected_delivery_date: Optional[date] = None
    farmer_confirmed: bool = False
    buyer_confirmed: bool = False

    class Config:
        from_attributes = True


@router.post("/", response_model=DealResponse)
async def create_deal(deal: DealCreate, db: AsyncSession = Depends(get_db)):
    total_value = deal.quantity_kg * deal.agreed_price_per_kg
    data = deal.model_dump()
    new_deal = Deal(**data, total_value=total_value)
    db.add(new_deal)
    await db.commit()
    await db.refresh(new_deal)
    return new_deal


@router.patch("/{deal_id}/status", response_model=DealResponse)
async def update_deal_status(deal_id: uuid.UUID, update: DealStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal.deal_status = update.deal_status
    if update.counter_price_per_kg is not None:
        deal.counter_price_per_kg = update.counter_price_per_kg
    await db.commit()
    await db.refresh(deal)
    return deal


class CounterOfferRequest(BaseModel):
    counter_price: float


@router.patch("/{deal_id}/counter", response_model=DealResponse)
async def send_counter_offer(deal_id: uuid.UUID, body: CounterOfferRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.deal_status in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail=f"Cannot counter a {deal.deal_status} deal")
    deal.counter_price_per_kg = body.counter_price
    deal.deal_status = "bargaining"
    await db.commit()
    await db.refresh(deal)
    return deal


@router.patch("/{deal_id}/accept", response_model=DealResponse)
async def accept_deal(deal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.deal_status == "rejected":
        raise HTTPException(status_code=400, detail="Cannot accept a rejected deal")
    # If there's a counter price, adopt it as the final agreed price
    if deal.counter_price_per_kg:
        deal.agreed_price_per_kg = deal.counter_price_per_kg
        deal.total_value = deal.quantity_kg * deal.counter_price_per_kg
    deal.deal_status = "accepted"
    await db.commit()
    await db.refresh(deal)
    return deal


@router.patch("/{deal_id}/reject", response_model=DealResponse)
async def reject_deal(deal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.deal_status == "accepted":
        raise HTTPException(status_code=400, detail="Cannot reject an accepted deal")
    deal.deal_status = "rejected"
    await db.commit()
    await db.refresh(deal)
    return deal


@router.get("/farmer/{farmer_id}", response_model=List[DealResponse])
async def get_farmer_deals(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.farmer_id == farmer_id))
    return result.scalars().all()


@router.get("/buyer/{buyer_id}", response_model=List[DealResponse])
async def get_buyer_deals(buyer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.buyer_id == buyer_id))
    return result.scalars().all()


class DealCompleteRequest(BaseModel):
    user_type: str  # "farmer" or "buyer"

@router.patch("/{deal_id}/complete", response_model=DealResponse)
async def complete_deal(deal_id: uuid.UUID, body: DealCompleteRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if body.user_type == "farmer":
        deal.farmer_confirmed = True
    elif body.user_type == "buyer":
        deal.buyer_confirmed = True
    else:
        raise HTTPException(status_code=400, detail="user_type must be farmer or buyer")
        
    if deal.farmer_confirmed and deal.buyer_confirmed:
        deal.deal_status = "completed"
        
    await db.commit()
    await db.refresh(deal)
    return deal
