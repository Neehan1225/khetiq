from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sqlfunc, desc
from app.database import get_db
from app.models.review import Review
from pydantic import BaseModel
from typing import List, Optional
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

class ReviewResponse(BaseModel):
    id: uuid.UUID
    deal_id: uuid.UUID
    reviewer_type: str
    reviewer_id: uuid.UUID
    reviewee_type: str
    reviewee_id: uuid.UUID
    rating: int
    comment: Optional[str]

@router.post("/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: AsyncSession = Depends(get_db)):
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Check if a review already exists for this deal by this reviewer
    existing = await db.execute(
        select(Review).where(
            Review.deal_id == review.deal_id,
            Review.reviewer_id == review.reviewer_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Review already submitted for this deal by this user")

    db_review = Review(**review.model_dump())
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
