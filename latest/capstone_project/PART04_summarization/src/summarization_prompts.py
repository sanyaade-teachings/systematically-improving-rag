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
        max_retries=3,
    )

    return response


async def conversation_summary_v2(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
) -> ConversationSummary:
    """
    Generate a comprehensive summary that captures conversation patterns, themes, and user interaction dynamics.

    This approach creates summaries that capture:
    - Conversation patterns and interaction types
    - User intent, behavior, and preferences
    - AI response characteristics and adjustments
    - Overall conversation flow and structure
    - User feedback and emotional context
    - Knowledge requests and learning progression
    - User Satisfaction and Frustration Points

    The summary should be detailed enough to match pattern-based queries and understand
    the full context of user-AI interaction dynamics.

    Args:
        client: instructor-patched client
        messages: List of conversation messages

    Returns:
        ConversationSummary object with comprehensive, pattern-focused summary
    """

    prompt = """
Your task is to create a detailed summary of the conversation, paying close attention to the user's explicit requests, feedback, and the assistant's responses.
This summary should be thorough in capturing key topics, important details, interaction patterns, and user preferences that would be essential for understanding the conversation's context and continuation.

Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Chronologically analyze each message and section of the conversation. For each section thoroughly identify:
   - The user's explicit requests and intents
   - The assistant's approach to addressing the user's requests
   - Key decisions, important concepts, and significant details
   - Specific information, examples, or resources mentioned
   - User feedback, preferences, and emotional responses
   - Learning progression and context switches
2. Double-check for accuracy and completeness, addressing each required element thoroughly.

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail

2. Knowledge Requests: Identify specific knowledge, explanations, or information the user is seeking from the AI

3. User Feedback and Preferences: Document any feedback about the AI's responses, communication style preferences, or corrections requested by the user (e.g., "be less verbose," "provide more examples," "explain differently")

4. Key Topics and Concepts: List all important topics, concepts, and subject matter discussed

5. Information and Resources: Enumerate specific information, examples, resources, or references provided or discussed. Pay special attention to the most recent messages and include important details where applicable

6. Problem Solving: Document problems addressed and any ongoing efforts to resolve issues

7. Conversation Dynamics: Note the user's communication style, level of expertise, emotional state (frustration, satisfaction, confusion), and any adjustments made to match their needs

8. User Frustration Points: Specifically identify and quote instances where the user expresses significant frustration, impatience, or dissatisfaction with the AI's responses or the conversation flow

9. Learning Progression: Track how the user's understanding evolves throughout the conversation and any knowledge building that occurs

10. Context Switches: Identify when the conversation shifts topics or focus areas, and note any repeated patterns or recurring themes

11. Clarifications and Corrections: Track instances where the user needed to clarify their request or correct the AI's understanding

12. User Goals and Success Metrics: Distinguish between immediate requests and broader objectives, noting what constitutes success for the user

13. Assumptions Made: Track assumptions the AI made about user needs, context, or expertise level

14. Pending Tasks: Outline any pending tasks or follow-up items that have been explicitly requested

15. Current Focus: Describe in detail precisely what was being discussed or worked on immediately before this summary request, paying special attention to the most recent messages from both user and assistant

16. Optional Next Step: List the next step that would logically follow based on the most recent work or discussion. IMPORTANT: ensure that this step is DIRECTLY in line with the user's explicit requests and the topic being addressed immediately before this summary request. If the last topic was concluded, then only list next steps if they are explicitly in line with the user's request

17. If there is a next step, include direct quotes from the most recent conversation showing exactly what was being discussed and where the conversation left off. This should be verbatim to ensure there's no drift in topic interpretation

18. User Journey & Task Completion: Analyze the user's workflow - did they complete their intended task? Where did they get stuck? How many exchanges were needed? What was their entry point and approach?

19. AI Performance Issues: Identify instances where the AI failed to understand, provided incorrect information, or hit capability limits. Note any hallucinations or clear mistakes.

20. User Behavior Patterns: Document the user's information-seeking strategies, trust indicators (verification, doubt), and usage intensity (quick question vs. deep exploration).

21. Product Experience Insights: Note any feature discoveries, expectation mismatches, or workaround behaviors the user developed to handle AI limitations.

22. Conversation Quality Indicators: Track satisfaction signals (thanks, success expressions), abandonment patterns, and any repetitive questioning that suggests the user wasn't getting what they needed.

Here's an example of how your output should be structured:

<example>
<chain_of_thought>
[Your thought process, ensuring all points are covered thoroughly and accurately]
</chain_of_thought>

<summary>
1. Primary Request and Intent:
   [Detailed description]

2. Knowledge Requests:
   - [Specific knowledge/explanation sought 1]
   - [Specific knowledge/explanation sought 2]
   - [...]

3. User Feedback and Preferences:
   - [Feedback about AI responses, style preferences, corrections]
   - [Communication preferences expressed]
   - [...]

4. Key Topics and Concepts:
   - [Topic/Concept 1]
   - [Topic/Concept 2]
   - [...]

5. Information and Resources:
   - [Resource/Information 1]
      - [Summary of why this information is important]
      - [Summary of how it was used or discussed]
      - [Important details or examples]
   - [...]

6. Problem Solving:
   [Description of problems addressed and ongoing efforts]

7. Conversation Dynamics:
   - User expertise level: [beginner/intermediate/advanced]
   - Communication style: [direct/detailed/collaborative/etc.]
   - Emotional state: [engaged/frustrated/satisfied/confused/etc.]
   - Adjustments made: [any changes to approach based on user feedback]

8. User Frustration Points:
   - [Direct quotes showing user frustration, impatience, or dissatisfaction]
   - [Context around what triggered the frustration]
   - [How the AI responded to user frustration]

9. Learning Progression:
   - [How user's understanding evolved]
   - [Knowledge building that occurred]
   - [Skills or concepts mastered]

10. Context Switches:
    - [Topic shifts and focus changes]
    - [Repeated patterns or recurring themes]

11. Clarifications and Corrections:
    - [Instances where user clarified or corrected]
    - [Misunderstandings that were resolved]

12. User Goals and Success Metrics:
    - Immediate goals: [short-term objectives]
    - Broader objectives: [long-term aims]
    - Success indicators: [what constitutes success]

13. Assumptions Made:
    - [Assumptions about user needs or context]
    - [Assumptions about expertise level]
    - [Assumptions about preferred approach]

14. Pending Tasks:
    - [Task 1]
    - [Task 2]
    - [...]

15. Current Focus:
    [Precise description of current discussion or work]

16. Optional Next Step:
    [Optional next step to take]

17. User Journey & Task Completion:
    - Task completion status: [completed/partially completed/abandoned]
    - Workflow efficiency: [number of exchanges needed, bottlenecks]
    - Entry point: [how user started the conversation]
    - Approach strategy: [user's problem-solving approach]

18. AI Performance Issues:
    - Failure points: [where AI failed to understand or help]
    - Incorrect information: [any hallucinations or mistakes]
    - Capability gaps: [tasks user wanted that AI couldn't handle]

19. User Behavior Patterns:
    - Information seeking: [how user phrases questions, iteration patterns]
    - Trust indicators: [verification behaviors, expressions of doubt]
    - Usage intensity: [quick question vs. deep exploration]

20. Product Experience Insights:
    - Feature discoveries: [new capabilities user found]
    - Expectation mismatches: [where user expected different behavior]
    - Workarounds: [strategies user developed for AI limitations]

21. Conversation Quality Indicators:
    - Satisfaction signals: [thanks, success expressions, positive feedback]
    - Abandonment patterns: [abrupt endings, unresolved issues]
    - Repetitive patterns: [similar questions asked multiple times]

</summary>
</example>

Please provide your summary based on the conversation so far, following this structure and ensuring precision and thoroughness in your response.

{% for message in messages %}
    <message role="{{ message.role }}">
        {{ message.content }}
    </message>
{% endfor %}
    """

    response = await client.chat.completions.create(
        response_model=ConversationSummary,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at analyzing and categorizing human-AI conversations, focusing on patterns, themes, interaction characteristics, and user experience dynamics across all types of conversations.",
            },
            {"role": "user", "content": prompt},
        ],
        context={"messages": messages},
        max_retries=3,
    )

    return response
