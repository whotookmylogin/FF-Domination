from typing import Dict, Any, List, Tuple
import logging

class TradeSuggestionEngine:
    """
    Manual trade suggestion engine for fantasy football trades.
    Calculates trade fairness scores and win probability deltas.
    """
    
    def __init__(self):
        """Initialize the trade suggestion engine."""
        pass
    
    def evaluate_trade(self, team_a_roster: Dict[str, Any], team_b_roster: Dict[str, Any],
                      team_a_offer: List[Dict[str, Any]], team_b_offer: List[Dict[str, Any]],
                      league_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a potential trade between two teams.
        
        Args:
            team_a_roster (dict): Team A's current roster
            team_b_roster (dict): Team B's current roster
            team_a_offer (list): Players Team A is offering
            team_b_offer (list): Players Team B is offering
            league_settings (dict): League scoring settings
            
        Returns:
            dict: Trade evaluation with fairness score and suggestions
        """
        # Calculate current roster values for both teams
        team_a_current_value = self._calculate_roster_value(team_a_roster, league_settings)
        team_b_current_value = self._calculate_roster_value(team_b_roster, league_settings)
        
        # Calculate roster values after the proposed trade
        team_a_new_roster = self._apply_trade_to_roster(team_a_roster, team_a_offer, team_b_offer)
        team_b_new_roster = self._apply_trade_to_roster(team_b_roster, team_b_offer, team_a_offer)
        
        team_a_new_value = self._calculate_roster_value(team_a_new_roster, league_settings)
        team_b_new_value = self._calculate_roster_value(team_b_new_roster, league_settings)
        
        # Calculate fairness score (1-100)
        # 50 is perfectly fair, >50 favors team A, <50 favors team B
        fairness_score = self._calculate_fairness_score(
            team_a_current_value, team_b_current_value,
            team_a_new_value, team_b_new_value
        )
        
        # Calculate win probability delta for both teams
        team_a_win_prob_delta = self._calculate_win_probability_delta(
            team_a_current_value, team_a_new_value
        )
        team_b_win_prob_delta = self._calculate_win_probability_delta(
            team_b_current_value, team_b_new_value
        )
        
        # Generate trade suggestion
        suggestion = self._generate_trade_suggestion(
            fairness_score, team_a_win_prob_delta, team_b_win_prob_delta,
            team_a_offer, team_b_offer
        )
        
        return {
            "fairness_score": fairness_score,
            "team_a_win_probability_delta": team_a_win_prob_delta,
            "team_b_win_probability_delta": team_b_win_prob_delta,
            "suggestion": suggestion,
            "team_a_new_value": team_a_new_value,
            "team_b_new_value": team_b_new_value
        }
    
    def _calculate_roster_value(self, roster: Dict[str, Any], league_settings: Dict[str, Any]) -> float:
        """
        Calculate the total value of a roster based on player projections and league settings.
        
        Args:
            roster (dict): Roster data with player information
            league_settings (dict): League scoring settings
            
        Returns:
            float: Total roster value
        """
        total_value = 0.0
        
        # For each player in the roster, add their projected value
        for player in roster.get('players', []):
            projected_score = player.get('projected_score', 0)
            positional_weight = self._get_positional_weight(player.get('position', 'RB'), league_settings)
            total_value += projected_score * positional_weight
            
        return total_value
    
    def _get_positional_weight(self, position: str, league_settings: Dict[str, Any]) -> float:
        """
        Get positional weighting based on league settings.
        
        Args:
            position (str): Player position
            league_settings (dict): League scoring settings
            
        Returns:
            float: Positional weight
        """
        # This would be more sophisticated in a real implementation
        # For now, we'll use simple weights
        weights = {
            'QB': 1.0,
            'RB': 1.2,
            'WR': 1.1,
            'TE': 1.0,
            'K': 0.8,
            'DEF': 0.9
        }
        
        return weights.get(position, 1.0)
    
    def _apply_trade_to_roster(self, roster: Dict[str, Any], players_out: List[Dict[str, Any]], 
                              players_in: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply a trade to a roster to create a new roster state.
        
        Args:
            roster (dict): Original roster
            players_out (list): Players being traded away
            players_in (list): Players being received
            
        Returns:
            dict: New roster state
        """
        # Create a copy of the roster
        new_roster = roster.copy()
        
        # Remove players going out
        current_players = new_roster.get('players', [])
        players_out_ids = [player.get('id') for player in players_out]
        remaining_players = [player for player in current_players if player.get('id') not in players_out_ids]
        
        # Add players coming in
        remaining_players.extend(players_in)
        
        new_roster['players'] = remaining_players
        return new_roster
    
    def _calculate_fairness_score(self, team_a_current: float, team_b_current: float,
                                 team_a_new: float, team_b_new: float) -> int:
        """
        Calculate trade fairness score (1-100).
        
        Args:
            team_a_current (float): Team A's current roster value
            team_b_current (float): Team B's current roster value
            team_a_new (float): Team A's roster value after trade
            team_b_new (float): Team B's roster value after trade
            
        Returns:
            int: Fairness score (1-100)
        """
        # Calculate value changes for both teams
        team_a_change = team_a_new - team_a_current
        team_b_change = team_b_new - team_b_current
        
        # If both teams have equal value changes, it's perfectly fair (50)
        if team_a_change == team_b_change:
            return 50
            
        # Calculate fairness based on relative changes
        total_change = abs(team_a_change) + abs(team_b_change)
        if total_change == 0:
            return 50
            
        # If team A gains more value than team B, score > 50
        # If team B gains more value than team A, score < 50
        fairness_ratio = (team_a_change + total_change/2) / total_change
        fairness_score = int(fairness_ratio * 100)
        
        # Clamp to 1-100 range
        return max(1, min(100, fairness_score))
    
    def _calculate_win_probability_delta(self, current_value: float, new_value: float) -> float:
        """
        Calculate change in win probability based on roster value change.
        
        Args:
            current_value (float): Current roster value
            new_value (float): New roster value
            
        Returns:
            float: Change in win probability (percentage points)
        """
        # Simplified calculation - in reality would be much more complex
        # and based on historical data and league context
        value_change = new_value - current_value
        
        # Rough approximation: 1 point of value = 0.5% win probability
        win_prob_delta = value_change * 0.5
        
        return win_prob_delta
    
    def _generate_trade_suggestion(self, fairness_score: int, team_a_win_delta: float, 
                                 team_b_win_delta: float, team_a_offer: List[Dict[str, Any]], 
                                 team_b_offer: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a trade suggestion based on evaluation metrics.
        
        Args:
            fairness_score (int): Trade fairness score (1-100)
            team_a_win_delta (float): Team A's win probability change
            team_b_win_delta (float): Team B's win probability change
            team_a_offer (list): Players Team A is offering
            team_b_offer (list): Players Team B is offering
            
        Returns:
            dict: Trade suggestion with recommendation and reasoning
        """
        suggestion = {
            "recommended_action": "NO_ACTION",
            "reasoning": "",
            "confidence": "LOW"
        }
        
        # Convert player lists to readable strings
        team_a_players = [player.get('name', 'Unknown Player') for player in team_a_offer]
        team_b_players = [player.get('name', 'Unknown Player') for player in team_b_offer]
        
        team_a_str = ", ".join(team_a_players)
        team_b_str = ", ".join(team_b_players)
        
        # Generate recommendation based on fairness and win probability changes
        if 40 <= fairness_score <= 60:
            # Fair trade
            if team_a_win_delta > 2.0:
                suggestion["recommended_action"] = "ACCEPT"
                suggestion["reasoning"] = f"Fair trade that improves your win probability by {team_a_win_delta:.1f}%"
                suggestion["confidence"] = "HIGH"
            elif team_a_win_delta > 0:
                suggestion["recommended_action"] = "ACCEPT"
                suggestion["reasoning"] = f"Fair trade with slight win probability improvement (+{team_a_win_delta:.1f}%)"
                suggestion["confidence"] = "MEDIUM"
            else:
                suggestion["recommended_action"] = "REJECT"
                suggestion["reasoning"] = f"Fair trade but doesn't improve your win probability"
                suggestion["confidence"] = "MEDIUM"
        elif fairness_score > 60:
            # Trade favors team A significantly
            if team_a_win_delta > 3.0:
                suggestion["recommended_action"] = "ACCEPT"
                suggestion["reasoning"] = f"Trade favors you significantly and improves win probability by {team_a_win_delta:.1f}%"
                suggestion["confidence"] = "HIGH"
            elif team_a_win_delta > 0:
                suggestion["recommended_action"] = "CONSIDER"
                suggestion["reasoning"] = f"Trade favors you but only slightly improves win probability (+{team_a_win_delta:.1f}%)"
                suggestion["confidence"] = "MEDIUM"
            else:
                suggestion["recommended_action"] = "REJECT"
                suggestion["reasoning"] = f"Trade favors you but doesn't improve win probability"
                suggestion["confidence"] = "LOW"
        else:
            # Trade favors team B significantly
            if team_a_win_delta > 5.0:
                suggestion["recommended_action"] = "ACCEPT"
                suggestion["reasoning"] = f"Despite trade favoring the other team, your win probability improves significantly by {team_a_win_delta:.1f}%"
                suggestion["confidence"] = "MEDIUM"
            elif team_a_win_delta < -3.0:
                suggestion["recommended_action"] = "REJECT"
                suggestion["reasoning"] = f"Trade heavily favors the other team and decreases your win probability by {abs(team_a_win_delta):.1f}%"
                suggestion["confidence"] = "HIGH"
            else:
                suggestion["recommended_action"] = "CONSIDER"
                suggestion["reasoning"] = f"Trade favors the other team but has minimal impact on your win probability"
                suggestion["confidence"] = "LOW"
                
        return suggestion

# Example usage:
# trade_engine = TradeSuggestionEngine()
# 
# team_a_roster = {
#     "players": [
#         {"id": "1", "name": "Player A1", "position": "QB", "projected_score": 15.0},
#         {"id": "2", "name": "Player A2", "position": "RB", "projected_score": 12.0}
#     ]
# }
# 
# team_b_roster = {
#     "players": [
#         {"id": "3", "name": "Player B1", "position": "WR", "projected_score": 10.0},
#         {"id": "4", "name": "Player B2", "position": "TE", "projected_score": 8.0}
#     ]
# }
# 
# team_a_offer = [{"id": "2", "name": "Player A2", "position": "RB", "projected_score": 12.0}]
# team_b_offer = [{"id": "3", "name": "Player B1", "position": "WR", "projected_score": 10.0}]
# 
# league_settings = {
#     "scoring_type": "PPR",
#     "roster_positions": ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"]
# }
# 
# evaluation = trade_engine.evaluate_trade(team_a_roster, team_b_roster, team_a_offer, team_b_offer, league_settings)
# print(evaluation)
