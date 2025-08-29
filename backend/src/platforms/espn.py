import requests
import time
from typing import Dict, Any, Optional
import logging
from requests.exceptions import RequestException

# ESPN Integration Service
# Cookie-based auth flow with rate limiting and error handling

class ESPNIntegration:
    def __init__(self, cookie: str):
        """
        Initialize ESPN integration with user cookie.
        
        Args:
            cookie (str): ESPN authentication cookie
        """
        self.cookie = cookie
        self.base_url = "https://fantasy.espn.com"
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.rate_limit = 100  # requests per minute
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
        Make a request to ESPN API with rate limiting and error handling.
        
        Args:
            url (str): API endpoint URL
            
        Returns:
            dict: JSON response or None if error
        """
        self._check_rate_limit()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            self.requests_made += 1
            
            if response.status_code == 200:
                # Check if response is actually JSON
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    return response.json()
                else:
                    logging.warning(f"ESPN API returned non-JSON content: {content_type}")
                    logging.warning("ESPN API may have changed access requirements or implemented anti-bot measures")
                    return None
            elif response.status_code == 429:
                # Rate limited, implement exponential backoff
                logging.warning("ESPN API rate limit exceeded, backing off...")
                time.sleep(2 ** (self.requests_made // 20))  # Exponential backoff
                return self._make_request(url)
            elif response.status_code in [400, 401, 403]:
                # Authentication or access issues
                logging.error(f"ESPN API access denied with status {response.status_code}")
                logging.error("This may be due to ESPN API changes or anti-bot measures")
                logging.error("Please check if your ESPN credentials are still valid")
                return None
            else:
                logging.error(f"ESPN API request failed with status {response.status_code}")
                return None
        except RequestException as e:
            logging.error(f"ESPN API request failed with network error: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"ESPN API request failed with unexpected error: {str(e)}")
            return None
    
    def get_roster_data(self, year: int, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch roster data for a specific league.
        
        Args:
            year (int): Fantasy football season year
            league_id (str): ESPN league ID
            
        Returns:
            dict: Roster data or None if error
        """
        url = f"{self.base_url}/fantasy/api/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
        return self._make_request(url)
    
    def get_transactions_data(self, year: int, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch transactions data for a specific league.
        
        Args:
            year (int): Fantasy football season year
            league_id (str): ESPN league ID
            
        Returns:
            dict: Transactions data or None if error
        """
        url = f"{self.base_url}/fantasy/api/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}/transactions"
        return self._make_request(url)
    
    def get_players_data(self, year: int) -> Optional[Dict[Any, Any]]:
        """
        Fetch players data for a specific season.
        
        Args:
            year (int): Fantasy football season year
            
        Returns:
            dict: Players data or None if error
        """
        url = f"{self.base_url}/fantasy/api/v3/games/ffl/seasons/{year}/players"
        return self._make_request(url)
    
    def get_user_data(self, user_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch user data from ESPN.
        
        Args:
            user_id (str): ESPN user ID
            
        Returns:
            dict: User data or None if error
        """
        url = f"{self.base_url}/fantasy/api/v3/users/{user_id}"
        return self._make_request(url)

# Example usage:
# espn = ESPNIntegration("your_espn_cookie_here")
# roster_data = espn.get_roster_data(2023, "123456")
# transactions_data = espn.get_transactions_data(2023, "123456")
# players_data = espn.get_players_data(2023)
