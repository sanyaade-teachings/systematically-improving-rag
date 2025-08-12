# Week 0: Foundation and Environment Setup

## Notebooks Overview

### 1. Using Jupyter Notebooks.ipynb

This notebook introduces the fundamental tool you'll use throughout the course: Jupyter Notebooks.

**What You'll Do:**

- Run basic Python code in interactive cells
- Execute shell commands directly within notebooks
- Create and visualize pandas DataFrames with sample sales data
- Learn about kernels and how to select the right one (using kernel.png as reference)
- Use magic commands like `%%time` to measure performance
- Configure the `autoreload` extension for smoother development

This hands-on introduction ensures you're comfortable with the notebook environment before diving into more complex RAG concepts.

### 2. LanceDB.ipynb

This notebook introduces vector databases with LanceDB, a crucial component for building RAG systems.

**What You'll Do:**

- Define schemas with Pydantic for consistent data structures
- Create and populate LanceDB tables with document data
- Implement three key search strategies:
  1. Vector search using OpenAI embeddings
  2. Full-text search with inverted indices via tantivy
  3. Hybrid search combining both approaches
- Apply Cohere reranking to improve result quality
- Compare search results for different query types
- Analyze when each search approach performs best

You'll gain hands-on experience with the retrieval foundations that power all RAG applications.

### 3. Using Pydantic Evals.ipynb

This notebook introduces Pydantic Evals, a framework for systematically evaluating AI systems and tracking results.

**What You'll Do:**

- Configure Logfire for tracking evaluation results
- Create your first evaluation with test cases, datasets, and evaluators
- Build custom evaluators to assess model outputs
- Evaluate an LLM-based classification system for customer queries
- Save and load evaluation datasets for consistent testing
- Track performance metrics across different test cases

You'll establish a foundation for systematically measuring model performance, which is essential for improving RAG systems throughout the course.

## Technical Requirements

- Python 3.9
- Required libraries: pandas, matplotlib, lancedb, openai, tantivy, cohere
- API keys for OpenAI (embeddings) and Cohere (reranking)

## Why These Notebooks Matter

These notebooks provide the essential tools and concepts you'll use throughout the course. The Jupyter environment will be your workspace for all experiments, while LanceDB introduces the vector search capabilities that form the backbone of RAG systems. Mastering these fundamentals prepares you for systematic RAG improvement in the following weeks.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
