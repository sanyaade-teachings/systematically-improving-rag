# ChromaDB Summary Loader

This script loads conversation summaries into ChromaDB using plain ChromaDB client (no DAO wrapper).

## Setup

1. Install dependencies:
```bash
uv add chromadb sentence-transformers python-dotenv rich typer
```

2. Set up environment variables for ChromaDB Cloud (if using cloud):
```bash
export CHROMA_API_KEY="your-api-key"
export CHROMA_TENANT="your-tenant"
export CHROMA_DATABASE="your-database"
```

## Usage

### Basic Usage
Load all v2 summaries to ChromaDB cloud:
```bash
python load_summaries_to_chromadb.py
```

### Local ChromaDB
Use local ChromaDB instead of cloud:
```bash
python load_summaries_to_chromadb.py --local
```

### Load v1 Summaries
Load v1 summaries instead of v2:
```bash
python load_summaries_to_chromadb.py --version v1
```

### Custom Collection Prefix
Specify a custom collection prefix:
```bash
python load_summaries_to_chromadb.py --prefix my-summaries
```

### Limit Number of Summaries
Load only first 1000 summaries:
```bash
python load_summaries_to_chromadb.py --limit 1000
```

### Reset Collection
Delete existing collection before loading:
```bash
python load_summaries_to_chromadb.py --reset
```

### Custom Batch Size
Adjust batch size for loading:
```bash
python load_summaries_to_chromadb.py --batch-size 100
```

## Additional Commands

### List Collections
View all collections in your ChromaDB instance:
```bash
python load_summaries_to_chromadb.py list-collections
```

For local ChromaDB:
```bash
python load_summaries_to_chromadb.py list-collections --local
```

### Delete Collection
Delete a specific collection:
```bash
python load_summaries_to_chromadb.py delete-collection --collection-name wildchat-synthetic-summaries-v2
```

With confirmation prompt:
```bash
python load_summaries_to_chromadb.py delete-collection --collection-name wildchat-synthetic-summaries-v2 --confirm
```

## Features

- **Plain ChromaDB**: Uses ChromaDB client directly without DAO wrapper
- **Batch Loading**: Processes summaries in configurable batches
- **Progress Tracking**: Shows progress bars during loading
- **Error Handling**: Graceful handling of duplicates and errors
- **Statistics**: Provides detailed loading statistics
- **Test Query**: Automatically tests the loaded data with a sample query
- **Dual Version Support**: Loads both v1 and v2 summaries into separate collections
- **Cloud and Local**: Supports both ChromaDB Cloud and local persistent storage

## Output

The script will:
1. Load summaries from the SQLite database
2. Create embeddings using sentence-transformers/all-MiniLM-L6-v2
3. Load them into ChromaDB collections
4. Provide statistics and test the loaded data

## Collections Created

- `wildchat-synthetic-summaries-v1`: Contains v1 summaries
- `wildchat-synthetic-summaries-v2`: Contains v2 summaries

Each collection includes metadata:
- `hash`: Original conversation hash
- `summary_version`: Version of the summary (v1 or v2)
- `model`: Model used to generate the summary
- `timestamp`: When the summary was loaded
- `text_length`: Length of the summary text

## Example Usage

```bash
# Load v2 summaries to local ChromaDB with custom settings
python load_summaries_to_chromadb.py \
    --local \
    --prefix my-summaries \
    --version v2 \
    --limit 5000 \
    --batch-size 100 \
    --reset

# List all collections
python load_summaries_to_chromadb.py list-collections --local

# Delete a collection
python load_summaries_to_chromadb.py delete-collection \
    --collection-name my-summaries-v2 \
    --local \
    --confirm
```

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
