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
            await conn.execute(text("ALTER TABLE reviews ADD COLUMN review_type VARCHAR(20);"))
            print("Added review_type")
        except Exception as e:
            print(f"review_type: {e}")

        try:
            await conn.execute(text("ALTER TABLE reviews ADD COLUMN reason VARCHAR(50);"))
            print("Added reason")
        except Exception as e:
            print(f"reason: {e}")

    await engine.dispose()
    print("Migration complete.")

asyncio.run(migrate())
