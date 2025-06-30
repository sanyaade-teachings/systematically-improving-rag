"""Base processor class for synthetic query generation."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class SearchQueries(BaseModel):
    """Generated search queries that could lead to discovering a conversation."""
    chain_of_thought: str = Field(
        description="Chain of thought process for generating the search queries"
    )
    queries: List[str] = Field(
        description="4-7 diverse search queries that users might type to find this conversation",
        min_items=3,
        max_items=8
    )


class BaseProcessor(ABC):
    """Abstract base class for query processors."""
    
    def __init__(self, client):
        """Initialize processor with instructor-patched client.
        
        Args:
            client: instructor-patched OpenAI client
        """
        self.client = client
    
    @abstractmethod
    async def process(self, messages: List[Dict[str, Any]]) -> SearchQueries:
        """Process conversation messages to generate search queries.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            SearchQueries object with generated queries
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Return the processor version identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of the processor's approach."""
        pass