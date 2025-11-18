# ESPN Firecrawl Integration
# Backup data extraction using Firecrawl web scraping when ESPN API is unavailable

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Try to import Firecrawl, but make it optional
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    logging.warning("Firecrawl SDK not installed. ESPN Firecrawl integration will be disabled.")

load_dotenv()

class ESPNFirecrawlIntegration:
    def __init__(self):
        """
        Initialize ESPN Firecrawl integration.
        """
        self.app = None
        self.enabled = False
        self.espn_cookie = os.getenv("ESPN_COOKIE", "")
        
        if FIRECRAWL_AVAILABLE:
            api_key = os.getenv("FIRECRAWL_API_KEY")
            if api_key and api_key != "your_firecrawl_api_key_here":
                try:
                    self.app = FirecrawlApp(api_key=api_key)
                    self.enabled = True
                    logging.info("ESPN Firecrawl integration enabled")
                except Exception as e:
                    logging.error(f"Failed to initialize Firecrawl: {e}")
            else:
                logging.warning("FIRECRAWL_API_KEY not set or invalid. ESPN Firecrawl integration disabled.")
        else:
            logging.warning("Firecrawl SDK not available. ESPN Firecrawl integration disabled.")
    
    def _extract_data_from_markdown(self, markdown_content: str, data_type: str) -> Optional[Dict[Any, Any]]:
        """
        Extract structured data from markdown content.
        
        Args:
            markdown_content (str): Markdown content from Firecrawl
            data_type (str): Type of data to extract (roster, transactions, etc.)
            
        Returns:
            dict: Extracted data or None if error
        """
        import re
        
        logging.info(f"Extracting {data_type} data from markdown content ({len(markdown_content)} chars)")
        
        # Check if we got a login page or error page
        if "Login and Account Issues" in markdown_content or "reCAPTCHA" in markdown_content:
            logging.warning("Received login/support page instead of data - authentication may be required")
            return None
        
        if data_type == "roster":
            return {
                "status": "success",
                "source": "firecrawl",
                "data": {
                    "teams": [],
                    "players": []
                }
            }
        elif data_type == "transactions":
            # Parse transaction data from markdown
            transactions = []
            
            # Look for transaction patterns in the content
            # ESPN typically shows transactions like "Team A traded/added/dropped Player X"
            transaction_patterns = [
                r"(\w[\w\s]+) added ([\w\s\.]+)",
                r"(\w[\w\s]+) dropped ([\w\s\.]+)",
                r"(\w[\w\s]+) traded ([\w\s\.]+)",
                r"Trade: ([^\n]+)"
            ]
            
            for pattern in transaction_patterns:
                matches = re.findall(pattern, markdown_content, re.IGNORECASE)
                for match in matches:
                    transactions.append({
                        "type": "transaction",
                        "details": match
                    })
            
            logging.info(f"Found {len(transactions)} transactions in scraped content")
            
            return {
                "status": "success",
                "source": "firecrawl",
                "data": {
                    "transactions": transactions,
                    "raw_content_sample": markdown_content[:500] if len(transactions) == 0 else None
                }
            }
        elif data_type == "user":
            return {
                "status": "success",
                "source": "firecrawl",
                "data": {
                    "user": {}
                }
            }
        
        return None
    
    def get_roster_data(self, year: int, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch roster data for a specific league using Firecrawl.
        
        Args:
            year (int): Fantasy football season year
            league_id (str): ESPN league ID
            
        Returns:
            dict: Roster data or None if error
        """
        if not self.enabled or not self.app:
            logging.warning("ESPN Firecrawl integration not enabled")
            return None
        
        try:
            # Construct the ESPN fantasy football URL
            url = f"https://fantasy.espn.com/football/team?leagueId={league_id}&seasonId={year}"
            
            logging.info(f"Scraping roster data from: {url}")
            
            # Prepare headers with ESPN authentication cookies if available
            headers = {}
            if self.espn_cookie:
                headers['Cookie'] = self.espn_cookie
                logging.info("Using ESPN authentication cookies")
            
            # Scrape the page using Firecrawl with authentication
            scrape_result = self.app.scrape_url(
                url, 
                formats=['markdown'],
                headers=headers
            )
            
            # Access the markdown content properly from ScrapeResponse object
            if scrape_result and hasattr(scrape_result, 'markdown'):
                markdown_content = scrape_result.markdown
                if markdown_content and len(markdown_content) > 100:
                    # Extract structured data from the markdown content
                    return self._extract_data_from_markdown(markdown_content, "roster")
                else:
                    logging.error(f"Scraped content too short or empty: {len(markdown_content) if markdown_content else 0} chars")
                    return None
            else:
                logging.error("Failed to scrape roster data")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching roster data with Firecrawl: {e}")
            return None
    
    def get_transactions_data(self, year: int, league_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch transactions data for a specific league using Firecrawl.
        
        Args:
            year (int): Fantasy football season year
            league_id (str): ESPN league ID
            
        Returns:
            dict: Transactions data or None if error
        """
        if not self.enabled or not self.app:
            logging.warning("ESPN Firecrawl integration not enabled")
            return None
        
        try:
            # Construct the ESPN fantasy football transactions URL
            url = f"https://fantasy.espn.com/football/league/transactions?leagueId={league_id}&seasonId={year}"
            
            logging.info(f"Scraping transactions data from: {url}")
            
            # Prepare headers with ESPN authentication cookies if available
            headers = {}
            if self.espn_cookie:
                headers['Cookie'] = self.espn_cookie
                logging.info("Using ESPN authentication cookies")
            
            # Scrape the page using Firecrawl with authentication
            scrape_result = self.app.scrape_url(
                url, 
                formats=['markdown'],
                headers=headers
            )
            
            # Access the markdown content properly from ScrapeResponse object
            if scrape_result and hasattr(scrape_result, 'markdown'):
                markdown_content = scrape_result.markdown
                if markdown_content and len(markdown_content) > 100:
                    # Extract structured data from the markdown content
                    return self._extract_data_from_markdown(markdown_content, "transactions")
                else:
                    logging.error(f"Scraped content too short or empty: {len(markdown_content) if markdown_content else 0} chars")
                    return None
            else:
                logging.error("Failed to scrape transactions data")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching transactions data with Firecrawl: {e}")
            return None
    
    def get_user_data(self, user_id: str) -> Optional[Dict[Any, Any]]:
        """
        Fetch user data using Firecrawl.
        
        Args:
            user_id (str): ESPN user ID
            
        Returns:
            dict: User data or None if error
        """
        if not self.enabled or not self.app:
            logging.warning("ESPN Firecrawl integration not enabled")
            return None
        
        try:
            # Construct the ESPN user profile URL
            url = f"https://fantasy.espn.com/football/profile?userId={user_id}"
            
            logging.info(f"Scraping user data from: {url}")
            
            # Scrape the page using Firecrawl
            scrape_result = self.app.scrape_url(url, formats=['markdown'])
            
            if scrape_result and 'markdown' in scrape_result:
                # Extract structured data from the markdown content
                return self._extract_data_from_markdown(scrape_result['markdown'], "user")
            else:
                logging.error("Failed to scrape user data")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching user data with Firecrawl: {e}")
            return None

# Example usage:
# firecrawl = ESPNFirecrawlIntegration()
# if firecrawl.enabled:
#     roster_data = firecrawl.get_roster_data(2023, "123456")
#     transactions_data = firecrawl.get_transactions_data(2023, "123456")
