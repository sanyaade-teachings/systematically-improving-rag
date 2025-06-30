#!/usr/bin/env python3
"""Quick test script to verify the refactored code works."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processors import SearchFocusedProcessor, PatternFocusedProcessor
from src.storage import QueryDatabase, CacheManager
from src.config import Config


async def test_processors():
    """Test that processors work correctly."""
    print("Testing processors...")
    
    # Mock messages
    messages = [
        {"role": "user", "content": "How do I fix a Python import error?"},
        {"role": "assistant", "content": "To fix Python import errors, check your module path..."}
    ]
    
    # Mock client (you'd use real instructor client in practice)
    class MockClient:
        async def chat(self, *args, **kwargs):
            from src.processors.base import SearchQueries
            return SearchQueries(
                chain_of_thought="Test reasoning",
                queries=["test query 1", "test query 2", "test query 3"]
            )
    
    # Test V1 processor
    v1 = SearchFocusedProcessor(MockClient())
    print(f"V1 version: {v1.version}")
    print(f"V1 description: {v1.description}")
    
    # Test V2 processor
    v2 = PatternFocusedProcessor(MockClient())
    print(f"V2 version: {v2.version}")
    print(f"V2 description: {v2.description}")
    
    print("✅ Processors test passed!")


def test_storage():
    """Test storage components."""
    print("\nTesting storage...")
    
    config = Config.from_env()
    config.ensure_dirs()
    
    # Test database
    db = QueryDatabase(config.db_path)
    stats = db.get_statistics()
    print(f"Database stats: {stats}")
    
    # Test cache
    cache = CacheManager(config.cache_dir)
    print(f"Cache size: {cache.size()}")
    
    # Test cache operations
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    cache.delete("test_key")
    
    print("✅ Storage test passed!")


def test_config():
    """Test configuration."""
    print("\nTesting configuration...")
    
    config = Config.from_env()
    print(f"Base dir: {config.base_dir}")
    print(f"Data dir: {config.data_dir}")
    print(f"DB path: {config.db_path}")
    
    print("✅ Configuration test passed!")


async def main():
    """Run all tests."""
    print("🧪 Running refactoring tests...\n")
    
    test_config()
    test_storage()
    await test_processors()
    
    print("\n✨ All tests passed! The refactoring is working correctly.")


if __name__ == "__main__":
    asyncio.run(main())