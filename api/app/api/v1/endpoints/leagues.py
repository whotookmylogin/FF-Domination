"""
League management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, UUID4

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.league import League, Platform

router = APIRouter()


class LeagueCreate(BaseModel):
    """Schema for creating a league connection"""
    platform: Platform
    external_id: str
    name: str
    season: int


class LeagueResponse(BaseModel):
    """Schema for league response"""
    id: UUID4
    platform: Platform
    name: str
    season: int
    team_count: int | None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[LeagueResponse])
async def get_user_leagues(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all leagues for the current user"""
    result = await db.execute(
        select(League).where(League.user_id == current_user.id)
    )
    leagues = result.scalars().all()
    return leagues


@router.post("/", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def connect_league(
    league_data: LeagueCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect a new league"""

    # Check if league already connected
    result = await db.execute(
        select(League).where(
            League.user_id == current_user.id,
            League.platform == league_data.platform,
            League.external_id == league_data.external_id
        )
    )
    existing_league = result.scalar_one_or_none()

    if existing_league:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League already connected"
        )

    # Create new league
    league = League(
        user_id=current_user.id,
        platform=league_data.platform,
        external_id=league_data.external_id,
        name=league_data.name,
        season=league_data.season
    )

    db.add(league)
    await db.commit()
    await db.refresh(league)

    return league


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_league(
    league_id: UUID4,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect a league"""
    result = await db.execute(
        select(League).where(
            League.id == league_id,
            League.user_id == current_user.id
        )
    )
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    await db.delete(league)
    await db.commit()
