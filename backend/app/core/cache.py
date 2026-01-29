"""Redis cache utilities."""

import json
from typing import Any, Optional
import redis
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Redis client (lazy initialization)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client.
    
    Returns:
        Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Test connection
            _redis_client.ping()
            logger.info("redis_connected", url=settings.REDIS_URL)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise
    return _redis_client


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None
    """
    try:
        client = get_redis_client()
        value = client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning("cache_get_failed", key=key, error=str(e))
    return None


def set_cache(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set value in cache.
    
    Args:
        key: Cache key
        value: Value to cache (must be JSON serializable)
        ttl: Time to live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        logger.warning("cache_set_failed", key=key, error=str(e))
        return False


def delete_cache(key: str) -> bool:
    """Delete key from cache.
    
    Args:
        key: Cache key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        client.delete(key)
        return True
    except Exception as e:
        logger.warning("cache_delete_failed", key=key, error=str(e))
        return False


def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "cache:*")
        
    Returns:
        Number of keys deleted
    """
    try:
        client = get_redis_client()
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
        return 0
    except Exception as e:
        logger.warning("cache_clear_pattern_failed", pattern=pattern, error=str(e))
        return 0






