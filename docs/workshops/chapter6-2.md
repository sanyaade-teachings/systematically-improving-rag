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

## What This Chapter Covers

- Implementing tool interfaces for different content types
- Building query routers with few-shot examples
- Creating feedback loops for routing improvement
- Measuring router vs retriever performance

## Implementing Tool Interfaces

Here's how to implement tool interfaces for a construction information system with blueprints, documents, and schedules.

**Related concepts from previous chapters:**
- Chapter 1: Evaluation metrics for testing router accuracy
- Chapter 3: Feedback showing which tools users need
- Chapter 4: Query analysis for tool requirements
- Chapter 5: Specialized retrievers as tools

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

### Tool Documentation Matters

Detailed docstrings help both developers and language models understand when to use each tool. Examples are especially important for pattern recognition.

### Tool Portfolio Design

**Key principle**: Tools don't map one-to-one with retrievers. Like command-line utilities, multiple tools can access the same underlying data in different ways.

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

### Model Context Protocol (MCP)

MCP is Anthropic's standard for connecting AI to data sources and tools. It's like USB-C for AI applications – a universal connection standard.

Benefits:
- **Standardization**: One protocol instead of many connectors
- **Interoperability**: Maintain context across tools
- **Ecosystem**: Reusable connectors for common systems
- **Security**: Built-in security considerations

MCP provides a standard way to implement the tools-as-APIs pattern.

**Note**: MCP is still new with limited production implementations. Early adopters should expect to build custom connectors and deal with an evolving standard.

## Building the Routing Layer

The routing layer needs to:

1. Understand the query
2. Select appropriate tools
3. Extract parameters
4. Execute tools
5. Combine results

Modern LLMs handle this well with clear tool definitions and examples.

**Important**: Distinguish between router performance (selecting tools) and retriever performance (finding information). Both need to work well for good results.

### Multi-Agent vs Single-Agent

**Multi-agent challenges:**
- Complex state sharing
- Message passing latency
- Harder debugging
- Error cascades

**Multi-agent benefits:**
- Token efficiency (each agent sees only relevant context)
- Specialization (different models for different tasks)
- Read/write separation for safety

**Example**: A coding assistant might use:
- Single agent for reading/analysis
- Specialized agent for code generation
- Separate agent for file operations

This separates safe read operations from potentially dangerous write operations.

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

### Few-Shot Examples for Better Routing

Good examples are critical for router effectiveness. They help the model recognize patterns that should trigger specific tools.

### RAG Architecture Evolution

**Generation 1: Pure Embeddings**
- Single vector database
- Semantic search only
- Limited to similarity

**Generation 2: Hybrid Search**
- Semantic + lexical
- Metadata filtering
- Still retrieval-focused

**Generation 3: Tool-Based**
- Multiple specialized tools
- Beyond retrieval to computation
- Matches user mental models

**Example progression:**
- V1: "Find documents about project X"
- V2: "Find recent documents about project X by John"
- V3: "Compare project X budget vs actuals"

V3 requires computation tools, not just retrieval.

### How This Connects

This chapter combines concepts from throughout the book:
- Chapter 0: Improvement flywheel
- Chapter 1: Evaluation frameworks
- Chapter 2: Fine-tuning
- Chapter 3: Feedback loops
- Chapter 4: Query understanding
- Chapter 5: Specialized capabilities

The unified architecture brings these pieces together.

### Creating Effective Few-Shot Examples

1. **Cover edge cases**: Include ambiguous queries
2. **Multi-tool examples**: Show when to use multiple tools
3. **Hard decisions**: Similar queries, different tools
4. **Real queries**: Use actual user examples when possible
5. **Diversity**: Cover all tools and parameter combinations

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

### Dynamic Example Selection

Once you have enough interaction data, select relevant examples dynamically for each query:

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

This creates a learning system that improves routing based on successful interactions.
