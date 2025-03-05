# Week 6: Tool Selection and Orchestration

## Notebooks Overview

### 1. Evaluate Tools.ipynb
This notebook introduces evaluation metrics for measuring tool selection performance.

**What You'll Do:**
- Define precision and recall metrics specifically for tool selection
- Create simulations of tool calls with various examples
- Implement Pydantic models for structured tool definitions
- Use the AsyncOpenAI client with instructor for tool generation
- Compare sequential and parallel tool calling approaches
- Evaluate when each approach performs better

You'll establish objective ways to measure tool selection quality and learn when parallel execution is appropriate.

### 2. Generate Dataset.ipynb
This notebook creates a synthetic dataset targeting common tool selection failure modes.

**What You'll Do:**
- Load available commands from `raw_commands.json` (70+ commands)
- Generate diverse test cases that mimic real user behavior
- Implement complex query generation with chain-of-thought reasoning
- Create contrastive examples to generate more realistic queries
- Analyze per-tool recall to identify specific weaknesses
- Build a benchmarking dataset for systematic improvement

You'll develop a comprehensive test suite that challenges tool selection capabilities.

### 3. Improving Performance.ipynb
This notebook explores techniques to systematically improve tool selection accuracy.

**What You'll Do:**
- Implement system prompts with detailed user behavior context
- Create few-shot examples demonstrating correct tool combinations
- Measure performance improvements across different prompting strategies
- Compare baseline, system prompt, and few-shot approaches
- Analyze which types of queries improve the most with each approach
- Achieve dramatic improvements in precision and recall

You'll see how targeted improvements can substantially boost tool selection performance:
- Baseline: 45% precision, 40% recall
- With system prompt: 64% precision (+42%), 54% recall (+35%)
- With system prompt + few-shot examples: 79% precision (+76%), 84% recall (+110%)

## Data Files and Assets
- `raw_commands.json`: List of 70+ available commands with descriptions
- `queries.jsonl`: Generated test queries with expected tool calls
- `helpers.py`: Utility functions for evaluation and metrics calculation

## Technical Requirements
- Required libraries: instructor, pydantic, openai.AsyncOpenAI, braintrust, pandas, asyncio
- OpenAI API access for tool calling capabilities
- Basic understanding of async programming concepts

## Why These Notebooks Matter
Modern RAG systems increasingly rely on tool orchestration beyond simple retrieval. These notebooks apply the same systematic improvement methodology to tool selection:

1. First, establish objective metrics to measure performance
2. Then, generate targeted test cases to identify weaknesses
3. Finally, implement and measure specific improvements

This approach demonstrates how simple prompting changes can dramatically improve tool selection, enabling RAG systems to coordinate multiple specialized capabilities rather than relying on retrieval alone.