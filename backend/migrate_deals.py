"""
Run this once to add the new columns to the existing deals table.
Usage: python migrate_deals.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Adjust this URL to match your actual DB URL from app/config.py
import sys
sys.path.insert(0, ".")
from app.config import settings

async def migrate():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        # Add counter_price_per_kg column (ignore error if already exists)
        try:
            await conn.execute(text(
                "ALTER TABLE deals ADD COLUMN counter_price_per_kg FLOAT"
            ))
            print("Added counter_price_per_kg")
        except Exception as e:
            print(f"counter_price_per_kg: {e}")

        # Add initiated_by column
        try:
            await conn.execute(text(
                "ALTER TABLE deals ADD COLUMN initiated_by VARCHAR(10) DEFAULT 'buyer'"
            ))
            print("Added initiated_by")
        except Exception as e:
            print(f"initiated_by: {e}")

        # Update deal_status default (existing rows stay as-is, new rows will be 'offer')
        # Rename old 'active' rows to 'locked' so they show as completed deals
        try:
            await conn.execute(text(
                "UPDATE deals SET deal_status='locked' WHERE deal_status='active'"
            ))
            print("Migrated old 'active' deals to 'locked'")
        except Exception as e:
            print(f"Update: {e}")

    await engine.dispose()
    print("Migration complete.")

asyncio.run(migrate())
