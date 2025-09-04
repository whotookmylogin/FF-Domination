"""
Sleeper API Integration for Fantasy Football
Provides complete integration with Sleeper's fantasy football platform
"""

import logging
import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SleeperAPIIntegration:
    """
    Complete Sleeper API integration for fantasy football data
    """
    
    def __init__(self, league_id: str, user_id: str = None, username: str = None):
        """
        Initialize Sleeper API integration
        
        Args:
            league_id: Sleeper league ID
            user_id: Sleeper user ID (optional)
            username: Sleeper username (optional)
        """
        self.league_id = league_id
        self.user_id = user_id
        self.username = username
        self.base_url = "https://api.sleeper.app/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "FantasyFootballDomination/1.0"
        })
        
        # Cache for API responses
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._last_cache_time = {}
        
        # NFL players cache (this is a large dataset)
        self._nfl_players = None
        self._nfl_players_cached_at = None
        
        logger.info(f"Initialized Sleeper API for league {league_id}")
    
    def _make_request(self, endpoint: str, use_cache: bool = True) -> Optional[Any]:
        """
        Make a request to Sleeper API with caching
        
        Args:
            endpoint: API endpoint (without base URL)
            use_cache: Whether to use cached response if available
            
        Returns:
            API response data or None if error
        """
        url = f"{self.base_url}/{endpoint}"
        
        # Check cache
        if use_cache and endpoint in self._cache:
            cache_time = self._last_cache_time.get(endpoint, 0)
            if time.time() - cache_time < self._cache_ttl:
                logger.debug(f"Using cached response for {endpoint}")
                return self._cache[endpoint]
        
        try:
            logger.debug(f"Making request to {url}")
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # Update cache
                self._cache[endpoint] = data
                self._last_cache_time[endpoint] = time.time()
                return data
            else:
                logger.error(f"Sleeper API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making Sleeper API request: {e}")
            return None
    
    def get_league_info(self) -> Optional[Dict[str, Any]]:
        """Get league information"""
        return self._make_request(f"league/{self.league_id}")
    
    def get_rosters(self) -> Optional[List[Dict[str, Any]]]:
        """Get all rosters in the league"""
        return self._make_request(f"league/{self.league_id}/rosters")
    
    def get_users(self) -> Optional[List[Dict[str, Any]]]:
        """Get all users in the league"""
        return self._make_request(f"league/{self.league_id}/users")
    
    def get_user_roster(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific user's roster
        
        Args:
            user_id: Sleeper user ID (uses instance user_id if not provided)
            
        Returns:
            User's roster data
        """
        user_id = user_id or self.user_id
        if not user_id:
            logger.error("No user_id provided")
            return None
        
        rosters = self.get_rosters()
        if not rosters:
            return None
        
        # Find the roster for this user
        for roster in rosters:
            if roster.get('owner_id') == user_id:
                return roster
        
        logger.warning(f"No roster found for user {user_id}")
        return None
    
    def get_roster_data(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get roster data formatted for our system
        
        Args:
            user_id: User ID to get roster for
            
        Returns:
            List of player dictionaries
        """
        user_id = user_id or self.user_id
        roster = self.get_user_roster(user_id)
        
        if not roster:
            logger.warning(f"No roster found for user {user_id}, returning empty list")
            return []
        
        # Get NFL players data (cached)
        nfl_players = self.get_nfl_players()
        if not nfl_players:
            logger.error("Could not fetch NFL players data")
            return []
        
        # Format roster players
        formatted_players = []
        player_ids = roster.get('players', [])
        starters = roster.get('starters', [])
        
        for player_id in player_ids:
            if player_id and player_id in nfl_players:
                player_data = nfl_players[player_id]
                
                # Map Sleeper position to our format
                position = player_data.get('position', 'Unknown')
                if position == 'DEF':
                    position = 'D/ST'
                
                # Determine injury status
                injury_status = player_data.get('injury_status')
                if not injury_status or injury_status == '':
                    injury_status = 'ACTIVE'
                elif injury_status == 'IR':
                    injury_status = 'OUT'
                
                formatted_player = {
                    'player_id': player_id,
                    'name': f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip(),
                    'position': position,
                    'team': player_data.get('team', 'FA'),
                    'status': 'Active',
                    'injury_status': injury_status,
                    'projected_points': self._estimate_projected_points(player_data),
                    'is_starter': player_id in starters
                }
                
                formatted_players.append(formatted_player)
        
        logger.info(f"Retrieved {len(formatted_players)} players for user {user_id}")
        return formatted_players
    
    def get_free_agents(self, position: str = None, size: int = 50) -> List[Dict[str, Any]]:
        """
        Get available free agents
        
        Args:
            position: Filter by position (optional)
            size: Number of free agents to return
            
        Returns:
            List of free agent player data
        """
        # Get all rosters to find rostered players
        rosters = self.get_rosters()
        if not rosters:
            return []
        
        # Collect all rostered player IDs
        rostered_players = set()
        for roster in rosters:
            rostered_players.update(roster.get('players', []))
        
        # Get NFL players
        nfl_players = self.get_nfl_players()
        if not nfl_players:
            return []
        
        # Find free agents
        free_agents = []
        for player_id, player_data in nfl_players.items():
            # Skip if rostered
            if player_id in rostered_players:
                continue
            
            # Skip if inactive
            if player_data.get('active') != True:
                continue
            
            # Filter by position if specified
            if position and player_data.get('position') != position:
                continue
            
            # Skip defenses for now (they have different IDs in Sleeper)
            if player_data.get('position') in ['DEF', None]:
                continue
            
            # Get player name
            player_name = f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip()
            if not player_name:
                continue  # Skip players without names
            
            formatted_player = {
                'player_id': player_id,
                'name': player_name,
                'position': player_data.get('position', 'Unknown'),
                'team': player_data.get('team', 'FA'),
                'projected_points': self._estimate_projected_points(player_data),
                'percent_owned': 0,  # Sleeper doesn't provide this
                'injury_status': player_data.get('injury_status') or 'ACTIVE',
                'age': player_data.get('age'),
                'years_exp': player_data.get('years_exp'),
                'depth_chart_position': player_data.get('depth_chart_position'),
                'status': player_data.get('status', 'Active'),
                'number': player_data.get('number')
            }
            
            free_agents.append(formatted_player)
        
        # Sort by projected points and return top N
        free_agents.sort(key=lambda x: x['projected_points'], reverse=True)
        return free_agents[:size]
    
    def get_nfl_players(self) -> Optional[Dict[str, Any]]:
        """
        Get all NFL players (cached due to large size)
        
        Returns:
            Dictionary of all NFL players keyed by player ID
        """
        # Check if we have cached players data
        if self._nfl_players and self._nfl_players_cached_at:
            # Cache for 24 hours (players don't change that often)
            if time.time() - self._nfl_players_cached_at < 86400:
                return self._nfl_players
        
        # Fetch fresh data
        players = self._make_request("players/nfl", use_cache=False)
        if players:
            self._nfl_players = players
            self._nfl_players_cached_at = time.time()
            logger.info(f"Cached {len(players)} NFL players")
        
        return self._nfl_players
    
    def get_user_data(self, username: str = None) -> Optional[Dict[str, Any]]:
        """
        Get user data by username
        
        Args:
            username: Sleeper username
            
        Returns:
            User data dictionary
        """
        username = username or self.username
        if not username:
            return None
        
        return self._make_request(f"user/{username}")
    
    def get_matchups(self, week: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get matchups for a specific week
        
        Args:
            week: Week number
            
        Returns:
            List of matchup data
        """
        return self._make_request(f"league/{self.league_id}/matchups/{week}")
    
    def get_transactions(self, week: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get transactions for a specific week
        
        Args:
            week: Week number
            
        Returns:
            List of transaction data
        """
        return self._make_request(f"league/{self.league_id}/transactions/{week}")
    
    def _estimate_projected_points(self, player_data: Dict[str, Any]) -> float:
        """
        Estimate projected points for a player (Sleeper doesn't provide projections via API)
        Enhanced with team quality and recent performance considerations
        
        Args:
            player_data: Player data from Sleeper
            
        Returns:
            Estimated projected points
        """
        position = player_data.get('position', '')
        team = player_data.get('team', '')
        
        # Enhanced base projections by position with team considerations
        base_projections = {
            'QB': 18.0,
            'RB': 10.0,
            'WR': 9.0,
            'TE': 7.0,
            'K': 8.0,
            'DEF': 8.0,
            'D/ST': 8.0
        }
        
        base = base_projections.get(position, 5.0)
        
        # Team quality multipliers (top teams get a boost)
        top_teams = ['KC', 'BUF', 'PHI', 'SF', 'MIA', 'BAL', 'DAL', 'DET']
        good_teams = ['CIN', 'JAX', 'LAC', 'SEA', 'MIN', 'GB', 'NO', 'LAR']
        
        if team in top_teams:
            base *= 1.15
        elif team in good_teams:
            base *= 1.05
        
        # Adjust based on injury status
        injury_status = player_data.get('injury_status', '')
        if injury_status == 'Questionable':
            base *= 0.8
        elif injury_status == 'Doubtful':
            base *= 0.4
        elif injury_status in ['Out', 'IR', 'PUP', 'Suspended']:
            base = 0
        
        # Adjust based on depth chart position (if available)
        depth_chart_position = player_data.get('depth_chart_position')
        if depth_chart_position:
            if depth_chart_position == 1:  # Starter
                base *= 1.25
            elif depth_chart_position == 2:  # Backup
                base *= 0.7
            else:  # Third string or lower
                base *= 0.3
        
        # Check for rookies and add variance
        if player_data.get('years_exp') == 0:
            base *= 0.85  # Rookies are less predictable
        
        # Age-based adjustments
        age = player_data.get('age')
        if age:
            if position == 'RB' and age > 28:
                base *= 0.9  # RBs decline after 28
            elif position == 'WR' and age < 24:
                base *= 0.9  # Young WRs less consistent
            elif position == 'QB' and 27 <= age <= 35:
                base *= 1.1  # Prime QB years
        
        return round(base, 1)
    
    def test_connection(self) -> bool:
        """
        Test connection to Sleeper API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            league_info = self.get_league_info()
            if league_info:
                logger.info(f"Successfully connected to Sleeper league: {league_info.get('name')}")
                return True
            logger.error(f"Failed to get league info for league_id: {self.league_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Sleeper: {e}, league_id: {self.league_id}")
            return False