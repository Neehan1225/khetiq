import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post("http://13.49.74.167:8000/api/copilot/ask", json={
            "user_type": "farmer",
            "user_id": "7d73e188-7c30-4571-83a0-d603934aecb4",
            "language": "en",
            "message": "hello"
        })
        print(res.status_code)
        print(res.text)

asyncio.run(test())
