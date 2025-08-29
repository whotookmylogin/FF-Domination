import requests
import time
from typing import Dict, Any, Optional
import logging

# Sleeper Integration Service
# Public API access with rate limiting (no authentication required for most endpoints)

class SleeperIntegration:
    def __init__(self, bearer_token: str = None):
        """
        Initialize Sleeper integration.
        
        Args:
            bearer_token (str, optional): Sleeper API bearer token for private endpoints
        """
        self.bearer_token = bearer_token
        self.base_url = "https://api.sleeper.app/v1"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "FantasyFootballDomination/1.0"
        }
        
        # Add authorization header only if token is provided
        if bearer_token:
            self.headers["Authorization"] = f"Bearer {bearer_token}"
            
        self.rate_limit = 1000  # requests per minute
        self.requests_made = 0
        self.last_reset = time.time()
        
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.requests_made = 0
            self.last_reset = current_time
        
        if self.requests_made >= self.rate_limit:
            sleep_time = 60 - (current_time - self.last_reset)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.requests_made = 0
                self.last_reset = time.time()
                
    def _make_request(self, url: str) -> Optional[Dict[Any, Any]]:
        """
        Make a request to Sleeper API with rate limiting and error handling.
        
        Args:
            url (str): API endpoint URL
            
        Returns:
            dict: JSON response or None if error
        """
        self._check_rate_limit()
        
        try:
            response = requests.get(url, headers=self.headers)
            self.requests_made += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited, implement exponential backoff
                logging.warning("Sleeper API rate limit exceeded, backing off...")
                time.sleep(2 ** (self.requests_made // 100))  # Exponential backoff
                return self._make_request(url)
            else:
                logging.error(f"Sleeper API request failed with status {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Sleeper API request failed with exception: {str(e)}")
            return None
    
    def get_user_data(self, username: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch user data.
        
        Args:
            username (str): Sleeper username
            
        Returns:
            dict: User data or None if error
        """
        url = f"{self.base_url}/user/{username}"
        return self._make_request(url)
    
    def get_rosters_data(self, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch rosters data for a specific league.
        
        Args:
            league_id (str): Sleeper league ID
            
        Returns:
            dict: Rosters data or None if error
        """
        url = f"{self.base_url}/league/{league_id}/rosters"
        return self._make_request(url)
    
    def get_transactions_data(self, league_id: str, week: int) -> Optional[Dict[Any, Any]]:
        """
        Fetch transactions data for a specific league and week.
        
        Args:
            league_id (str): Sleeper league ID
            week (int): Week number
            
        Returns:
            dict: Transactions data or None if error
        """
        url = f"{self.base_url}/league/{league_id}/transactions/{week}"
        return self._make_request(url)
    
    def get_user_leagues(self, user_id: str, season: str = "2024") -> Optional[Dict[Any, Any]]:
        """
        Fetch user's leagues for a specific season.
        
        Args:
            user_id (str): Sleeper user ID
            season (str): Season year (default: "2024")
            
        Returns:
            dict: User leagues data or None if error
        """
        url = f"{self.base_url}/user/{user_id}/leagues/nfl/{season}"
        return self._make_request(url)
    
    def get_league_users(self, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch all users in a specific league.
        
        Args:
            league_id (str): Sleeper league ID
            
        Returns:
            dict: League users data or None if error
        """
        url = f"{self.base_url}/league/{league_id}/users"
        return self._make_request(url)
    
    def get_league_info(self, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch league information.
        
        Args:
            league_id (str): Sleeper league ID
            
        Returns:
            dict: League information or None if error
        """
        url = f"{self.base_url}/league/{league_id}"
        return self._make_request(url)
    
    def get_nfl_players(self) -> Optional[Dict[Any, Any]]:
        """
        Fetch all NFL players data.
        
        Returns:
            dict: NFL players data or None if error
        """
        url = f"{self.base_url}/players/nfl"
        return self._make_request(url)

# Example usage:
# sleeper = SleeperIntegration()  # No token needed for public endpoints
# user_data = sleeper.get_user_data("username")
# rosters_data = sleeper.get_rosters_data("league_id")
# transactions_data = sleeper.get_transactions_data("league_id", 1)
# user_leagues = sleeper.get_user_leagues("user_id", "2024")
