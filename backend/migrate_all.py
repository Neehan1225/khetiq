"""
Run ALL pending migrations at once.
Safe to re-run — each ALTER is wrapped in try/except so existing columns are skipped.
Usage: docker compose exec backend python migrate_all.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
sys.path.insert(0, ".")
from app.config import settings


async def migrate():
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as conn:
        # ── deals table columns ──
        deal_columns = [
            ("counter_price_per_kg", "FLOAT"),
            ("counter_quantity_kg", "FLOAT"),
            ("counter_by", "VARCHAR(10)"),
            ("initiated_by", "VARCHAR(10) DEFAULT 'buyer'"),
            ("proposed_delivery_date", "DATE"),
            ("proposed_time_slot", "VARCHAR(20)"),
            ("delivery_notes", "VARCHAR(100)"),
        ]
        for col_name, col_type in deal_columns:
            try:
                await conn.execute(text(
                    f"ALTER TABLE deals ADD COLUMN {col_name} {col_type}"
                ))
                print(f"  ✓ Added deals.{col_name}")
            except Exception:
                print(f"  · deals.{col_name} already exists, skipped")

        # ── reviews table columns ──
        review_columns = [
            ("review_type", "VARCHAR(20)"),
            ("reason", "VARCHAR(50)"),
        ]
        for col_name, col_type in review_columns:
            try:
                await conn.execute(text(
                    f"ALTER TABLE reviews ADD COLUMN {col_name} {col_type}"
                ))
                print(f"  ✓ Added reviews.{col_name}")
            except Exception:
                print(f"  · reviews.{col_name} already exists, skipped")

        # ── deal_status renames ──
        try:
            res = await conn.execute(text(
                "UPDATE deals SET deal_status='locked' WHERE deal_status='active'"
            ))
            print(f"  ✓ Migrated {res.rowcount} 'active' → 'locked'")
        except Exception as e:
            print(f"  · Status update: {e}")

    await engine.dispose()
    print("\n✅ All migrations complete!")

asyncio.run(migrate())
