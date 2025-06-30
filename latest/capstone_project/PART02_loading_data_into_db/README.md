# PART02: Loading Data into Vector Databases

This directory contains scripts that load WildChat conversations into different vector databases (ChromaDB, LanceDB, and TurboPuffer).

## Key Implementation Detail

**Important**: These scripts only embed the **first message** of each conversation, not the entire conversation. This is intentionally simplified and not what you'd typically do in practice, but it serves as a critical example for PART03's evaluation experiments.

## Scripts

- `load_data_chroma.py` - Loads data into ChromaDB
- `load_data_lance.py` - Loads data into LanceDB  
- `load_data_turbopuffer.py` - Loads data into TurboPuffer
- `dao.py` - Defines the data access interface

Each loader:
1. Reads conversations from the SQLite database
2. Generates embeddings for just the first message
3. Stores in the respective vector database
4. Runs a test search query

The embedding strategy (first message only) will become important in PART03 when we see how different query generation approaches succeed or fail based on this design choice.