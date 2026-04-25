from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.crop import Crop
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid

router = APIRouter()

class CropCreate(BaseModel):
    farmer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    field_size_acres: Optional[float] = None
    expected_harvest_date: datetime

class CropResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    crop_type: str
    quantity_kg: float
    expected_harvest_date: datetime

@router.post("/", response_model=CropResponse)
async def create_crop(crop: CropCreate, db: AsyncSession = Depends(get_db)):
    new_crop = Crop(**crop.dict())
    db.add(new_crop)
    await db.commit()
    await db.refresh(new_crop)
    return new_crop

@router.get("/farmer/{farmer_id}", response_model=List[CropResponse])
async def get_farmer_crops(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Crop).where(Crop.farmer_id == farmer_id))
    return result.scalars().all()
