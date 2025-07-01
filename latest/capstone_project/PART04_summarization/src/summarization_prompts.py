from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    """Generated summary of a conversation."""

    chain_of_thought: str = Field(
        description="Chain of thought process for generating the summary"
    )
    summary: str = Field(
        description="The conversation summary based on the specified approach"
    )


async def conversation_summary_v1(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
) -> ConversationSummary:
    """
    Generate a concise summary focused on key topics and searchable terms.

    This approach creates summaries optimized for semantic search by focusing on:
    - Main topics discussed
    - Key questions asked
    - Primary solutions or information provided
    - Important technical terms or concepts

    The summary should be 2-3 sentences that capture the essence of what a user
    might search for to find this conversation.

    Args:
        client: instructor-patched client
        messages: List of conversation messages

    Returns:
        ConversationSummary object with concise, search-optimized summary
    """

    prompt = """
    You are creating search-optimized summaries of conversations for a RAG system.
    Your goal is to summarize this conversation in a way that makes it easily discoverable
    through semantic search.
    
    Generate a 2-3 sentence summary that:
    1. Captures the main topic or problem discussed
    2. Includes key technical terms, concepts, or domain-specific vocabulary
    3. Mentions the type of assistance provided (explanation, troubleshooting, code example, etc.)
    4. Uses natural language that someone might use when searching
    
    Focus on WHAT the conversation is about, not HOW it progresses.
    
    <conversation>
    {% for message in messages %}
        <message role="{{ message.role }}">
            {{ message.content }}
        </message>
    {% endfor %}
    </conversation>
    
    Generate a concise, searchable summary of this conversation.
    """

    response = await client.chat.completions.create(
        response_model=ConversationSummary,
        messages=[{"role": "user", "content": prompt}],
        context={"messages": messages},
    )

    return response


async def conversation_summary_v2(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
) -> ConversationSummary:
    """
    Generate a comprehensive summary that captures conversation patterns and themes.

    This approach creates summaries that align with the V2 query style by focusing on:
    - Conversation patterns and interaction types
    - User intent and behavior
    - AI response characteristics
    - Overall conversation flow and structure
    - Thematic categorization

    The summary should be detailed enough to match pattern-based queries while
    remaining concise (4-6 sentences).

    Args:
        client: instructor-patched client
        messages: List of conversation messages

    Returns:
        ConversationSummary object with pattern-focused comprehensive summary
    """

    prompt = """
    You are a conversation analyst studying patterns in human-AI interactions.
    Your goal is to create a summary that captures the patterns, themes, and 
    characteristics of this conversation for research purposes.
    
    Generate a 4-6 sentence summary that describes:
    1. The type of conversation and interaction pattern (Q&A, creative collaboration, 
       troubleshooting, educational discussion, etc.)
    2. The user's primary intent or goal
    3. Key themes or domains covered (technical, creative, medical, etc.)
    4. Notable characteristics of the interaction (role-playing, refusals, 
       clarifications, iterative refinement, etc.)
    5. The overall flow and progression of the conversation
    
    Think about how a researcher would categorize and describe this conversation
    when looking for similar interaction patterns.
    
    Examples of pattern-focused descriptions:
    - "A technical troubleshooting conversation where the user seeks help debugging Python code"
    - "An educational Q&A session about machine learning concepts with iterative clarifications"
    - "A creative writing collaboration involving character development and plot refinement"
    
    <conversation>
    {% for message in messages %}
        <message role="{{ message.role }}">
            {{ message.content }}
        </message>
    {% endfor %}
    </conversation>
    
    Generate a comprehensive summary that captures the conversation's patterns and characteristics.
    """

    response = await client.chat.completions.create(
        response_model=ConversationSummary,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at analyzing and categorizing human-AI conversations, focusing on patterns, themes, and interaction characteristics rather than specific content details.",
            },
            {"role": "user", "content": prompt},
        ],
        context={"messages": messages},
    )

    return response