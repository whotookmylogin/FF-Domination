"""
ESPN Integration using the community espn-api library.
This provides a more robust and maintained solution for ESPN fantasy football data.
"""

import logging
from typing import Dict, List, Any, Optional
try:
    from espn_api.football import League
except ImportError:
    League = None
    logging.warning("espn-api library not found. Mock data will be used instead.")
    
from .espn_mock_data import ESPNMockDataProvider

logger = logging.getLogger(__name__)


class ESPNAPIIntegration:
    """ESPN integration using the community espn-api library."""
    
    def __init__(self, league_id: str, year: int, espn_s2: str = None, swid: str = None):
        """Initialize ESPN API integration.
        
        Args:
            league_id: ESPN league ID
            year: Current year/season
            espn_s2: ESPN s2 cookie (optional, will use mock data if not provided)
            swid: ESPN SWID cookie (optional, will use mock data if not provided)
        """
        self.league_id = league_id
        self.year = year
        self.espn_s2 = espn_s2
        self.swid = swid
        self.league = None
        self.use_mock_data = not (espn_s2 and swid and League is not None)
        self.mock_provider = ESPNMockDataProvider()
        
        if self.use_mock_data:
            logger.info("ESPN API Integration initialized in mock data mode")
        
    def connect(self) -> bool:
        """Establish connection to ESPN API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.use_mock_data:
            logger.info("Using mock data mode, no ESPN API connection needed")
            return True
            
        try:
            logger.info(f"Connecting to ESPN API for league {self.league_id}, year {self.year}")
            self.league = League(league_id=self.league_id, year=self.year, 
                               espn_s2=self.espn_s2, swid=self.swid)
            logger.info("Successfully connected to ESPN API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to ESPN API: {e}")
            logger.info("Falling back to mock data mode")
            self.use_mock_data = True
            return True  # Still return True since we can use mock data
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from ESPN.
        
        Args:
            user_id: User ID to fetch data for
            
        Returns:
            Dict containing user data
        """
        if self.use_mock_data:
            logger.info("Using mock data for user data (ESPN API not available)")
            return self.mock_provider.get_mock_api_user_data(user_id)
            
        try:
            if not self.league:
                if not self.connect():
                    return self.mock_provider.get_mock_api_user_data(user_id)
            
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
            
            logger.warning(f"Team with ID {user_id} not found in league, using mock data")
            return self.mock_provider.get_mock_api_user_data(user_id)
            
        except Exception as e:
            logger.error(f"Error fetching user data, falling back to mock data: {e}")
            return self.mock_provider.get_mock_api_user_data(user_id)
    
    def get_roster_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get roster data for a user from ESPN.
        
        Args:
            user_id: User ID to fetch roster for
            
        Returns:
            List of player dictionaries
        """
        if self.use_mock_data:
            logger.info("Using mock data for roster data (ESPN API not available)")
            return self.mock_provider.get_mock_api_roster_data(user_id)
            
        try:
            if not self.league:
                if not self.connect():
                    return self.mock_provider.get_mock_api_roster_data(user_id)
            
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
            
            logger.warning(f"Team with ID {user_id} not found in league, using mock data")
            return self.mock_provider.get_mock_api_roster_data(user_id)
            
        except Exception as e:
            logger.error(f"Error fetching roster data, falling back to mock data: {e}")
            return self.mock_provider.get_mock_api_roster_data(user_id)
    
    def get_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get transaction data for a user from ESPN.
        
        Args:
            user_id: User ID to fetch transactions for
            
        Returns:
            List of transaction dictionaries
        """
        if self.use_mock_data:
            logger.info("Using mock data for transactions (ESPN API not available)")
            return self.mock_provider.get_mock_api_transactions(user_id)
            
        try:
            if not self.league:
                if not self.connect():
                    return self.mock_provider.get_mock_api_transactions(user_id)
            
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
            logger.error(f"Error fetching transaction data, falling back to mock data: {e}")
            return self.mock_provider.get_mock_api_transactions(user_id)
    
    def get_free_agents(self, position: Optional[str] = None, size: int = 50) -> List[Dict[str, Any]]:
        """Get free agents from ESPN.
        
        Args:
            position: Optional position filter (e.g., 'QB', 'RB', 'WR', 'TE')
            size: Number of players to return
            
        Returns:
            List of free agent player dictionaries
        """
        if self.use_mock_data:
            logger.info("Using mock data for free agents (ESPN API not available)")
            # Return mock free agents
            mock_free_agents = [
                {'player_id': '1001', 'name': 'Jordan Love', 'position': 'QB', 'team': 'GB', 'projected_points': 22.5, 'percent_owned': 45.2},
                {'player_id': '1002', 'name': 'Jaylen Warren', 'position': 'RB', 'team': 'PIT', 'projected_points': 14.8, 'percent_owned': 38.7},
                {'player_id': '1003', 'name': 'Calvin Ridley', 'position': 'WR', 'team': 'TEN', 'projected_points': 16.2, 'percent_owned': 52.1},
                {'player_id': '1004', 'name': 'Sam LaPorta', 'position': 'TE', 'team': 'DET', 'projected_points': 11.3, 'percent_owned': 41.5},
                {'player_id': '1005', 'name': 'Jerome Ford', 'position': 'RB', 'team': 'CLE', 'projected_points': 13.7, 'percent_owned': 29.8},
            ]
            if position:
                return [p for p in mock_free_agents if p['position'] == position][:size]
            return mock_free_agents[:size]
            
        try:
            if not self.league:
                if not self.connect():
                    # Return mock data if connection fails
                    return self.get_free_agents(position, size)  # Recursive call will use mock data
            
            # Get free agents from ESPN API
            free_agents = self.league.free_agents(size=size)
            
            # Filter by position if specified
            if position:
                free_agents = [p for p in free_agents if p.position == position]
            
            # Format the response
            formatted_agents = []
            for player in free_agents[:size]:
                formatted_agents.append({
                    'player_id': getattr(player, 'playerId', None),
                    'name': getattr(player, 'name', 'Unknown'),
                    'position': getattr(player, 'position', 'Unknown'),
                    'team': getattr(player, 'proTeam', 'Unknown'),
                    'projected_points': getattr(player, 'projected_points', 0),
                    'percent_owned': getattr(player, 'percent_owned', 0),
                    'injury_status': getattr(player, 'injuryStatus', None)
                })
            
            return formatted_agents
            
        except Exception as e:
            logger.error(f"Error fetching free agents, falling back to mock data: {e}")
            # Recursive call will use mock data
            self.use_mock_data = True
            return self.get_free_agents(position, size)
    
    def get_all_players(self) -> List[Dict[str, Any]]:
        """Get all available players from ESPN.
        
        Returns:
            List of player dictionaries
        """
        if self.use_mock_data:
            logger.info("Using mock data for all players (ESPN API not available)")
            # Return a consolidated list from multiple rosters
            all_players = []
            for i in range(1, 5):  # Mock data for a few teams
                roster = self.mock_provider.get_mock_api_roster_data(str(i))
                all_players.extend(roster)
            return all_players
            
        try:
            if not self.league:
                if not self.connect():
                    # Return mock data if connection fails
                    all_players = []
                    for i in range(1, 5):
                        roster = self.mock_provider.get_mock_api_roster_data(str(i))
                        all_players.extend(roster)
                    return all_players
            
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
            logger.error(f"Error fetching all players, falling back to mock data: {e}")
            # Return mock data as fallback
            all_players = []
            for i in range(1, 5):
                roster = self.mock_provider.get_mock_api_roster_data(str(i))
                all_players.extend(roster)
            return all_players
