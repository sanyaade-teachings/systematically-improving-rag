#!/usr/bin/env python3
"""
WildChat-1M Data Access Object (DAO)

Provides a unified interface for accessing WildChat data across different vector databases
with support for various search types and filtering options.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import instructor

class SearchType(Enum):
    """Types of search supported"""
    VECTOR = "vector"
    FULL_TEXT = "full_text"
    HYBRID = "hybrid"


class SearchArgs(BaseModel):
    """Search arguments"""
    date_range: Optional[tuple[datetime, datetime]] = Field(default=None)
    conversation_length_range: Optional[tuple[int, int]] = Field(default=None)
    model_names: Optional[List[str]] = Field(default=None)
    languages: Optional[List[str]] = Field(default=None)
    countries: Optional[List[str]] = Field(default=None)
    exclude_toxic: bool = Field(default=True)
    exclude_redacted: bool = Field(default=True)
    turn_range: Optional[tuple[int, int]] = Field(default=None)


class SearchRequest(SearchArgs):
    """Search request with query, parameters, and filters"""
    query: str
    top_k: int = 10
    search_type: SearchType = SearchType.VECTOR


class SearchResult(BaseModel):
    """Single search result"""
    id: str
    text: str
    conversation_string: str
    score: float  # Similarity score or relevance score
    metadata: Dict[str, Any]  # Additional metadata (timestamp, model, etc.)


class SearchResults(BaseModel):
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



async def decompose_query(natural_language_query: str, *, model: str = "openai/gpt-4o-mini", top_k: int = 10) -> SearchRequest:
    """
    Convert natural language query to structured SearchRequest
    
    Args:
        natural_language_query: Natural language search query
        
    Returns:
        SearchRequest object with decomposed components
    """
    prompt = f"""
    Analyze the following natural language query and decompose it into a structured search request.
    
    
    Extract:
    1. The main search query
    2. Search type (semantic, keyword, or hybrid)
    3. Any filters (language, toxic, country, etc.)
    4. Number of results needed
    
    Available search types:
    - semantic: For meaning-based search
    - keyword: For exact text matching
    - hybrid: For combined semantic and keyword search
    
    Available filters:
    - language: Language filter (e.g., "English", "Spanish")
    - toxic: Boolean filter for toxic content
    - country: Country filter
    - min_length: Minimum message length
    - model_name: ('gpt-3.5-turbo', 'gpt-4') only
    
    Return a structured response with the decomposed components.
    <query>
    {natural_language_query}
    </query>
    """

    class SearchRequestDecomposition(BaseModel):
        """Structured output for query decomposition"""
        query: str = Field(description="The main search query extracted from user input")
        search_type: SearchType = Field(description="Type of search to perform")
        filters: Dict[str, Any] = Field(description="Any filters extracted from the query")
        explanation: str = Field(description="Explanation of how the query was decomposed")
        
    client = instructor.from_provider(model)
    
    try:
        decomposition = await client.chat.completions.create(
            response_model=SearchRequestDecomposition,
            messages=[{"role": "user", "content": prompt}],
            context={
                "query": natural_language_query
            }
        )
        
        return SearchRequest(
            query=decomposition.query,
            search_type=decomposition.search_type,
            filters=decomposition.filters,
            top_k=top_k,
        )
        
    except Exception as e:
        # Fallback to simple keyword search if decomposition fails
        return SearchRequest(
            query=natural_language_query,
            top_k=10,
            search_type=SearchType.KEYWORD,
            filters={}
        )