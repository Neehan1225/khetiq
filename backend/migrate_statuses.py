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
            # Update 'offer' to 'pending'
            res = await conn.execute(text(
                "UPDATE deals SET deal_status='pending' WHERE deal_status='offer'"
            ))
            print(f"Updated {res.rowcount} deals from 'offer' to 'pending'")
            
            # Update 'bargaining' to 'counter_offered'
            res2 = await conn.execute(text(
                "UPDATE deals SET deal_status='counter_offered' WHERE deal_status='bargaining'"
            ))
            print(f"Updated {res2.rowcount} deals from 'bargaining' to 'counter_offered'")
        except Exception as e:
            print(f"Migration error: {e}")
    await engine.dispose()
    print("Migration complete.")

asyncio.run(migrate())
