from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.deal import Deal
from datetime import datetime, timezone
import uuid

router = APIRouter()


@router.get("/{user_type}/{user_id}")
async def get_notifications(
    user_type: str,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Compute real-time notifications from deal state for a farmer or buyer."""

    if user_type == "farmer":
        result = await db.execute(select(Deal).where(Deal.farmer_id == user_id))
    else:
        result = await db.execute(select(Deal).where(Deal.buyer_id == user_id))

    deals = result.scalars().all()
    notifications = []
    now = datetime.now(timezone.utc)

    for d in deals:
        created = d.created_at
        if created and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_h = (now - created).total_seconds() / 3600 if created else 999

        # 1. New incoming offer (buyer → farmer)
        if user_type == "farmer" and d.initiated_by == "buyer" and d.deal_status == "offer" and age_h < 72:
            notifications.append({
                "id": f"offer_{d.id}",
                "type": "new_offer",
                "icon": "📩",
                "title": f"New offer for your {d.crop_type.title()}",
                "body": f"₹{d.agreed_price_per_kg}/kg for {d.quantity_kg}kg — respond now",
                "color": "#fbbf24",
                "deal_id": str(d.id),
                "is_new": age_h < 24,
            })

        # 2. New incoming offer (farmer → buyer)
        if user_type == "buyer" and d.initiated_by == "farmer" and d.deal_status == "offer" and age_h < 72:
            notifications.append({
                "id": f"offer_{d.id}",
                "type": "new_offer",
                "icon": "📩",
                "title": f"Farmer offer: {d.crop_type.title()}",
                "body": f"₹{d.agreed_price_per_kg}/kg for {d.quantity_kg}kg",
                "color": "#fbbf24",
                "deal_id": str(d.id),
                "is_new": age_h < 24,
            })

        # 3. Counter-offer received (farmer gets buyer counter)
        if (d.deal_status == "bargaining" and d.counter_price_per_kg and
                user_type == "farmer" and d.initiated_by == "buyer" and age_h < 48):
            notifications.append({
                "id": f"counter_{d.id}",
                "type": "counter_offer",
                "icon": "⇄",
                "title": f"Counter-offer on {d.crop_type.title()}",
                "body": f"Buyer proposes ₹{d.counter_price_per_kg}/kg — accept or negotiate",
                "color": "#fb923c",
                "deal_id": str(d.id),
                "is_new": age_h < 12,
            })

        # 4. Counter-offer received (buyer gets farmer counter)
        if (d.deal_status == "bargaining" and d.counter_price_per_kg and
                user_type == "buyer" and d.initiated_by == "farmer" and age_h < 48):
            notifications.append({
                "id": f"counter_{d.id}",
                "type": "counter_offer",
                "icon": "⇄",
                "title": f"Farmer counter on {d.crop_type.title()}",
                "body": f"₹{d.counter_price_per_kg}/kg proposed — respond",
                "color": "#fb923c",
                "deal_id": str(d.id),
                "is_new": age_h < 12,
            })

        # 5. Deal accepted recently
        if d.deal_status == "accepted" and age_h < 48:
            notifications.append({
                "id": f"accepted_{d.id}",
                "type": "deal_accepted",
                "icon": "✅",
                "title": f"Deal accepted — {d.crop_type.title()}",
                "body": f"₹{d.agreed_price_per_kg}/kg locked • Total ₹{round(d.total_value):,}",
                "color": "#4ade80",
                "deal_id": str(d.id),
                "is_new": age_h < 24,
            })

        # 6. Late delivery warning
        if d.expected_delivery_date and d.deal_status in ("accepted", "locked"):
            from datetime import date
            days_overdue = (date.today() - d.expected_delivery_date).days
            if days_overdue > 0:
                notifications.append({
                    "id": f"late_{d.id}",
                    "type": "late_delivery",
                    "icon": "⚠️",
                    "title": f"Overdue delivery — {d.crop_type.title()}",
                    "body": f"{days_overdue} day(s) past delivery date — coordinate now",
                    "color": "#f87171",
                    "deal_id": str(d.id),
                    "is_new": True,
                })

    # Sort: new first, then by type priority
    type_order = {"late_delivery": 0, "counter_offer": 1, "new_offer": 2, "deal_accepted": 3}
    notifications.sort(key=lambda x: (not x["is_new"], type_order.get(x["type"], 9)))

    return {
        "notifications": notifications,
        "unread_count": sum(1 for n in notifications if n["is_new"]),
    }
