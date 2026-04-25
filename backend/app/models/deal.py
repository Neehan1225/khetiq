import uuid
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id"), nullable=False)
    crop_type = Column(String(50), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    agreed_price_per_kg = Column(Float, nullable=False)
    transport_cost = Column(Float, default=0)
    expected_delivery_date = Column(Date, nullable=True)
    payment_status = Column(String(20), default="pending")
    deal_status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())