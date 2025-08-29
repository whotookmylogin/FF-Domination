import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from sqlalchemy.orm import Session
from .recommendation_engine import AIRecommendationEngine
from ..database.models import League, Team, Player, RosterSlot

class MultiLeagueOptimizer:
    """
    Multi-league optimization service that extends the AI recommendation engine
    to provide recommendations across multiple leagues for a single user.
    """
    
    def __init__(self, db_session: Session = None):
        """Initialize the multi-league optimizer."""
        self.ai_engine = AIRecommendationEngine()
        self.db_session = db_session
        self.optimization_version = "1.0"
        
    def analyze_user_leagues(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze all leagues for a user to provide cross-league optimization recommendations.
        
        Args:
            user_id (str): User ID to analyze leagues for
            
        Returns:
            dict: Multi-league analysis with recommendations
        """
        if not self.db_session:
            logging.warning("No database session provided, returning empty analysis")
            return {"leagues": [], "recommendations": []}
            
        try:
            # Get all leagues for the user
            leagues = self.db_session.query(League).filter(League.user_id == user_id).all()
            
            league_analysis = []
            for league in leagues:
                analysis = self._analyze_single_league(league)
                league_analysis.append(analysis)
                
            # Generate cross-league recommendations
            recommendations = self._generate_cross_league_recommendations(league_analysis)
            
            return {
                "user_id": user_id,
                "leagues": league_analysis,
                "recommendations": recommendations,
                "optimization_version": self.optimization_version
            }
            
        except Exception as e:
            logging.error(f"Error analyzing user leagues: {str(e)}")
            return {"error": str(e), "leagues": [], "recommendations": []}
    
    def _analyze_single_league(self, league: League) -> Dict[str, Any]:
        """
        Analyze a single league for optimization opportunities.
        
        Args:
            league (League): League model instance
            
        Returns:
            dict: League analysis data
        """
        try:
            # Get user's team in this league
            user_teams = [team for team in league.teams if team.owner == league.user.username]
            if not user_teams:
                return {"league_id": league.id, "error": "User team not found in league"}
                
            user_team = user_teams[0]
            
            # Get team roster data
            roster_slots = user_team.roster
            players = [slot.player for slot in roster_slots]
            
            # Get team strength analysis from AI engine
            team_data = {
                "players": [
                    {
                        "name": player.name,
                        "position": player.position,
                        "projected_score": player.projected_points,
                        "injury_status": player.injury_status
                    }
                    for player in players
                ]
            }
            
            team_strength = self.ai_engine._calculate_team_strength(team_data)
            
            return {
                "league_id": league.id,
                "platform": league.platform,
                "league_name": league.league_name,
                "team_name": user_team.team_name,
                "team_strength": team_strength,
                "rank": user_team.rank,
                "total_teams": league.total_teams,
                "current_week": league.current_week
            }
            
        except Exception as e:
            logging.error(f"Error analyzing league {league.id}: {str(e)}")
            return {"league_id": league.id, "error": str(e)}
    
    def _generate_cross_league_recommendations(self, league_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on cross-league analysis.
        
        Args:
            league_analysis (list): List of league analysis data
            
        Returns:
            list: Cross-league recommendations
        """
        recommendations = []
        
        # Filter out leagues with errors
        valid_leagues = [league for league in league_analysis if "error" not in league]
        
        if not valid_leagues:
            return recommendations
            
        # Calculate overall user performance across leagues
        avg_rank = np.mean([league["rank"] for league in valid_leagues])
        avg_strength = np.mean([league["team_strength"] for league in valid_leagues])
        
        # Identify leagues where user is underperforming
        for league in valid_leagues:
            # If user's rank is worse than average rank position
            avg_rank_position = league["total_teams"] / 2
            if league["rank"] > avg_rank_position:
                recommendations.append({
                    "type": "focus_league",
                    "league_id": league["league_id"],
                    "league_name": league["league_name"],
                    "reason": f"Team rank ({league['rank']}) is below average position ({avg_rank_position})",
                    "priority": "HIGH"
                })
                
            # If team strength is below average
            if league["team_strength"] < avg_strength * 0.8:
                recommendations.append({
                    "type": "optimize_roster",
                    "league_id": league["league_id"],
                    "league_name": league["league_name"],
                    "reason": f"Team strength ({league['team_strength']:.2f}) is below average ({avg_strength:.2f})",
                    "priority": "MEDIUM"
                })
        
        # Add resource allocation recommendation
        if len(valid_leagues) > 1:
            recommendations.append({
                "type": "resource_allocation",
                "description": "Consider allocating more time to leagues where you're underperforming",
                "priority": "LOW"
            })
            
        return recommendations
