# ChromaDB Summary Loader

This script loads conversation summaries into ChromaDB using the WildChatDAOChromaDB class.

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
Load all summaries to ChromaDB cloud:
```bash
python load_summaries_to_chromadb.py
```

### Local ChromaDB
Use local ChromaDB instead of cloud:
```bash
python load_summaries_to_chromadb.py --local
```

### Custom Collection Name
Specify a custom collection name:
```bash
python load_summaries_to_chromadb.py --collection-name my-summaries
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
python load_summaries_to_chromadb.py --batch-size 50
```

## Features

- **Async Processing**: Uses async/await for better performance
- **Batch Loading**: Processes summaries in configurable batches
- **Progress Tracking**: Shows progress bars during loading
- **Error Handling**: Graceful handling of duplicates and errors
- **Statistics**: Provides detailed loading statistics
- **Test Query**: Automatically tests the loaded data with a sample query
- **Dual Version Support**: Loads both v1 and v2 summaries into separate collections

## Output

The script will:
1. Load summaries from the SQLite database
2. Convert them to WildChatDocument format
3. Create embeddings using sentence-transformers/all-MiniLM-L6-v2
4. Load them into ChromaDB collections
5. Provide statistics and test the loaded data

## Collections Created

- `wildchat-summaries-v1`: Contains v1 summaries
- `wildchat-summaries-v2`: Contains v2 summaries

Each collection includes:
- Vector embeddings for semantic search
- Full text for keyword search
- Metadata (hash, version, timestamps, etc.) 
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
