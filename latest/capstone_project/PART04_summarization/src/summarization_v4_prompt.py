async def conversation_summary_v4(
    client,  # instructor-patched client
    messages: List[Dict[str, Any]],
) -> ConversationSummary:
    """
    Generate a pattern-focused summary optimized for v2-style queries.

    This approach creates summaries that explicitly capture:
    - Conversation categorization and type
    - Interaction patterns and dynamics
    - Domain and thematic classification
    - User behavior patterns
    - AI response patterns
    - Meta-conversation characteristics

    The summary uses pattern-descriptive language that aligns with v2 query style.

    Args:
        client: instructor-patched client
        messages: List of conversation messages

    Returns:
        ConversationSummary object with pattern-optimized summary
    """

    prompt = """
You are a conversation analyst creating searchable summaries that capture conversation PATTERNS and TYPES, not just content details.

Your goal is to create a summary that would match pattern-based search queries like:
- "conversations involving role-playing with fictional characters"
- "technical troubleshooting discussions"
- "conversations where AI refuses medical advice"
- "educational Q&A about scientific concepts"

Analyze this conversation and create a structured summary with these components:

1. **Conversation Classification** (1-2 sentences):
   Start with: "This is a [TYPE] conversation involving/where/about..."
   Examples:
   - "This is a technical troubleshooting conversation involving database configuration issues"
   - "This is a role-playing conversation where the user asks the AI to act as a fictional character"
   - "This is an educational Q&A conversation about quantum physics concepts"

2. **Interaction Patterns** (2-3 patterns):
   Use pattern-descriptive phrases like:
   - "User seeks step-by-step guidance for [topic]"
   - "AI provides explanatory responses with examples"
   - "Conversation follows problem-diagnosis-solution pattern"
   - "User tests AI boundaries with controversial requests"
   - "Collaborative creative writing with iterative refinement"

3. **Domain and Theme Tags** (3-5 tags):
   Include categorical descriptors:
   - Technical domains: "software development", "database management", "API design"
   - Creative domains: "creative writing", "storytelling", "character development"
   - Educational domains: "science education", "language learning", "skill tutorials"
   - Interaction types: "troubleshooting", "advisory", "collaborative", "exploratory"

4. **User Behavior Patterns**:
   - "User demonstrates [expertise level] in [domain]"
   - "User exhibits [frustration/satisfaction/curiosity] about [aspect]"
   - "User's approach is [methodical/exploratory/direct/iterative]"

5. **AI Response Characteristics**:
   - "AI provides [detailed/concise/cautious] responses"
   - "AI [accepts/refuses/redirects] user requests about [topic]"
   - "AI adjusts communication style to match user's [expertise/tone/needs]"

6. **Key Content Elements** (brief):
   List the main topics/concepts discussed, but keep it concise and pattern-focused.

Remember: Focus on HOW the conversation unfolds and WHAT TYPE it represents, not just WHAT was discussed.

<conversation>
{% for message in messages %}
    <message role="{{ message.role }}">
        {{ message.content }}
    </message>
{% endfor %}
</conversation>

Generate a pattern-focused summary that would be discoverable by researchers looking for specific conversation types and interaction patterns.
"""

    response = await client.chat.completions.create(
        response_model=ConversationSummary,
        messages=[
            {
                "role": "system",
                "content": "You are an expert at categorizing conversations by their patterns, types, and interaction dynamics. Focus on creating summaries that match how researchers search for conversation patterns rather than specific content.",
            },
            {"role": "user", "content": prompt},
        ],
        context={"messages": messages},
        max_retries=3,
    )

    return response
