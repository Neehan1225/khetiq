from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.recommendations import Recommendation
from app.models.farmer import Farmer
from app.models.crop import Crop
from app.models.buyer import Buyer
from app.agents.resilience_agent import run_resilience_agent
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()


@router.post("/analyze/{crop_id}")
async def analyze_crop(crop_id: uuid.UUID, lang: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    Main KhetIQ endpoint. Takes a crop ID, runs the full
    resilience agent, returns AI recommendation.
    """

    # Get crop
    crop_result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = crop_result.scalar_one_or_none()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    # Get farmer
    farmer_result = await db.execute(select(Farmer).where(Farmer.id == crop.farmer_id))
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # Get all buyers
    buyers_result = await db.execute(select(Buyer))
    buyers = buyers_result.scalars().all()

    if not buyers:
        raise HTTPException(status_code=400, detail="No buyers in system")

    # Use provided language or fall back to farmer preference
    target_lang = lang or farmer.language

    # Run the AI agent
    result = await run_resilience_agent(farmer, crop, buyers, target_lang)

    # Save recommendation to database
    best_buyer_id = None
    if result["best_buyer"]:
        best_buyer_id = uuid.UUID(result["best_buyer"]["buyer_id"])

    db_rec = Recommendation(
        farmer_id=farmer.id,
        crop_id=crop.id,
        recommended_buyer_id=best_buyer_id,
        net_profit_estimate=result["net_profit_estimate"],
        resilience_index=result["resilience_index"],
        risk_level=result["risk_level"],
        reasoning=result["reasoning"]
    )
    db.add(db_rec)
    await db.commit()

    return result


@router.get("/farmer/{farmer_id}")
async def get_recommendations_by_farmer(
    farmer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Recommendation).where(Recommendation.farmer_id == farmer_id)
    )
    return result.scalars().all()