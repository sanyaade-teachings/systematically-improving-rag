"""V2 Pattern-focused processor for synthetic query generation."""

from typing import List, Dict, Any
from .base import BaseProcessor, SearchQueries


class PatternFocusedProcessor(BaseProcessor):
    """Generate search queries focused on conversation patterns and characteristics."""
    
    @property
    def version(self) -> str:
        """Return the processor version identifier."""
        return "v2"
    
    @property
    def description(self) -> str:
        """Return a description of the processor's approach."""
        return "Pattern-focused: Identifies conversation types, themes, and patterns for research/analysis"
    
    async def process(self, messages: List[Dict[str, Any]]) -> SearchQueries:
        """Process conversation messages to generate pattern-focused search queries.
        
        This approach focuses on identifying conversation types, themes, and patterns that would be
        useful for researchers, content moderators, or analysts studying human-AI interactions.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            SearchQueries object with pattern-focused search queries
        """
        prompt = """
        You are a research analyst studying patterns in human-AI conversations from the WildChat dataset.
        Your goal is to identify the key characteristics and patterns in this conversation that would help
        researchers find similar types of conversations.
        
        Analyze this conversation and generate search queries that would help find conversations with:
        - Similar content themes or domains (medical, creative, technical, etc.)
        - Similar user intents (seeking advice, creative collaboration, testing AI limits, etc.)
        - Similar interaction patterns (role-playing, Q&A, refusal situations, etc.)
        - Similar AI behaviors or response types
        
        Focus on generating queries that capture the ESSENCE and PATTERNS rather than specific details.
        
        Examples of good pattern queries:
        - "conversations where users ask about medical diagnoses"
        - "role-playing scenarios with fictional characters"
        - "conversations where AI refuses medical advice"
        - "creative writing collaborations"
        - "technical troubleshooting discussions"
        - "conversations testing AI content policies"
        - "users seeking relationship advice"
        - "educational Q&A about scientific concepts"
        
        <conversation>
        {% for message in messages %}
            <message role="{{ message.role }}">
                {{ message.content }}
            </message>
        {% endfor %}
        </conversation>
        
        Generate 5-7 search queries that focus on conversation patterns, themes, and characteristics
        rather than specific content details. Think about what makes this conversation type distinct
        and how researchers would categorize it.
        """
        
        response = await self.client.chat.completions.create(
            response_model=SearchQueries,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert conversation analyst specializing in categorizing and understanding patterns in human-AI interactions. Focus on identifying conversation types, themes, and structural patterns rather than specific content details."
                },
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