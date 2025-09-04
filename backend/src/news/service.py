from typing import List, Dict, Any, Optional
from .sources import ESPNNewsSource, NFLNewsSource, RotowireNewsSource
from .article_analyzer import ArticleAnalyzer
try:
    from .perplexity_source import PerplexityNewsSource
except ImportError:
    PerplexityNewsSource = None
import logging
import os
try:
    from sqlalchemy.orm import Session
except ImportError:
    Session = Any  # Fallback type hint if SQLAlchemy not available

class NewsAggregationService:
    """
    Main service for aggregating news from multiple sources.
    """
    
    def __init__(self, rotowire_api_key: str = None, perplexity_api_key: str = None):
        """
        Initialize news aggregation service with all sources.
        
        Args:
            rotowire_api_key (str, optional): API key for Rotowire service
            perplexity_api_key (str, optional): API key for Perplexity service
        """
        self.espn_source = ESPNNewsSource()
        self.nfl_source = NFLNewsSource()
        self.rotowire_source = RotowireNewsSource(rotowire_api_key)
        self.sources = [self.espn_source, self.nfl_source, self.rotowire_source]
        
        # Add Perplexity source if available
        perplexity_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
        if PerplexityNewsSource and perplexity_key:
            self.perplexity_source = PerplexityNewsSource(perplexity_key)
            self.sources.append(self.perplexity_source)
            logging.info("Perplexity news source initialized")
        else:
            self.perplexity_source = None
            if not perplexity_key:
                logging.info("Perplexity API key not configured")
        
        # Initialize article analyzer for enhanced summaries
        self.article_analyzer = ArticleAnalyzer(perplexity_api_key=perplexity_key)
        logging.info("Article analyzer initialized for enhanced summaries")
        
    def aggregate_news(self, enhance_articles: bool = True, max_enhance: int = 5) -> List[Dict[str, Any]]:
        """
        Aggregate news from all sources with optional article enhancement.
        
        Args:
            enhance_articles: Whether to fetch full articles and generate detailed summaries
            max_enhance: Maximum number of articles to enhance (to avoid delays)
        
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
        
        # Enhance articles with full content analysis if requested
        if enhance_articles and self.article_analyzer:
            try:
                logging.info(f"Enhancing top {max_enhance} articles with full content analysis...")
                all_news = self.article_analyzer.enhance_news_batch(all_news, max_items=max_enhance)
            except Exception as e:
                logging.error(f"Failed to enhance articles: {e}")
        
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

    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate news items based on content similarity.
        
        Args:
            news_items (list): List of news items to deduplicate
            
        Returns:
            list: Deduplicated news items
        """
        if not news_items:
            return []
        
        seen_hashes = set()
        unique_news = []
        
        for item in news_items:
            # Create a hash based on title and first 100 chars of content
            title = item.get('title', '').strip().lower()
            content = item.get('content', '')[:100].strip().lower()
            
            # Create unique identifier
            content_hash = hashlib.md5(f"{title}_{content}".encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_news.append(item)
        
        return unique_news
    
    def _enhance_urgency_scores(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance urgency scores based on advanced keyword analysis.
        
        Args:
            news_items (list): List of news items to enhance
            
        Returns:
            list: News items with enhanced urgency scores
        """
        for item in news_items:
            enhanced_score = self._calculate_enhanced_urgency(item)
            item['urgency_score'] = max(item.get('urgency_score', 0), enhanced_score)
        
        return news_items
    
    def _calculate_enhanced_urgency(self, item: Dict[str, Any]) -> int:
        """
        Calculate enhanced urgency score based on multiple factors.
        
        Args:
            item (dict): News item to score
            
        Returns:
            int: Urgency score (1-5)
        """
        title = item.get('title', '').lower()
        content = item.get('content', '').lower()
        text = f"{title} {content}"
        
        # Check for urgent keywords
        for urgency_level in sorted(self.urgent_keywords.keys(), reverse=True):
            keywords = self.urgent_keywords[urgency_level]
            if any(keyword in text for keyword in keywords):
                return urgency_level
        
        # Default urgency
        return 1
    
    def refresh_cache(self) -> Dict[str, Any]:
        """
        Force refresh of all cached news data.
        
        Returns:
            dict: Status of cache refresh operation
        """
        try:
            # Clear all news-related cache keys
            cache_keys = [
                "aggregated_news",
                "breaking_news_4",
                "breaking_news_5",
                "news_source_espn",
                "news_source_nfl",
                "news_source_rotowire"
            ]
            
            cleared_count = 0
            for key in cache_keys:
                if self.cache_service.delete(key):
                    cleared_count += 1
            
            # Fetch fresh data
            fresh_news = self.aggregate_news(use_cache=False)
            
            self.logger.info(f"Cache refresh completed: {cleared_count} keys cleared, {len(fresh_news)} fresh items")
            
            return {
                "status": "success",
                "cleared_keys": cleared_count,
                "fresh_items": len(fresh_news)
            }
        except Exception as e:
            self.logger.error(f"Cache refresh failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def save_news_to_database(self, league_id: str, news_items: List[Dict[str, Any]], db_session: Session) -> int:
        """
        Save news items to the database for persistent storage.
        
        Args:
            league_id (str): League ID to associate with news items
            news_items (list): List of news items to save
            db_session (Session): Database session
            
        Returns:
            int: Number of news items saved
        """
        saved_count = 0
        
        try:
            for item in news_items:
                # Check if news item already exists
                existing = db_session.query(NewsItem).filter_by(
                    title=item.get('title'),
                    source=item.get('source'),
                    league_id=league_id
                ).first()
                
                if not existing:
                    news_item = NewsItem(
                        id=hashlib.md5(f"{item.get('title')}_{item.get('source')}_{league_id}".encode()).hexdigest()[:32],
                        league_id=league_id,
                        title=item.get('title', ''),
                        source=item.get('source', ''),
                        urgency=item.get('urgency_score', 1),
                        summary=item.get('content', '')[:1000],  # Truncate to fit TEXT field
                        link=item.get('url', ''),
                        published_at=datetime.fromisoformat(item.get('timestamp', datetime.now().isoformat())),
                        created_at=datetime.now()
                    )
                    
                    db_session.add(news_item)
                    saved_count += 1
            
            db_session.commit()
            self.logger.info(f"Saved {saved_count} news items to database")
            
        except Exception as e:
            db_session.rollback()
            self.logger.error(f"Failed to save news items to database: {str(e)}")
            raise
        
        return saved_count

# Example usage:
# cache_service = CacheService()
# news_service = NewsAggregationService(rotowire_api_key="your_api_key_here", cache_service=cache_service)
# all_news = news_service.aggregate_news()
# breaking_news = news_service.get_breaking_news()
# espn_news = news_service.get_news_by_source("ESPN")
# refresh_status = news_service.refresh_cache()
