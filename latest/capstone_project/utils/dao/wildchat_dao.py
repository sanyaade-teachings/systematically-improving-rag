#!/usr/bin/env python3
"""
WildChat-1M Data Access Object (DAO)

Provides a unified interface for accessing WildChat data across different vector databases
with support for various search types and filtering options.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class SearchType(Enum):
    """Types of search supported"""
    VECTOR = "vector"
    FULL_TEXT = "full_text"
    HYBRID = "hybrid"


@dataclass
class SearchRequest:
    """Search request with query, parameters, and filters"""
    query: str
    top_k: int = 10
    search_type: SearchType = SearchType.VECTOR
    
    # Filters
    date_range: Optional[tuple[datetime, datetime]] = None  # (start_date, end_date)
    conversation_length_range: Optional[tuple[int, int]] = None  # (min_length, max_length)
    model_names: Optional[List[str]] = None  # List of model names to include
    languages: Optional[List[str]] = None  # List of languages to include
    countries: Optional[List[str]] = None  # List of countries to include
    exclude_toxic: bool = True  # Whether to exclude toxic conversations
    exclude_redacted: bool = True  # Whether to exclude redacted conversations
    turn_range: Optional[tuple[int, int]] = None  # (min_turn, max_turn)
    
    # Hybrid search weights
    vector_weight: float = 0.7
    text_weight: float = 0.3


@dataclass
class SearchResult:
    """Single search result"""
    id: str
    text: str
    conversation_string: str
    score: float  # Similarity score or relevance score
    metadata: Dict[str, Any]  # Additional metadata (timestamp, model, etc.)


@dataclass
class SearchResults:
    """Search results container"""
    results: List[SearchResult]
    total_count: int
    query_time_ms: float
    search_type: SearchType
    request: SearchRequest


@dataclass
class WildChatDocument:
    """WildChat document structure"""
    id: str
    text: str  # First message text
    conversation_string: str  # Full formatted conversation
    hash: str
    timestamp: datetime
    language: str
    model_name: str
    conversation_length: int
    country: str
    toxic: bool
    redacted: bool
    turn: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion"""
        return {
            'id': self.id,
            'text': self.text,
            'conversation_string': self.conversation_string,
            'hash': self.hash,
            'timestamp': self.timestamp.isoformat(),
            'language': self.language,
            'model_name': self.model_name,
            'conversation_length': self.conversation_length,
            'country': self.country,
            'toxic': self.toxic,
            'redacted': self.redacted,
            'turn': self.turn
        }


class WildChatDAOBase(ABC):
    """
    Abstract base class for WildChat data access objects
    
    Provides a unified interface for different vector database implementations
    """
    
    def __init__(self, table_name: str = "wildchat_2k"):
        self.table_name = table_name
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def add(self, documents: List[WildChatDocument]) -> Dict[str, Any]:
        """
        Add documents to the database
        
        Args:
            documents: List of WildChatDocument objects to add
            
        Returns:
            Dict with success status and metrics (added_count, skipped_count, etc.)
        """
        pass
    
    @abstractmethod
    async def delete(self, document_ids: List[str]) -> Dict[str, Any]:
        """
        Delete specific documents by ID
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            Dict with success status and count of deleted documents
        """
        pass
    
    @abstractmethod
    async def delete_table(self) -> Dict[str, Any]:
        """
        Delete the entire table/collection/namespace
        
        Returns:
            Dict with success status
        """
        pass
    
    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResults:
        """
        Execute search based on request parameters
        
        Args:
            request: SearchRequest object containing query, top_k, search_type, and filters
            
        Returns:
            SearchResults object with results and metadata
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get database/table statistics
        
        Returns:
            Dict with statistics like document count, size, etc.
        """
        pass
