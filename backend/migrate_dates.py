import asyncio
import sys
sys.path.insert(0, ".")
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

async def migrate():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE deals ADD COLUMN proposed_delivery_date DATE;"))
            print("Added proposed_delivery_date")
        except Exception as e:
            print(f"proposed_delivery_date: {e}")

        try:
            await conn.execute(text("ALTER TABLE deals ADD COLUMN proposed_time_slot VARCHAR(20);"))
            print("Added proposed_time_slot")
        except Exception as e:
            print(f"proposed_time_slot: {e}")

        try:
            await conn.execute(text("ALTER TABLE deals ADD COLUMN delivery_notes VARCHAR(100);"))
            print("Added delivery_notes")
        except Exception as e:
            print(f"delivery_notes: {e}")

    await engine.dispose()
    print("Migration complete.")

asyncio.run(migrate())
