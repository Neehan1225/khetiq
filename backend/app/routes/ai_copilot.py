from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.deal import Deal
from app.models.farmer import Farmer
from app.models.buyer import Buyer
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

APMC_PRICES = {
    "tomato": 18, "onion": 22, "potato": 15, "brinjal": 20,
    "cabbage": 12, "cauliflower": 25, "beans": 35, "carrot": 28,
    "chilli": 45, "garlic": 80, "ginger": 60, "maize": 20,
    "wheat": 22, "rice": 28, "banana": 18, "mango": 35,
    "grapes": 55, "pomegranate": 70, "jowar": 28, "sugarcane": 3.5,
    "sunflower": 45, "groundnut": 55, "cotton": 65, "bengal gram": 58,
    "tur dal": 95, "chickpea": 55, "paddy": 22, "linseed": 40,
}


class CopilotRequest(BaseModel):
    user_type: str          # "farmer" | "buyer"
    user_id: uuid.UUID
    language: str = "kn"   # language code
    message: str
    context: Optional[dict] = None   # optional deal/crop context


@router.post("/ask")
async def ask_copilot(req: CopilotRequest, db: AsyncSession = Depends(get_db)):
    """Gemini-powered conversational AI advisor for farmers and buyers."""
    from app.services.gemini_service import get_copilot_response

    # Fetch user name
    user_name = "User"
    if req.user_type == "farmer":
        result = await db.execute(select(Farmer).where(Farmer.id == req.user_id))
        farmer = result.scalar_one_or_none()
        if farmer:
            user_name = farmer.name
    else:
        result = await db.execute(select(Buyer).where(Buyer.id == req.user_id))
        buyer = result.scalar_one_or_none()
        if buyer:
            user_name = buyer.name

    # Enrich context with recent deals if not provided
    context = req.context or {}
    if not context.get("recent_deals"):
        if req.user_type == "farmer":
            r = await db.execute(
                select(Deal).where(Deal.farmer_id == req.user_id)
                .order_by(Deal.created_at.desc()).limit(3)
            )
        else:
            r = await db.execute(
                select(Deal).where(Deal.buyer_id == req.user_id)
                .order_by(Deal.created_at.desc()).limit(3)
            )
        recent = r.scalars().all()
        context["recent_deals"] = [
            {"crop": d.crop_type, "price": d.agreed_price_per_kg,
             "qty": d.quantity_kg, "status": d.deal_status}
            for d in recent
        ]

    response_data = await get_copilot_response(
        user_type=req.user_type,
        user_name=user_name,
        language=req.language,
        context=context,
        message=req.message,
        apmc_prices=APMC_PRICES,
    )
    return response_data


@router.post("/voice")
async def voice_copilot(
    user_type: str,
    user_id: uuid.UUID,
    language: str = "kn",
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Processes raw audio using Gemini's multi-modal capabilities."""
    from app.services.gemini_service import get_copilot_voice_response
    
    audio_bytes = await audio.read()
    
    # Context logic (simplified)
    context = {"recent_deals": []}
    
    response_data = await get_copilot_voice_response(
        user_type=user_type,
        language=language,
        audio_bytes=audio_bytes,
        context=context,
        apmc_prices=APMC_PRICES
    )
    return response_data
