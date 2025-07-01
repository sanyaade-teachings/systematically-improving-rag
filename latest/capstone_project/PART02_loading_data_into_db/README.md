# PART02: Loading Data into Vector Databases

Scripts that load WildChat conversations into different vector databases for experimentation and comparison.

## Overview

This part demonstrates how to load conversational data into three popular vector databases:
- **ChromaDB**: Simple, lightweight, embedded database
- **LanceDB**: Columnar database with advanced indexing
- **Turbopuffer**: High-performance cloud-native solution

## Key Implementation Detail

**Important**: These scripts only embed the **first message** of each conversation, not the entire conversation. This is intentionally simplified and not what you'd typically do in practice, but it serves as a critical learning example for PART03's evaluation experiments.

This design choice will reveal important lessons about:
- The impact of embedding strategy on retrieval performance
- How query types must align with what's actually embedded
- Why understanding your data structure is crucial for RAG success

## Scripts

### Data Loaders
- `load_to_chromadb.py` - Loads data into ChromaDB
- `load_to_lancedb.py` - Loads data into LanceDB  
- `load_to_turbopuffer.py` - Loads data into Turbopuffer

### Each Loader Performs
1. **Data Reading**: Loads conversations from the prepared SQLite database
2. **Embedding Generation**: Creates embeddings for just the first message using OpenAI
3. **Storage**: Inserts embeddings and metadata into the vector database
4. **Verification**: Runs a test search query to confirm successful loading

## Usage

Load data into each database:

```bash
# ChromaDB (local storage)
python load_to_chromadb.py

# LanceDB (local storage with columnar format)
python load_to_lancedb.py

# Turbopuffer (requires API key)
export TURBOPUFFER_API_KEY="your-key"
python load_to_turbopuffer.py
```

## Database Comparison

### ChromaDB
- **Pros**: Easy setup, no dependencies, good for prototyping
- **Cons**: Limited scalability, fewer advanced features
- **Best for**: Local development, small datasets

### LanceDB
- **Pros**: Columnar storage, efficient queries, built-in versioning
- **Cons**: Larger storage footprint, more complex API
- **Best for**: Analytics workloads, time-series data

### Turbopuffer
- **Pros**: Blazing fast, cloud-native, automatic scaling
- **Cons**: Requires API key, cloud dependency
- **Best for**: Production systems, large-scale applications

## Configuration

Each script uses environment variables:
```bash
# Required
OPENAI_API_KEY="your-openai-key"

# Optional (for Turbopuffer)
TURBOPUFFER_API_KEY="your-turbopuffer-key"

# Data location
SQLITE_DB_PATH="path/to/wildchat.db"  # Defaults to local file
```

## What's Actually Stored

For each conversation, we store:
- **Vector**: 1536-dimensional embedding of the first message
- **Metadata**:
  - `conversation_id`: Unique identifier
  - `language`: Language of the conversation
  - `model`: Which GPT model was used
  - `turn_count`: Number of messages in conversation
  - `first_message`: The actual text (for debugging)

## Important Lessons

1. **Embedding Strategy Matters**: We only embed first messages, which will dramatically affect what queries can successfully retrieve conversations

2. **Metadata is Crucial**: Store enough information to filter and understand results

3. **Test Your Pipeline**: Each script includes a test query to verify the setup

4. **Database Choice Affects Architecture**: Consider scalability, features, and operational complexity

## Next Steps

After loading data, proceed to:
- **PART03**: Generate synthetic queries and discover how embedding strategy affects retrieval
- **PART04**: Learn how summarization can align embeddings with different query types

The intentionally simplified embedding approach (first message only) sets up important learning opportunities in the next parts about alignment between queries and embeddings.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
