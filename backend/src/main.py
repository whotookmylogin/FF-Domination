from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os

from src.database.connection import get_db
from src.analytics.advanced_analytics_service import AdvancedAnalyticsService
from src.platforms.service import PlatformIntegrationService
from src.ai.enhanced_trade_analyzer import AITradeAnalyzer
from src.ai.expert_draft_agent import ExpertDraftAgent
from src.news.service import NewsAggregationService
try:
    from src.news.advanced_monitor import AdvancedNewsMonitor, NewsScheduler
    from src.news.intelligent_notifications import IntelligentNotificationEngine, NotificationFormatter
    advanced_monitoring_available = True
except ImportError:
    advanced_monitoring_available = False
from src.cache.service import CacheService
from src.notifications.service import create_notification_service, NotificationService
from src.notifications.scheduler import (
    start_notification_scheduler, 
    stop_notification_scheduler, 
    schedule_lineup_reminder,
    schedule_breaking_news_alert
)
from src.waivers.enhanced_analyzer import EnhancedWaiverAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="Fantasy Football Domination API",
    description="API for Fantasy Football Domination App - Phase 3 Features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize platform integration service with credentials from environment
espn_s2 = os.getenv("ESPN_S2")
espn_swid = os.getenv("ESPN_SWID")
sleeper_token = os.getenv("SLEEPER_TOKEN")
platform_service = PlatformIntegrationService(espn_s2=espn_s2, espn_swid=espn_swid, sleeper_token=sleeper_token)

# Initialize cache, news, and notification services
cache_service = CacheService()
rotowire_api_key = os.getenv("ROTOWIRE_API_KEY")
news_service = NewsAggregationService(rotowire_api_key=rotowire_api_key)
notification_service = create_notification_service()

# Initialize waiver wire analyzer
waiver_analyzer = EnhancedWaiverAnalyzer(
    platform_service=platform_service,
    news_service=news_service
)

# Initialize advanced monitoring (will run 4x daily) if available
if advanced_monitoring_available:
    advanced_monitor = AdvancedNewsMonitor(
        openai_key=os.getenv("OPENAI_API_KEY"),
        x_bearer_token=os.getenv("X_BEARER_TOKEN"),
        check_frequency_hours=6  # 4 times per day
    )
    news_scheduler = NewsScheduler(advanced_monitor)
else:
    advanced_monitor = None
    news_scheduler = None

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
        # Get the league data and find the specific team
        league_id = os.getenv("ESPN_LEAGUE_ID", "83806")
        league_data = platform_service.get_league_data("espn", league_id)
        
        if not league_data:
            raise HTTPException(status_code=404, detail="League data not found")
        
        # Find the specific team
        team_data = None
        for team in league_data:
            if str(team.get("id")) == str(team_id):
                team_data = team
                break
        
        if not team_data:
            # Return default data for team 7
            team_data = {
                "id": team_id,
                "team_name": "Trashy McTrash-Face",
                "wins": 6,
                "losses": 8,
                "ties": 0,
                "points_for": 1636.0,
                "points_against": 1750.0
            }
        
        return {"status": "success", "data": team_data}
    except Exception as e:
        logger.error(f"Error fetching team data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/league/{league_id}/teams")
def get_all_league_teams(league_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get all teams in an ESPN league with their details.
    
    Args:
        league_id (str): ESPN league ID
        db (Session): Database session dependency
        
    Returns:
        dict: All teams in the league with their details
    """
    try:
        from src.platforms.espn_api_integration import ESPNAPIIntegration
        
        espn_s2 = os.getenv("ESPN_S2")
        espn_swid = os.getenv("ESPN_SWID")
        year = int(os.getenv("ESPN_SEASON_YEAR", "2025"))
        
        espn_integration = ESPNAPIIntegration(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2,
            swid=espn_swid
        )
        
        if not espn_integration.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to ESPN API")
        
        # Access the league object directly
        if not espn_integration.league:
            raise HTTPException(status_code=404, detail="League not found")
        
        teams_data = []
        for team in espn_integration.league.teams:
            team_info = {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "owners": [owner.get("firstName", "") + " " + owner.get("lastName", "") 
                          for owner in (team.owners if hasattr(team, "owners") else [])] if hasattr(team, "owners") else [],
                "wins": team.wins,
                "losses": team.losses,
                "ties": team.ties,
                "points_for": team.points_for,
                "points_against": team.points_against if hasattr(team, "points_against") else 0,
                "standing": team.standing,
                "roster_size": len(team.roster) if hasattr(team, "roster") else 0
            }
            teams_data.append(team_info)
        
        # Sort by standing
        teams_data.sort(key=lambda x: x["standing"])
        
        return {
            "status": "success",
            "league_id": league_id,
            "league_name": espn_integration.league.settings.name if hasattr(espn_integration.league, "settings") else "Unknown League",
            "season": year,
            "total_teams": len(teams_data),
            "teams": teams_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching league teams: {e}")
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
async def analyze_league_trades(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze all possible trades across the entire league using AI.
    Results are cached for 4 hours to avoid expensive recomputation.
    
    Body:
        {
            "league_id": "83806",
            "focus_team_id": "7",  # Optional: filter to trades involving this team
            "openai_key": "optional_openai_key",
            "openrouter_key": "optional_openrouter_key",
            "force_refresh": false,  # Optional: bypass cache
            "test_mode": false  # Optional: use mock data instead of real AI
        }
        
    Returns:
        dict: List of ranked trade opportunities with AI analysis
    """
    try:
        league_id = request_data.get("league_id")
        focus_team_id = request_data.get("focus_team_id")
        force_refresh = request_data.get("force_refresh", False)
        test_mode = request_data.get("test_mode", False)
        openai_key = request_data.get("openai_key") or os.getenv("OPENAI_API_KEY")
        openrouter_key = request_data.get("openrouter_key") or os.getenv("OPENROUTER_API_KEY")
        
        if not league_id:
            raise HTTPException(status_code=400, detail="league_id is required")
        
        # Create cache key based on league and team
        cache_key = f"trade_analysis:{league_id}"
        if focus_team_id:
            cache_key += f":team_{focus_team_id}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            try:
                cached_result = cache_service.get(cache_key)
                if cached_result:
                    logger.info(f"Returning cached trade analysis for {cache_key}")
                    cached_result["from_cache"] = True
                    cached_result["cache_key"] = cache_key
                    return cached_result
            except Exception as cache_error:
                logger.warning(f"Cache retrieval failed, proceeding with fresh analysis: {cache_error}")
        
        # Initialize AI trade analyzer with API keys from env if not provided
        trade_analyzer = AITradeAnalyzer(
            openai_key=openai_key,
            openrouter_key=openrouter_key
        )
        
        # Analyze all trades in the league
        logger.info(f"Starting AI trade analysis for league {league_id}")
        if focus_team_id:
            logger.info(f"Focusing on trades involving team {focus_team_id}")
        
        trade_opportunities = trade_analyzer.analyze_all_league_trades(league_id, platform_service, focus_team_id)
        
        # Filter to focus team if specified
        if focus_team_id:
            trade_opportunities = [
                t for t in trade_opportunities 
                if t.team_a_id == focus_team_id or t.team_b_id == focus_team_id
            ]
            logger.info(f"Filtered to {len(trade_opportunities)} trades involving team {focus_team_id}")
        
        if not trade_opportunities:
            return {
                "status": "success",
                "message": f"No viable trade opportunities found{' for team ' + focus_team_id if focus_team_id else ''}",
                "trades": []
            }
        
        # Convert dataclass objects to dictionaries
        trades_data = []
        for trade in trade_opportunities:
            trade_dict = {
                "team_a_id": trade.team_a_id,
                "team_b_id": trade.team_b_id,
                "team_a_name": getattr(trade, 'team_a_name', f'Team {trade.team_a_id}'),
                "team_b_name": getattr(trade, 'team_b_name', f'Team {trade.team_b_id}'),
                "team_a_gives": trade.team_a_gives,
                "team_a_gets": trade.team_a_gets,
                "team_b_gives": trade.team_b_gives,
                "team_b_gets": trade.team_b_gets,
                "fairness_score": trade.fairness_score,
                "team_a_improvement": trade.team_a_improvement,
                "team_b_improvement": trade.team_b_improvement,
                "ai_analysis": trade.ai_analysis,
                "confidence_score": trade.confidence_score,
                "urgency": trade.urgency,
                "bye_week_impact": getattr(trade, 'bye_week_impact', None),
                "matchup_advantage": getattr(trade, 'matchup_advantage', None),
                "timing_recommendation": getattr(trade, 'timing_recommendation', None)
            }
            trades_data.append(trade_dict)
        
        logger.info(f"Found {len(trades_data)} trade opportunities")
        
        # Prepare response
        response_data = {
            "status": "success",
            "message": f"Found {len(trades_data)} trade opportunities",
            "trades": trades_data,
            "analysis_timestamp": datetime.now().isoformat(),
            "from_cache": False
        }
        
        # Cache the results for 4 hours (240 minutes)
        try:
            cache_success = cache_service.set(cache_key, response_data, expiration_minutes=240)
            if cache_success:
                logger.info(f"Cached trade analysis results with key: {cache_key}")
            else:
                logger.warning(f"Failed to cache trade analysis results")
        except Exception as cache_error:
            logger.warning(f"Cache storage failed: {cache_error}")
        
        return response_data
        
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

@app.get("/cache/status")
def get_cache_status() -> Dict[str, Any]:
    """
    Get cache status and statistics
    """
    try:
        # Try to get info from Redis
        info = cache_service.redis_client.info('memory')
        keys = cache_service.redis_client.keys('trade_analysis:*')
        
        cached_analyses = []
        for key in keys:
            ttl = cache_service.redis_client.ttl(key)
            cached_analyses.append({
                "key": key,
                "ttl_seconds": ttl,
                "ttl_minutes": ttl // 60 if ttl > 0 else 0
            })
        
        return {
            "status": "connected",
            "memory_used": info.get('used_memory_human', 'unknown'),
            "cached_trade_analyses": len(keys),
            "cache_entries": cached_analyses
        }
    except Exception as e:
        logger.warning(f"Cache status check failed: {e}")
        return {
            "status": "disconnected",
            "message": "Redis cache not available",
            "error": str(e)
        }

@app.post("/cache/clear")
def clear_cache(
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Clear specific cache entries or all cache
    
    Body:
        {
            "pattern": "trade_analysis:*",  # Optional pattern to clear
            "all": false  # Clear all cache entries
        }
    """
    try:
        pattern = request_data.get("pattern")
        clear_all = request_data.get("all", False)
        
        if clear_all:
            result = cache_service.flush()
            return {
                "status": "success",
                "message": "All cache entries cleared"
            }
        elif pattern:
            keys = cache_service.redis_client.keys(pattern)
            deleted_count = 0
            for key in keys:
                if cache_service.delete(key):
                    deleted_count += 1
            return {
                "status": "success",
                "message": f"Cleared {deleted_count} cache entries matching pattern: {pattern}"
            }
        else:
            return {
                "status": "error",
                "message": "Specify either 'pattern' or 'all' parameter"
            }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        return {
            "status": "error",
            "message": f"Failed to clear cache: {str(e)}"
        }

@app.post("/ai/quick-trade-analysis")
async def quick_trade_analysis(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Quick mock trade analysis for testing (no AI, instant response)
    """
    league_id = request_data.get("league_id", "83806")
    focus_team_id = request_data.get("focus_team_id", "7")
    
    # Generate some mock trades with full data structure
    mock_trades = [
        {
            "team_a_id": focus_team_id,
            "team_b_id": "3",
            "team_a_gives": [{"name": "Austin Ekeler", "position": "RB", "team": "LAC"}],
            "team_a_gets": [{"name": "Calvin Ridley", "position": "WR", "team": "JAX"}],
            "team_b_gives": [{"name": "Calvin Ridley", "position": "WR", "team": "JAX"}],
            "team_b_gets": [{"name": "Austin Ekeler", "position": "RB", "team": "LAC"}],
            "fairness_score": 52,
            "team_a_improvement": 3.5,
            "team_b_improvement": 2.1,
            "ai_analysis": "Mock: This trade helps your WR depth while Team 3 gets RB help. Fair value exchange.",
            "confidence_score": 0.75,
            "urgency": "MEDIUM",
            "bye_week_impact": {
                "team_a": {"improves": True, "weeks_affected": [], "details": "Better bye week coverage at WR"},
                "team_b": {"improves": False, "weeks_affected": [7], "details": "Loses WR depth for week 7"}
            },
            "matchup_advantage": {
                "team_a": {"weeks_improved": [1, 3], "strength_change": 4, "details": "Ridley has easy matchups weeks 1 and 3"},
                "team_b": {"weeks_improved": [], "strength_change": -4, "details": ""}
            },
            "timing_recommendation": "EXECUTE THIS WEEK - Strong upcoming matchups"
        },
        {
            "team_a_id": focus_team_id,
            "team_b_id": "5",
            "team_a_gives": [{"name": "Darren Waller", "position": "TE", "team": "NYG"}],
            "team_a_gets": [{"name": "George Kittle", "position": "TE", "team": "SF"}],
            "team_b_gives": [{"name": "George Kittle", "position": "TE", "team": "SF"}],
            "team_b_gets": [{"name": "Darren Waller", "position": "TE", "team": "NYG"}],
            "fairness_score": 45,
            "team_a_improvement": 5.2,
            "team_b_improvement": -1.3,
            "ai_analysis": "Mock: Significant upgrade at TE position. Kittle is elite when healthy.",
            "confidence_score": 0.82,
            "urgency": "HIGH",
            "bye_week_impact": {
                "team_a": {"improves": False, "weeks_affected": [9], "details": "Same bye week (9) for both TEs"},
                "team_b": {"improves": False, "weeks_affected": [9], "details": "Same bye week (9) for both TEs"}
            },
            "matchup_advantage": {
                "team_a": {"weeks_improved": [2, 4, 5], "strength_change": 8, "details": "Kittle faces weak TE defenses"},
                "team_b": {"weeks_improved": [], "strength_change": -8, "details": "Downgrade in matchups"}
            },
            "timing_recommendation": "EXECUTE IMMEDIATELY - Bye week coverage needed"
        }
    ]
    
    return {
        "status": "success",
        "message": f"Mock analysis complete for league {league_id}",
        "trades": mock_trades
    }

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

# News Aggregation Endpoints

@app.get("/news/aggregated")
def get_aggregated_news() -> Dict[str, Any]:
    """
    Get aggregated news from all sources with deduplication and caching.
    
    Returns:
        dict: Aggregated news from ESPN, NFL.com, and FantasyPros
    """
    try:
        news_items = news_service.aggregate_news()
        
        return {
            "status": "success",
            "count": len(news_items),
            "data": news_items
        }
    except Exception as e:
        logger.error(f"Error fetching aggregated news: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/breaking")
def get_breaking_news(min_urgency: int = 4) -> Dict[str, Any]:
    """
    Get breaking news items with urgency score above threshold.
    
    Args:
        min_urgency (int): Minimum urgency score (1-5, default: 4)
        
    Returns:
        dict: Breaking news items with high urgency
    """
    try:
        if min_urgency < 1 or min_urgency > 5:
            raise HTTPException(status_code=400, detail="min_urgency must be between 1 and 5")
        
        breaking_news = news_service.get_breaking_news(min_urgency=min_urgency)
        
        return {
            "status": "success",
            "min_urgency": min_urgency,
            "count": len(breaking_news),
            "data": breaking_news
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching breaking news: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/source/{source_name}")
def get_news_by_source(source_name: str) -> Dict[str, Any]:
    """
    Get news items from a specific source.
    
    Args:
        source_name (str): Source name ('espn', 'nfl', 'fantasypros')
        
    Returns:
        dict: News items from the specified source
    """
    try:
        valid_sources = ['espn', 'nfl', 'fantasypros']
        if source_name.lower() not in valid_sources:
            raise HTTPException(status_code=400, detail=f"Invalid source. Must be one of: {', '.join(valid_sources)}")
        
        news_items = news_service.get_news_by_source(source_name)
        
        return {
            "status": "success",
            "source": source_name,
            "count": len(news_items),
            "data": news_items
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news from {source_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/refresh")
def refresh_news_cache() -> Dict[str, Any]:
    """
    Force refresh of news cache and fetch fresh data from all sources.
    
    Returns:
        dict: Cache refresh status and statistics
    """
    try:
        refresh_result = news_service.refresh_cache()
        
        return {
            "status": "success",
            "message": "News cache refreshed successfully",
            "details": refresh_result
        }
    except Exception as e:
        logger.error(f"Error refreshing news cache: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/save/{league_id}")
def save_news_to_database(league_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Save current aggregated news to database for a specific league.
    
    Args:
        league_id (str): League ID to associate with news items
        db (Session): Database session dependency
        
    Returns:
        dict: Number of news items saved
    """
    try:
        # Get fresh aggregated news
        news_items = news_service.aggregate_news()
        
        # Save to database
        saved_count = news_service.save_news_to_database(league_id, news_items, db)
        
        return {
            "status": "success",
            "message": f"Saved {saved_count} news items to database",
            "league_id": league_id,
            "saved_count": saved_count
        }
    except Exception as e:
        logger.error(f"Error saving news to database: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/test")
def test_news_sources() -> Dict[str, Any]:
    """
    Test all news sources and return their status.
    
    Returns:
        dict: Status information for all news sources
    """
    try:
        from src.news.sources import test_all_sources
        
        test_results = test_all_sources(rotowire_api_key)
        
        return {
            "status": "success",
            "message": "News source testing completed",
            "sources": test_results
        }
    except Exception as e:
        logger.error(f"Error testing news sources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/stats")
def get_news_statistics() -> Dict[str, Any]:
    """
    Get statistics about the current news aggregation.
    
    Returns:
        dict: News aggregation statistics
    """
    try:
        # Get news from all sources
        all_news = news_service.aggregate_news()
        
        # Calculate statistics
        total_count = len(all_news)
        source_counts = {}
        urgency_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for item in all_news:
            source = item.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
            
            urgency = item.get('urgency_score', 1)
            if urgency in urgency_counts:
                urgency_counts[urgency] += 1
        
        return {
            "status": "success",
            "total_news_items": total_count,
            "source_breakdown": source_counts,
            "urgency_breakdown": urgency_counts,
            "breaking_news_count": sum(count for urgency, count in urgency_counts.items() if urgency >= 4)
        }
    except Exception as e:
        logger.error(f"Error getting news statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# News Background Task Management Endpoints

@app.post("/news/tasks/refresh")
def trigger_news_refresh() -> Dict[str, Any]:
    """
    Manually trigger a news refresh task.
    
    Returns:
        dict: Task execution result
    """
    try:
        from src.news.scheduler import refresh_all_caches
        
        # Trigger async task
        task = refresh_all_caches.delay()
        
        return {
            "status": "success",
            "message": "News refresh task triggered",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Error triggering news refresh: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/tasks/test-sources")
def trigger_source_test() -> Dict[str, Any]:
    """
    Manually trigger a news sources test task.
    
    Returns:
        dict: Task execution result
    """
    try:
        from src.news.scheduler import test_all_sources
        
        # Trigger async task
        task = test_all_sources.delay()
        
        return {
            "status": "success",
            "message": "Source test task triggered",
            "task_id": task.id
        }
    except Exception as e:
        logger.error(f"Error triggering source test: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/tasks/{task_id}")
def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a background task.
    
    Args:
        task_id (str): Task ID to check
        
    Returns:
        dict: Task status and result
    """
    try:
        from src.news.scheduler import celery_app
        
        task = celery_app.AsyncResult(task_id)
        
        return {
            "status": "success",
            "task_id": task_id,
            "task_status": task.status,
            "task_result": task.result if task.ready() else None,
            "task_info": task.info
        }
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/tasks/active")
def get_active_tasks() -> Dict[str, Any]:
    """
    Get information about active background tasks.
    
    Returns:
        dict: Active tasks information
    """
    try:
        from src.news.scheduler import celery_app
        
        # Get active tasks
        active_tasks = celery_app.control.inspect().active()
        
        # Get scheduled tasks
        scheduled_tasks = celery_app.control.inspect().scheduled()
        
        return {
            "status": "success",
            "active_tasks": active_tasks or {},
            "scheduled_tasks": scheduled_tasks or {},
            "available_workers": list(active_tasks.keys()) if active_tasks else []
        }
    except Exception as e:
        logger.error(f"Error getting active tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Notification System Endpoints

@app.post("/notifications/send")
def send_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send a notification to a user.
    
    Body:
        {
            "user_id": "user123",
            "title": "Test Notification",
            "message": "This is a test message",
            "type": "test",
            "priority": 1,
            "data": {},
            "channels": ["email", "push", "sms"]
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        title = request_data.get("title")
        message = request_data.get("message")
        notification_type = request_data.get("type", "general")
        priority = request_data.get("priority", 1)
        data = request_data.get("data")
        force_channels = request_data.get("channels")
        
        if not all([user_id, title, message]):
            raise HTTPException(status_code=400, detail="user_id, title, and message are required")
        
        result = notification_service.send_notification(
            db, user_id, title, message, notification_type, priority, data, force_channels
        )
        
        return {
            "status": "success",
            "message": "Notification sent successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/notifications/user/{user_id}")
def get_user_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get notifications for a user.
    
    Args:
        user_id (str): User ID
        unread_only (bool): Only return unread notifications
        limit (int): Maximum number of notifications to return
        
    Returns:
        dict: User notifications
    """
    try:
        notifications = notification_service.get_user_notifications(
            db, user_id, unread_only, limit
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "count": len(notifications),
            "unread_only": unread_only,
            "notifications": notifications
        }
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/mark-read")
def mark_notifications_as_read(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Mark notifications as read.
    
    Body:
        {
            "user_id": "user123",
            "notification_ids": ["notif1", "notif2"] // optional, marks all if not provided
        }
        
    Returns:
        dict: Number of notifications marked as read
    """
    try:
        user_id = request_data.get("user_id")
        notification_ids = request_data.get("notification_ids")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        count = notification_service.mark_notifications_as_read(
            db, user_id, notification_ids
        )
        
        return {
            "status": "success",
            "message": f"Marked {count} notifications as read",
            "user_id": user_id,
            "count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notifications as read: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/notifications/preferences/{user_id}")
def get_notification_preferences(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's notification preferences.
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: User's notification preferences
    """
    try:
        preferences = notification_service.get_user_preferences(db, user_id)
        
        return {
            "status": "success",
            "user_id": user_id,
            "preferences": {
                "email_enabled": preferences.email_enabled,
                "email_trade_proposals": preferences.email_trade_proposals,
                "email_waiver_results": preferences.email_waiver_results,
                "email_breaking_news": preferences.email_breaking_news,
                "email_lineup_reminders": preferences.email_lineup_reminders,
                "email_injury_updates": preferences.email_injury_updates,
                "push_enabled": preferences.push_enabled,
                "push_trade_proposals": preferences.push_trade_proposals,
                "push_waiver_results": preferences.push_waiver_results,
                "push_breaking_news": preferences.push_breaking_news,
                "push_lineup_reminders": preferences.push_lineup_reminders,
                "push_injury_updates": preferences.push_injury_updates,
                "sms_enabled": preferences.sms_enabled,
                "sms_phone_number": preferences.sms_phone_number,
                "sms_urgent_only": preferences.sms_urgent_only,
                "in_app_enabled": preferences.in_app_enabled,
                "lineup_reminder_time": preferences.lineup_reminder_time,
                "quiet_hours_start": preferences.quiet_hours_start,
                "quiet_hours_end": preferences.quiet_hours_end
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/notifications/preferences/{user_id}")
def update_notification_preferences(
    user_id: str,
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update user's notification preferences.
    
    Args:
        user_id (str): User ID
        
    Body:
        {
            "email_enabled": true,
            "email_trade_proposals": true,
            "push_enabled": true,
            "sms_enabled": false,
            "sms_phone_number": "+1234567890",
            ...
        }
        
    Returns:
        dict: Updated preferences
    """
    try:
        updated_preferences = notification_service.update_notification_preferences(
            db, user_id, request_data
        )
        
        return {
            "status": "success",
            "message": "Notification preferences updated successfully",
            "user_id": user_id,
            "updated_at": updated_preferences.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/test/{user_id}")
def test_notification_channels(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test all notification channels for a user.
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: Test results for each channel
    """
    try:
        result = notification_service.test_notification_channels(db, user_id)
        
        return {
            "status": "success",
            "message": "Notification test completed",
            "user_id": user_id,
            "test_results": result
        }
        
    except Exception as e:
        logger.error(f"Error testing notification channels: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Template-based notification endpoints

@app.post("/notifications/trade-proposal")
def send_trade_proposal_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send a trade proposal notification using template.
    
    Body:
        {
            "user_id": "user123",
            "trade_data": {
                "you_give": ["Player A", "Player B"],
                "you_get": ["Player C"],
                "fairness_score": 85,
                "win_probability_delta": 12.5
            }
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        trade_data = request_data.get("trade_data", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        result = notification_service.send_trade_proposal_notification(
            db, user_id, trade_data
        )
        
        return {
            "status": "success",
            "message": "Trade proposal notification sent",
            "user_id": user_id,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending trade proposal notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/waiver-wire/{league_id}")
def get_waiver_wire_players(
    league_id: str,
    position: Optional[str] = None,
    size: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get available free agents from ESPN waiver wire.
    
    Args:
        league_id (str): ESPN league ID
        position (str, optional): Filter by position (QB, RB, WR, TE)
        size (int): Number of players to return
        db (Session): Database session dependency
        
    Returns:
        dict: Available free agents with recommendations
    """
    try:
        # Get free agents from ESPN
        from src.platforms.espn_api_integration import ESPNAPIIntegration
        import os
        
        espn_s2 = os.getenv("ESPN_S2")
        espn_swid = os.getenv("ESPN_SWID")
        year = int(os.getenv("ESPN_SEASON_YEAR", "2025"))
        
        espn_integration = ESPNAPIIntegration(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2,
            swid=espn_swid
        )
        
        if not espn_integration.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to ESPN API")
        
        free_agents = espn_integration.get_free_agents(position=position, size=size)
        
        # Add recommendation scores based on projected points and ownership
        for player in free_agents:
            # Simple recommendation logic
            proj_points = player.get('projected_points', 0)
            percent_owned = player.get('percent_owned', 0)
            
            # Calculate recommendation score (0-100)
            score = (proj_points * 2) + ((100 - percent_owned) * 0.3)
            player['recommendation_score'] = min(100, max(0, score))
            
            # Add bid recommendation based on score
            if score > 70:
                player['bid_recommendation'] = 'CLAIM'
                player['recommended_bid'] = max(5, int(score / 5))
            elif score > 40:
                player['bid_recommendation'] = 'WATCH'
                player['recommended_bid'] = max(1, int(score / 10))
            else:
                player['bid_recommendation'] = 'PASS'
                player['recommended_bid'] = 0
        
        # Sort by recommendation score
        free_agents.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        
        return {
            "status": "success",
            "league_id": league_id,
            "position_filter": position,
            "count": len(free_agents),
            "free_agents": free_agents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching waiver wire data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/waiver-wire/{league_id}/enhanced-analysis")
async def get_enhanced_waiver_analysis(
    league_id: str,
    team_id: str,
    platform: str = "espn",
    current_week: int = 1,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get personalized waiver wire recommendations based on team needs,
    bye weeks, matchups, and value comparisons.
    
    Args:
        league_id (str): League ID
        team_id (str): Team ID to analyze for
        platform (str): Platform (espn or sleeper)
        current_week (int): Current NFL week
        db (Session): Database session dependency
        
    Returns:
        dict: Enhanced waiver analysis with personalized recommendations
    """
    try:
        # Run enhanced waiver analysis
        analysis = await waiver_analyzer.analyze_waiver_opportunities(
            league_id=league_id,
            team_id=team_id,
            platform=platform,
            current_week=current_week
        )
        
        if analysis.get("status") == "error":
            raise HTTPException(status_code=500, detail=analysis.get("message"))
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced waiver analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/waiver-wire/compare-players")
def compare_waiver_players(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare a waiver wire player with current roster player.
    
    Body:
        {
            "waiver_player_id": "player123",
            "roster_player_id": "player456",
            "league_id": "league789",
            "platform": "espn",
            "weeks_ahead": 4
        }
        
    Returns:
        dict: Detailed comparison with recommendation
    """
    try:
        waiver_player_id = request_data.get("waiver_player_id")
        roster_player_id = request_data.get("roster_player_id")
        league_id = request_data.get("league_id")
        platform = request_data.get("platform", "espn")
        weeks_ahead = request_data.get("weeks_ahead", 4)
        
        if not all([waiver_player_id, roster_player_id, league_id]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Get player data based on platform
        if platform == "espn":
            from src.platforms.espn_api_integration import ESPNAPIIntegration
            espn_integration = ESPNAPIIntegration(
                league_id=league_id,
                year=int(os.getenv("ESPN_SEASON_YEAR", "2025")),
                espn_s2=os.getenv("ESPN_S2"),
                swid=os.getenv("ESPN_SWID")
            )
            if not espn_integration.connect():
                raise HTTPException(status_code=500, detail="Failed to connect to ESPN API")
            
            # Get player comparisons (would need to implement in ESPN integration)
            waiver_player = {"id": waiver_player_id, "name": "Waiver Player", "projected_points": 12.5}
            roster_player = {"id": roster_player_id, "name": "Roster Player", "projected_points": 10.2}
        else:
            # Sleeper implementation
            waiver_player = {"id": waiver_player_id, "name": "Waiver Player", "projected_points": 12.5}
            roster_player = {"id": roster_player_id, "name": "Roster Player", "projected_points": 10.2}
        
        # Calculate comparison metrics
        points_diff = waiver_player["projected_points"] - roster_player["projected_points"]
        percentage_improvement = (points_diff / roster_player["projected_points"]) * 100 if roster_player["projected_points"] > 0 else 0
        
        comparison = {
            "waiver_player": waiver_player,
            "roster_player": roster_player,
            "points_difference": points_diff,
            "percentage_improvement": percentage_improvement,
            "recommendation": "CLAIM" if points_diff > 3 else "HOLD" if points_diff > 0 else "PASS",
            "analysis": {
                "immediate_impact": points_diff > 5,
                "season_long_value": points_diff > 2,
                "matchup_advantage_next_week": True,  # Would calculate based on actual matchups
                "injury_risk_comparison": "similar"  # Would analyze injury history
            }
        }
        
        return {
            "status": "success",
            "comparison": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing players: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/waiver-results")
def send_waiver_results_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send waiver results notification using template.
    
    Body:
        {
            "user_id": "user123",
            "waiver_data": {
                "successful_claims": [
                    {"player_name": "Player A", "bid_amount": 25}
                ],
                "failed_claims": [
                    {"player_name": "Player B", "winning_bid": 50}
                ]
            }
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        waiver_data = request_data.get("waiver_data", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        result = notification_service.send_waiver_results_notification(
            db, user_id, waiver_data
        )
        
        return {
            "status": "success",
            "message": "Waiver results notification sent",
            "user_id": user_id,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending waiver results notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/breaking-news")
def send_breaking_news_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send breaking news notification using template.
    
    Body:
        {
            "user_id": "user123",
            "news_data": {
                "headline": "Player X suffers season-ending injury",
                "summary": "Details about the injury...",
                "urgency_score": 5,
                "affected_players": ["Player X"],
                "source": "ESPN"
            }
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        news_data = request_data.get("news_data", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        result = notification_service.send_breaking_news_notification(
            db, user_id, news_data
        )
        
        return {
            "status": "success",
            "message": "Breaking news notification sent",
            "user_id": user_id,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending breaking news notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/lineup-reminder")
def send_lineup_reminder_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send lineup reminder notification using template.
    
    Body:
        {
            "user_id": "user123",
            "reminder_data": {
                "week": 8,
                "hours_until_games": 2
            }
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        reminder_data = request_data.get("reminder_data", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        result = notification_service.send_lineup_reminder_notification(
            db, user_id, reminder_data
        )
        
        return {
            "status": "success",
            "message": "Lineup reminder notification sent",
            "user_id": user_id,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending lineup reminder notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/injury-update")
def send_injury_update_notification(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send injury update notification using template.
    
    Body:
        {
            "user_id": "user123",
            "injury_data": {
                "player_name": "Player X",
                "status": "out",
                "injury_type": "ACL tear",
                "expected_return": "Next season",
                "fantasy_impact": "Drop immediately"
            }
        }
        
    Returns:
        dict: Notification send result
    """
    try:
        user_id = request_data.get("user_id")
        injury_data = request_data.get("injury_data", {})
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        result = notification_service.send_injury_update_notification(
            db, user_id, injury_data
        )
        
        return {
            "status": "success",
            "message": "Injury update notification sent",
            "user_id": user_id,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending injury update notification: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Notification Scheduler Endpoints

@app.post("/notifications/scheduler/start")
def start_scheduler() -> Dict[str, Any]:
    """
    Start the notification scheduler.
    
    Returns:
        dict: Scheduler start status
    """
    try:
        start_notification_scheduler()
        
        return {
            "status": "success",
            "message": "Notification scheduler started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting notification scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/scheduler/stop")
def stop_scheduler() -> Dict[str, Any]:
    """
    Stop the notification scheduler.
    
    Returns:
        dict: Scheduler stop status
    """
    try:
        stop_notification_scheduler()
        
        return {
            "status": "success",
            "message": "Notification scheduler stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping notification scheduler: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/schedule/lineup-reminder")
def schedule_lineup_reminder_endpoint(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule a lineup reminder for a user.
    
    Body:
        {
            "user_id": "user123",
            "game_time": "2024-01-07T13:00:00Z",
            "hours_before": 2
        }
        
    Returns:
        dict: Schedule result
    """
    try:
        user_id = request_data.get("user_id")
        game_time_str = request_data.get("game_time")
        hours_before = request_data.get("hours_before", 2)
        
        if not all([user_id, game_time_str]):
            raise HTTPException(status_code=400, detail="user_id and game_time are required")
        
        # Parse game time
        from datetime import datetime
        game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
        
        schedule_lineup_reminder(db, user_id, game_time, hours_before)
        
        return {
            "status": "success",
            "message": "Lineup reminder scheduled successfully",
            "user_id": user_id,
            "game_time": game_time_str,
            "hours_before": hours_before
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling lineup reminder: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/notifications/schedule/breaking-news")
def schedule_breaking_news_endpoint(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Send breaking news alerts to affected users.
    
    Body:
        {
            "news_data": {
                "headline": "Player X suffers injury",
                "summary": "Details...",
                "urgency_score": 5,
                "affected_players": ["Player X"],
                "source": "ESPN"
            },
            "affected_user_ids": ["user1", "user2"]
        }
        
    Returns:
        dict: Alert send result
    """
    try:
        news_data = request_data.get("news_data", {})
        affected_user_ids = request_data.get("affected_user_ids", [])
        
        if not news_data:
            raise HTTPException(status_code=400, detail="news_data is required")
        
        schedule_breaking_news_alert(db, news_data, affected_user_ids)
        
        return {
            "status": "success",
            "message": "Breaking news alerts sent successfully",
            "affected_users": len(affected_user_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending breaking news alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/notifications/scheduler/status")
def get_scheduler_status() -> Dict[str, Any]:
    """
    Get notification scheduler status.
    
    Returns:
        dict: Scheduler status information
    """
    try:
        from src.notifications.scheduler import notification_scheduler
        
        return {
            "status": "success",
            "scheduler_running": notification_scheduler.running,
            "thread_alive": notification_scheduler.scheduler_thread.is_alive() if notification_scheduler.scheduler_thread else False
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Advanced Monitoring Endpoints

@app.get("/news/advanced/monitor")
async def monitor_advanced_news() -> Dict[str, Any]:
    """
    Run advanced news monitoring across all sources.
    Checks training camps, X/Twitter, and provides strategic recommendations.
    
    Returns:
        dict: Analyzed news items with fantasy impact and recommendations
    """
    if not advanced_monitor:
        raise HTTPException(status_code=503, detail="Advanced monitoring not available")
    
    try:
        import asyncio
        news_items = await advanced_monitor.monitor_all_sources()
        
        # Format for response
        formatted_items = []
        for item in news_items[:20]:  # Return top 20 items
            formatted_items.append({
                "source": item.source,
                "title": item.title,
                "content": item.content[:500],  # Truncate content
                "url": item.url,
                "timestamp": item.timestamp.isoformat(),
                "players_mentioned": item.players_mentioned,
                "teams_affected": item.teams_affected,
                "impact_level": item.impact_level.value,
                "fantasy_relevance_score": item.fantasy_relevance_score,
                "recommendation": item.recommendation.value if item.recommendation else None,
                "strategic_analysis": item.strategic_analysis,
                "action_deadline": item.action_deadline.isoformat() if item.action_deadline else None
            })
        
        return {
            "status": "success",
            "count": len(formatted_items),
            "data": formatted_items,
            "last_check": advanced_monitor.last_check.isoformat()
        }
    except Exception as e:
        logger.error(f"Error in advanced monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/intelligent-notifications/{user_team_id}")
def get_intelligent_notifications(
    user_team_id: str,
    league_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get intelligent, personalized notifications for a user's team.
    
    Args:
        user_team_id: User's team ID
        league_id: League ID
        
    Returns:
        dict: Personalized actionable notifications
    """
    if not advanced_monitor:
        raise HTTPException(status_code=503, detail="Advanced monitoring not available")
    
    try:
        # Initialize notification engine
        notif_engine = IntelligentNotificationEngine(user_team_id, league_id)
        
        # Get user roster and league context (would fetch from DB)
        user_roster = []  # TODO: Fetch from database
        league_context = {"standings": {}, "settings": {}}  # TODO: Fetch from database
        upcoming_matchups = []  # TODO: Fetch from database
        
        # Generate notifications
        notifications = notif_engine.generate_notifications(
            news_items=advanced_monitor.news_cache,
            user_roster=user_roster,
            league_context=league_context,
            upcoming_matchups=upcoming_matchups
        )
        
        # Format notifications
        formatted_notifs = []
        for notif in notifications[:10]:  # Return top 10 notifications
            formatted_notifs.append(NotificationFormatter.format_for_ui(notif))
        
        return {
            "status": "success",
            "count": len(formatted_notifs),
            "data": formatted_notifs,
            "team_id": user_team_id,
            "league_id": league_id
        }
    except Exception as e:
        logger.error(f"Error getting intelligent notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/news/strategic-recommendations/{user_team_id}")
def get_strategic_recommendations(
    user_team_id: str,
    league_id: str,
    upcoming_opponent: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get strategic recommendations including blocking opponents and long-term positioning.
    
    Args:
        user_team_id: User's team ID
        league_id: League ID
        upcoming_opponent: Next opponent's team name
        
    Returns:
        dict: Strategic recommendations for maximizing league position
    """
    if not advanced_monitor:
        raise HTTPException(status_code=503, detail="Advanced monitoring not available")
    
    try:
        # Get user roster and league standings (would fetch from DB)
        user_roster = []  # TODO: Fetch from database
        league_standings = {}  # TODO: Fetch from database
        
        # Get actionable notifications
        notifications = advanced_monitor.get_actionable_notifications(
            user_roster=user_roster,
            league_standings=league_standings,
            upcoming_opponent=upcoming_opponent
        )
        
        # Separate by strategy type
        direct_benefit = []
        strategic_blocks = []
        opponent_recommendations = []
        
        for notif in notifications:
            if notif["type"] == "roster_alert":
                direct_benefit.append(notif)
            elif notif["type"] == "strategic_block":
                strategic_blocks.append(notif)
            elif notif["type"] == "strategic_recommendation":
                opponent_recommendations.append(notif)
        
        return {
            "status": "success",
            "direct_benefit": direct_benefit,
            "strategic_blocks": strategic_blocks,
            "opponent_recommendations": opponent_recommendations,
            "upcoming_opponent": upcoming_opponent
        }
    except Exception as e:
        logger.error(f"Error getting strategic recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/monitoring/start")
async def start_news_monitoring() -> Dict[str, Any]:
    """
    Start the automated news monitoring scheduler (runs 4x daily).
    
    Returns:
        dict: Scheduler status
    """
    if not news_scheduler:
        raise HTTPException(status_code=503, detail="News scheduler not available")
    
    try:
        import asyncio
        # Start scheduler in background
        asyncio.create_task(news_scheduler.start())
        
        return {
            "status": "success",
            "message": "News monitoring started",
            "check_frequency_hours": advanced_monitor.check_frequency,
            "running": news_scheduler.running
        }
    except Exception as e:
        logger.error(f"Error starting news monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/news/monitoring/stop")
def stop_news_monitoring() -> Dict[str, Any]:
    """
    Stop the automated news monitoring scheduler.
    
    Returns:
        dict: Scheduler status
    """
    if not news_scheduler:
        raise HTTPException(status_code=503, detail="News scheduler not available")
    
    try:
        news_scheduler.stop()
        
        return {
            "status": "success",
            "message": "News monitoring stopped",
            "running": news_scheduler.running
        }
    except Exception as e:
        logger.error(f"Error stopping news monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
