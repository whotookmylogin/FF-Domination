import requests
import time
import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class NewsSource(ABC):
    """Abstract base class for news sources."""
    
    def __init__(self, name: str, base_url: str, rate_limit: int = 60):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit  # requests per minute
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
    
    @abstractmethod
    def get_news(self) -> List[Dict[str, Any]]:
        """Fetch news from the source."""
        pass

class ESPNNewsSource(NewsSource):
    """ESPN NFL News API integration."""
    
    def __init__(self):
        super().__init__("ESPN", "https://sports.core.api.espn.com", rate_limit=100)
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from ESPN API.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        try:
            # ESPN news endpoint
            url = f"{self.base_url}/v2/sports/football/leagues/nfl/news"
            response = requests.get(url)
            self.requests_made += 1
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('items', []):
                    news_items.append({
                        'title': item.get('headline', ''),
                        'content': item.get('description', ''),
                        'timestamp': item.get('lastModified', ''),
                        'url': item.get('links', {}).get('web', {}).get('href', ''),
                        'source': self.name,
                        'urgency_score': self._calculate_urgency(item)
                    })
                
                return news_items
            else:
                logging.error(f"ESPN news API request failed with status {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"ESPN news fetching failed with exception: {str(e)}")
            return []
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from ESPN API
            
        Returns:
            int: Urgency score (1-5)
        """
        # Placeholder implementation - would be more sophisticated in reality
        categories = item.get('categories', [])
        if any('breaking' in cat.get('description', '').lower() for cat in categories):
            return 5
        elif any('injury' in cat.get('description', '').lower() for cat in categories):
            return 4
        elif any('trade' in cat.get('description', '').lower() for cat in categories):
            return 3
        else:
            return 2

class NFLNewsSource(NewsSource):
    """NFL.com News API integration."""
    
    def __init__(self):
        super().__init__("NFL.com", "https://www.nfl.com", rate_limit=100)
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from NFL.com.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        try:
            # NFL news endpoint (this is a placeholder - actual API might differ)
            url = f"{self.base_url}/api/news?limit=50"
            response = requests.get(url)
            self.requests_made += 1
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('news', []):
                    news_items.append({
                        'title': item.get('title', ''),
                        'content': item.get('summary', ''),
                        'timestamp': item.get('published', ''),
                        'url': item.get('url', ''),
                        'source': self.name,
                        'urgency_score': self._calculate_urgency(item)
                    })
                
                return news_items
            else:
                logging.error(f"NFL.com news API request failed with status {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"NFL.com news fetching failed with exception: {str(e)}")
            return []
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from NFL.com API
            
        Returns:
            int: Urgency score (1-5)
        """
        # Placeholder implementation
        categories = item.get('categories', [])
        if 'breaking-news' in categories:
            return 5
        elif 'injuries' in categories:
            return 4
        elif 'transactions' in categories:
            return 3
        elif 'fantasy' in categories:
            return 3
        else:
            return 1

class RotowireNewsSource(NewsSource):
    """Rotowire News API integration."""
    
    def __init__(self, api_key: str = None):
        super().__init__("Rotowire", "https://api.rotowire.com", rate_limit=1000)
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}
        
    def get_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from Rotowire API.
        
        Returns:
            list: List of news items with title, content, timestamp, and url
        """
        self._check_rate_limit()
        
        try:
            # Rotowire news endpoint (placeholder - actual API might differ)
            url = f"{self.base_url}/v1/news/football/nfl"
            response = requests.get(url, headers=self.headers)
            self.requests_made += 1
            
            if response.status_code == 200:
                data = response.json()
                news_items = []
                
                for item in data.get('data', []):
                    news_items.append({
                        'title': item.get('headline', ''),
                        'content': item.get('body', ''),
                        'timestamp': item.get('date', ''),
                        'url': item.get('url', ''),
                        'source': self.name,
                        'urgency_score': self._calculate_urgency(item)
                    })
                
                return news_items
            else:
                logging.error(f"Rotowire news API request failed with status {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"Rotowire news fetching failed with exception: {str(e)}")
            return []
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate urgency score for a news item (1-5).
        
        Args:
            item (dict): News item from Rotowire API
            
        Returns:
            int: Urgency score (1-5)
        """
        # Placeholder implementation
        tags = item.get('tags', [])
        if 'breaking' in tags:
            return 5
        elif 'injury' in tags:
            return 4
        elif 'trade' in tags:
            return 3
        elif 'suspension' in tags:
            return 3
        else:
            return 2

# Example usage:
# espn_news = ESPNNewsSource()
# nfl_news = NFLNewsSource()
# rotowire_news = RotowireNewsSource("your_api_key_here")
# 
# all_news = []
# all_news.extend(espn_news.get_news())
# all_news.extend(nfl_news.get_news())
# all_news.extend(rotowire_news.get_news())
