from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.models.deal import Deal
from pydantic import BaseModel, Field
from datetime import date, datetime, timezone
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
    proposed_delivery_date: Optional[date] = None
    proposed_time_slot: Optional[str] = None   # morning | afternoon | evening
    delivery_notes: Optional[str] = Field(None, max_length=100)


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
    proposed_delivery_date: Optional[date] = None
    proposed_time_slot: Optional[str] = None
    delivery_notes: Optional[str] = None
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
    counter_price_per_kg: float


@router.patch("/{deal_id}/counter", response_model=DealResponse)
async def send_counter_offer(deal_id: uuid.UUID, body: CounterOfferRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.deal_status in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail=f"Cannot counter a {deal.deal_status} deal")
    deal.counter_price_per_kg = body.counter_price_per_kg
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
    if deal.counter_price_per_kg:
        deal.agreed_price_per_kg = deal.counter_price_per_kg
        deal.total_value = deal.quantity_kg * deal.counter_price_per_kg
    deal.deal_status = "accepted"
    
    # Auto-cancel competing offers for the same crop type from this farmer
    stmt = (
        update(Deal)
        .where(Deal.farmer_id == deal.farmer_id)
        .where(Deal.crop_type == deal.crop_type)
        .where(Deal.id != deal_id)
        .where(Deal.deal_status.in_(["offer", "bargaining"]))
        .values(deal_status="cancelled")
    )
    await db.execute(stmt)

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


def _enrich_deal(deal: Deal) -> dict:
    """Add is_overdue and overdue_days to a deal dict."""
    d = {
        c.name: getattr(deal, c.name)
        for c in deal.__table__.columns
    }
    today = datetime.now(timezone.utc).date()
    ref_date = deal.proposed_delivery_date or deal.expected_delivery_date
    if ref_date and deal.deal_status in ("offer", "accepted", "bargaining") and ref_date < today:
        d["is_overdue"] = True
        d["overdue_days"] = (today - ref_date).days
    else:
        d["is_overdue"] = False
        d["overdue_days"] = 0
    return d


@router.get("/farmer/{farmer_id}")
async def get_farmer_deals(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.farmer_id == farmer_id))
    return [_enrich_deal(d) for d in result.scalars().all()]


@router.get("/buyer/{buyer_id}")
async def get_buyer_deals(buyer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.buyer_id == buyer_id))
    return [_enrich_deal(d) for d in result.scalars().all()]


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

@router.patch("/{deal_id}/fail", response_model=DealResponse)
async def fail_deal(deal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal.deal_status = "failed"
    await db.commit()
    await db.refresh(deal)
    return deal


class ProposeDateRequest(BaseModel):
    proposed_delivery_date: date
    proposed_time_slot: str          # morning | afternoon | evening
    proposed_by: str                  # farmer | buyer


@router.patch("/{deal_id}/propose-date", response_model=DealResponse)
async def propose_delivery_date(
    deal_id: uuid.UUID,
    body: ProposeDateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Let either party propose or update the delivery date and time slot."""
    if body.proposed_time_slot not in ("morning", "afternoon", "evening"):
        raise HTTPException(
            status_code=422,
            detail="proposed_time_slot must be morning, afternoon, or evening"
        )
    if body.proposed_by not in ("farmer", "buyer"):
        raise HTTPException(status_code=422, detail="proposed_by must be farmer or buyer")

    result = await db.execute(select(Deal).where(Deal.id == deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    if deal.deal_status in ("rejected", "completed", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot propose a date for a {deal.deal_status} deal"
        )

    deal.proposed_delivery_date = body.proposed_delivery_date
    deal.proposed_time_slot = body.proposed_time_slot
    await db.commit()
    await db.refresh(deal)
    return deal
