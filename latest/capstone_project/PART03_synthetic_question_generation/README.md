# Synthetic Query Generation

This directory contains scripts for generating synthetic search queries from WildChat conversations.

## Files

- `generate_synthetic_queries.py` - Main script to generate synthetic queries
- `synthetic_queries.db` - SQLite database containing generated queries (created after running script)

## Usage

1. Ensure you have an OpenAI API key set in your environment:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Run the script:
   ```bash
   python generate_synthetic_queries.py
   ```

## Database Schema

The SQLite database contains a single table `synthetic_queries` with the following columns:

- `id` - Primary key (auto-increment)
- `conversation_hash` - Hash of the source conversation
- `prompt_version` - Version of prompt used (v1 or v2)
- `query` - Generated search query
- `created_at` - Timestamp when record was created

## Expected Output

- Processes 1000 conversations from WildChat dataset
- Generates 4-7 queries per conversation per version (v1 and v2)
- Expected total: ~8,000-14,000 queries
- Processing time: ~10-20 minutes depending on API rate limits

## Features

- **Concurrent Processing**: Uses asyncio with rate limiting (10 concurrent requests)
- **Error Handling**: Gracefully handles API errors and continues processing
- **Progress Tracking**: Shows progress every 50 completed conversations
- **Batch Saving**: Saves results to database in batches of 100
- **Deduplication**: Uses conversation hashes to avoid duplicate processing
