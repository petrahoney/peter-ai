"""
cache_service.py - Simple in-memory cache for performance
"""

from typing import Optional, Any
from datetime import datetime, timedelta
import json

class CacheService:
    """Simple in-memory caching"""
    
    def __init__(self):
        self.cache = {}
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set cache with TTL"""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl_seconds)
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache (check expiration)"""
        if key not in self.cache:
            return None
        
        item = self.cache[key]
        if datetime.now() > item["expires_at"]:
            del self.cache[key]
            return None
        
        return item["value"]
    
    def delete(self, key: str):
        """Delete cache entry"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
    
    def cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = []
        for key, item in self.cache.items():
            if datetime.now() > item["expires_at"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]

# Global instance
_cache: Optional[CacheService] = None

def get_cache() -> CacheService:
    """Get cache service"""
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache

def init_cache() -> CacheService:
    """Initialize cache"""
    global _cache
    _cache = CacheService()
    return _cache