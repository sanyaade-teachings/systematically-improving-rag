# Case Study: RAG System Analysis

This case study analyzes conversation data from the WildChat dataset to improve RAG (Retrieval-Augmented Generation) systems.

## Getting Started

### 1. Load Data into Local SQLite Database

**First, you need to load the WildChat dataset into a local SQLite database.**

Run the CLI command to download and load the data:

```bash
uv run main.py
```

This will:
- Download the WildChat-1M dataset from HuggingFace
- Process 10,000 conversations by default
- Create a SQLite database at `data/db.sqlite`
- Load conversation data with proper error handling for duplicates

**Expected output:**
- Progress updates every 100 conversations processed
- Final count of successfully inserted conversations (typically ~9,930 out of 10,000 due to duplicates)
- Database file size: ~101 MB

### 2. Verify Data Loading

You can verify the data was loaded correctly using SQLite:

```bash
# Check table structure
sqlite3 data/db.sqlite "SELECT name FROM sqlite_master WHERE type='table';"

# Check conversation count
sqlite3 data/db.sqlite "SELECT COUNT(*) FROM conversation;"

# View sample data
sqlite3 data/db.sqlite "SELECT conversation_hash, language, country FROM conversation LIMIT 5;"
```

## Database Schema

The SQLite database contains the following tables:

- **conversation**: Main conversation data with hash, text, language, country, timestamps
- **question**: Generated questions for evaluation
- **summary**: Generated summaries using different techniques  
- **evaluation**: Evaluation results and metrics

## Next Steps

After loading the data, you can:
- Explore the conversation data distribution
- Generate synthetic questions for evaluation
- Create summaries using different techniques
- Run evaluation pipelines
- Analyze results and improve the RAG system

## Configuration

Database path and other settings can be configured in `config.py`. 
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
