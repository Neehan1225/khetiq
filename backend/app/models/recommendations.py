import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("farmers.id"), nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id"), nullable=True)
    recommended_buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id"), nullable=True)
    net_profit_estimate = Column(Float, nullable=True)
    resilience_index = Column(Float, nullable=True)
    risk_level = Column(String(10), nullable=True)
    reasoning = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())