---
title: Tool Interfaces and Implementation
description: Learn how to implement tool interfaces for specialized retrievers and build an effective routing layer
authors:
  - Jason Liu
date: 2025-04-11
tags:
  - tool-interfaces
  - implementation
  - few-shot-learning
  - microservices
---

# Tool Interfaces and Implementation: Building the Components

!!! abstract "Chapter Overview"

```
This part explores how to implement the key components of a unified RAG system:

- Implementing tool interfaces for different content types
- Building an effective query router using few-shot examples
- Creating a feedback loop that improves routing over time
- Measuring router performance separately from retriever performance
```

## Implementing Tool Interfaces for Retrieval

Let's look at how to implement this pattern with a concrete example. Imagine we're building a construction information system that includes blueprints, text documents, and project schedules.

!!! note "Drawing from Previous Chapters" - **[Chapter 1](chapter1.md)**: Evaluation metrics help test router accuracy - **[Chapter 3](chapter3-1.md)**: Feedback reveals which tools users need - **[Chapter 4](chapter4-2.md)**: Query analysis identifies tool requirements - **[Chapter 5](chapter5-1.md)**: Specialized retrievers become the tools

### Building a Blueprint Search Tool

Based on our analysis in Chapter 5, we've determined that users often search for blueprints by description and date range. We'll define a tool interface that captures this functionality:

```python
from pydantic import BaseModel

class SearchBlueprint(BaseModel):
    description: str
    start_date: str | None = None
    end_date: str | None = None

    def execute(
        self,
    ) -> List[BlueprintResult]:
        """
        Search for blueprints matching the description and date range.

        Args:
            description: Text to search for in blueprint descriptions
            start_date: Optional start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format

        Returns:
            List of matching blueprint documents
        """
        # Implementation details would depend on your database
        query = self._build_query(
            query=self.description,
            start_date=self.start_date,
            end_date=self.end_date)
        results = self._execute_query(query)
        return self._format_results(results)

        ...
```

### Building a Document Search Tool

Similarly, we can define a tool for searching text documents:

```python
from pydantic import BaseModel

class SearchText(BaseModel):
    query: str
    document_type: Literal["contract", "proposal", "bid"] | None = None

    def execute(
        self,
    ) -> List[DocumentResult]:
        if self.document_type:
            filter_params["type"] = self.document_type

        results = self._search_database(
            query=self.query,
            filters=filter_params)
        return self._format_results(results)
```

### The Power of Tool Documentation

Notice the detailed docstrings and examples in these tool definitions. These aren't just for human developers—they're critical for language models to understand how and when to use each tool. The examples in particular help models recognize the patterns of queries that should trigger each tool.

!!! tip "Tool Portfolio Design Principles"
**Tools vs Retrievers:** - Tools are NOT one-to-one with retrievers - Think of tools like command-line utilities: multiple ways to access the same data - A single retriever might power multiple tools with different interfaces

    **Example: Document Retriever, Multiple Tools**
    ```python
    # One retriever, multiple access patterns
    class DocumentRetriever:
        """Core retrieval engine for all documents"""
        pass

    # Tool 1: Search by keyword
    class SearchDocuments(BaseModel):
        query: str

    # Tool 2: Find by metadata
    class FindDocumentsByMetadata(BaseModel):
        author: Optional[str]
        date_range: Optional[DateRange]
        document_type: Optional[str]

    # Tool 3: Get related documents
    class GetRelatedDocuments(BaseModel):
        document_id: str
        similarity_threshold: float = 0.8
    ```

    This separation allows users to access the same underlying data in ways that match their mental models.

### Aside on MCP

The Model Context Protocol (MCP) is an open standard developed by Anthropic that standardizes how applications provide context to large language models. Conceptually similar to the tool interface pattern we've discussed, MCP creates a universal protocol for connecting AI systems to various data sources and tools.

Think of MCP like a "USB-C port for AI applications" – just as USB-C provides a standardized way to connect devices to various peripherals, MCP provides a standardized way for AI models to interact with different data sources and tools.

Key benefits of MCP include:

1. **Standardization**: Developers can build against a single protocol instead of maintaining separate connectors for each data source
1. **Interoperability**: AI systems can maintain context as they move between different tools and datasets
1. **Ecosystem**: Pre-built connectors for popular systems like GitHub, Slack, and databases can be shared and reused
1. **Security**: The protocol is designed with security considerations for connecting AI to sensitive data sources

MCP represents an important step toward the unified architecture vision we've discussed in this chapter, offering a standardized way to implement the "tools as APIs" pattern across different AI systems and data sources.

!!! warning "MCP is Still Emerging"

```
While MCP represents a promising approach to standardizing AI tool interfaces, it's important to note that it's still very new. As of now, there aren't many production-ready MCP implementations available, and the ecosystem of useful MCPs is still in its early stages of development. Organizations adopting MCP should be prepared for an evolving standard and limited availability of pre-built connectors. As with any emerging technology, early adopters will need to invest in building custom implementations and should expect the standard to evolve over time.
```

## Building the Routing Layer

Once we have defined our specialized retrieval tools, we need a system that can route queries to the appropriate tools. This routing layer is responsible for:

1. Understanding the user's query
1. Determining which tool(s) to call
1. Extracting the necessary parameters from the query
1. Calling the appropriate tools with those parameters
1. Combining results when multiple tools are used

Modern language models excel at this kind of task, especially when provided with clear tool definitions and examples.

!!! warning "Router vs. Individual Retrievers"
It's critical to distinguish between the performance of your router (selecting the right tools) and the performance of each individual retriever (finding relevant information). A perfect router with mediocre retrievers will still yield mediocre results, while a mediocre router with perfect retrievers might miss capabilities entirely.

!!! info "Multi-Agent vs Single-Agent Architecture"
**When to Use Multi-Agent Systems:**

    **Coordination Challenges:**
    - Agents sharing state is complex
    - Message passing adds latency
    - Debugging becomes harder
    - Error cascades are common

    **Primary Benefits:**
    1. **Token Efficiency**: Each agent sees only relevant context
    2. **Specialization**: Different models for different tasks
    3. **Read/Write Separation**: Critical for safety

    **Read-Only vs Write Operations:**
    - Keep read operations in single agent when possible
    - Separate write operations into specialized agents
    - Example: Reading code (safe) vs modifying code (requires careful agent)

    **Real-World Example:**
    A coding assistant might use:
    - Single agent for code reading, analysis, explanation
    - Specialized agent for code generation with guardrails
    - Separate agent for file system operations

    This separation ensures safety while maintaining efficiency.

### Implementing a Simple Router

Here's a basic implementation of a query router using the Instructor library for structured outputs:

```python
import instructor
from typing import List, Literal, Iterable
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()
client = instructor.from_openai(client)

class ClarifyQuestion(BaseModel):
    """Use this when you need more information from the user to understand their request."""
    question: str

class AnswerQuestion(BaseModel):
    """Use this when you can answer directly without retrieving documents."""
    content: str
    follow_ups: List[str] | None = None

class SearchBlueprint(BaseModel):
    """Use this to search for building plans and blueprints."""
    blueprint_description: str
    start_date: str | None = None
    end_date: str | None = None

class SearchText(BaseModel):
    """Use this to search for text documents like contracts, proposals, and bids."""
    query: str
    document_type: Literal["contract", "proposal", "bid"] | None = None

def route_query(query: str) -> Iterable[SearchBlueprint | SearchText | AnswerQuestion | ClarifyQuestion]:
    """
    Routes a user query to the appropriate tool(s) based on the query content.

    This function analyzes the user's query and determines which tool or tools
    would be most appropriate to handle it. Multiple tools can be returned if needed.

    Args:
        query: The user's natural language query

    Returns:
        An iterable of tool objects that should be used to process this query
    """
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are a query router for a construction information system.

                Your job is to analyze the user's query and decide which tool(s) should handle it.
                You can return multiple tools if the query requires different types of information.

                Available tools:
                - SearchBlueprint: For finding building plans and blueprints
                - SearchText: For finding text documents like contracts and proposals
                - AnswerQuestion: For directly answering conceptual questions without retrieval
                - ClarifyQuestion: For asking follow-up questions when the query is unclear

                Here are examples of how to route different types of queries:

                <examples>
                ...
                </examples>
                """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        response_model=Iterable[SearchBlueprint | SearchText | AnswerQuestion | ClarifyQuestion]
    )

# Example usage
def process_user_query(query: str):
    """Process a user query by routing it to the appropriate tools and executing them."""
    # Step 1: Route the query to appropriate tools
    tools = route_query(query)

    # Step 2: Execute each tool and collect results
    results = []
    for tool in tools:
        if isinstance(tool, SearchBlueprint):
            # Execute blueprint search
            blueprints = search_blueprints(
                description=tool.blueprint_description,
                start_date=tool.start_date,
                end_date=tool.end_date
            )
            results.append({"type": "blueprints", "data": blueprints})

        elif isinstance(tool, SearchText):
            # Execute text search
            documents = search_documents(
                query=tool.query,
                document_type=tool.document_type
            )
            results.append({"type": "documents", "data": documents})

        elif isinstance(tool, AnswerQuestion):
            # Direct answer without retrieval
            results.append({"type": "answer", "data": tool.content})

        elif isinstance(tool, ClarifyQuestion):
            # Return clarification question to user
            return {"action": "clarify", "question": tool.question}

    # Step 3: Generate a response using the collected results
    return {"action": "respond", "results": results}
```

### Using Few-Shot Examples to Improve Routing

The effectiveness of the router depends significantly on providing good examples of when to use each tool. These few-shot examples help the model understand the patterns that should trigger different tools.

!!! info "Evolution of RAG Architectures"
**From Embeddings to Tools:**

    The progression of RAG architectures follows a predictable pattern:

    1. **Generation 1: Pure Embeddings**
       - Single vector database
       - Semantic search only
       - Limited to similarity matching

    2. **Generation 2: Hybrid Search**
       - Combine semantic + lexical
       - Add metadata filtering
       - Still retrieval-focused

    3. **Generation 3: Tool-Based**
       - Multiple specialized tools
       - Goes beyond retrieval
       - Includes actions and computations

    **Why This Evolution Happens:**
    - Users don't just want to find information
    - They want to analyze, compare, compute
    - Tools enable richer interactions
    - Better matches user mental models

    **Example Evolution:**
    ```
    V1: "Find documents about project X"
    V2: "Find recent documents about project X by John"
    V3: "Compare project X budget vs actuals and identify variances"
    ```

    The third query requires tools that can compute, not just retrieve.

!!! tip "Complete the Journey"
This chapter brings together all the concepts from the book: - The improvement flywheel from [Chapter 0](chapter0.md) - Evaluation frameworks from [Chapter 1](chapter1.md) - Fine-tuning from [Chapter 2](chapter2.md) - Feedback loops from [Chapter 3](chapter3-1.md) - Query understanding from [Chapter 4](chapter4-2.md) - Specialized capabilities from [Chapter 5](chapter5-1.md)

    The unified architecture is where everything comes together into a cohesive product.

!!! tip "Effective Few-Shot Examples"
When creating few-shot examples for query routing:

```
1. **Cover edge cases**: Include examples of ambiguous queries that could be interpreted multiple ways
2. **Include multi-tool examples**: Show when multiple tools should be used together
3. **Demonstrate hard decisions**: Show when similar-sounding queries should route to different tools
4. **Use real user queries**: Whenever possible, use actual queries from your users
5. **Maintain diversity**: Ensure examples cover all tools and important parameter combinations
```

For instance, a system prompt for routing might include examples like:

```
<examples>
- "Find blueprints for the city hall built in 2010."
{
    "blueprint_description": "city hall blueprints",
    "start_date": "2010-01-01",
    "end_date": "2010-12-31"
}
- "I need plans for residential buildings constructed after 2015."
{
    "blueprint_description": "residential building plans",
    "start_date": "2015-01-01",
    "end_date": null
}
- "Can you find me the plans for a the 123 main st building?"
{
    "blueprint_description": "123 main st building",
    "start_date": null,
    "end_date": null
}
- "Show me blueprints for schools built between 2018 and 2020."
{
    "blueprint_description": "school blueprints",
    "start_date": "2018-01-01",
    "end_date": "2020-12-31"
}
- "I need the contract for the Johnson project."
{
    "query": "Johnson project contract",
    "document_type": "contract"
}
- "What's the difference between a blueprint and a floor plan?"
{
    "content": "Blueprints are technical architectural drawings that include detailed specifications for construction, while floor plans focus primarily on the layout and dimensions of rooms and spaces within a building.",
    "follow_ups": ["How do I read a blueprint?", "Can you show me examples of floor plans?"]
}
- "Can you explain what a load-bearing wall is?"
{
    "content": "A load-bearing wall is a structural element that supports the weight of the building above it, helping to transfer the load to the foundation. Removing or modifying load-bearing walls requires careful engineering considerations.",
    "follow_ups": ["How can I identify a load-bearing wall?", "What happens if you remove a load-bearing wall?"]
}
- "I'm not sure what kind of building plans I need for my renovation."
{
    "question": "Could you tell me more about your renovation project? What type of building is it, what changes are you planning to make, and do you need plans for permits or for construction guidance?"
}
- "Find me school building plans from 2018-2020 and any related bid documents."
[
    {
        "blueprint_description": "school building plans",
        "start_date": "2018-01-01",
        "end_date": "2020-12-31"
    },
    {
        "query": "school building bids",
        "document_type": "bid"
    }
]
</examples>
```

### Dynamic Few-Shot Example Selection

As your system collects more data about successful interactions, you can move beyond static examples to a dynamic approach that selects the most relevant few-shot examples for each query:

```python
def get_dynamic_examples(query: str, example_database: List[dict], num_examples: int = 5) -> List[dict]:
    """
    Select the most relevant examples for a given query from an example database.

    Args:
        query: The user's query
        example_database: Database of previous successful interactions
        num_examples: Number of examples to return

    Returns:
        List of the most relevant examples for this query
    """
    # Embed the query
    query_embedding = get_embedding(query)

    # Calculate similarity with all examples in database
    similarities = []
    for example in example_database:
        example_embedding = example["embedding"]
        similarity = cosine_similarity(query_embedding, example_embedding)
        similarities.append((similarity, example))

    # Sort by similarity and return top examples
    similarities.sort(reverse=True)
    return [example for _, example in similarities[:num_examples]]

def route_query_with_dynamic_examples(query: str) -> Iterable[Tool]:
    """Route query using dynamically selected examples."""
    # Get relevant examples for this query
    relevant_examples = get_dynamic_examples(query, example_database)

    # Format examples for inclusion in prompt
    examples_text = format_examples(relevant_examples)

    # Create prompt with dynamic examples
    system_prompt = f"""
    You are a query router for a construction information system.
    Your job is to analyze the user's query and decide which tool(s) should handle it.

    Available tools:
    - SearchBlueprint: For finding building plans and blueprints
    - SearchText: For finding text documents like contracts and proposals
    - AnswerQuestion: For directly answering conceptual questions without retrieval
    - ClarifyQuestion: For asking follow-up questions when the query is unclear

    Here are examples of how to route different types of queries:

    {examples_text}
    """

    # Perform routing with dynamic prompt
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        response_model=Iterable[SearchBlueprint | SearchText | AnswerQuestion | ClarifyQuestion]
    )
```

This approach ensures that your routing layer continuously improves as you collect more examples of successful interactions, creating a learning system that adapts to your users' query patterns.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
