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
    if ref_date and deal.deal_status in ("offer", "pending", "accepted", "bargaining", "counter_offered", "locked") and ref_date < today:
        is_late = True
        
    if deal.deal_status == "completed":
        review_type = "verified"
    elif deal.deal_status in ("accepted", "locked") and not is_late:
        # For ongoing accepted/locked deals that are on time, we treat them as verified reviews
        review_type = "verified"
    elif deal.deal_status in ("rejected", "failed") or is_late:
        review_type = "feedback"
        valid_reasons = ["price_disagreement", "quality_concern", "communication_issue", "other"]
        if review.reason not in valid_reasons:
            raise HTTPException(status_code=400, detail=f"Feedback review requires a valid reason: {valid_reasons}")
    else:
        raise HTTPException(status_code=400, detail="Deal must be completed, accepted, locked, rejected, or late to be reviewed.")

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


@router.get("/dashboard/{reviewee_type}/{reviewee_id}")
async def get_reviews_dashboard(reviewee_type: str, reviewee_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Full reviews dashboard: all reviews with reviewer names, star breakdown, and reliability score."""
    from app.models.farmer import Farmer
    from app.models.buyer import Buyer

    # All reviews for this user
    reviews_result = await db.execute(
        select(Review)
        .where(Review.reviewee_type == reviewee_type, Review.reviewee_id == reviewee_id)
        .order_by(desc(Review.created_at))
    )
    all_reviews = reviews_result.scalars().all()

    # Gather reviewer names (buyers reviewed the farmer, farmers reviewed the buyer)
    reviewer_ids = list({r.reviewer_id for r in all_reviews})
    reviewer_names = {}
    if reviewer_ids:
        if reviewee_type == "farmer":
            names_result = await db.execute(select(Buyer).where(Buyer.id.in_(reviewer_ids)))
            for b in names_result.scalars().all():
                reviewer_names[str(b.id)] = b.name
        else:
            names_result = await db.execute(select(Farmer).where(Farmer.id.in_(reviewer_ids)))
            for f in names_result.scalars().all():
                reviewer_names[str(f.id)] = f.name

    # Star breakdown
    star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_rating = 0
    verified_count = 0
    feedback_count = 0
    for r in all_reviews:
        star_counts[r.rating] = star_counts.get(r.rating, 0) + 1
        total_rating += r.rating
        if r.review_type == "verified":
            verified_count += 1
        else:
            feedback_count += 1

    review_count = len(all_reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0.0

    # Reliability score — computed from deals
    if reviewee_type == "farmer":
        completed = await db.execute(
            select(sqlfunc.count(Deal.id)).where(Deal.farmer_id == reviewee_id, Deal.deal_status == "completed")
        )
        failed = await db.execute(
            select(sqlfunc.count(Deal.id)).where(Deal.farmer_id == reviewee_id, Deal.deal_status == "failed")
        )
        total_attempted = await db.execute(
            select(sqlfunc.count(Deal.id)).where(
                Deal.farmer_id == reviewee_id,
                Deal.deal_status.in_(["completed", "failed", "accepted", "locked"])
            )
        )
    else:
        completed = await db.execute(
            select(sqlfunc.count(Deal.id)).where(Deal.buyer_id == reviewee_id, Deal.deal_status == "completed")
        )
        failed = await db.execute(
            select(sqlfunc.count(Deal.id)).where(Deal.buyer_id == reviewee_id, Deal.deal_status == "failed")
        )
        total_attempted = await db.execute(
            select(sqlfunc.count(Deal.id)).where(
                Deal.buyer_id == reviewee_id,
                Deal.deal_status.in_(["completed", "failed", "accepted", "locked"])
            )
        )

    completed_count = completed.scalar_one()
    failed_count = failed.scalar_one()
    attempted_count = total_attempted.scalar_one()
    reliability_score = round((completed_count / attempted_count) * 100, 1) if attempted_count > 0 else 100.0

    # Build enriched review list
    enriched_reviews = []
    for r in all_reviews:
        enriched_reviews.append({
            "id": str(r.id),
            "deal_id": str(r.deal_id),
            "reviewer_name": reviewer_names.get(str(r.reviewer_id), "Anonymous"),
            "reviewer_type": r.reviewer_type,
            "rating": r.rating,
            "comment": r.comment,
            "review_type": r.review_type or "verified",
            "reason": r.reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "average_rating": avg_rating,
        "review_count": review_count,
        "verified_count": verified_count,
        "feedback_count": feedback_count,
        "star_breakdown": star_counts,
        "reliability_score": reliability_score,
        "completed_deals": completed_count,
        "failed_deals": failed_count,
        "total_attempted_deals": attempted_count,
        "reviews": enriched_reviews,
    }
