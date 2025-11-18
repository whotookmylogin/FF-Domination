"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, leagues, ai, trades, health, billing

router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(leagues.router, prefix="/leagues", tags=["leagues"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(trades.router, prefix="/trades", tags=["trades"])
router.include_router(billing.router, prefix="/billing", tags=["billing"])
router.include_router(health.router, prefix="/health", tags=["health"])
