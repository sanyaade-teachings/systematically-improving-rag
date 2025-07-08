# Latest Course Content - AGENTS.md

## Overview
This directory contains the current version of the "Systematically Improving RAG Applications" course with weekly modules, case studies, and hands-on implementations. The content follows the RAG Flywheel methodology: Measure → Analyze → Improve → Iterate.

## Build/Test Commands
- Install dependencies: `uv install` or `pip install -e .`
- Run notebooks: `jupyter notebook` or `jupyter lab`
- Package management: Always use `uv` instead of `pip` (e.g., `uv add <package>`)
- Case study CLI: `uv run python main.py --help` (in case_study/)

## Directory Structure
- **week0/**: Getting started (Jupyter, LanceDB, pydantic-evals)
- **week1/**: RAG evaluation foundations (synthetic questions, benchmarking, visualization)
- **week2/**: Embedding fine-tuning (Cohere, open-source models, synthetic transactions)
- **week4/**: Query understanding (topic modeling, classification, BERTopic)
- **week5/**: Multimodal & structured data (PDFs, metadata filtering, Text-to-SQL)
- **week6/**: Architecture & product integration (tool evaluation, performance optimization)
- **case_study/**: Complete RAG system implementation with WildChat dataset
- **extra_kura/**: Additional advanced notebooks

## Technologies Used
- **Vector Databases**: LanceDB, ChromaDB, Turbopuffer
- **LLM APIs**: OpenAI, Anthropic, Cohere
- **ML Frameworks**: Sentence-transformers, BERTopic, Transformers
- **Evaluation**: Braintrust, Pydantic-evals, Logfire
- **Data Processing**: Pandas, NumPy, Datasets (HuggingFace)
- **Visualization**: Matplotlib, Seaborn
- **Database**: SQLite, SQL operations

## Code Style & Conventions
- **Educational focus**: Write at 9th-grade reading level
- **Jupyter notebooks**: Educational markdown between code sections
- **Async preferred**: Use async/await patterns when possible
- **CLI tools**: Use `typer` + `rich` for command-line interfaces
- **Console output**: Use `rich.console` with text indicators ("Success:", "Error:", "Warning:")
- **Package management**: Always use `uv` instead of `pip`
- **Helper functions**: Common utilities in `helpers.py` files (MRR, recall calculations)

## Key Learning Patterns
- **RAG Flywheel**: Systematic improvement through measurement and iteration
- **Synthetic data generation**: Cold-start problem solving with generated questions
- **Evaluation-first approach**: Measure before and after every change
- **Progressive complexity**: Each week builds on previous concepts
- **Real-world datasets**: WildChat, HuggingFace datasets for practical experience
- **Production considerations**: Cost, latency, storage trade-offs

## File Types & Conventions
- **Jupyter notebooks**: `.ipynb` files with educational content and code
- **Helper modules**: `helpers.py` with utility functions
- **Configuration files**: `config.yml`, `categories.yml`, `taxonomy.yml`
- **Data files**: JSON, YAML, SQL files for queries and configurations
- **README files**: Overview and setup instructions for each week

## Common Implementation Patterns
- **Evaluation metrics**: Recall@k, MRR, precision calculations
- **Embedding workflows**: Generate embeddings → Store in vector DB → Retrieve → Evaluate
- **Query generation**: Synthetic question creation with different strategies (v1, v2)
- **Fine-tuning pipelines**: Custom embedding models for specific domains
- **Topic modeling**: BERTopic for query pattern analysis
- **Multimodal integration**: PDF parsing, image processing, structured data
</synth>

## Expected Learning Outcomes
By completing this course, students will:
- Understand the RAG improvement flywheel methodology
- Build evaluation frameworks for RAG systems
- Implement synthetic data generation for cold-start problems
- Fine-tune embedding models for specific domains
- Analyze query patterns and user behavior
- Integrate multimodal data effectively
- Build production-ready RAG architectures
- Optimize performance and cost trade-offs
