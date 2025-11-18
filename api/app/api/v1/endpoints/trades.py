"""
Trade management endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, UUID4

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.analytics import Trade

router = APIRouter()


class TradeResponse(BaseModel):
    """Schema for trade response"""
    id: UUID4
    team_from_id: UUID4
    team_to_id: UUID4
    players_offered: List[str]
    players_requested: List[str]
    ai_score: float | None
    status: str

    class Config:
        from_attributes = True


@router.get("/{league_id}", response_model=List[TradeResponse])
async def get_league_trades(
    league_id: UUID4,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all trades for a league"""
    result = await db.execute(
        select(Trade).where(Trade.league_id == league_id)
    )
    trades = result.scalars().all()
    return trades
