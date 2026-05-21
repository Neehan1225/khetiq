import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import sys
sys.path.insert(0, ".")
from app.config import settings

async def migrate():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        try:
            await conn.execute(text(
                "ALTER TABLE deals ADD COLUMN counter_by VARCHAR(10)"
            ))
            print("Added counter_by")
        except Exception as e:
            print(f"counter_by: {e}")
    await engine.dispose()
    print("Migration complete.")

asyncio.run(migrate())
