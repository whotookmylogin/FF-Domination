import redis
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

class CacheService:
    """
    Redis caching service for Fantasy Football Domination App.
    Implements caching strategies for performance optimization.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """
        Initialize Redis cache service.
        
        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis database number
        """
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
    def set(self, key: str, value: Any, expiration_minutes: int = 60) -> bool:
        """
        Set a value in the cache with expiration.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            expiration_minutes (int): Expiration time in minutes
            
        Returns:
            bool: Success status
        """
        try:
            # Serialize value to JSON string
            serialized_value = json.dumps(value, default=str)
            
            # Set in Redis with expiration
            result = self.redis_client.setex(
                key, 
                timedelta(minutes=expiration_minutes), 
                serialized_value
            )
            
            return result
        except Exception as e:
            logging.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Any: Cached value or None if not found/expired
        """
        try:
            # Get from Redis
            value = self.redis_client.get(key)
            
            if value is None:
                return None
                
            # Deserialize JSON string
            deserialized_value = json.loads(value)
            
            return deserialized_value
        except Exception as e:
            logging.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key (str): Cache key to delete
            
        Returns:
            bool: Success status
        """
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logging.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    def flush(self) -> bool:
        """
        Flush all cache entries.
        
        Returns:
            bool: Success status
        """
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logging.error(f"Failed to flush cache: {str(e)}")
            return False
    
    def cache_player_data(self, player_id: str, player_data: dict, 
                         expiration_minutes: int = 120) -> bool:
        """
        Cache player data with specific expiration.
        
        Args:
            player_id (str): Player identifier
            player_data (dict): Player data to cache
            expiration_minutes (int): Expiration time in minutes
            
        Returns:
            bool: Success status
        """
        key = f"player:{player_id}"
        return self.set(key, player_data, expiration_minutes)
    
    def get_cached_player_data(self, player_id: str) -> Optional[dict]:
        """
        Get cached player data.
        
        Args:
            player_id (str): Player identifier
            
        Returns:
            dict: Cached player data or None
        """
        key = f"player:{player_id}"
        return self.get(key)
    
    def cache_team_analysis(self, team_id: str, analysis_data: dict, 
                           expiration_minutes: int = 60) -> bool:
        """
        Cache team analysis data.
        
        Args:
            team_id (str): Team identifier
            analysis_data (dict): Team analysis data to cache
            expiration_minutes (int): Expiration time in minutes
            
        Returns:
            bool: Success status
        """
        key = f"team_analysis:{team_id}"
        return self.set(key, analysis_data, expiration_minutes)
    
    def get_cached_team_analysis(self, team_id: str) -> Optional[dict]:
        """
        Get cached team analysis data.
        
        Args:
            team_id (str): Team identifier
            
        Returns:
            dict: Cached team analysis data or None
        """
        key = f"team_analysis:{team_id}"
        return self.get(key)
    
    def cache_news_items(self, league_id: str, news_items: list, 
                        expiration_minutes: int = 30) -> bool:
        """
        Cache news items for a league.
        
        Args:
            league_id (str): League identifier
            news_items (list): News items to cache
            expiration_minutes (int): Expiration time in minutes
            
        Returns:
            bool: Success status
        """
        key = f"news:{league_id}"
        return self.set(key, news_items, expiration_minutes)
    
    def get_cached_news_items(self, league_id: str) -> Optional[list]:
        """
        Get cached news items for a league.
        
        Args:
            league_id (str): League identifier
            
        Returns:
            list: Cached news items or None
        """
        key = f"news:{league_id}"
        return self.get(key)
    
    def cache_trade_suggestions(self, team_id: str, suggestions: list, 
                               expiration_minutes: int = 60) -> bool:
        """
        Cache trade suggestions for a team.
        
        Args:
            team_id (str): Team identifier
            suggestions (list): Trade suggestions to cache
            expiration_minutes (int): Expiration time in minutes
            
        Returns:
            bool: Success status
        """
        key = f"trade_suggestions:{team_id}"
        return self.set(key, suggestions, expiration_minutes)
    
    def get_cached_trade_suggestions(self, team_id: str) -> Optional[list]:
        """
        Get cached trade suggestions for a team.
        
        Args:
            team_id (str): Team identifier
            
        Returns:
            list: Cached trade suggestions or None
        """
        key = f"trade_suggestions:{team_id}"
        return self.get(key)

# Example usage:
# cache_service = CacheService()
# 
# # Cache player data
# player_data = {
#     "id": "player123",
#     "name": "John Smith",
#     "position": "RB",
#     "projected_points": 18.5,
#     "injury_status": 0
# }
# 
# cache_service.cache_player_data("player123", player_data)
# 
# # Retrieve cached player data
# cached_player = cache_service.get_cached_player_data("player123")
# print(cached_player)
