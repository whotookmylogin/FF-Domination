from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import os

from src.database.connection import get_db
from src.analytics.advanced_analytics_service import AdvancedAnalyticsService
from src.platforms.service import PlatformIntegrationService
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer
from src.ai.expert_draft_agent import ExpertDraftAgent

# Initialize FastAPI app
app = FastAPI(
    title="Fantasy Football Domination API",
    description="API for Fantasy Football Domination App - Phase 3 Features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize platform integration service with credentials from environment
espn_cookie = os.getenv("ESPN_COOKIE")
sleeper_token = os.getenv("SLEEPER_TOKEN")
platform_service = PlatformIntegrationService(espn_cookie=espn_cookie, sleeper_token=sleeper_token)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    """Root endpoint for API health check."""
    return {"message": "Fantasy Football Domination API - Phase 3"}

@app.get("/analytics/league/{league_id}")
def get_league_analytics(league_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive analytics for a league.
    
    Args:
        league_id (str): League ID to get analytics for
        db (Session): Database session dependency
        
    Returns:
        dict: Comprehensive league analytics
    """
    analytics_service = AdvancedAnalyticsService(db_session=db)
    result = analytics_service.get_league_analytics(league_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    
    return result

@app.get("/user/league/{league_id}")
def get_user_league_data(league_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get user league data from ESPN.
    
    Args:
        league_id (str): ESPN league ID
        db (Session): Database session dependency
        
    Returns:
        dict: User league data
    """
    try:
        # For ESPN, we need to get the user's team data
        # Using your league ID: 83806
        data = platform_service.get_league_data("espn", league_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="League data not found")
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error fetching league data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/user/team/{team_id}")
def get_user_team_data(team_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get user team data from ESPN.
    
    Args:
        team_id (str): ESPN team ID
        db (Session): Database session dependency
        
    Returns:
        dict: User team data
    """
    try:
        # For ESPN, we need to get the user's team roster data
        data = platform_service.get_user_data("espn", team_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="Team data not found")
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error fetching team data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/user/roster/{team_id}")
def get_user_roster_data(team_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get user roster data from ESPN.
    
    Args:
        team_id (str): ESPN team ID
        db (Session): Database session dependency
        
    Returns:
        dict: User roster data
    """
    try:
        # For ESPN, we need to get the user's team roster data
        data = platform_service.get_roster_data("espn", team_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="Roster data not found")
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error fetching roster data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/analytics/team/{team_id}")
def get_team_analytics(team_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive analytics for a specific team.
    
    Args:
        team_id (str): Team ID to get analytics for
        db (Session): Database session dependency
        
    Returns:
        dict: Comprehensive team analytics
    """
    analytics_service = AdvancedAnalyticsService(db_session=db)
    result = analytics_service.get_team_analytics(team_id)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    
    return result

# AI-Powered Trade Analysis Endpoints

@app.post("/ai/analyze-league-trades")
def analyze_league_trades(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze all possible trades across the entire league using AI.
    
    Body:
        {
            "league_id": "83806",
            "openai_key": "optional_openai_key",
            "openrouter_key": "optional_openrouter_key"
        }
        
    Returns:
        dict: List of ranked trade opportunities with AI analysis
    """
    try:
        league_id = request_data.get("league_id")
        openai_key = request_data.get("openai_key")
        openrouter_key = request_data.get("openrouter_key")
        
        if not league_id:
            raise HTTPException(status_code=400, detail="league_id is required")
        
        # Initialize AI trade analyzer
        trade_analyzer = AITradeAnalyzer(
            openai_key=openai_key,
            openrouter_key=openrouter_key
        )
        
        # Analyze all trades in the league
        logger.info(f"Starting AI trade analysis for league {league_id}")
        trade_opportunities = trade_analyzer.analyze_all_league_trades(league_id, platform_service)
        
        if not trade_opportunities:
            return {
                "status": "success",
                "message": "No viable trade opportunities found",
                "trades": []
            }
        
        # Convert dataclass objects to dictionaries
        trades_data = []
        for trade in trade_opportunities:
            trade_dict = {
                "team_a_id": trade.team_a_id,
                "team_b_id": trade.team_b_id,
                "team_a_gives": trade.team_a_gives,
                "team_a_gets": trade.team_a_gets,
                "team_b_gives": trade.team_b_gives,
                "team_b_gets": trade.team_b_gets,
                "fairness_score": trade.fairness_score,
                "team_a_improvement": trade.team_a_improvement,
                "team_b_improvement": trade.team_b_improvement,
                "ai_analysis": trade.ai_analysis,
                "confidence_score": trade.confidence_score,
                "urgency": trade.urgency
            }
            trades_data.append(trade_dict)
        
        logger.info(f"Found {len(trades_data)} trade opportunities")
        
        return {
            "status": "success",
            "message": f"Found {len(trades_data)} trade opportunities",
            "trades": trades_data
        }
        
    except Exception as e:
        logger.error(f"Error analyzing league trades: {e}")
        raise HTTPException(status_code=500, detail=f"Trade analysis failed: {str(e)}")

@app.post("/ai/draft-strategy")
def create_draft_strategy(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create AI-powered draft strategy for specific league settings.
    
    Body:
        {
            "league_settings": {
                "scoring_type": "ppr",
                "roster_size": 16,
                "starting_lineup": {...}
            },
            "draft_position": 7,
            "total_teams": 12,
            "openai_key": "optional_openai_key",
            "openrouter_key": "optional_openrouter_key"
        }
        
    Returns:
        dict: Comprehensive draft strategy with round-by-round plan
    """
    try:
        league_settings = request_data.get("league_settings", {})
        draft_position = request_data.get("draft_position")
        total_teams = request_data.get("total_teams", 12)
        openai_key = request_data.get("openai_key")
        openrouter_key = request_data.get("openrouter_key")
        
        if not draft_position:
            raise HTTPException(status_code=400, detail="draft_position is required")
        
        # Initialize expert draft agent
        draft_agent = ExpertDraftAgent(
            openai_key=openai_key,
            openrouter_key=openrouter_key
        )
        
        # Create draft strategy
        logger.info(f"Creating draft strategy for position {draft_position}")
        strategy = draft_agent.create_draft_strategy(league_settings, draft_position, total_teams)
        
        # Convert dataclass to dictionary
        strategy_dict = {
            "league_settings": strategy.league_settings,
            "draft_position": strategy.draft_position,
            "total_teams": strategy.total_teams,
            "strategy_name": strategy.strategy_name,
            "round_by_round_plan": strategy.round_by_round_plan,
            "key_targets": strategy.key_targets,
            "avoid_list": strategy.avoid_list,
            "handcuff_strategy": strategy.handcuff_strategy
        }
        
        return {
            "status": "success",
            "strategy": strategy_dict
        }
        
    except Exception as e:
        logger.error(f"Error creating draft strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Draft strategy creation failed: {str(e)}")

# Simplified draft endpoints (can be expanded later)
@app.get("/ai/test-trade-analysis")
def test_trade_analysis() -> Dict[str, Any]:
    """Test endpoint for AI trade analysis without API keys"""
    try:
        # Test with your league
        trade_analyzer = AITradeAnalyzer()  # No AI keys - uses fallback
        trades = trade_analyzer.analyze_all_league_trades("83806", platform_service)
        
        return {
            "status": "success",
            "message": f"Trade analysis test completed",
            "trades_found": len(trades),
            "sample_trade": trades[0].__dict__ if trades else None
        }
        
    except Exception as e:
        logger.error(f"Error in trade analysis test: {e}")
        return {
            "status": "error",
            "message": f"Test failed: {str(e)}"
        }

# Sleeper Integration Endpoints for Team Import

@app.get("/sleeper/user/{username}")
def get_sleeper_user(username: str) -> Dict[str, Any]:
    """
    Get Sleeper user data by username.
    
    Args:
        username (str): Sleeper username
        
    Returns:
        dict: User data from Sleeper API
    """
    try:
        user_data = platform_service.get_user_data("sleeper", username)
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"status": "success", "data": user_data}
    except Exception as e:
        logger.error(f"Error fetching Sleeper user: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/sleeper/user/{user_id}/leagues")
def get_sleeper_user_leagues(user_id: str, season: str = "2024") -> Dict[str, Any]:
    """
    Get user's Sleeper leagues for a specific season.
    
    Args:
        user_id (str): Sleeper user ID
        season (str): Season year (default: "2024")
        
    Returns:
        dict: User leagues data from Sleeper API
    """
    try:
        leagues_data = platform_service.get_sleeper_user_leagues(user_id, season)
        
        if not leagues_data:
            raise HTTPException(status_code=404, detail="No leagues found for user")
        
        return {"status": "success", "data": leagues_data}
    except Exception as e:
        logger.error(f"Error fetching Sleeper user leagues: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/sleeper/league/{league_id}/rosters")
def get_sleeper_league_rosters(league_id: str) -> Dict[str, Any]:
    """
    Get all rosters in a Sleeper league.
    
    Args:
        league_id (str): Sleeper league ID
        
    Returns:
        dict: League rosters data from Sleeper API
    """
    try:
        rosters_data = platform_service.get_sleeper_league_rosters(league_id)
        
        if not rosters_data:
            raise HTTPException(status_code=404, detail="League rosters not found")
        
        return {"status": "success", "data": rosters_data}
    except Exception as e:
        logger.error(f"Error fetching Sleeper league rosters: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/sleeper/league/{league_id}/users")  
def get_sleeper_league_users(league_id: str) -> Dict[str, Any]:
    """
    Get all users in a Sleeper league.
    
    Args:
        league_id (str): Sleeper league ID
        
    Returns:
        dict: League users data from Sleeper API
    """
    try:
        users_data = platform_service.get_sleeper_league_users(league_id)
        
        if not users_data:
            raise HTTPException(status_code=404, detail="League users not found")
        
        return {"status": "success", "data": users_data}
    except Exception as e:
        logger.error(f"Error fetching Sleeper league users: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
