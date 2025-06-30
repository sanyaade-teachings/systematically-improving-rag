"""Cache management for synthetic query generation."""

from pathlib import Path
from typing import Any, Optional
from diskcache import Cache


class CacheManager:
    """Manage disk cache for query generation and recall verification."""
    
    def __init__(self, cache_dir: Path):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = Cache(str(cache_dir))
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Optional expiration time in seconds
        """
        self.cache.set(key, value, expire=expire)
    
    def delete(self, key: str):
        """Delete value from cache.
        
        Args:
            key: Cache key to delete
        """
        self.cache.delete(key)
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get number of items in cache.
        
        Returns:
            Number of cached items
        """
        return len(self.cache)
    
    def get_size_bytes(self) -> int:
        """Get total size of cache in bytes.
        
        Returns:
            Cache size in bytes
        """
        return self.cache.volume()
    
    def create_query_key(self, conversation_hash: str, version: str) -> str:
        """Create a cache key for query generation.
        
        Args:
            conversation_hash: Hash of the conversation
            version: Processor version
            
        Returns:
            Cache key string
        """
        return f"query_{version}_{conversation_hash}"
    
    def create_recall_key(self, conversation_hash: str, query: str) -> str:
        """Create a cache key for recall verification.
        
        Args:
            conversation_hash: Hash of the conversation
            query: Search query (will be truncated)
            
        Returns:
            Cache key string
        """
        # Truncate query to keep key reasonable length
        query_truncated = query[:50] if len(query) > 50 else query
        return f"recall_{conversation_hash}_{query_truncated}"
    
    def close(self):
        """Close the cache connection."""
        self.cache.close()