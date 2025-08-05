import redis
import json
import logging
from django.conf import settings
from typing import Any, Optional, Dict, List

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for caching operations"""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.default_ttl = 3600  # 1 hour default TTL
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a key-value pair in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis by key"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.decode('utf-8')
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting Redis key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis key {key}: {str(e)}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key"""
        try:
            return bool(self.redis_client.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error setting expiration for Redis key {key}: {str(e)}")
            return False
    
    def clear_cache(self, pattern: str = "*") -> bool:
        """Clear cache by pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache with pattern {pattern}: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
            }
        except Exception as e:
            logger.error(f"Error getting Redis stats: {str(e)}")
            return {}


# Global Redis client instance
redis_client = RedisClient() 