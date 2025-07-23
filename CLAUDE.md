# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an educational course repository for "Systematically Improving RAG Applications" that teaches data-driven approaches to building and improving Retrieval-Augmented Generation (RAG) systems. The repository contains multiple course cohorts, comprehensive documentation, hands-on workshops, and real-world case studies.

## Common Development Commands

### Package Management

- **Install dependencies**: `uv install` or `pip install -e .`
- **Add new packages**: `uv add <package>` (preferred over pip)
- **Sync dependencies**: `uv sync`

### Documentation

- **Local development**: `mkdocs serve` (serves at localhost:8000)
- **Build static site**: `mkdocs build`

### Code Quality

- **Lint and fix**: `uv run ruff check --fix --unsafe-fixes .`
- **Format code**: `uv run ruff format .`

### Running Tests

- **Test runner**: `pytest` (no test files currently in repository)
- **With coverage**: `pytest --cov`

## High-Level Architecture

### Course Structure

The repository follows a progressive learning path organized by cohorts and weeks:

- **latest/**: Current course version with weeks 0-6
- **cohort_1/, cohort_2/**: Previous versions showing course evolution
- **docs/**: MkDocs documentation with workshops, office hours, and talks

### Core RAG Flywheel Philosophy

1. **Measure**: Establish baseline metrics using evaluation frameworks
2. **Analyze**: Identify failure modes and improvement opportunities
3. **Improve**: Implement targeted solutions (embeddings, reranking, etc.)
4. **Iterate**: Continuous improvement based on data

### Key Technologies Stack

- **Vector Databases**: ChromaDB, LanceDB, Turbopuffer
- **LLM APIs**: OpenAI, Anthropic, Cohere
- **Embeddings**: Sentence-transformers, OpenAI text-embedding models
- **Evaluation**: Braintrust, pydantic-evals
- **CLI Framework**: Typer + Rich for command-line interfaces
- **Async Operations**: asyncio, httpx for concurrent processing

### Case Study Architecture (latest/case_study/)

The WildChat case study demonstrates a complete RAG system:

1. **Data Loading**: Processes conversation data from HuggingFace datasets
2. **Question Generation**: Creates synthetic queries for evaluation
3. **Embedding Pipeline**: Multiple strategies (v1-v5) for document processing
4. **Evaluation Framework**: Comprehensive metrics using Braintrust
5. **Reranking**: Cohere and other reranking models for result optimization

### Code Patterns

- **Async-first**: Use async/await for I/O operations
- **CLI Commands**: Typer commands with Rich console output
- **Evaluation-driven**: Always measure before and after changes
- **Modular Design**: Separate concerns (data loading, embedding, evaluation)

## Development Guidelines

### When Working on Workshops

- Each week's workshop corresponds to book chapters
- Notebooks should be educational with clear markdown explanations
- Use the latest/ directory for new content

### When Working on the Case Study

- Follow the existing CLI command structure in main.py
- Use Braintrust for evaluation tracking
- Implement new embedding strategies as v6, v7, etc.
- Always include evaluation metrics for new approaches

### Adding New Features

1. Check existing patterns in latest/case_study/
2. Use async operations for API calls
3. Add CLI commands using Typer decorators
4. Include progress bars with Rich for long operations
5. Store results in appropriate formats (Parquet, JSON)

### Documentation Updates

- Update relevant workshop notebooks
- Add entries to docs/ if creating new tutorials
- Keep markdown conversions in md/ directory synchronized
