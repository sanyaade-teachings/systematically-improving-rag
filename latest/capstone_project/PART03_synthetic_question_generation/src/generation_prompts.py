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
        max_items=8,
    )


async def synthetic_question_generation_v1(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
) -> SearchQueries:
    """
    Generate diverse synthetic search queries from a chat conversation.

    As a product manager analyzing ChatGPT usage patterns, this function creates
    search queries that users might have typed to discover similar conversations.
    The queries should be diverse and cover different aspects of the conversation.

    Args:
        client: instructor-patched client
        conversation: Dictionary containing conversation data with 'messages' or 'conversation' key

    Returns:
        SearchQueries object with 4-5 diverse search queries and reasoning
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

    response = await client.chat.completions.create(
        response_model=SearchQueries,
        messages=[{"role": "user", "content": prompt}],
        context={"messages": messages},
    )

    return response


async def synthetic_question_generation_v2(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
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
        response_model=SearchQueries,
        messages=[
            {
                "role": "system",
                "content": "You are an expert conversation analyst specializing in categorizing and understanding patterns in human-AI interactions. Focus on identifying conversation types, themes, and structural patterns rather than specific content details.",
            },
            {"role": "user", "content": prompt},
        ],
        context={"messages": messages},
    )

    return response
