from typing import List, Dict, Any, Callable
from pydantic import BaseModel, Field
import instructor
from openai import AsyncOpenAI
import diskcache as dc
import hashlib
import json
import functools
import asyncio
from pathlib import Path


# Initialize disk cache
cache_dir = Path(__file__).parent / "cache"
cache = dc.Cache(str(cache_dir))


def cache_with_ttl(ttl_seconds: int = 86400 * 7):
    """
    Decorator for caching function results with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds (default: 7 days)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'function': func.__name__,
                'args': args[1:],  # Skip client argument
                'kwargs': kwargs
            }
            cache_key = f"{func.__name__}_v1_{hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()}"
            
            # Check cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                # Return cached result as the appropriate Pydantic model
                if hasattr(func, '_return_type'):
                    return func._return_type(**cached_result)
                return cached_result
            
            try:
                # Call the function
                result = await func(*args, **kwargs)
                
                # Cache the result
                if hasattr(result, 'model_dump'):
                    cache.set(cache_key, result.model_dump(), expire=ttl_seconds)
                else:
                    cache.set(cache_key, result, expire=ttl_seconds)
                
                return result
                
            except Exception as e:
                # Cache fallback results for shorter time
                fallback_result = getattr(func, '_fallback_result', None)
                if fallback_result:
                    cache.set(cache_key, fallback_result.model_dump(), expire=3600)
                    return fallback_result
                raise e
                
        return wrapper
    return decorator


class SearchQueries(BaseModel):
    """Generated search queries that could lead to discovering a conversation."""
    chain_of_thought: str = Field(
        description="Chain of thought process for generating the search queries"
    )
    queries: List[str] = Field(
        description="4-5 diverse search queries that users might type to find this conversation",
        min_items=4,
        max_items=5
    )


class ConversationPatternQueries(BaseModel):
    """Generated search queries for finding conversations with similar patterns and characteristics."""
    reasoning: str = Field(
        description="Analysis of the conversation's key patterns, themes, and characteristics"
    )
    pattern_queries: List[str] = Field(
        description="5-7 search queries focused on finding conversations with similar patterns, themes, or characteristics",
        min_items=5,
        max_items=7
    )
    content_type: str = Field(
        description="Primary category of this conversation (e.g., medical, creative, technical, educational, role-playing, etc.)"
    )
    user_intent: str = Field(
        description="What the user was primarily trying to accomplish (e.g., get medical advice, create content, learn something, test AI limits, etc.)"
    )


class CombinedQueries(BaseModel):
    """Combined result containing both v1 and v2 query generations."""
    conversation_id: str = Field(description="ID of the conversation analyzed")
    search_queries: SearchQueries = Field(description="V1 queries: Basic search queries for finding similar conversations")
    pattern_queries: ConversationPatternQueries = Field(description="V2 queries: Pattern-focused queries for research and analysis")


def create_cache_key(conversation_id: str, conversation: Dict[str, Any]) -> str:
    """
    Create a stable cache key based on conversation content.
    
    Args:
        conversation_id: ID of the conversation
        conversation: Dictionary containing conversation data
        
    Returns:
        String cache key
    """
    # Extract messages for hashing
    messages = conversation.get('conversation', conversation.get('messages', []))
    
    # Create a stable representation of the conversation
    conversation_data = {
        'id': conversation_id,
        'messages': [
            {
                'role': msg.get('role', ''),
                'content': msg.get('content', '')
            }
            for msg in messages[:50]  # Only use first 50 messages (same as in processing)
        ]
    }
    
    # Create hash of conversation data
    conversation_str = json.dumps(conversation_data, sort_keys=True)
    cache_key = f"search_queries_v1_{hashlib.md5(conversation_str.encode()).hexdigest()}"
    
    return cache_key


# Set up fallback result for the decorator
_fallback_queries = SearchQueries(
    chain_of_thought="Fallback reasoning due to error",
    queries=["error fallback query 1", "error fallback query 2", "error fallback query 3", "error fallback query 4"]
)

_fallback_pattern_queries = ConversationPatternQueries(
    reasoning="Fallback reasoning due to error",
    pattern_queries=["error fallback pattern query 1", "error fallback pattern query 2", "error fallback pattern query 3", "error fallback pattern query 4", "error fallback pattern query 5"],
    content_type="error",
    user_intent="error fallback intent"
)

_fallback_combined = CombinedQueries(
    conversation_id="error",
    search_queries=_fallback_queries,
    pattern_queries=_fallback_pattern_queries
)


@cache_with_ttl(ttl_seconds=86400 * 7)  # Cache for 7 days
async def synthetic_question_generation_v1(
    client,  # instructor-patched client
    conversation_id: str,
    conversation: Dict[str, Any],
) -> SearchQueries:
    """
    Generate diverse synthetic search queries from a chat conversation.
    
    As a product manager analyzing ChatGPT usage patterns, this function creates
    search queries that users might have typed to discover similar conversations.
    The queries should be diverse and cover different aspects of the conversation.
    
    Args:
        conversation_id: ID of the conversation to generate search queries for
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key
        client: instructor-patched client
        
    Returns:
        SearchQueries object with 4-5 diverse search queries and reasoning
    """
    # Extract conversation content
    messages = conversation.get('conversation', conversation.get('messages', []))
    if not messages:
        raise ValueError("No messages found in conversation")
    
    # Create conversation text for analysis
    conversation_text = ""
    for i, msg in enumerate(messages[:50]):  # Limit to first 50 messages to avoid token limits
        role = msg.get('role', f'message_{i}')  
        content = msg.get('content', str(msg))
        conversation_text += f"{role}: {content}\n\n"
    
    prompt = f"""
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
    {conversation_text}
    </conversation>
    
    Generate queries that would realistically lead someone to discover this conversation.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=SearchQueries,
        messages=[
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )
    
    return response


@cache_with_ttl(ttl_seconds=86400 * 7)  # Cache for 7 days
async def synthetic_question_generation_v2(
    client,  # instructor-patched client
    conversation_id: str,
    conversation: Dict[str, Any],
) -> ConversationPatternQueries:
    """
    Generate search queries for finding conversations with similar patterns and characteristics.
    
    This version focuses on identifying conversation types, themes, and patterns that would be
    useful for researchers, content moderators, or analysts studying human-AI interactions.
    
    Args:
        conversation_id: ID of the conversation to analyze
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key
        client: instructor-patched client
        
    Returns:
        ConversationPatternQueries object with pattern-focused search queries
    """
    # Extract conversation content
    messages = conversation.get('conversation', conversation.get('messages', []))
    if not messages:
        raise ValueError("No messages found in conversation")
    
    # Create conversation text for analysis - limit to avoid token limits
    conversation_text = ""
    for i, msg in enumerate(messages[:50]):
        role = msg.get('role', f'message_{i}')
        content = msg.get('content', str(msg))
        conversation_text += f"{role}: {content}\n\n"
    
    prompt = f"""
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
    {conversation_text}
    </conversation>
    
    Generate 5-7 search queries that focus on conversation patterns, themes, and characteristics
    rather than specific content details. Think about what makes this conversation type distinct
    and how researchers would categorize it.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=ConversationPatternQueries,
        messages=[
            {
                "role": "system",
                "content": "You are an expert conversation analyst specializing in categorizing and understanding patterns in human-AI interactions. Focus on identifying conversation types, themes, and structural patterns rather than specific content details."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )
    
    return response


@cache_with_ttl(ttl_seconds=86400 * 7)  # Cache for 7 days
async def synthetic_question_generation_combined(
    client,  # instructor-patched client
    conversation_id: str,
    conversation: Dict[str, Any],
) -> CombinedQueries:
    """
    Generate both v1 and v2 query types for comprehensive analysis.
    
    This function combines both basic search queries (v1) and pattern-focused queries (v2)
    to provide a complete set of synthetic questions for a conversation.
    
    Args:
        conversation_id: ID of the conversation to analyze
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key
        client: instructor-patched client
        
    Returns:
        CombinedQueries object containing both types of generated queries
    """
    # Run both query generation functions in parallel
    search_queries, pattern_queries = await asyncio.gather(
        synthetic_question_generation_v1(client, conversation_id, conversation),
        synthetic_question_generation_v2(client, conversation_id, conversation)
    )
    
    return CombinedQueries(
        conversation_id=conversation_id,
        search_queries=search_queries,
        pattern_queries=pattern_queries
    )


# Set up the decorator metadata
synthetic_question_generation_v1._return_type = SearchQueries
synthetic_question_generation_v1._fallback_result = _fallback_queries

synthetic_question_generation_v2._return_type = ConversationPatternQueries
synthetic_question_generation_v2._fallback_result = _fallback_pattern_queries

synthetic_question_generation_combined._return_type = CombinedQueries
synthetic_question_generation_combined._fallback_result = _fallback_combined


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics for monitoring.
    
    Returns:
        Dictionary with cache statistics
    """
    try:
        stats = {
            'size': cache.volume(),
            'count': len(cache),
            'cache_dir': str(cache_dir),
            'exists': cache_dir.exists()
        }
        return stats
    except Exception as e:
        return {
            'error': str(e),
            'cache_dir': str(cache_dir),
            'exists': cache_dir.exists() if cache_dir else False
        }


def clear_cache() -> bool:
    """
    Clear all cached results.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cache.clear()
        return True
    except Exception:
        return False


def is_cached(conversation_id: str, conversation: Dict[str, Any]) -> bool:
    """
    Check if a conversation's results are cached.
    
    Args:
        conversation_id: ID of the conversation
        conversation: Dictionary containing conversation data
        
    Returns:
        True if cached, False otherwise
    """
    try:
        cache_key = create_cache_key(conversation_id, conversation)
        return cache_key in cache
    except Exception:
        return False