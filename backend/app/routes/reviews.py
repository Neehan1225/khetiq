from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc, desc
from app.database import get_db
from app.models.review import Review
from app.models.deal import Deal
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter()

class ReviewCreate(BaseModel):
    deal_id: uuid.UUID
    reviewer_type: str
    reviewer_id: uuid.UUID
    reviewee_type: str
    reviewee_id: uuid.UUID
    rating: int
    comment: Optional[str] = None
    reason: Optional[str] = None

class ReviewResponse(BaseModel):
    id: uuid.UUID
    deal_id: uuid.UUID
    reviewer_type: str
    reviewer_id: uuid.UUID
    reviewee_type: str
    reviewee_id: uuid.UUID
    rating: int
    comment: Optional[str]
    review_type: Optional[str] = None
    reason: Optional[str] = None

@router.post("/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check deal status
    result = await db.execute(select(Deal).where(Deal.id == review.deal_id))
    deal = result.scalar_one_or_none()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    today = datetime.now(timezone.utc).date()
    ref_date = deal.proposed_delivery_date or deal.expected_delivery_date
    is_late = False
    if ref_date and deal.deal_status in ("offer", "accepted", "bargaining") and ref_date < today:
        is_late = True
        
    if deal.deal_status in ("completed", "accepted"):
        review_type = "verified"
    elif deal.deal_status in ("rejected", "failed") or is_late:
        review_type = "feedback"
        valid_reasons = ["price_disagreement", "quality_concern", "communication_issue", "other"]
        if review.reason not in valid_reasons:
            raise HTTPException(status_code=400, detail=f"Feedback review requires a valid reason: {valid_reasons}")
    else:
        raise HTTPException(status_code=400, detail="Deal must be completed, accepted, rejected, or late to be reviewed.")

    # Check if a review already exists for this deal by this reviewer
    existing = await db.execute(
        select(Review).where(
            Review.deal_id == review.deal_id,
            Review.reviewer_id == review.reviewer_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Review already submitted for this deal by this user")

    data = review.model_dump()
    data["review_type"] = review_type
    db_review = Review(**data)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.get("/{reviewee_type}/{reviewee_id}")
async def get_reviews(reviewee_type: str, reviewee_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Get top 3 recent reviews
    reviews_result = await db.execute(
        select(Review)
        .where(Review.reviewee_type == reviewee_type, Review.reviewee_id == reviewee_id)
        .order_by(desc(Review.created_at))
        .limit(3)
    )
    recent_reviews = reviews_result.scalars().all()

    # Get average rating and count
    stats_result = await db.execute(
        select(
            sqlfunc.avg(Review.rating).label('average_rating'),
            sqlfunc.count(Review.id).label('review_count')
        ).where(Review.reviewee_type == reviewee_type, Review.reviewee_id == reviewee_id)
    )
    stats = stats_result.one()
    
    avg_rating = float(stats.average_rating) if stats.average_rating else 0.0

    return {
        "average_rating": round(avg_rating, 1),
        "review_count": stats.review_count,
        "recent_reviews": recent_reviews
    }
