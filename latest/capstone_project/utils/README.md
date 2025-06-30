# WildChat Data Loaders

CLI tools for loading WildChat-1M conversation data into various vector databases.

## Overview

This suite provides three data loaders for ingesting WildChat data into different vector databases:
- **ChromaDB** - For local or cloud-based vector search
- **LanceDB** - For local or cloud-based vector search with embedded compute
- **Turbopuffer** - For cloud-based vector search with full-text capabilities

## Prerequisites

1. Install dependencies:
```bash
uv pip install -r requirements.txt
```

2. Set up environment variables in `.env` file for cloud deployments:

### ChromaDB Cloud
```bash
CHROMA_API_KEY=your_api_key
CHROMA_TENANT=your_tenant
CHROMA_DATABASE=your_database
```

### LanceDB Cloud
```bash
LANCEDB_API_KEY=your_api_key
LANCEDB_URI=your_uri
```

### Turbopuffer
```bash
TURBOPUFFER_API_KEY=your_api_key
TURBOPUFFER_REGION=gcp-us-central1  # optional, defaults to gcp-us-central1
```

## Usage

### ChromaDB

Load data to local ChromaDB:
```bash
python utils/load_to_chromadb.py
```

Load data to ChromaDB Cloud:
```bash
python utils/load_to_chromadb.py --cloud
```

### LanceDB

Load data to local LanceDB:
```bash
python utils/load_to_lancedb.py
```

Load data to LanceDB Cloud:
```bash
python utils/load_to_lancedb.py --cloud
```

### Turbopuffer

Load data to Turbopuffer (cloud only):
```bash
python utils/load_to_turbopuffer.py
```

## CLI Options

All loaders support the following options:

| Option | Default | Description |
|--------|---------|-------------|
| `--limit` | 2000 | Maximum number of records to load |
| `--batch-size` | 25 | Number of records to process in each batch |
| `--language` | English | Filter conversations by language |
| `--min-length` | 30 | Minimum message length to include |
| `--reset` | False | **Delete existing data** before loading new data |

### Cloud Options

ChromaDB and LanceDB support:
- `--cloud` - Use cloud storage instead of local persistence

### Database-specific Options

ChromaDB:
- `--collection-name` - Name of the ChromaDB collection (default: wildchat_2k)

LanceDB:
- `--table-name` - Name of the LanceDB table (default: wildchat_2k)

Turbopuffer:
- `--namespace-name` - Name of the Turbopuffer namespace (default: wildchat_2k)

## Examples

### Load 5000 English conversations to ChromaDB Cloud with reset
```bash
python utils/load_to_chromadb.py --cloud --limit 5000 --reset
```

### Load 1000 Spanish conversations to local LanceDB
```bash
python utils/load_to_lancedb.py --limit 1000 --language Spanish
```

### Load data to Turbopuffer with larger batch size
```bash
python utils/load_to_turbopuffer.py --batch-size 50 --reset
```

## Important Notes

- The `--reset` flag will **delete all existing data** in the target collection/table/namespace before loading new data
- All loaders use the `sentence-transformers/all-MiniLM-L6-v2` model for generating embeddings
- Data is filtered to exclude toxic conversations by default
- Each loader provides progress tracking and performance metrics
- After loading, each tool performs a test query to verify the data was loaded correctly

## Data Schema

All loaders store the following fields:
- `id` - Unique conversation hash
- `text` - First message of the conversation (embedded)
- `hash` - Conversation hash
- `timestamp` - Conversation timestamp
- `language` - Conversation language
- `model_name` - Model used in conversation
- `conversation_length` - Number of turns
- `country` - User's country
- `toxic` - Whether conversation contains toxic content
- `redacted` - Whether conversation was redacted
- `turn` - Turn number in conversation

Turbopuffer additionally stores:
- `conversation_history` - Formatted full conversation
- `conversation_summary` - Brief summary for better search