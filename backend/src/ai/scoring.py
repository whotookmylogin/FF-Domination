import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

class SimpleScoringAlgorithm:
    """
    Simple scoring algorithm for player performance projections.
    Based on statistical analysis, positional weighting, team matchups, and weather impact.
    """
    
    def __init__(self):
        """Initialize the scoring algorithm with default weights."""
        # Positional weighting factors
        self.position_weights = {
            'QB': 1.0,
            'RB': 1.2,
            'WR': 1.1,
            'TE': 1.0,
            'K': 0.8,
            'DEF': 0.9
        }
        
        # Team matchup factors (simplified)
        self.matchup_factors = {
            'easy': 1.1,  # Opponent with weak defense
            'average': 1.0,  # Average opponent
            'difficult': 0.9  # Strong opponent
        }
        
        # Weather impact factors
        self.weather_factors = {
            'ideal': 1.05,  # Perfect weather conditions
            'good': 1.0,  # Good weather conditions
            'poor': 0.95,  # Poor weather (rain, snow, wind)
            'severe': 0.9  # Severe weather conditions
        }
        
    def project_player_score(self, player_data: Dict[str, Any], matchup_data: Dict[str, Any], 
                             weather_data: Dict[str, Any]) -> float:
        """
        Project a player's fantasy score for the upcoming week.
        
        Args:
            player_data (dict): Player statistics and information
            matchup_data (dict): Team matchup information
            weather_data (dict): Weather conditions for the game
            
        Returns:
            float: Projected fantasy score
        """
        try:
            # Base projection from historical performance
            base_score = self._calculate_base_score(player_data)
            
            # Apply positional weighting
            position = player_data.get('position', 'RB')
            position_weight = self.position_weights.get(position, 1.0)
            projected_score = base_score * position_weight
            
            # Apply matchup factor
            matchup_difficulty = matchup_data.get('difficulty', 'average')
            matchup_factor = self.matchup_factors.get(matchup_difficulty, 1.0)
            projected_score *= matchup_factor
            
            # Apply weather factor
            weather_condition = weather_data.get('condition', 'good')
            weather_factor = self.weather_factors.get(weather_condition, 1.0)
            projected_score *= weather_factor
            
            # Apply recent performance trend
            trend_factor = self._calculate_trend_factor(player_data)
            projected_score *= trend_factor
            
            return projected_score
            
        except Exception as e:
            logging.error(f"Error projecting score for player: {str(e)}")
            return 0.0
    
    def _calculate_base_score(self, player_data: Dict[str, Any]) -> float:
        """
        Calculate base score from historical performance.
        
        Args:
            player_data (dict): Player statistics and information
            
        Returns:
            float: Base fantasy score
        """
        # This is a simplified calculation - in reality would be much more complex
        # Using basic fantasy football scoring rules
        
        # Get recent average stats (last 4 weeks)
        recent_stats = player_data.get('recent_stats', {})
        
        # Standard fantasy scoring (simplified)
        passing_yards = recent_stats.get('passing_yards', 0)
        passing_tds = recent_stats.get('passing_tds', 0)
        interceptions = recent_stats.get('interceptions', 0)
        rushing_yards = recent_stats.get('rushing_yards', 0)
        rushing_tds = recent_stats.get('rushing_tds', 0)
        receiving_yards = recent_stats.get('receiving_yards', 0)
        receiving_tds = recent_stats.get('receiving_tds', 0)
        receptions = recent_stats.get('receptions', 0)
        fumbles = recent_stats.get('fumbles', 0)
        
        # Calculate base score using standard scoring rules
        score = 0.0
        score += passing_yards * 0.04  # 0.04 points per passing yard
        score += passing_tds * 4.0     # 4 points per passing TD
        score -= interceptions * 2.0   # -2 points per interception
        score += rushing_yards * 0.1   # 0.1 points per rushing yard
        score += rushing_tds * 6.0     # 6 points per rushing TD
        score += receiving_yards * 0.1 # 0.1 points per receiving yard
        score += receiving_tds * 6.0   # 6 points per receiving TD
        score += receptions * 1.0     # 1 point per reception (PPR)
        score -= fumbles * 2.0        # -2 points per fumble
        
        return score
    
    def _calculate_trend_factor(self, player_data: Dict[str, Any]) -> float:
        """
        Calculate trend factor based on recent performance.
        
        Args:
            player_data (dict): Player statistics and information
            
        Returns:
            float: Trend factor multiplier
        """
        recent_stats = player_data.get('recent_stats', {})
        historical_stats = player_data.get('historical_stats', {})
        
        # Calculate recent average vs historical average
        recent_avg = recent_stats.get('average_score', 0)
        historical_avg = historical_stats.get('average_score', 1)  # Avoid division by zero
        
        if historical_avg == 0:
            return 1.0
            
        trend_ratio = recent_avg / historical_avg
        
        # Apply trend factor
        if trend_ratio > 1.2:
            return 1.1  # Player is trending up
        elif trend_ratio > 1.0:
            return 1.05  # Player is slightly trending up
        elif trend_ratio < 0.8:
            return 0.9  # Player is trending down
        elif trend_ratio < 1.0:
            return 0.95  # Player is slightly trending down
        else:
            return 1.0  # Player is performing at expected level
    
    def rank_players(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank players based on their projected scores.
        
        Args:
            players (list): List of player data dictionaries
            
        Returns:
            list: Ranked list of players with projected scores
        """
        # Add projected scores to each player
        for player in players:
            # In a real implementation, we would fetch actual matchup and weather data
            # For now, we'll use placeholder data
            matchup_data = {'difficulty': 'average'}
            weather_data = {'condition': 'good'}
            
            projected_score = self.project_player_score(player, matchup_data, weather_data)
            player['projected_score'] = projected_score
        
        # Sort players by projected score (descending)
        ranked_players = sorted(players, key=lambda x: x.get('projected_score', 0), reverse=True)
        
        # Add rankings
        for i, player in enumerate(ranked_players):
            player['rank'] = i + 1
            
        return ranked_players

# Example usage:
# scoring_algorithm = SimpleScoringAlgorithm()
# 
# player_data = {
#     'name': 'Player Name',
#     'position': 'RB',
#     'recent_stats': {
#         'rushing_yards': 100,
#         'rushing_tds': 1,
#         'receptions': 3,
#         'receiving_yards': 20,
#         'average_score': 15.0
#     },
#     'historical_stats': {
#         'average_score': 12.0
#     }
# }
# 
# matchup_data = {'difficulty': 'easy'}
# weather_data = {'condition': 'ideal'}
# 
# projected_score = scoring_algorithm.project_player_score(player_data, matchup_data, weather_data)
# print(f"Projected score: {projected_score}")
