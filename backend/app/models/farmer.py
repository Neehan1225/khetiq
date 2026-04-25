import uuid
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    district = Column(String(50), nullable=False)
    state = Column(String(50), default="Karnataka")
    language = Column(String(10), default="kn")
    created_at = Column(DateTime(timezone=True), server_default=func.now())