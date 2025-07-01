# Capstone Project - Systematically Improving RAG

A project focused on systematically improving Retrieval-Augmented Generation (RAG) systems using the WildChat dataset.

All of this material is supported by the **Systematically Improving RAG Course**. [**Click here to get 20% off →**](https://maven.com/applied-llms/rag-playbook?promoCode=EBOOK)

## Getting Started

### Prerequisites

- Python 3.9+
- uv (recommended) or pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd capstone_project
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in editable mode:
```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Project Structure

```
capstone_project/
├── .env                                # Environment variables (create from .env.example)
├── .env.example                        # Example environment variables template
├── pyproject.toml                      # Package configuration
├── README.md                           # This file
│
├── PART01_exploring_wildchat.ipynb     # Initial data exploration notebook
│
├── PART02_loading_data_into_db/        # Data loading into various vector databases
│   ├── load_to_chromadb.py            # ChromaDB loader script
│   ├── load_to_lancedb.py             # LanceDB loader script
│   ├── load_to_turbopuffer.py         # Turbopuffer loader script
│   └── logs/                          # Loading logs directory
│
├── PART03_synthetic_question_generation/  # Synthetic query generation pipeline
│   ├── README.md                      # Part 3 documentation
│   ├── extraction_pipeline.py         # Main extraction pipeline
│   ├── generate_synthetic_queries.py  # Query generation script
│   ├── processor.py                   # Data processing utilities
│   └── review_examples.ipynb          # Review generated examples
│
├── utils/                              # Shared utility modules
│   ├── __init__.py
│   ├── dataloader.py                  # Data loading utilities
│   └── dao/                           # Data Access Objects
│       ├── __init__.py
│       ├── wildchat_dao.py            # Base DAO interface
│       ├── wildchat_dao_chromadb.py   # ChromaDB implementation
│       └── wildchat_dao_turbopuffer.py # Turbopuffer implementation
│
└── tests/                              # Test suite
    ├── __init__.py
    ├── conftest.py                    # Pytest configuration
    ├── test_dao_chromadb.py           # ChromaDB DAO tests
    ├── test_dao_turbopuffer.py        # Turbopuffer DAO tests
    └── test_processor.py              # Processor tests
```

## Workflow Overview

### Part 1: Data Exploration
Explore the WildChat dataset using the Jupyter notebook to understand the data structure and characteristics.

### Part 2: Loading Data into Vector Databases
Load the WildChat data into different vector databases for experimentation:

```bash
# Load into ChromaDB
python PART02_loading_data_into_db/load_to_chromadb.py

# Load into LanceDB
python PART02_loading_data_into_db/load_to_lancedb.py

# Load into Turbopuffer
python PART02_loading_data_into_db/load_to_turbopuffer.py
```

### Part 3: Synthetic Question Generation
Generate synthetic queries for testing RAG systems:

```bash
python PART03_synthetic_question_generation/generate_synthetic_queries.py
```

## Usage

After installation, you can import utilities from anywhere in your project:

```python
# Import data loading utilities
from utils import dataloader

# Import specific DAO modules
from utils.dao import wildchat_dao

# Import from specific parts
from PART03_synthetic_question_generation import generate_synthetic_queries
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Linting
ruff check .

# Formatting
black .
```

## Environment Variables

The `.env.example` file contains the following configuration options:
- Database connection strings
- API keys for various services
- Configuration parameters

Copy `.env.example` to `.env` and update with your specific values.

## License

MIT

## 📧 Free Email Course

Want to learn more about RAG? Take our free email course and get the latest news and information about RAG techniques and best practices.

[**Sign up for the free RAG Crash Course →**](https://fivesixseven.ck.page/rag-crash-course)

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
