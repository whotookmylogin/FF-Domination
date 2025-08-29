from typing import List, Dict, Any
from .sources import ESPNNewsSource, NFLNewsSource, RotowireNewsSource
import logging

class NewsAggregationService:
    """
    Main service for aggregating news from multiple sources.
    """
    
    def __init__(self, rotowire_api_key: str = None):
        """
        Initialize news aggregation service with all sources.
        
        Args:
            rotowire_api_key (str, optional): API key for Rotowire service
        """
        self.espn_source = ESPNNewsSource()
        self.nfl_source = NFLNewsSource()
        self.rotowire_source = RotowireNewsSource(rotowire_api_key)
        self.sources = [self.espn_source, self.nfl_source, self.rotowire_source]
        
    def aggregate_news(self) -> List[Dict[str, Any]]:
        """
        Aggregate news from all sources.
        
        Returns:
            list: Combined list of news items from all sources, sorted by timestamp
        """
        all_news = []
        
        for source in self.sources:
            try:
                news_items = source.get_news()
                all_news.extend(news_items)
                logging.info(f"Fetched {len(news_items)} news items from {source.name}")
            except Exception as e:
                logging.error(f"Failed to fetch news from {source.name}: {str(e)}")
        
        # Sort news by timestamp (newest first)
        all_news.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_news
    
    def get_breaking_news(self, min_urgency: int = 4) -> List[Dict[str, Any]]:
        """
        Get breaking news items with urgency score above threshold.
        
        Args:
            min_urgency (int): Minimum urgency score (default: 4)
            
        Returns:
            list: List of breaking news items
        """
        all_news = self.aggregate_news()
        breaking_news = [item for item in all_news if item.get('urgency_score', 0) >= min_urgency]
        return breaking_news
    
    def get_news_by_source(self, source_name: str) -> List[Dict[str, Any]]:
        """
        Get news items from a specific source.
        
        Args:
            source_name (str): Name of the source ('ESPN', 'NFL.com', or 'Rotowire')
            
        Returns:
            list: List of news items from the specified source
        """
        source_map = {
            'espn': self.espn_source,
            'nfl': self.nfl_source,
            'rotowire': self.rotowire_source
        }
        
        source_key = source_name.lower()
        if source_key in source_map:
            return source_map[source_key].get_news()
        else:
            logging.error(f"Unknown news source: {source_name}")
            return []

# Example usage:
# news_service = NewsAggregationService(rotowire_api_key="your_api_key_here")
# all_news = news_service.aggregate_news()
# breaking_news = news_service.get_breaking_news()
# espn_news = news_service.get_news_by_source("ESPN")
