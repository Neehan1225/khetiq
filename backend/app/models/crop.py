import uuid
from sqlalchemy import Column, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Crop(Base):
    __tablename__ = "crops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_type = Column(String(50), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    field_size_acres = Column(Float, nullable=True)
    sowing_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    amed_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())