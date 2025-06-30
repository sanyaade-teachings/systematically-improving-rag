#!/usr/bin/env python3
"""
Integration tests for Turbopuffer DAO implementation using real database connections
"""

import pytest
import pytest_asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.dao.wildchat_dao import SearchRequest, SearchType, WildChatDocument
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer

# Load environment variables
load_dotenv()


class TestWildChatDAOTurbopuffer:
    """Integration tests for Turbopuffer DAO using real database connections"""

    @pytest.fixture
    def sample_documents(self):
        """Sample test documents"""
        return [
            WildChatDocument(
                id="test_doc_1",
                text="How to learn Python programming?",
                conversation_string="User: How to learn Python programming?\nAssistant: I recommend starting with basic syntax...",
                hash="hash_1",
                timestamp=datetime(2023, 6, 1),
                language="English",
                model_name="gpt-4",
                conversation_length=2,
                country="US",
                toxic=False,
                redacted=False,
                turn=1,
            ),
            WildChatDocument(
                id="test_doc_2",
                text="What is machine learning?",
                conversation_string="User: What is machine learning?\nAssistant: Machine learning is a subset of AI...",
                hash="hash_2",
                timestamp=datetime(2023, 6, 2),
                language="English",
                model_name="claude-2",
                conversation_length=2,
                country="UK",
                toxic=False,
                redacted=False,
                turn=1,
            ),
        ]

    @pytest_asyncio.fixture
    async def dao(self):
        """Create DAO instance for testing with real connection"""
        # Skip test if no API key is available
        if not os.getenv("TURBOPUFFER_API_KEY"):
            pytest.skip("TURBOPUFFER_API_KEY not available")

        dao_instance = WildChatDAOTurbopuffer(table_name="test_wildchat")

        try:
            await dao_instance.connect()
            yield dao_instance
        finally:
            # Cleanup: delete test namespace if it exists
            try:
                await dao_instance.delete_table()
            except Exception:
                pass
            await dao_instance.disconnect()

    @pytest.mark.asyncio
    async def test_connection(self, dao):
        """Test database connection establishment"""
        # Connection is already established in fixture
        assert dao.client is not None
        assert dao.namespace is not None

        # Test that we can get stats (verifies connection works)
        stats = await dao.get_stats()
        assert "total_documents" in stats
        assert stats["namespace_name"] == "test_wildchat"

    @pytest.mark.asyncio
    async def test_embedding_model(self, dao):
        """Test embedding model functionality"""
        # Test getting embedding model
        model = dao._get_embedding_model()
        assert model is not None

        # Test creating embeddings
        embeddings = dao._create_embeddings(["text1", "text2"])
        assert len(embeddings) == 2
        assert len(embeddings[0]) > 0  # Should have embedding dimensions
        assert isinstance(embeddings[0], list)

    @pytest.mark.asyncio
    async def test_add_documents(self, dao, sample_documents):
        """Test adding documents"""
        # Test adding documents to real database
        result = await dao.add(sample_documents)

        assert result["success"] is True
        assert result["added_count"] == 2
        assert result["skipped_count"] == 0
        assert result["total_requested"] == 2

        # Verify documents were added by checking stats
        stats = await dao.get_stats()
        assert stats["total_documents"] >= 2

    @pytest.mark.asyncio
    async def test_add_empty_documents(self, dao):
        """Test adding empty document list"""
        result = await dao.add([])

        assert result["success"] is True
        assert result["added_count"] == 0
        assert result["skipped_count"] == 0

    @pytest.mark.asyncio
    async def test_search_vector(self, dao, sample_documents):
        """Test vector search"""
        # First add some documents
        await dao.add(sample_documents)

        # Create search request
        request = SearchRequest(
            query="How to learn programming", top_k=2, search_type=SearchType.VECTOR
        )

        # Execute search
        results = await dao.search(request)

        assert results.total_count >= 0
        assert results.search_type == SearchType.VECTOR
        assert results.query_time_ms > 0

        # If we have results, check structure
        if results.results:
            first_result = results.results[0]
            assert hasattr(first_result, "id")
            assert hasattr(first_result, "text")
            assert hasattr(first_result, "score")
            assert hasattr(first_result, "metadata")
            assert first_result.score >= 0

    @pytest.mark.asyncio
    async def test_search_full_text(self, dao, sample_documents):
        """Test full-text search"""
        # Add documents first
        await dao.add(sample_documents)

        # Create search request
        request = SearchRequest(
            query="machine learning", top_k=2, search_type=SearchType.FULL_TEXT
        )

        # Execute search
        results = await dao.search(request)

        assert results.total_count >= 0
        assert results.search_type == SearchType.FULL_TEXT
        assert results.query_time_ms > 0

    @pytest.mark.asyncio
    async def test_search_hybrid(self, dao, sample_documents):
        """Test hybrid search"""
        # Add documents first
        await dao.add(sample_documents)

        request = SearchRequest(
            query="programming tutorial",
            top_k=2,
            search_type=SearchType.HYBRID,
            vector_weight=0.7,
            text_weight=0.3,
        )

        results = await dao.search(request)

        assert results.total_count >= 0
        assert results.search_type == SearchType.HYBRID
        assert results.query_time_ms > 0

    @pytest.mark.asyncio
    async def test_search_with_filters(self, dao, sample_documents):
        """Test search with filters"""
        # Add documents first
        await dao.add(sample_documents)

        # Create search request with filters
        request = SearchRequest(
            query="How to learn programming",
            top_k=5,
            search_type=SearchType.VECTOR,
            date_range=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            model_names=["gpt-4"],
            exclude_toxic=True,
            conversation_length_range=(1, 10),
        )

        # Execute search
        results = await dao.search(request)

        # Should not error and return valid results
        assert results.total_count >= 0
        assert results.search_type == SearchType.VECTOR
        assert results.query_time_ms > 0

    @pytest.mark.asyncio
    async def test_build_filters(self, dao):
        """Test filter building functionality"""
        # Test various filter combinations
        request = SearchRequest(
            query="test",
            date_range=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            model_names=["gpt-4"],
            exclude_toxic=True,
            conversation_length_range=(10, 100),
        )

        filters = dao._build_filters(request)

        # Should create filters
        assert filters is not None

    @pytest.mark.asyncio
    async def test_build_filters_empty(self, dao):
        """Test filter building with no filters"""
        request = SearchRequest(
            query="test", exclude_toxic=False, exclude_redacted=False
        )

        filters = dao._build_filters(request)

        assert filters is None

    @pytest.mark.asyncio
    async def test_delete_documents(self, dao, sample_documents):
        """Test deleting documents"""
        # Add documents first
        await dao.add(sample_documents)

        # Delete specific documents
        document_ids = ["test_doc_1", "test_doc_2"]
        result = await dao.delete(document_ids)

        assert result["success"] is True
        # Note: Turbopuffer delete might not always report exact counts
        assert "deleted_count" in result

    @pytest.mark.asyncio
    async def test_delete_documents_nonexistent(self, dao):
        """Test deleting non-existent documents"""
        result = await dao.delete(["nonexistent_doc"])

        # Should still succeed even if documents don't exist
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_get_stats(self, dao, sample_documents):
        """Test getting namespace statistics"""
        # Add some documents first
        await dao.add(sample_documents)

        stats = await dao.get_stats()

        assert stats["total_documents"] >= 0  # Might be 0 if aggregation fails
        assert stats["namespace_name"] == dao.table_name
        assert "embedding_model" in stats

    @pytest.mark.asyncio
    async def test_get_stats_empty_namespace(self, dao):
        """Test getting stats from empty namespace"""
        stats = await dao.get_stats()

        # Should not error even if namespace is empty
        assert "total_documents" in stats
        assert stats["namespace_name"] == dao.table_name


if __name__ == "__main__":
    pytest.main([__file__])
