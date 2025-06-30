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
            # Extract conversation_hash from kwargs or args
            conversation_hash = kwargs.get('conversation_hash')
            if not conversation_hash and len(args) >= 3:
                # Try to get from positional args (client, conversation_id, conversation, conversation_hash)
                conversation_hash = args[3] if len(args) > 3 else None
            
            if not conversation_hash:
                raise ValueError("conversation_hash is required for caching")
            
            # Create simple cache key with function name, version, and conversation_hash
            cache_key = f"{func.__name__}_v1_{conversation_hash}"
            
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


@cache_with_ttl(ttl_seconds=86400 * 7)  # Cache for 7 days
async def synthetic_question_generation_v1(
    client,  # instructor-patched client
    conversation_id: str,
    conversation: Dict[str, Any],
    conversation_hash: str,
) -> SearchQueries:
    """
    Generate diverse synthetic search queries from a chat conversation.
    
    As a product manager analyzing ChatGPT usage patterns, this function creates
    search queries that users might have typed to discover similar conversations.
    The queries should be diverse and cover different aspects of the conversation.
    
    Args:
        client: instructor-patched client
        conversation_id: ID of the conversation to generate search queries for
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key
        conversation_hash: Unique hash of the conversation for caching
        
    Returns:
        SearchQueries object with 4-5 diverse search queries and reasoning
    """
    # Extract conversation content
    messages = conversation.get('conversation', conversation.get('messages', []))
    if not messages:
        raise ValueError("No messages found in conversation")
    
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
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
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


@cache_with_ttl(ttl_seconds=86400 * 7)  # Cache for 7 days
async def synthetic_question_generation_v2(
    client,  # instructor-patched client
    conversation_id: str,
    conversation: Dict[str, Any],
    conversation_hash: str,
) -> SearchQueries:
    """
    Generate search queries for finding conversations with similar patterns and characteristics.
    
    This version focuses on identifying conversation types, themes, and patterns that would be
    useful for researchers, content moderators, or analysts studying human-AI interactions.
    
    Args:
        client: instructor-patched client
        conversation_id: ID of the conversation to analyze
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key
        conversation_hash: Unique hash of the conversation for caching
        
    Returns:
        SearchQueries object with pattern-focused search queries
    """
    # Extract conversation content
    messages = conversation.get('conversation', conversation.get('messages', []))
    if not messages:
        raise ValueError("No messages found in conversation")
    
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
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
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


def is_cached(conversation_hash: str, function_name: str = "synthetic_question_generation_v1") -> bool:
    """
    Check if a conversation's results are cached.
    
    Args:
        conversation_hash: Unique hash of the conversation
        function_name: Name of the function to check cache for
        
    Returns:
        True if cached, False otherwise
    """
    try:
        cache_key = f"{function_name}_v1_{conversation_hash}"
        return cache_key in cache
    except Exception:
        return False