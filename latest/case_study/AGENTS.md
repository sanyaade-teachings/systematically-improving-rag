# Case Study: Systematically Improving RAG - AGENTS.md

## Overview

Comprehensive case study demonstrating systematic identification and solution of alignment problems in RAG systems. Uses real WildChat dataset to show how different query strategies lead to dramatically different retrieval performance, with concrete solutions through intelligent system design.

## Build/Test Commands

- Install dependencies: `uv install` or `pip install -e .`
- Load data: `uv run python main.py load-wildchat --limit 100`
- Run tests: `pytest` (if tests exist)
- Code quality: `uv run ruff check --fix --unsafe-fixes .` && `uv run ruff format .`
- Check status: `uv run python main.py stats`

## Architecture & Structure

- **main.py**: CLI interface using `typer` + `rich` for all operations
- **core/**: Core functionality modules (db, embeddings, evaluation, summarization, queries)
- **pipelines/**: High-level pipeline scripts (setup, generation, indexing, evaluation)
- **teaching/**: Documentation with step-by-step tutorials (part01-part04)
- **data/**: Generated data (SQLite DB, JSON results, embeddings, ChromaDB)
- **config.py**: Configuration settings and constants

## Key Technologies

- **Database**: SQLite for structured data, ChromaDB for vector storage
- **Embeddings**: OpenAI text-embedding-3-small/large, Sentence-transformers
- **Reranking**: Cohere rerank-english-v3.0, SentenceTransformers cross-encoders
- **CLI**: Typer with Rich for console output
- **Data Processing**: Pandas, NumPy, Datasets (HuggingFace)
- **Evaluation**: Custom recall@k metrics, comprehensive result storage

## Code Style & Conventions

- **CLI patterns**: Use `typer` with `rich.console` for user-friendly output
- **Async preferred**: Use async/await patterns throughout
- **Database operations**: SQLModel for ORM, comprehensive result storage
- **Error handling**: Graceful failures with informative error messages
- **Logging**: Detailed logging for debugging and analysis
- **Console output**: Use text indicators ("Success:", "Error:", "Warning:")

## Core Concepts

- **Alignment Problem**: Query generation vs embedding strategy misalignment (50% performance gap)
- **Query Strategies**: v1 (content-focused), v2 (pattern-focused)
- **Embedding Strategies**: First-message, full-conversation, summaries (v1-v5)
- **Summary Techniques**: v1 (search-optimized), v3 (balanced), v4 (pattern-optimized), v5 (hybrid)
- **Reranking**: Cohere and SentenceTransformers rerankers with different candidate counts
- **Evaluation Framework**: Comprehensive recall@k metrics with full result storage

## CLI Commands Reference

### Data Management

- `uv run python main.py load-wildchat --limit 1000`: Load conversations
- `uv run python main.py stats`: View database statistics

### Generation

- `uv run python main.py generate-questions --version v1 --limit 1000`: Generate content queries
- `uv run python main.py generate-questions --version v2 --limit 1000`: Generate pattern queries
- `uv run python main.py generate-summaries --versions v1,v3,v4,v5 --limit 1000`: Generate summaries

### Embedding Creation

- `uv run python main.py embed-conversations --embedding-model text-embedding-3-small`: Embed conversations
- `uv run python main.py embed-summaries --technique v5 --embedding-model text-embedding-3-small`: Embed summaries

### Evaluation

- `uv run python main.py evaluate --question-version v1 --embedding-model text-embedding-3-small`: Basic evaluation
- `uv run python main.py evaluate --question-version v2 --embedding-model text-embedding-3-small --target-type summary --target-technique v4 --reranker cohere/rerank-english-v3.0 --reranker-n 60`: Advanced evaluation with reranking

## Expected Performance Results

- **v1 queries on first messages**: ~55-62% Recall@1 (good alignment)
- **v2 queries on first messages**: ~11-12% Recall@1 (poor alignment)
- **v5 summaries**: 82.0% v1, 55.0% v2 (optimized hybrid approach)
- **Reranking improvement**: Modest gains (alignment matters more than reranking)

## Database Schema

- **conversation**: Main conversation data with metadata
- **question**: Generated questions (v1/v2) linked to conversations
- **summary**: Generated summaries using different techniques (v1-v5)
- **evaluation**: Aggregated evaluation metrics
- **evaluationresult**: Detailed results for every query with full context

## Key Learning Outcomes

- **Alignment Problem**: Understanding and diagnosing query/embedding misalignment
- **Systematic Evaluation**: Comprehensive metrics and result storage
- **Iterative Improvement**: RAG Flywheel methodology in practice
- **Trade-off Analysis**: Performance vs storage vs compute cost decisions
- **Production Insights**: Real-world considerations for RAG deployment
