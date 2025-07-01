#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures
"""

import pytest
import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Remove the mock_env_vars fixture since we want to use real connections


@pytest.fixture
def sample_text_documents():
    """Sample text documents for testing"""
    return [
        "How do I learn Python programming?",
        "What is machine learning and how does it work?",
        "Can you explain the difference between supervised and unsupervised learning?",
        "What are the best practices for writing clean code?",
        "How do I set up a development environment for web development?",
    ]


@pytest.fixture
def sample_conversations():
    """Sample conversation data"""
    return [
        {
            "user": "How do I learn Python programming?",
            "assistant": "I recommend starting with the basics: variables, data types, and control structures. Then move on to functions and object-oriented programming.",
        },
        {
            "user": "What is machine learning?",
            "assistant": "Machine learning is a subset of AI that enables computers to learn and make decisions from data without being explicitly programmed for every task.",
        },
    ]


# Performance testing helpers
@pytest.fixture
def performance_threshold():
    """Performance thresholds for tests"""
    return {
        "search_time_ms": 5000,  # 5 seconds max for search
        "add_documents_time_ms": 10000,  # 10 seconds max for adding documents
        "connection_time_ms": 3000,  # 3 seconds max for connection
    }


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup any test data after each test"""
    yield
    # Cleanup code would go here if we were using real databases
    pass
