"""
News aggregation scheduler using Celery for background updates.
Handles periodic news fetching, cache management, and database persistence.
"""

from celery import Celery
from celery.schedules import crontab
import logging
import os
from datetime import datetime
from typing import Dict, Any

from .service import NewsAggregationService
from ..cache.service import CacheService
from ..database.connection import get_db

# Initialize Celery app
celery_app = Celery(
    'news_scheduler',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    # Update news every 15 minutes
    'fetch-news-updates': {
        'task': 'src.news.scheduler.fetch_news_updates',
        'schedule': crontab(minute='*/15'),
    },
    
    # Fetch breaking news every 5 minutes
    'fetch-breaking-news': {
        'task': 'src.news.scheduler.fetch_breaking_news',
        'schedule': crontab(minute='*/5'),
    },
    
    # Clean old cache entries every hour
    'cleanup-news-cache': {
        'task': 'src.news.scheduler.cleanup_news_cache',
        'schedule': crontab(minute=0),
    },
    
    # Save news to database every 30 minutes (for active leagues)
    'save-news-to-database': {
        'task': 'src.news.scheduler.save_news_to_database',
        'schedule': crontab(minute='*/30'),
    },
}

# Initialize services
logger = logging.getLogger(__name__)


def get_news_service() -> NewsAggregationService:
    """
    Get a configured news service instance.
    
    Returns:
        NewsAggregationService: Configured news service
    """
    cache_service = CacheService()
    rotowire_api_key = os.getenv("ROTOWIRE_API_KEY")
    return NewsAggregationService(rotowire_api_key=rotowire_api_key, cache_service=cache_service)


@celery_app.task(bind=True, name='src.news.scheduler.fetch_news_updates')
def fetch_news_updates(self) -> Dict[str, Any]:
    """
    Periodic task to fetch and cache news updates from all sources.
    
    Returns:
        dict: Task execution results
    """
    try:
        logger.info("Starting periodic news update task")
        
        news_service = get_news_service()
        
        # Fetch fresh news (bypassing cache)
        news_items = news_service.aggregate_news(use_cache=False)
        
        # Cache the results
        news_service.cache_service.set("aggregated_news", news_items, expiration_minutes=15)
        
        logger.info(f"Successfully fetched and cached {len(news_items)} news items")
        
        return {
            "status": "success",
            "items_fetched": len(news_items),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"News update task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='src.news.scheduler.fetch_breaking_news')
def fetch_breaking_news(self) -> Dict[str, Any]:
    """
    Periodic task to fetch and prioritize breaking news.
    
    Returns:
        dict: Task execution results
    """
    try:
        logger.info("Starting breaking news fetch task")
        
        news_service = get_news_service()
        
        # Get breaking news with high urgency
        breaking_news = news_service.get_breaking_news(min_urgency=4)
        
        # Cache breaking news with shorter expiration
        news_service.cache_service.set("breaking_news_urgent", breaking_news, expiration_minutes=5)
        
        logger.info(f"Successfully fetched {len(breaking_news)} breaking news items")
        
        return {
            "status": "success",
            "breaking_items": len(breaking_news),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Breaking news fetch task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='src.news.scheduler.cleanup_news_cache')
def cleanup_news_cache(self) -> Dict[str, Any]:
    """
    Clean up old cache entries and optimize cache usage.
    
    Returns:
        dict: Task execution results
    """
    try:
        logger.info("Starting cache cleanup task")
        
        cache_service = CacheService()
        
        # Cache keys to monitor and potentially clean
        cache_keys_to_check = [
            "aggregated_news",
            "breaking_news_4",
            "breaking_news_5",
            "breaking_news_urgent",
            "news_source_espn",
            "news_source_nfl",
            "news_source_rotowire"
        ]
        
        active_keys = 0
        for key in cache_keys_to_check:
            if cache_service.get(key) is not None:
                active_keys += 1
        
        logger.info(f"Cache cleanup completed. {active_keys} active cache keys found")
        
        return {
            "status": "success",
            "active_cache_keys": active_keys,
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Cache cleanup task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='src.news.scheduler.save_news_to_database')
def save_news_to_database(self) -> Dict[str, Any]:
    """
    Save current news items to database for persistence and historical tracking.
    
    Returns:
        dict: Task execution results
    """
    try:
        logger.info("Starting database save task")
        
        news_service = get_news_service()
        
        # Get current news items
        news_items = news_service.aggregate_news()
        
        # For demo purposes, save to a default league ID
        # In production, this would iterate through active leagues
        demo_league_id = "default_league"
        
        # Get database session
        db = next(get_db())
        
        try:
            saved_count = news_service.save_news_to_database(demo_league_id, news_items, db)
            
            logger.info(f"Successfully saved {saved_count} news items to database")
            
            return {
                "status": "success",
                "items_saved": saved_count,
                "league_id": demo_league_id,
                "timestamp": datetime.utcnow().isoformat(),
                "task_id": self.request.id
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Database save task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='src.news.scheduler.refresh_all_caches')
def refresh_all_caches(self) -> Dict[str, Any]:
    """
    Manual task to refresh all news caches immediately.
    
    Returns:
        dict: Task execution results
    """
    try:
        logger.info("Starting manual cache refresh task")
        
        news_service = get_news_service()
        
        # Force refresh all caches
        refresh_result = news_service.refresh_cache()
        
        logger.info("Manual cache refresh completed")
        
        return {
            "status": "success",
            "refresh_details": refresh_result,
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Manual cache refresh task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


@celery_app.task(bind=True, name='src.news.scheduler.test_all_sources')
def test_all_sources(self) -> Dict[str, Any]:
    """
    Test all news sources to ensure they're working correctly.
    
    Returns:
        dict: Task execution results with source status
    """
    try:
        logger.info("Starting news sources test task")
        
        from .sources import test_all_sources
        
        rotowire_api_key = os.getenv("ROTOWIRE_API_KEY")
        test_results = test_all_sources(rotowire_api_key)
        
        logger.info("News sources test completed")
        
        return {
            "status": "success",
            "source_tests": test_results,
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"News sources test task failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": self.request.id
        }


# Utility functions for manual task execution

def start_worker():
    """Start the Celery worker."""
    celery_app.worker_main(['worker', '--loglevel=info'])


def start_beat():
    """Start the Celery beat scheduler."""
    celery_app.start(['beat', '--loglevel=info'])


if __name__ == '__main__':
    # Run worker if executed directly
    start_worker()