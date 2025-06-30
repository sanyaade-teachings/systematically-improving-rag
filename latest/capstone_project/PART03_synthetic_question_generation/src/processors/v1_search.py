"""V1 Search-focused processor for synthetic query generation."""

from typing import List, Dict, Any
from .base import BaseProcessor, SearchQueries


class SearchFocusedProcessor(BaseProcessor):
    """Generate search queries focused on how users would naturally search."""
    
    @property
    def version(self) -> str:
        """Return the processor version identifier."""
        return "v1"
    
    @property
    def description(self) -> str:
        """Return a description of the processor's approach."""
        return "Search-focused: Generates queries that users might naturally type to find similar conversations"
    
    async def process(self, messages: List[Dict[str, Any]]) -> SearchQueries:
        """Process conversation messages to generate search queries.
        
        This approach takes the perspective of a product manager analyzing ChatGPT usage patterns,
        creating search queries that users might have typed to discover similar conversations.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            SearchQueries object with 4-5 diverse search queries
        """
        prompt = """
        You are a product manager analyzing ChatGPT usage patterns. Your goal is to understand 
        how users might search to find conversations like this one.
        
        Given this conversation, generate 4-5 diverse search queries that different users might 
        type when looking for similar help or information. The queries should:
        
        1. Cover different aspects of the conversation (technical terms, problem description, solution type)
        2. Vary in specificity (some broad, some specific)
        3. Use different phrasings and vocabulary levels
        4. Reflect natural user search behavior
        5. Include both question-style and keyword-style queries
        
        <conversation>
        {% for message in messages %}
            <message role="{{ message.role }}">
                {{ message.content }}
            </message>
        {% endfor %}
        </conversation>
        
        Generate queries that would realistically lead someone to discover this conversation.
        """
        
        response = await self.client.chat.completions.create(
            response_model=SearchQueries,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            context={
                "messages": messages
            }
        )
        
        return response