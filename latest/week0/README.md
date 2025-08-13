# Week 0: Foundation and Environment Setup

## Overview

This week establishes the fundamental tools and concepts you'll use throughout the course. You'll learn to work effectively with Jupyter Notebooks, understand vector databases through hands-on LanceDB implementation, and master systematic evaluation using Pydantic Evals. These foundations are essential before diving into more complex RAG improvement techniques.

Vector search forms the backbone of RAG systems, and understanding different retrieval strategies (vector, full-text, and hybrid) will help you make informed decisions throughout the course. The evaluation framework you learn here will be used to measure every improvement you make in subsequent weeks.

## Learning Objectives

By the end of this week, you'll be able to:

- Navigate and utilize Jupyter Notebooks effectively for interactive development
- Implement vector, full-text, and hybrid search strategies in LanceDB
- Apply reranking techniques to improve search result quality
- Build systematic evaluation frameworks using Pydantic Evals
- Track and compare model performance across different test cases

## Notebooks

### 1. 01_using_jupyter_notebooks.ipynb

**Purpose**: Master the Jupyter Notebook environment for effective course participation

**What You'll Learn**:

- Running Python code in interactive cells
- Executing shell commands within notebooks
- Using magic commands for performance measurement
- Understanding kernels and kernel selection
- Configuring autoreload for smooth development

**What You'll Build**:

- Interactive data visualizations with pandas and matplotlib
- Performance benchmarks using `%%time` magic commands
- A configured notebook environment for the course

### 2. 02_lancedb.ipynb

**Purpose**: Implement and compare different retrieval strategies using LanceDB

**What You'll Learn**:

- Creating vector embeddings with OpenAI
- Building inverted indices for full-text search
- Implementing hybrid search combining multiple strategies
- Applying Cohere reranking for result improvement
- When to use each search approach

**What You'll Build**:

- A LanceDB table with document embeddings
- Three different search implementations (vector, full-text, hybrid)
- A reranking pipeline using Cohere
- Comparative analysis of search approaches

### 3. 03_using_pydantic_evals.ipynb

**Purpose**: Establish systematic evaluation practices for AI systems

**What You'll Learn**:

- Configuring Logfire for result tracking
- Creating evaluation datasets with test cases
- Building custom evaluators for specific metrics
- Saving and loading evaluation datasets
- Tracking performance over time

**What You'll Build**:

- An evaluation framework for LLM classification
- Custom evaluators for your use case
- A reusable evaluation dataset
- Performance tracking dashboard in Logfire

## Key Concepts

- **Vector Search**: Finding semantically similar content using embeddings
- **Full-Text Search**: Traditional keyword-based retrieval using inverted indices
- **Hybrid Search**: Combining vector and full-text approaches for better coverage
- **Reranking**: Using advanced models to reorder initial search results
- **Systematic Evaluation**: Consistent, reproducible measurement of system performance

## Prerequisites

### Knowledge Requirements

- Basic Python programming
- Familiarity with pandas DataFrames
- Understanding of embeddings concept (will be explained)

### Technical Requirements

- Python packages: `jupyter`, `pandas`, `matplotlib`, `lancedb`, `openai`, `tantivy`, `cohere`, `pydantic-evals`
- API keys: OpenAI (for embeddings), Cohere (for reranking), Logfire (for tracking)
- Hardware: No special requirements

## Project Structure

```
week0/
├── README.md
├── 01_using_jupyter_notebooks.ipynb
├── 02_lancedb.ipynb
├── 03_using_pydantic_evals.ipynb
└── assets/
    └── kernel.png
```

## Datasets

- **Sample Sales Data**: Generated within notebooks for pandas practice
- **Document Corpus**: Created in notebooks for search experiments
- **Classification Test Cases**: Built for evaluation framework testing

## Expected Outcomes

After completing this week's materials, you'll have:

1. A fully configured development environment with all necessary tools
2. Hands-on experience with three different search strategies and their trade-offs
3. A reusable evaluation framework for measuring RAG system improvements
4. Clear understanding of when to use vector vs. full-text vs. hybrid search

## Common Issues and Solutions

### Issue 1: Kernel Selection Problems

**Solution**: Check the kernel dropdown in Jupyter and ensure you're using the course virtual environment

### Issue 2: API Key Errors

**Solution**: Verify your `.env` file is properly configured and loaded using `load_dotenv()`

### Issue 3: LanceDB Import Errors

**Solution**: Ensure you've installed all requirements with `uv sync` or `pip install -e .`

## Next Steps

- Complete all three notebooks in order
- Experiment with different search queries to understand retrieval behavior
- Review Week 1 materials on building evaluation foundations
- Join office hours if you have questions about the setup

## Additional Resources

- [LanceDB Documentation](https://lancedb.github.io/lancedb/)
- [Jupyter Notebook Tips & Tricks](https://www.dataquest.io/blog/jupyter-notebook-tips-tricks-shortcuts/)
- [Understanding Vector Embeddings](https://www.pinecone.io/learn/vector-embeddings/)
- [Pydantic Evals Documentation](https://docs.pydantic.dev/latest/)

---

## **Note**: This week's content is foundational. Take time to understand each concept thoroughly as they'll be used extensively throughout the course.

--8<--
"snippets/enrollment-button.md"
--8<--

---
