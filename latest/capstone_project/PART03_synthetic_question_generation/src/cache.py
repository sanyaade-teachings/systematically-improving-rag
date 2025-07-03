#!/usr/bin/env python3
"""
Generic caching utilities for synthetic query generation and recall verification.

This module provides a generic cache wrapper around diskcache with
utilities for different caching use cases.
"""

from pathlib import Path
from typing import Any
from diskcache import Cache as DiskCache


class GenericCache:
    """Generic cache wrapper with utilities for different use cases"""

    def __init__(self, cache_dir: Path):
        """Initialize cache with given directory"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._cache = DiskCache(str(self.cache_dir))

    def get(self, key: str) -> Any:
        """Get value from cache"""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self._cache.set(key, value)

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

    def __len__(self) -> int:
        """Get number of items in cache"""
        return len(self._cache)

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {"size": len(self._cache), "directory": str(self.cache_dir)}

    @staticmethod
    def make_conversation_key(conversation_hash: str, prompt_version: str) -> str:
        """Generate cache key for conversation and prompt version"""
        return f"conversation_{conversation_hash}_{prompt_version}"

    @staticmethod
    def make_recall_key(
        conversation_hash: str, query: str, max_query_length: int = 50
    ) -> str:
        """Generate cache key for recall verification"""
        truncated_query = query[:max_query_length]
        # Replace problematic characters that might cause issues in cache keys
        safe_query = "".join(
            c if c.isalnum() or c in "-_" else "_" for c in truncated_query
        )
        return f"recall_{conversation_hash}_{safe_query}"

    @staticmethod
    def make_generic_key(*parts: str) -> str:
        """Generate generic cache key from multiple parts"""
        safe_parts = []
        for part in parts:
            # Replace problematic characters
            safe_part = "".join(
                c if c.isalnum() or c in "-_" else "_" for c in str(part)
            )
            safe_parts.append(safe_part)
        return "_".join(safe_parts)


def setup_cache(cache_dir: Path, clear_cache: bool = False) -> GenericCache:
    """Setup and return a configured cache instance"""
    cache = GenericCache(cache_dir)

    if clear_cache:
        print("[yellow]Clearing cache...[/yellow]")
        cache.clear()
    else:
        cache_size = len(cache)
        if cache_size > 0:
            print(f"[yellow]Found {cache_size} cached items[/yellow]")

    return cache


class NoOpCache:
    """No-op cache implementation"""

    def __init__(self):
        pass

    def get(self, key: str) -> Any:
        return None

    def set(self, key: str, value: Any) -> None:
        pass

    def clear(self) -> None:
        pass

    def __len__(self) -> int:
        return 0
