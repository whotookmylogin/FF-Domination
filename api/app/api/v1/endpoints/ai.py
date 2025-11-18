"""
AI analysis endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, UUID4
from typing import List, Optional
import asyncio
from openai import AsyncOpenAI

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User, SubscriptionTier
from app.models.analytics import AIQuery

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class TradeAnalysisRequest(BaseModel):
    """Request for trade analysis"""
    league_id: UUID4
    team_from_players: List[str]
    team_to_players: List[str]


class TradeAnalysisResponse(BaseModel):
    """Response for trade analysis"""
    value_score: float  # 0-100
    winner: str
    reasoning: str
    risk_level: str


class DraftStrategyRequest(BaseModel):
    """Request for draft strategy"""
    draft_position: int
    league_size: int
    scoring_type: str


class DraftStrategyResponse(BaseModel):
    """Response for draft strategy"""
    strategy: str
    target_players: List[str]
    round_by_round: List[str]


@router.post("/analyze-trade", response_model=TradeAnalysisResponse)
async def analyze_trade(
    request: TradeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a trade using AI (Pro+ tier required)"""

    # Check subscription tier
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro or Champion tier required for AI trade analysis"
        )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured"
        )

    # Create AI prompt
    prompt = f"""Analyze this fantasy football trade:

Team A gives: {', '.join(request.team_from_players)}
Team B gives: {', '.join(request.team_to_players)}

Provide:
1. Value score (0-100) indicating overall trade value
2. Winner of the trade (Team A, Team B, or Fair)
3. 2-3 sentence reasoning
4. Risk level (Low, Medium, High)

Format as JSON: {{"value_score": X, "winner": "...", "reasoning": "...", "risk_level": "..."}}
"""

    try:
        # Call OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert fantasy football analyst with 30 years of experience."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        # Track usage
        ai_query = AIQuery(
            user_id=current_user.id,
            query_type="trade",
            input_data={
                "team_from": request.team_from_players,
                "team_to": request.team_to_players
            },
            output_data=result,
            tokens_used=response.usage.total_tokens,
            model="gpt-4o-mini"
        )
        db.add(ai_query)
        await db.commit()

        import json
        return json.loads(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/draft-strategy", response_model=DraftStrategyResponse)
async def draft_strategy(
    request: DraftStrategyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI draft strategy (Pro+ tier required)"""

    # Check subscription tier
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro or Champion tier required for AI draft strategy"
        )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured"
        )

    prompt = f"""Create a fantasy football draft strategy for:
- Draft position: {request.draft_position}
- League size: {request.league_size} teams
- Scoring: {request.scoring_type}

Provide:
1. Overall draft strategy
2. Top 5 target players
3. Round-by-round approach (first 5 rounds)

Format as JSON.
"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert fantasy football draft strategist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        # Track usage
        ai_query = AIQuery(
            user_id=current_user.id,
            query_type="draft",
            input_data=request.dict(),
            output_data=result,
            tokens_used=response.usage.total_tokens,
            model="gpt-4o-mini"
        )
        db.add(ai_query)
        await db.commit()

        import json
        return json.loads(result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )
