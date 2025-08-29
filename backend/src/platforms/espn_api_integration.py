"""
ESPN Integration using the community espn-api library.
This provides a more robust and maintained solution for ESPN fantasy football data.
"""

import logging
from typing import Dict, List, Any, Optional
from espn_api.football import League

logger = logging.getLogger(__name__)


class ESPNAPIIntegration:
    """ESPN integration using the community espn-api library."""
    
    def __init__(self, league_id: str, year: int, espn_s2: str, swid: str):
        """Initialize ESPN API integration.
        
        Args:
            league_id: ESPN league ID
            year: Current year/season
            espn_s2: ESPN s2 cookie
            swid: ESPN SWID cookie
        """
        self.league_id = league_id
        self.year = year
        self.espn_s2 = espn_s2
        self.swid = swid
        self.league = None
        
    def connect(self) -> bool:
        """Establish connection to ESPN API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to ESPN API for league {self.league_id}, year {self.year}")
            self.league = League(league_id=self.league_id, year=self.year, 
                               espn_s2=self.espn_s2, swid=self.swid)
            logger.info("Successfully connected to ESPN API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ESPN API: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from ESPN.
        
        Args:
            user_id: User ID to fetch data for
            
        Returns:
            Dict containing user data
        """
        try:
            if not self.league:
                if not self.connect():
                    return {}
            
            # Find the team for this user
            for team in self.league.teams:
                if str(team.team_id) == user_id:
                    return {
                        'user_id': user_id,
                        'team_name': team.team_name,
                        'wins': getattr(team, 'wins', 0),
                        'losses': getattr(team, 'losses', 0),
                        'ties': getattr(team, 'ties', 0),
                        'points_for': getattr(team, 'points_for', 0),
                        'points_against': getattr(team, 'points_against', 0)
                    }
            
            logger.warning(f"Team with ID {user_id} not found in league")
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching user data: {e}")
            return {}
    
    def get_roster_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get roster data for a user from ESPN.
        
        Args:
            user_id: User ID to fetch roster for
            
        Returns:
            List of player dictionaries
        """
        try:
            if not self.league:
                if not self.connect():
                    return []
            
            # Find the team for this user
            for team in self.league.teams:
                if str(team.team_id) == user_id:
                    roster = []
                    for player in team.roster:
                        roster.append({
                            'player_id': getattr(player, 'playerId', None),
                            'name': getattr(player, 'name', 'Unknown'),
                            'position': getattr(player, 'position', 'Unknown'),
                            'team': getattr(player, 'proTeam', 'Unknown'),
                            'status': getattr(player, 'status', 'Active'),
                            'injury_status': getattr(player, 'injuryStatus', None)
                        })
                    return roster
            
            logger.warning(f"Team with ID {user_id} not found in league")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching roster data: {e}")
            return []
    
    def get_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get transaction data for a user from ESPN.
        
        Args:
            user_id: User ID to fetch transactions for
            
        Returns:
            List of transaction dictionaries
        """
        try:
            if not self.league:
                if not self.connect():
                    return []
            
            # Get recent activity for the league
            activities = self.league.recent_activity()
            
            # Filter activities for this user's team
            user_transactions = []
            for activity in activities:
                # Check if this activity involves the user's team
                if hasattr(activity, 'team') and str(activity.team.team_id) == user_id:
                    user_transactions.append({
                        'type': getattr(activity, 'action', 'Unknown'),
                        'player': getattr(activity, 'player', 'Unknown'),
                        'date': getattr(activity, 'date', None)
                    })
                
            return user_transactions
            
        except Exception as e:
            logger.error(f"Error fetching transaction data: {e}")
            return []
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all available players from ESPN.
        
        Returns:
            List of player dictionaries
        """
        try:
            if not self.league:
                if not self.connect():
                    return []
            
            # Get all players in the league
            all_players = []
            for team in self.league.teams:
                for player in team.roster:
                    all_players.append({
                        'player_id': getattr(player, 'playerId', None),
                        'name': getattr(player, 'name', 'Unknown'),
                        'position': getattr(player, 'position', 'Unknown'),
                        'team': getattr(player, 'proTeam', 'Unknown'),
                        'status': getattr(player, 'status', 'Active')
                    })
            
            return all_players
            
        except Exception as e:
            logger.error(f"Error fetching all players: {e}")
            return []
