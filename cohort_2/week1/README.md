# Week 1: Building Your RAG Evaluation Foundation

## Notebooks Overview

### 1. synthetic_questions.ipynb

This notebook focuses on creating diverse, realistic test questions to evaluate your RAG system.

**What You'll Do:**

- Load the Bird-Bench dataset of SQL queries as sample documents
- Define Pydantic models (`Chunk`, `Question`, `ChunkEval`) for structured data
- Generate diverse synthetic questions with varying complexity using GPT models
- Implement asynchronous processing with rate limiting for efficient generation
- Apply randomized constraints to ensure question diversity
- Create a test dataset that challenges your retrieval system

You'll leave with a robust set of synthetic questions that serve as your evaluation benchmark.

### 1. synthetic_questions_modal.ipynb

This notebook introduces a practical approach to evaluating RAG systems through synthetic data generation.

**What You'll Do**:

- Learn why retrieval metrics are more efficient than content generation metrics
- Set up an open-source model (Qwen-2.5-7B-Instruct) via Modal for cost-effective evaluation
- Define Pydantic models for structured data output with instructor using vLLM
- Load and analyze the Bird-Bench Text-2-SQL dataset for challenging examples
- Create a comprehensive evaluation dataset using Pydantic-Evals

You'll leave with both a set of synthetic questions for benchmarking and the knowledge to deploy and use open-source models for cost-effective RAG evaluation.

### 2. benchmark_retrieval.ipynb

This notebook creates a systematic framework for comparing different retrieval strategies.

**What You'll Do:**

- Set up LanceDB with multiple embedding models for comparison
- Implement key retrieval metrics (recall@k, MRR@k)
- Create a parameterized retrieval function supporting different strategies
- Benchmark multiple approaches:
  - Different embedding models
  - Vector vs. hybrid search
  - With and without reranking
- Use Braintrust to track and compare experiment results
- Run parallel evaluations with `concurrent.futures`

You'll establish an objective way to measure which retrieval approaches work best.

### 3. visualise_results.ipynb

This notebook introduces statistical validation to verify that improvements are significant.

**What You'll Do:**

- Implement bootstrapping to simulate multiple experimental runs
- Calculate confidence intervals for different retrieval metrics
- Visualize confidence intervals with error bars
- Perform t-tests to determine statistical significance between approaches
- Make data-driven decisions about which improvements to implement

You'll gain the ability to distinguish real improvements from random variation.

## Technical Requirements

- Required libraries: pandas, numpy, matplotlib, openai, instructor, lancedb, braintrust, scipy
- Bird-Bench dataset from "567-labs/bird-rag"
- OpenAI API access for question generation
- Braintrust account for experiment tracking

## Why These Notebooks Matter

Together, these notebooks provide a complete evaluation framework for RAG systems:

1. Generate challenging test questions
2. Measure retrieval performance objectively
3. Verify that improvements are statistically significant

This approach ensures you invest in retrieval techniques that provide measurable value rather than randomly trying different approaches. The evaluation framework you build here will guide all future RAG improvements in this course.

---

--8<--
  "snippets/enrollment-button.md"
--8<--

---

