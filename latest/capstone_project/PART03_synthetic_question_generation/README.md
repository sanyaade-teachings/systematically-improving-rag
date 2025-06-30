# Synthetic Query Generation

A modular system for generating and evaluating synthetic search queries from WildChat conversations. This project demonstrates how different prompting strategies dramatically affect RAG system performance.

## Overview

This system provides:
- **Two query generation strategies**: V1 (search-focused) and V2 (pattern-focused)
- **Recall verification**: Test how well generated queries retrieve their source conversations
- **Modular architecture**: Easy to extend with new generation strategies
- **CLI interface**: Simple commands for generation, verification, and analysis

## Key Insights

Our experiments show that prompt design is critical:
- **V1 (Search-focused)**: 35.4% recall@1, 60.4% recall@10
- **V2 (Pattern-focused)**: 2.5% recall@1, 9.2% recall@10

The dramatic difference occurs because we embed only the first user message, and V1 generates queries that match natural search behavior while V2 generates abstract categorizations.

See [COMMENTARY.md](COMMENTARY.md) for detailed analysis.

## Installation

1. Install dependencies:
   ```bash
   pip install instructor rich diskcache pydantic asyncio
   ```

2. Set up environment:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Quick Start

```bash
# Generate synthetic queries (both v1 and v2)
./main.py generate --limit 100

# Generate only v1 queries with dry run
./main.py generate --limit 50 --version v1 --dry-run

# Generate sample queries for testing
./main.py generate --limit 10 --sample

# Verify recall for all queries
./main.py verify

# Verify recall for v1 queries and export results
./main.py verify --version v1 --export results.json

# Show database statistics
./main.py stats
```

## Architecture

```
PART03_synthetic_question_generation/
├── src/
│   ├── processors/          # Query generation strategies
│   │   ├── base.py         # Abstract base class
│   │   ├── v1_search.py    # Search-focused generation
│   │   └── v2_pattern.py   # Pattern-focused generation
│   ├── storage/            # Data persistence
│   │   ├── database.py     # SQLite operations
│   │   └── cache.py        # Disk cache management
│   ├── cli/                # Command implementations
│   │   ├── generate.py     # Generate queries command
│   │   └── verify.py       # Verify recall command
│   └── config.py           # Configuration management
├── data/                   # Git-ignored data directory
│   ├── cache/              # Query generation cache
│   ├── cache_recall/       # Recall verification cache
│   └── databases/          # SQLite databases
├── notebooks/              # Jupyter notebooks
├── tests/                  # Unit tests
└── main.py                # CLI entry point
```

## Command Reference

### Generate Command

Generate synthetic queries from conversations:

```bash
./main.py generate [options]
```

Options:
- `--limit N`: Number of conversations to process (default: 500)
- `--version {v1,v2,all}`: Which processor to use (default: all)
- `--batch-size N`: Database batch size (default: 100)
- `--max-concurrent N`: Max concurrent API requests (default: 10)
- `--model MODEL`: Model to use (default: openai/gpt-4o-mini)
- `--clear-cache`: Clear cache before starting
- `--dry-run`: Run without saving to database
- `--sample`: Generate samples (ignores already processed)
- `--data-dir PATH`: Override data directory location

### Verify Command

Verify recall of generated queries:

```bash
./main.py verify [options]
```

Options:
- `--limit N`: Limit queries to verify
- `--version {v1,v2,all}`: Which version to verify (default: all)
- `--update-interval N`: Update metrics every N queries (default: 50)
- `--use-local`: Use local ChromaDB instead of cloud
- `--export PATH`: Export results to JSON file
- `--data-dir PATH`: Override data directory location

### Stats Command

Show database statistics:

```bash
./main.py stats [options]
```

## Database Schema

### synthetic_queries table
- `id`: Primary key (auto-increment)
- `conversation_hash`: Hash of source conversation
- `prompt_version`: Version used (v1 or v2)
- `query`: Generated search query
- `chain_of_thought`: Generation reasoning
- `created_at`: Timestamp
- `metadata`: Additional metadata (JSON)

### processed_conversations table
- `conversation_hash`: Primary key
- `processed_at`: Timestamp
- `versions_processed`: Comma-separated versions

## Configuration

Configuration via environment variables:
- `SQ_BATCH_SIZE`: Database batch size (default: 100)
- `SQ_MAX_CONCURRENT`: Max concurrent requests (default: 10)
- `SQ_UPDATE_INTERVAL`: Metric update interval (default: 50)
- `SQ_MODEL_NAME`: Model to use (default: openai/gpt-4o-mini)
- `SQ_USE_CLOUD_CHROMADB`: Use cloud ChromaDB (default: true)

## Extending the System

To add a new query generation strategy:

1. Create a new processor in `src/processors/`
2. Inherit from `BaseProcessor`
3. Implement `process()`, `version`, and `description` properties
4. Import in `src/processors/__init__.py`
5. Add to CLI in `src/cli/generate.py`

Example:
```python
from .base import BaseProcessor, SearchQueries

class MyProcessor(BaseProcessor):
    @property
    def version(self) -> str:
        return "v3"
    
    @property
    def description(self) -> str:
        return "My custom query generation approach"
    
    async def process(self, messages: List[Dict[str, Any]]) -> SearchQueries:
        # Your implementation here
        pass
```

## Performance

- Concurrent processing with configurable limits
- Disk caching to avoid redundant API calls
- Batch database operations
- Progress tracking with live updates
- Typical processing: ~100-200 conversations/minute