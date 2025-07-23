# Week 1: Building Your RAG Evaluation Foundation

## Overview

This week establishes the fundamental evaluation framework needed to systematically improve RAG applications. Rather than randomly trying different retrieval techniques and hoping for improvement, you'll build a rigorous testing framework that measures performance objectively. This approach ensures every change you make is backed by data, not intuition.

The evaluation framework consists of three essential components: synthetic question generation for creating challenging test cases, benchmarking tools for measuring retrieval performance across different approaches, and statistical validation to ensure improvements are real rather than random variation. Together, these create a scientific approach to RAG improvement that will guide all future optimization efforts in this course.

## Learning Objectives

By the end of this week, you'll be able to:

- Generate diverse, realistic synthetic questions that challenge your RAG system
- Implement key retrieval metrics (recall@k, MRR@k) to measure performance objectively
- Compare multiple retrieval strategies using controlled experiments
- Apply statistical methods to verify that improvements are significant
- Deploy open-source models for cost-effective evaluation at scale
- Track and visualize experiment results using modern ML tools

## Notebooks

### 1. synthetic_questions.ipynb

**Purpose**: Create diverse, realistic test questions to evaluate your RAG system comprehensively

**What You'll Learn**:

- How to structure evaluation data using Pydantic models
- Techniques for generating diverse synthetic questions with GPT models
- Asynchronous processing patterns with rate limiting
- Methods to ensure question variety through randomized constraints

**What You'll Build**:

- A complete synthetic question generation pipeline
- Structured evaluation dataset with questions of varying complexity
- Reusable models for chunk and question evaluation

### 2. synthetic_questions_modal.ipynb

**Purpose**: Deploy open-source models for cost-effective synthetic data generation at scale

**What You'll Learn**:

- Why retrieval metrics provide more efficient evaluation than generation metrics
- How to deploy open-source models (Qwen-2.5-7B-Instruct) using Modal
- Structured output generation with instructor and vLLM
- Working with challenging datasets like Bird-Bench Text-2-SQL

**What You'll Build**:

- A Modal deployment for scalable question generation
- Cost-effective evaluation pipeline using open-source models
- Comprehensive evaluation dataset with Pydantic-Evals

### 3. benchmark_retrieval.ipynb

**Purpose**: Create a systematic framework for comparing and measuring different retrieval strategies

**What You'll Learn**:

- Implementation of key retrieval metrics (recall@k, MRR@k)
- How to set up controlled experiments with multiple variables
- Experiment tracking and comparison using Braintrust
- Parallel evaluation techniques for faster benchmarking

**What You'll Build**:

- A parameterized retrieval system supporting multiple strategies
- Comprehensive benchmarking framework with LanceDB
- Experiment tracking pipeline for reproducible results

### 4. visualise_results.ipynb

**Purpose**: Apply statistical validation to verify that retrieval improvements are significant

**What You'll Learn**:

- Bootstrapping techniques for simulating experimental variation
- Confidence interval calculation and interpretation
- Statistical significance testing with t-tests
- Data visualization for comparing approaches

**What You'll Build**:

- Statistical validation pipeline for experiments
- Visualization tools for confidence intervals
- Framework for making data-driven decisions

## Key Concepts

- **Synthetic Question Generation**: Creating realistic test questions that challenge retrieval systems without manual annotation
- **Retrieval Metrics**: Quantitative measures like recall@k and MRR@k that objectively assess retrieval quality
- **Statistical Validation**: Using bootstrapping and significance tests to ensure improvements aren't due to random chance
- **Experiment Tracking**: Systematic recording and comparison of different approaches using tools like Braintrust
- **Asynchronous Processing**: Efficient parallel execution for faster evaluation cycles

## Prerequisites

### Knowledge Requirements

- Basic understanding of embeddings and vector search
- Familiarity with Python async/await patterns
- Elementary statistics concepts (mean, standard deviation, confidence intervals)

### Technical Requirements

- Python packages: `pandas`, `numpy`, `matplotlib`, `openai`, `instructor`, `lancedb`, `braintrust`, `scipy`, `modal`
- API keys: OpenAI API access for question generation
- Accounts: Braintrust account for experiment tracking, Modal account (optional)
- Hardware: No GPU required

## Project Structure

```text
week1/
├── README.md
├── synthetic_questions.ipynb
├── synthetic_questions_modal.ipynb
├── benchmark_retrieval.ipynb
├── visualise_results.ipynb
├── data/
│   ├── bird-bench/          # SQL query dataset
│   └── synthetic_questions/ # Generated questions
└── results/                 # Experiment outputs
```

## Datasets

- **Bird-Bench**: A challenging dataset of SQL queries and database schemas from "567-labs/bird-rag", used as source documents for generating synthetic questions
- **Synthetic Questions**: Generated dataset of diverse questions targeting different retrieval challenges

## Expected Outcomes

After completing this week's materials, you'll have:

1. A robust synthetic question generation pipeline producing hundreds of diverse test cases
2. A comprehensive benchmarking framework comparing multiple retrieval strategies
3. Statistical validation tools proving which improvements are significant
4. Clear performance metrics showing baseline retrieval capabilities
5. Experience with modern ML experiment tracking and visualization

## Common Issues and Solutions

### Issue 1: Rate limiting when generating synthetic questions

**Solution**: Implement exponential backoff and use the provided async rate limiting patterns. Consider using Modal deployment for higher throughput.

### Issue 2: Inconsistent results between benchmark runs

**Solution**: Ensure you're using the same random seed for reproducibility. Check that your evaluation dataset hasn't changed between runs.

### Issue 3: Statistical tests showing no significant differences

**Solution**: Increase your sample size or ensure your test cases are sufficiently challenging to reveal performance differences.

## Next Steps

- Complete all notebooks in order (synthetic questions → benchmarking → visualization)
- Review Week 2 on fine-tuning to understand how baseline metrics guide improvement efforts
- Experiment with different question generation prompts to create even more challenging test cases

## Additional Resources

- [Information Retrieval Metrics](<https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)>)
- [Braintrust Documentation](https://www.braintrust.dev/docs)
- [Modal Platform Guide](https://modal.com/docs/guide)
- [Statistical Significance in ML](https://arxiv.org/abs/1904.10922)

---

**Note**: Ensure you've completed all prerequisites before starting these notebooks. Each notebook builds on previous concepts, and the evaluation framework created here is essential for all subsequent weeks.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
