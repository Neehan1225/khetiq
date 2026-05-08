import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False)
    reviewer_type = Column(String(20), nullable=False) # 'farmer' or 'buyer'
    reviewer_id = Column(UUID(as_uuid=True), nullable=False)
    reviewee_type = Column(String(20), nullable=False)
    reviewee_id = Column(UUID(as_uuid=True), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
