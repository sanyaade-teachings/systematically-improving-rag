# Systematic Improvements in RAG: Building Automated Tools for Data Analysis

## Abstract

This document presents findings from a series of experiments aimed at improving retrieval-augmented generation (RAG) performance through iterative refinement of query generation and summarization strategies. We demonstrate how systematic analysis of failure modes led to a 3x improvement in recall performance, with the ultimate goal of building automated tools that help teams identify patterns in user feedback and create specialized retrieval systems.

## Introduction

The core challenge in RAG systems is matching user queries to relevant documents. Our experiments explored this challenge through two complementary approaches:

1. Query generation strategies (how users might search)
2. Document summarization strategies (how content is indexed)

## Experimental Design

### Query Generation Prompts (V1, V2, V3)

#### V1: Content-Focused Queries

- **Hypothesis**: Users search using specific technical terms and concrete questions
- **Design**: Generate queries mimicking natural search behavior with specific vocabulary
- **Characteristics**: Direct, keyword-heavy, problem-specific

**Prompt excerpt**:
```
Given this conversation, generate 4-5 diverse search queries that different users might 
type when looking for similar help or information. The queries should:

1. Cover different aspects of the conversation (technical terms, problem description, solution type)
2. Vary in specificity (some broad, some specific)
3. Use different phrasings and vocabulary levels
4. Reflect natural user search behavior
5. Include both question-style and keyword-style queries
```

**Example V1 queries generated**:
- "How to build a REST API with Node.js and Express for a business directory"
- "Python code for sorting tweets by reply count ratio"
- "Translate economic report to Chinese"
- "How to test resistors and capacitors"
- "Creating unique skills for characters like a brute, a seductress, and a lone wolf"

#### V2: Pattern-Based Queries

- **Hypothesis**: Researchers and analysts search for conversation types and patterns
- **Design**: Generate meta-queries about conversation characteristics
- **Characteristics**: Abstract, categorical, pattern-focused
- **Rationale**: Useful for studying AI behavior patterns across similar interactions

**Prompt excerpt**:
```
Analyze this conversation and generate search queries that would help find conversations with:
- Similar content themes or domains (medical, creative, technical, etc.)
- Similar user intents (seeking advice, creative collaboration, testing AI limits, etc.)
- Similar interaction patterns (role-playing, Q&A, refusal situations, etc.)
- Similar AI behaviors or response types

Focus on generating queries that capture the ESSENCE and PATTERNS rather than specific details.
```

**Example V2 queries generated**:
- "conversations involving role-playing with fictional characters"
- "technical troubleshooting discussions"
- "conversations where AI refuses medical advice"
- "creative writing collaborations"
- "conversations exploring ethical and philosophical questions"
- "AI interactions focused on visual and artistic style descriptions"
- "conversations demonstrating AI boundary testing"

#### V3: Specific Pattern Queries

- **Hypothesis**: Combining pattern awareness with specific details would improve precision
- **Design**: Balance between abstraction and specificity, including satisfaction signals
- **Key innovation**: Explicitly captures user satisfaction/frustration signals
- **Characteristics**: Pattern + specifics + emotional context

**Prompt excerpt**:
```
Analyze this conversation and generate 5-7 search queries that:

1. COMBINE pattern descriptions with specific details:
   - Start with the conversation type/pattern
   - Add unique technical terms, concepts, or specifics mentioned
   - Include memorable phrases, examples, or distinctive elements

2. CAPTURE user satisfaction signals:
   - User frustration: "conversation where user gets frustrated about [specific issue]"
   - User satisfaction: "helpful AI conversation successfully solving [specific problem]"
   - Failed attempts: "AI struggling to understand user's request about [topic]"
   - Misunderstandings: "conversation with miscommunication about [specific concept]"

3. USE this query structure:
   - "[conversation type] + [specific topic/issue] + [distinguishing detail]"
```

**Example V3 queries generated**:
- "molecular cloning troubleshooting low DNA concentration gel electrophoresis BamHI HindIII differences"
- "user frustrated with Docker PostgreSQL connection refused error"
- "AI successfully helping debug React useState infinite loop issue"
- "role-playing conversation medieval blacksmith discussing enchanted sword crafting"
- "frustrated user requesting medical advice AI refuses to provide"
- "helpful AI conversation successfully providing list of platforms like YouTube EDU, Coursera, edX"
- "user satisfied with detailed Morocco travel narrative including Al-Attarine Madrasa and Bahia Palace"

### Summarization Prompts (V1, V2, V3, V4)

#### V1: Concise Topic Summary

- **Design**: 2-3 sentences capturing main topics and searchable terms
- **Focus**: Keywords and technical terms for traditional search

**Prompt excerpt**:
```
Generate a 2-3 sentence summary that:
1. Captures the main topic or problem discussed
2. Includes key technical terms, concepts, or domain-specific vocabulary
3. Mentions the type of assistance provided (explanation, troubleshooting, code example, etc.)
4. Uses natural language that someone might use when searching
```

**Example V1 summary**:
> "User seeks help debugging a Node.js REST API with PostgreSQL connection issues. The conversation covers Express middleware setup, database connection pooling, and error handling strategies for production deployment."

#### V2 & V3: Comprehensive Pattern Analysis

- **Design**: Detailed analysis of conversation dynamics, user journey, and AI performance
- **Focus**: Extensive metadata capture including frustration points, task completion, and behavior patterns
- **Innovation**: 22-point analysis framework capturing user satisfaction signals

**Prompt excerpt for V2/V3** (abbreviated):
```
Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Knowledge Requests: Identify specific knowledge, explanations, or information the user is seeking
3. User Feedback and Preferences: Document any feedback about the AI's responses
4. Key Topics and Concepts: List all important topics discussed
5. User Frustration Points: Specifically identify where the user expresses frustration
6. Learning Progression: Track how the user's understanding evolves
7. AI Performance Issues: Identify instances where the AI failed to understand
[... continues with 22 total sections ...]
```

**Example V2/V3 summary structure**:
> **Primary Request**: User wants to implement OAuth2 authentication in a React application with TypeScript
> 
> **User Frustration Points**: "This is the third time I'm explaining this - I need CLIENT-SIDE OAuth, not server-side!"
> 
> **AI Performance Issues**: Initially misunderstood and provided server-side Node.js examples when user specifically requested React implementation
> 
> **Task Completion**: Partially completed - user got basic implementation but struggled with TypeScript types

#### V4: Pattern-Optimized Summary

- **Design**: Structured summaries explicitly matching V2 query patterns
- **Format**: "This is a [TYPE] conversation involving..."
- **Focus**: Conversation classification, interaction patterns, domain tags
- **Innovation**: Aligned summary language with query patterns

**Prompt excerpt**:
```
Analyze this conversation and create a structured summary with these components:

1. **Conversation Classification** (1-2 sentences):
   Start with: "This is a [TYPE] conversation involving/where/about..."
   
2. **Interaction Patterns** (2-3 patterns):
   Use pattern-descriptive phrases like:
   - "User seeks step-by-step guidance for [topic]"
   - "Conversation follows problem-diagnosis-solution pattern"
   
3. **Domain and Theme Tags** (3-5 tags):
   Include categorical descriptors:
   - Technical domains: "software development", "database management"
   - Interaction types: "troubleshooting", "advisory", "collaborative"
```

**Example V4 summaries**:

> "This is a technical troubleshooting conversation involving Docker container networking issues. The interaction follows a problem-diagnosis-solution pattern where the user seeks step-by-step guidance for connecting containers across different networks. Patterns include iterative debugging with the AI providing diagnostic commands and the user reporting results. Domain tags include 'DevOps', 'container orchestration', and 'network debugging'. User demonstrates intermediate expertise in Docker, approaching the problem methodically. AI provides detailed, command-line focused responses, successfully helping resolve the bridge network configuration."

> "This is an educational medical discussion where the user presents a clinical case and asks about risk factors for a condition. The AI provides an explanatory response highlighting relevant health factors and their impact on risk. Patterns involve a clinical reasoning inquiry and educational clarification. Domain tags include 'medical diagnosis', 'cardiology', and 'risk assessment'. User demonstrates a basic understanding of medical concepts, approaching the question in a straightforward, factual manner. AI responds with a detailed, explanatory style, synthesizing multiple health factors to address the question."

## Results and Analysis

### Experiment 1: Baseline Performance

| Query Type | Summary Type | Recall@10 | Example Match/Miss |
|------------|--------------|-----------|-------------------|
| V1         | V1          | 66.75%    | ✓ "Docker PostgreSQL error" finds Docker troubleshooting |
| V2         | V1          | 15.57%    | ✗ "technical troubleshooting conversation" misses specific instances |

**Finding**: V2 queries performed poorly with traditional summaries, suggesting a fundamental mismatch between pattern-based queries and content-focused summaries.

### Experiment 2: Summary Optimization

| Query Type | Summary Version | Recall@10 | Improvement |
|------------|----------------|-----------|-------------|
| V2         | V1             | 15.57%    | baseline    |
| V2         | V2             | 18.75%    | +20%        |
| V2         | V3             | 19.18%    | +23%        |
| V2         | V4             | 21.64%    | +39%        |

**Finding**: Progressive improvement with each summary version, but still suboptimal performance.

### Critical Discovery: The Specificity Problem

Upon analyzing failed V2 queries, we discovered they were finding topically relevant conversations, just not the exact target. 

**Example failure analysis**:
- Query: "conversations involving role-playing with fictional characters"
- Retrieved: 5 different role-playing conversations (all relevant!)
- Problem: Target conversation was ranked #47 out of hundreds of role-playing conversations

This wasn't a retrieval failure but a specificity problem. V2 queries were too generic for precise retrieval.

### Experiment 3: V3 Query Generation

**Design Process**:

1. Analyzed failure patterns from V2
2. Identified need for distinguishing details
3. Added customer satisfaction signals based on user feedback patterns
4. Included specific technical details and error messages

**Results**:

| Metric     | V2 Queries | V3 Queries | Improvement | Example Success |
|------------|------------|------------|-------------|-----------------|
| Recall@1   | 7.67%      | 28.69%     | +274%       | "frustrated user Docker PostgreSQL connection refused" → exact match |
| Recall@5   | 16.34%     | 53.20%     | +226%       | Specific error messages help narrow results |
| Recall@10  | 21.64%     | 62.95%     | +191%       | Combination of pattern + details works |
| Recall@30  | 30.45%     | 71.87%     | +136%       | Most queries find target with specificity |

## Key Insights

### 1. Query-Summary Alignment is Critical

- Mismatched strategies (V2 queries + V1 summaries) yield poor results
- Aligned strategies (V2 queries + V4 summaries) show improvement
- Best results from appropriate specificity (V3 queries + V4 summaries)

### 2. Different Query Types Serve Different Purposes

- **V1**: Known-item search ("I know exactly what I want")
- **V2**: Exploratory search ("Show me conversations about X")
- **V3**: Targeted pattern search ("Find specific instances of X with Y characteristics")

### 3. Satisfaction Signals Matter

V3's inclusion of user satisfaction signals ("frustrated", "successfully", "satisfied") provided crucial distinguishing context that significantly improved retrieval accuracy.

### 4. Remaining Challenges

Even with 63% Recall@10, certain patterns remain difficult:

- Multi-topic conversations: "game discussion + weather + homework"
- Highly constrained requests: "Greek plays without titles or authors"
- Creative content with multiple disparate elements: "Disney game + treasure + alien storms"

## Methodology Notes

### Iterative Hypothesis Testing

Each experiment built upon previous findings:

1. V1 established baseline
2. V2 revealed pattern-matching potential but exposed specificity issues
3. V4 summaries partially addressed V2 limitations
4. V3 queries synthesized learnings for dramatic improvement

### Failure Analysis as Design Driver

Systematic analysis of failed queries drove each iteration:

- V2 failures → revealed specificity problem
- Specificity problem → inspired V3 design
- V3 failures → identified remaining edge cases

## Conclusions

1. **Specificity is paramount**: Generic pattern queries fail in large datasets
2. **User satisfaction signals are valuable**: Emotional context helps distinguish similar conversations
3. **Iterative refinement works**: Each experiment provided insights for the next
4. **Multiple strategies needed**: No single approach fits all use cases

## Building an AI Agent for Continuous Improvement

### The Vision: Automated Analysis and Hypothesis Generation

The true power of our improved retrieval system isn't just better search—it's enabling an AI agent to autonomously analyze conversation patterns and propose system improvements. By combining V3 queries (with satisfaction signals) and V4 summaries (with detailed failure analysis), we've created the foundation for a self-improving system.

### Key Capabilities for the Analysis Agent

1. **Failure Pattern Detection**
   - Query: "frustrated user AI misunderstood request multiple times"
   - Retrieves conversations where the AI failed to understand user intent
   - Identifies common misunderstanding patterns across similar failures

2. **Usage Pattern Analysis**
   - Query: "successful creative writing collaboration with specific techniques"
   - Retrieves conversations showing effective AI behaviors
   - Learns which approaches work best for different use cases

3. **Edge Case Discovery**
   - Query: "AI struggling with ambiguous request eventually succeeded"
   - Retrieves conversations with recovery patterns
   - Identifies opportunities for proactive clarification

### Example Agent Workflow

```python
# Pseudo-code for an analysis agent
async def analyze_system_performance(retrieval_client):
    # 1. Retrieve failure patterns
    failures = await retrieval_client.search(
        "user frustrated AI failed to understand technical request"
    )
    
    # 2. Analyze common themes
    failure_patterns = extract_patterns(failures)
    
    # 3. Generate hypotheses
    hypotheses = []
    for pattern in failure_patterns:
        if pattern.frequency > 10 and pattern.impact == "high":
            hypotheses.append({
                "pattern": pattern.description,
                "hypothesis": f"Creating specialized handler for {pattern.domain} queries",
                "expected_impact": pattern.frequency * pattern.severity,
                "implementation_effort": estimate_effort(pattern)
            })
    
    # 4. Prioritize improvements
    return sorted(hypotheses, key=lambda h: h["expected_impact"] / h["implementation_effort"])
```

### Enabling Research Iterations

The V3/V4 system specifically captures:

1. **Satisfaction Signals**: Direct indicators of success/failure
2. **Interaction Patterns**: How conversations evolve over time
3. **Recovery Strategies**: How the AI recovered from initial failures
4. **Domain Context**: Technical details that distinguish similar conversations

This rich metadata enables the agent to:
- Form testable hypotheses about system improvements
- Measure the impact of changes by comparing before/after patterns
- Identify emerging usage patterns that warrant new capabilities
- Detect regression by monitoring satisfaction signals over time

### From Reactive to Proactive Development

Traditional approach:
- Wait for user complaints
- Manually review logs
- Guess at root causes
- Implement broad fixes

Agent-enabled approach:
- Continuously monitor satisfaction patterns
- Automatically identify failure clusters
- Generate specific, data-backed hypotheses
- Implement targeted improvements with measurable impact

## V5: Agent-Optimized Prompts

### Design Philosophy

V5 represents a paradigm shift from human-searchable content to agent-analyzable intelligence. While V1-V4 focused on improving retrieval for finding specific conversations, V5 transforms the system into an analytical tool for continuous improvement.

### V5 Query Generation: Root Cause Focus

**Key innovations**:
1. **Failure mode queries**: "AI failed to [capability] when user [context]"
2. **Recovery patterns**: "AI successfully recovered from [failure] by [action]"
3. **Impact assessment**: "high-impact failure in [domain] affecting [user goal]"
4. **Improvement opportunities**: "conversation revealing need for [capability]"

**Example V5 queries**:
- "AI failed to understand Docker networking when user provided compose file"
- "misunderstanding about state management leading to infinite loop suggestion"
- "system limitation in file handling causing user abandoned task"
- "AI successfully recovered from math error by showing step-by-step work"
- "conversation revealing need for real-time data access capability"

### V5 Summary Generation: Actionable Analysis

**Structure optimized for agent parsing**:
1. **Failure Analysis**: Root cause, pattern type, user impact, recovery attempts
2. **Interaction Dynamics**: Communication breakdowns, clarification loops, frustration indicators
3. **Capability Gaps**: Missing features, workarounds, knowledge limitations
4. **Success Patterns**: What worked well and why
5. **Improvement Hypotheses**: Specific suggestions with priority and implementation approach
6. **Analysis Metadata**: Domain, complexity, severity, business impact

**Example V5 summary excerpt**:
```
FAILURE ANALYSIS:
- Root cause: AI lacked understanding of TypeScript generics with conditional types
- Failure pattern: Knowledge limitation compounded by reasoning failure
- User impact: 45-minute conversation that should have taken 5 minutes
- Recovery attempts: AI suggested workarounds but missed the elegant solution

IMPROVEMENT HYPOTHESES:
- Would benefit from specialized TypeScript type system knowledge base
- Similar to other advanced type system failures (found in 23 conversations)
- Priority: HIGH (affects expert developers working on type-safe APIs)
- Implementation: Create specialized retriever for TS documentation + examples
```

### Agent Analysis Workflow

The `agent_analysis_example.py` demonstrates how an AI agent would:

1. **Query for patterns**: Use V5 queries to find similar failures across conversations
2. **Extract insights**: Parse V5 summaries to understand root causes and impacts
3. **Group patterns**: Identify systemic issues vs one-off problems
4. **Generate hypotheses**: Propose specific improvements with ROI estimates
5. **Prioritize investments**: Rank improvements by expected impact vs effort

### Measurable Outcomes

With V5, we can answer questions like:
- What are the top 5 capability gaps causing user frustration?
- Which domains have the highest failure rates?
- What recovery strategies are most effective?
- Where would specialized retrievers provide the most value?
- How do failure patterns change over time?

This transforms our RAG system from a passive search tool into an active intelligence system that continuously learns from its interactions and identifies opportunities for improvement.

## Future Directions

1. **Autonomous Hypothesis Generation**: Agent that continuously analyzes conversation patterns and proposes experiments
2. **Impact Prediction Models**: Estimate the value of potential improvements before implementation
3. **Automated A/B Testing**: Deploy improvements selectively and measure real-world impact
4. **Regression Detection**: Alert when new changes negatively impact existing capabilities
5. **Cross-Domain Learning**: Transfer successful patterns from one domain to improve others

## Reproducibility

All experiments used:

- Dataset: WildChat (11,000+ conversations)
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Vector database: TurboPuffer
- Query model: GPT-4.1-nano
- Consistent evaluation: Recall@K metrics with exact conversation matching

The systematic approach of hypothesis → experiment → analysis → refinement proved effective in achieving a 3x improvement in retrieval performance, demonstrating the value of iterative experimentation in RAG system optimization.
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
