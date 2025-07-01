# AGENT.md - Capstone Project Development Guide

## Build/Test/Lint Commands
- **Run tests**: `pytest` or `pytest tests/test_specific.py` for single test file
- **Lint**: `ruff check .` or `ruff check path/to/file.py` for specific files  
- **Format**: `black .` or `black path/to/file.py` for specific files
- **Install**: `uv pip install -e .` (preferred) or `pip install -e .`

## Architecture & Structure
- **RAG system** with WildChat dataset processing across 4 main parts
- **PART01**: Jupyter notebook for data exploration (`PART01_exploring_wildchat.ipynb`)
- **PART02**: Vector DB loaders (ChromaDB, LanceDB, Turbopuffer) in `PART02_loading_data_into_db/`
- **PART03**: Synthetic query generation pipeline in `PART03_synthetic_question_generation/`
- **PART04**: Summarization functionality in `PART04_summarization/`
- **utils/**: Shared utilities including dataloader and DAO interfaces
- **tests/**: Test suite with pytest fixtures and async test support

## Code Style & Conventions
- Use **type hints** everywhere (Pydantic models for validation)
- **Async/await** patterns for DB operations (see DAO base classes)
- **ABC/abstract methods** for database interfaces (`utils/dao/wildchat_dao.py`)
- **Docstrings** in Google style with Args/Returns sections
- **Import order**: stdlib, third-party, local imports
- **Error handling**: Silent failures in data processing, proper exceptions in APIs
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Environment**: Use `.env` file for config (copy from `.env.example`)

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
