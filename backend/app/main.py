from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routes import farmers, crops, buyers, deals, recommendations, analytics, reviews
from app.routes import notifications, ai_copilot

app = FastAPI(
    title="KhetIQ API",
    description="AI-Driven Supply Chain & Resilience Co-pilot for Farmers",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(crops.router, prefix="/api/crops", tags=["Crops"])
app.include_router(buyers.router, prefix="/api/buyers", tags=["Buyers"])
app.include_router(deals.router, prefix="/api/deals", tags=["Deals"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(
    recommendations.router,
    prefix="/api/recommendations",
    tags=["Recommendations"]
)
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"]
)
app.include_router(
    notifications.router,
    prefix="/api/notifications",
    tags=["Notifications"]
)
app.include_router(
    ai_copilot.router,
    prefix="/api/copilot",
    tags=["AI Copilot"]
)


@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/")
async def root():
    return {
        "message": "KhetIQ API running",
        "status": "healthy"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}