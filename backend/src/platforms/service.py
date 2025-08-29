from typing import Dict, Any, Optional
from .espn import ESPNIntegration
from .espn_api_integration import ESPNAPIIntegration
from .sleeper import SleeperIntegration
from .espn_firecrawl import ESPNFirecrawlIntegration
import logging
import os

class PlatformIntegrationService:
    """
    Main service for integrating with multiple fantasy football platforms.
    """
    
    def __init__(self, espn_cookie: str = None, sleeper_token: str = None):
        """
        Initialize platform integration service.
        
        Args:
            espn_cookie (str, optional): ESPN authentication cookie
            sleeper_token (str, optional): Sleeper API bearer token
        """
        # Try to use the new ESPNAPIIntegration first (community library)
        self.espn_api_integration = None
        self.espn_integration = ESPNIntegration(espn_cookie) if espn_cookie else None
        # Sleeper integration doesn't require authentication for public endpoints
        self.sleeper_integration = SleeperIntegration(sleeper_token)
        self.espn_firecrawl_integration = ESPNFirecrawlIntegration()
        
        # If we have ESPN credentials, try to initialize the community library integration
        if espn_cookie:
            try:
                # Extract espn_s2 and SWID from the cookie
                espn_s2 = None
                swid = None
                
                if "espn_s2=" in espn_cookie:
                    # Extract espn_s2 value
                    start = espn_cookie.find("espn_s2=") + len("espn_s2=")
                    end = espn_cookie.find(";", start)
                    if end == -1:  # If there's no semicolon after espn_s2, go to the end of string
                        espn_s2 = espn_cookie[start:]
                    else:
                        espn_s2 = espn_cookie[start:end]
                
                if "SWID=" in espn_cookie:
                    # Extract SWID value
                    start = espn_cookie.find("SWID=") + len("SWID=")
                    end = espn_cookie.find(";", start)
                    if end == -1:  # If there's no semicolon after SWID, go to the end of string
                        swid = espn_cookie[start:]
                    else:
                        swid = espn_cookie[start:end]
                
                if espn_s2 and swid:
                    # Get league ID from environment or use default
                    league_id = os.getenv("ESPN_LEAGUE_ID", "83806")  # Default to user's league ID
                    year = 2024  # Most recent completed season
                    
                    self.espn_api_integration = ESPNAPIIntegration(league_id, year, espn_s2, swid)
                    if self.espn_api_integration.connect():
                        logging.info("Successfully initialized ESPN API integration (community library)")
                    else:
                        logging.warning("Failed to connect to ESPN API via community library")
                        self.espn_api_integration = None
                else:
                    logging.warning("Could not extract ESPN credentials for community library integration")
            except Exception as e:
                logging.warning(f"Failed to initialize ESPN API integration (community library): {e}")
                self.espn_api_integration = None
        
    def get_league_data(self, platform: str, league_id: str, year: int = 2023) -> Optional[Dict[Any, Any]]:
        """
        Fetch league data from specified platform.
        
        Args:
            platform (str): Platform name ('espn' or 'sleeper')
            league_id (str): League identifier
            year (int): Season year (default: 2023)
            
        Returns:
            dict: League data or None if error
        """
        if platform.lower() == 'espn':
            # Try ESPNAPIIntegration (community library) first
            if self.espn_api_integration:
                try:
                    # For roster data, we need to pass user_id instead of year/league_id
                    # Let's assume league_id is actually user_id in this context
                    data = self.espn_api_integration.get_roster_data(league_id)  # league_id is user_id here
                    if data:
                        return data
                except Exception as e:
                    logging.warning(f"ESPN API integration (community library) failed: {e}")
            
            # Fallback to our custom ESPN integration
            if self.espn_integration:
                data = self.espn_integration.get_roster_data(year, league_id)
                if data is None:
                    logging.warning("ESPN API data unavailable. This may be due to ESPN API changes or anti-bot measures implemented in 2025.")
                    logging.warning("Please check ESPN API community repositories for updates or workarounds.")
                    
                    # Try Firecrawl as fallback
                    if self.espn_firecrawl_integration and self.espn_firecrawl_integration.enabled:
                        logging.info("Attempting to fetch data via Firecrawl as fallback")
                        firecrawl_data = self.espn_firecrawl_integration.get_roster_data(year, league_id)
                        if firecrawl_data:
                            logging.info("Successfully fetched data via Firecrawl fallback")
                            return firecrawl_data
                        else:
                            logging.warning("Firecrawl fallback also failed to fetch data")
                return data
        elif platform.lower() == 'sleeper' and self.sleeper_integration:
            return self.sleeper_integration.get_rosters_data(league_id)
        else:
            logging.error(f"Unsupported platform or missing credentials: {platform}")
            return None
            
    def get_transactions_data(self, platform: str, league_id: str, year: int = 2023, week: int = 1) -> Optional[Dict[Any, Any]]:
        """
        Fetch transactions data from specified platform.
        
        Args:
            platform (str): Platform name ('espn' or 'sleeper')
            league_id (str): League identifier
            year (int): Season year (default: 2023)
            week (int): Week number (default: 1)
            
        Returns:
            dict: Transactions data or None if error
        """
        if platform.lower() == 'espn':
            # Try ESPNAPIIntegration (community library) first
            if self.espn_api_integration:
                try:
                    # For transactions data, we need to pass user_id instead of year/league_id
                    # Let's assume league_id is actually user_id in this context
                    data = self.espn_api_integration.get_transactions(league_id)  # league_id is user_id here
                    if data:
                        return data
                except Exception as e:
                    logging.warning(f"ESPN API integration (community library) failed: {e}")
            
            # Fallback to our custom ESPN integration
            if self.espn_integration:
                data = self.espn_integration.get_transactions_data(year, league_id)
                if data is None:
                    logging.warning("ESPN API data unavailable. This may be due to ESPN API changes or anti-bot measures implemented in 2025.")
                    logging.warning("Please check ESPN API community repositories for updates or workarounds.")
                    
                    # Try Firecrawl as fallback
                    if self.espn_firecrawl_integration and self.espn_firecrawl_integration.enabled:
                        logging.info("Attempting to fetch data via Firecrawl as fallback")
                        firecrawl_data = self.espn_firecrawl_integration.get_transactions_data(year, league_id)
                        if firecrawl_data:
                            logging.info("Successfully fetched data via Firecrawl fallback")
                            return firecrawl_data
                        else:
                            logging.warning("Firecrawl fallback also failed to fetch data")
                return data
        elif platform.lower() == 'sleeper' and self.sleeper_integration:
            return self.sleeper_integration.get_transactions_data(league_id, week)
        else:
            logging.error(f"Unsupported platform or missing credentials: {platform}")
            return None
            
    def get_user_data(self, platform: str, user_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch user data from specified platform.
        
        Args:
            platform (str): Platform name ('espn' or 'sleeper')
            user_id (str): User identifier or username
            
        Returns:
            dict: User data or None if error
        """
        if platform.lower() == 'espn':
            # Try ESPNAPIIntegration (community library) first
            if self.espn_api_integration:
                try:
                    data = self.espn_api_integration.get_user_data(user_id)
                    if data:
                        return data
                except Exception as e:
                    logging.warning(f"ESPN API integration (community library) failed: {e}")
            
            # Fallback to our custom ESPN integration
            if self.espn_integration:
                data = self.espn_integration.get_user_data(user_id)
                if data is None:
                    logging.warning("ESPN API data unavailable. This may be due to ESPN API changes or anti-bot measures implemented in 2025.")
                    logging.warning("Please check ESPN API community repositories for updates or workarounds.")
                    
                    # Try Firecrawl as fallback
                    if self.espn_firecrawl_integration and self.espn_firecrawl_integration.enabled:
                        logging.info("Attempting to fetch data via Firecrawl as fallback")
                        firecrawl_data = self.espn_firecrawl_integration.get_user_data(user_id)
                        if firecrawl_data:
                            logging.info("Successfully fetched data via Firecrawl fallback")
                            return firecrawl_data
                        else:
                            logging.warning("Firecrawl fallback also failed to fetch data")
                return data
        elif platform.lower() == 'sleeper':
            return self.sleeper_integration.get_user_data(user_id)
        else:
            logging.error(f"Unsupported platform: {platform}")
            return None

    def get_roster_data(self, platform: str, user_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch roster data from specified platform.
        
        Args:
            platform (str): Platform name ('espn' or 'sleeper')
            user_id (str): User identifier or username
            
        Returns:
            dict: Roster data or None if error
        """
        if platform.lower() == 'espn':
            # Try ESPNAPIIntegration (community library) first
            if self.espn_api_integration:
                try:
                    data = self.espn_api_integration.get_roster_data(user_id)
                    if data:
                        return {"status": "success", "data": data}
                except Exception as e:
                    logging.warning(f"ESPN API integration (community library) failed: {e}")
            
            # Fallback to our custom ESPN integration
            if self.espn_integration:
                data = self.espn_integration.get_roster_data(2024, user_id)  # Using 2024 as default year
                if data is None:
                    logging.warning("ESPN API data unavailable. This may be due to ESPN API changes or anti-bot measures implemented in 2025.")
                    logging.warning("Please check ESPN API community repositories for updates or workarounds.")
                    
                    # Try Firecrawl as fallback
                    if self.espn_firecrawl_integration and self.espn_firecrawl_integration.enabled:
                        logging.info("Attempting to fetch data via Firecrawl as fallback")
                        firecrawl_data = self.espn_firecrawl_integration.get_roster_data(2024, user_id)  # Using 2024 as default year
                        if firecrawl_data:
                            logging.info("Successfully fetched data via Firecrawl fallback")
                            return firecrawl_data
                        else:
                            logging.warning("Firecrawl fallback also failed to fetch data")
                return data
        elif platform.lower() == 'sleeper':
            return self.sleeper_integration.get_roster_data(user_id)
        else:
            logging.error(f"Unsupported platform: {platform}")
            return None

    def get_sleeper_user_leagues(self, user_id: str, season: str = "2024") -> Optional[Dict[Any, Any]]:
        """
        Fetch user's Sleeper leagues for a specific season.
        
        Args:
            user_id (str): Sleeper user ID
            season (str): Season year (default: "2024")
            
        Returns:
            dict: User leagues data or None if error
        """
        return self.sleeper_integration.get_user_leagues(user_id, season)
    
    def get_sleeper_league_users(self, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch all users in a specific Sleeper league.
        
        Args:
            league_id (str): Sleeper league ID
            
        Returns:
            dict: League users data or None if error
        """
        return self.sleeper_integration.get_league_users(league_id)
    
    def get_sleeper_league_rosters(self, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch all rosters in a specific Sleeper league.
        
        Args:
            league_id (str): Sleeper league ID
            
        Returns:
            dict: League rosters data or None if error
        """
        return self.sleeper_integration.get_rosters_data(league_id)

# Example usage:
# platform_service = PlatformIntegrationService(espn_cookie="cookie", sleeper_token="token")
# league_data = platform_service.get_league_data("espn", "123456", 2023)
# transactions_data = platform_service.get_transactions_data("sleeper", "league_id", 2023, 1)
# roster_data = platform_service.get_roster_data("epn", "user_id")
# sleeper_leagues = platform_service.get_sleeper_user_leagues("user_id", "2024")
