import logging
from typing import Dict, Any, List
import json
from sqlalchemy.orm import Session
from ..database.models import League
from ..ai.scoring import SimpleScoringAlgorithm

class CustomScoringService:
    """
    Custom scoring service that allows leagues to define their own scoring rules.
    This service extends the simple scoring algorithm to support custom scoring formats.
    """
    
    def __init__(self, db_session: Session = None):
        """Initialize the custom scoring service."""
        self.db_session = db_session
        self.service_version = "1.0"
        self.default_scoring = SimpleScoringAlgorithm()
        
    def get_league_scoring_settings(self, league_id: str) -> Dict[str, Any]:
        """
        Get custom scoring settings for a league.
        
        Args:
            league_id (str): League ID to get scoring settings for
            
        Returns:
            dict: League scoring settings or default settings if none found
        """
        if not self.db_session:
            logging.warning("No database session provided, returning default scoring settings")
            return self._get_default_scoring_settings()
            
        try:
            league = self.db_session.query(League).filter(League.id == league_id).first()
            
            if league and hasattr(league, 'scoring_settings') and league.scoring_settings:
                # Parse JSON string back to dict
                return json.loads(league.scoring_settings)
            else:
                return self._get_default_scoring_settings()
                
        except Exception as e:
            logging.error(f"Error getting scoring settings for league {league_id}: {str(e)}")
            return self._get_default_scoring_settings()
    
    def apply_custom_scoring(self, player_data: Dict[str, Any], matchup_data: Dict[str, Any], 
                            weather_data: Dict[str, Any], league_id: str) -> float:
        """
        Apply custom scoring rules to project a player's fantasy score.
        
        Args:
            player_data (dict): Player statistics and information
            matchup_data (dict): Team matchup information
            weather_data (dict): Weather conditions for the game
            league_id (str): League ID to get custom scoring rules for
            
        Returns:
            float: Projected fantasy score with custom scoring applied
        """
        # Get league scoring settings
        scoring_settings = self.get_league_scoring_settings(league_id)
        
        # If using default scoring, use the existing algorithm
        if scoring_settings.get("scoring_type", "default") == "default":
            return self.default_scoring.project_player_score(player_data, matchup_data, weather_data)
        
        # Apply custom scoring rules
        try:
            score = self._calculate_custom_score(player_data, scoring_settings)
            return score
        except Exception as e:
            logging.error(f"Error applying custom scoring for league {league_id}: {str(e)}")
            # Fallback to default scoring
            return self.default_scoring.project_player_score(player_data, matchup_data, weather_data)
    
    def _calculate_custom_score(self, player_data: Dict[str, Any], scoring_settings: Dict[str, Any]) -> float:
        """
        Calculate a player's score based on custom scoring settings.
        
        Args:
            player_data (dict): Player statistics and information
            scoring_settings (dict): Custom scoring rules
            
        Returns:
            float: Calculated score based on custom rules
        """
        total_score = 0.0
        
        # Get scoring multipliers
        scoring_multipliers = scoring_settings.get("scoring_multipliers", {})
        
        # Calculate score based on stats and multipliers
        for stat, value in player_data.items():
            if stat in scoring_multipliers:
                multiplier = scoring_multipliers[stat]
                total_score += value * multiplier
                
        # Apply positional weighting if specified
        position_weighting = scoring_settings.get("position_weighting", True)
        if position_weighting and "position" in player_data:
            position = player_data["position"]
            position_weights = scoring_settings.get("position_weights", self.default_scoring.position_weights)
            if position in position_weights:
                total_score *= position_weights[position]
                
        # Apply matchup factor if specified
        matchup_adjustment = scoring_settings.get("matchup_adjustment", True)
        if matchup_adjustment and "matchup_difficulty" in scoring_settings:
            matchup_difficulty = scoring_settings["matchup_difficulty"]
            matchup_factors = scoring_settings.get("matchup_factors", self.default_scoring.matchup_factors)
            if matchup_difficulty in matchup_factors:
                total_score *= matchup_factors[matchup_difficulty]
                
        # Apply weather factor if specified
        weather_adjustment = scoring_settings.get("weather_adjustment", True)
        if weather_adjustment and "weather_condition" in scoring_settings:
            weather_condition = scoring_settings["weather_condition"]
            weather_factors = scoring_settings.get("weather_factors", self.default_scoring.weather_factors)
            if weather_condition in weather_factors:
                total_score *= weather_factors[weather_condition]
                
        return total_score
    
    def _get_default_scoring_settings(self) -> Dict[str, Any]:
        """
        Get default scoring settings.
        
        Returns:
            dict: Default scoring settings
        """
        return {
            "scoring_type": "default",
            "scoring_multipliers": {
                "passing_yards": 0.04,
                "passing_touchdowns": 4.0,
                "interceptions": -2.0,
                "rushing_yards": 0.1,
                "rushing_touchdowns": 6.0,
                "receiving_yards": 0.1,
                "receiving_touchdowns": 6.0,
                "fumbles": -2.0,
                "two_point_conversions": 2.0,
                "field_goals": 3.0,
                "extra_points": 1.0,
                "sacks": 1.0,
                "interceptions_def": 2.0,
                "fumbles_recovered": 2.0,
                "defensive_touchdowns": 6.0
            },
            "position_weights": self.default_scoring.position_weights,
            "matchup_factors": self.default_scoring.matchup_factors,
            "weather_factors": self.default_scoring.weather_factors
        }
    
    def update_league_scoring_settings(self, league_id: str, scoring_settings: Dict[str, Any]) -> bool:
        """
        Update custom scoring settings for a league.
        
        Args:
            league_id (str): League ID to update scoring settings for
            scoring_settings (dict): New scoring settings
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_session:
            logging.warning("No database session provided, cannot update scoring settings")
            return False
            
        try:
            league = self.db_session.query(League).filter(League.id == league_id).first()
            
            if not league:
                logging.error(f"League {league_id} not found")
                return False
                
            # Convert dict to JSON string for storage
            league.scoring_settings = json.dumps(scoring_settings)
            self.db_session.commit()
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating scoring settings for league {league_id}: {str(e)}")
            self.db_session.rollback()
            return False
