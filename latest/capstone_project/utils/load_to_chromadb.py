#!/usr/bin/env python3
"""
Load WildChat data to ChromaDB

This script loads WildChat-1M data into ChromaDB with options for:
- Local persistent storage
- Cloud storage  
- Configurable batch size and limits
"""

import os
import sys
import time
import chromadb
from chromadb.utils import embedding_functions
import typer
from rich.console import Console
from rich.progress import Progress
from dotenv import load_dotenv

# Import from the same directory since we're in utils/
from dataloader import WildChatDataLoader

load_dotenv()

console = Console()
app = typer.Typer(help="Load WildChat data to ChromaDB")


def create_client(use_cloud: bool = False) -> chromadb.ClientAPI:
    """
    Create ChromaDB client - either local persistent or cloud
    
    Args:
        use_cloud: If True, use cloud client. If False, use local persistent client.
        
    Returns:
        ChromaDB client instance
    """
    if use_cloud:
        # Load environment variables for cloud connection
        load_dotenv()
        
        required_env_vars = ['CHROMA_API_KEY', 'CHROMA_TENANT', 'CHROMA_DATABASE']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables for cloud: {missing_vars}")
        
        print("Connecting to ChromaDB Cloud...")
        client = chromadb.CloudClient(
            api_key=os.getenv('CHROMA_API_KEY'),
            tenant=os.getenv('CHROMA_TENANT'),
            database=os.getenv('CHROMA_DATABASE')
        )
        print(f"Connected to cloud database: {os.getenv('CHROMA_DATABASE')}")
        
    else:
        # Use local persistent client
        db_path = "./chroma_db"
        print(f"Using local persistent ChromaDB at: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        print("Connected to local persistent ChromaDB")
    
    return client


def load_to_chromadb(
    client: chromadb.ClientAPI,
    collection_name: str = "wildchat_2k",
    limit: int = 2000,
    batch_size: int = 25,
    filter_language: str = "English",
    min_message_length: int = 30,
    reset_collection: bool = False
) -> None:
    """
    Load WildChat data to ChromaDB using streaming approach
    
    Args:
        client: ChromaDB client instance
        collection_name: Name of the collection to create/use
        limit: Maximum number of records to load
        batch_size: Number of records to process in each batch
        filter_language: Language filter for conversations
        min_message_length: Minimum message length to include
        reset_collection: If True, delete existing collection before loading
    """
    
    console.print(f"Starting data load to collection: {collection_name}", style="blue")
    console.print(f"Config: limit={limit}, batch_size={batch_size}, language={filter_language}")
    console.print("Using embedding model: sentence-transformers/all-MiniLM-L6-v2", style="cyan")
    
    try:
        # Handle collection creation/reset
        if reset_collection:
            try:
                client.delete_collection(collection_name)
                console.print(f"Deleted existing collection: {collection_name}", style="yellow")
            except Exception:
                pass  # Collection might not exist
        
        # Create sentence transformer embedding function (suppress loading messages)
        with console.status("Loading embedding model...", spinner="dots"):
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        console.print("Embedding model loaded successfully", style="green")
        
        # Create or get collection with custom embedding function
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=sentence_transformer_ef,
            metadata={
                "description": f"WildChat-1M data - {limit} records",
                "language_filter": filter_language,
                "min_message_length": str(min_message_length),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        )
        
        # Initialize data loader
        loader = WildChatDataLoader()
        
        # Batch processing variables
        documents = []
        metadatas = []
        ids = []
        total_processed = 0
        total_added = 0
        duplicates_skipped = 0
        
        console.print("Loading conversations...", style="blue")
        
        # Start timing the data load
        load_start_time = time.time()
        
        conversation_stream = loader.stream_conversations(
            limit=limit,
            min_message_length=min_message_length,
            filter_language=filter_language,
            filter_toxic=True
        )
        
        # Use rich progress bar
        with Progress() as progress:
            task = progress.add_task("Processing conversations...", total=limit)
            
            for conversation in conversation_stream:
                total_processed += 1
                progress.update(task, advance=1)
                
                # Prepare document ID and check for duplicates
                doc_id = conversation['conversation_hash']
                
                # Skip if we already have this ID in current batch
                if doc_id in ids:
                    duplicates_skipped += 1
                    continue
                
                # Prepare metadata - ChromaDB doesn't accept None values
                metadata = {
                    "hash": conversation['conversation_hash'] or "",
                    "timestamp": str(conversation['timestamp']) if conversation['timestamp'] else "",
                    "language": conversation['language'] or "Unknown",
                    "model": conversation['model'] or "Unknown",
                    "conversation_length": conversation['conversation_length'] or 0,
                    "country": conversation.get('country') or "Unknown",
                    "toxic": bool(conversation.get('toxic', False)),
                    "redacted": bool(conversation.get('redacted', False)),
                    "turn": conversation.get('turn', 1) or 1
                }
                
                # Truncate message if too long (ChromaDB has limits)
                message_text = conversation['first_message'][:2000]
                
                # Add to batch
                documents.append(message_text)
                metadatas.append(metadata)
                ids.append(doc_id)
                
                # Process batch when full
                if len(documents) >= batch_size:
                    try:
                        collection.add(
                            documents=documents,
                            metadatas=metadatas,
                            ids=ids
                        )
                        total_added += len(documents)
                        
                    except Exception as e:
                        if "Expected IDs to be unique" in str(e):
                            console.print("Warning: Duplicate IDs detected in batch, skipping", style="yellow")
                            duplicates_skipped += len(documents)
                        else:
                            console.print(f"Error writing batch: {e}", style="red")
                            raise
                    
                    # Reset batch
                    documents = []
                    metadatas = []
                    ids = []
        
        # Write final batch
        if documents:
            try:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(documents)
                console.print("Final batch written", style="green")
                
            except Exception as e:
                if "Expected IDs to be unique" in str(e):
                    console.print("Warning: Duplicate IDs in final batch, skipping", style="yellow")
                    duplicates_skipped += len(documents)
                else:
                    console.print(f"Error writing final batch: {e}", style="red")
        
        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time
        
        # Final statistics
        final_count = collection.count()
        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Collection size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")
        
        # Test query with timing
        console.print("\nTesting collection with sample query...", style="blue")
        search_start_time = time.time()
        results = collection.query(
            query_texts=["How to learn programming"],
            n_results=3
        )
        search_end_time = time.time()
        search_duration_ms = (search_end_time - search_start_time) * 1000
        
        console.print(f"Success: Query found {len(results['documents'][0])} similar conversations", style="green")
        console.print(f"   - Search time: {search_duration_ms:.1f} ms")
        if results['documents'][0]:
            console.print(f"   Most similar: '{results['documents'][0][0][:100]}...'") 
        
    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise


@app.command()
def main(
    cloud: bool = typer.Option(False, "--cloud", help="Use ChromaDB Cloud instead of local persistent storage"),
    collection_name: str = typer.Option("wildchat_2k", "--collection-name", help="Name of the ChromaDB collection"),
    limit: int = typer.Option(2000, "--limit", help="Maximum number of records to load"),
    batch_size: int = typer.Option(25, "--batch-size", help="Batch size for writing to ChromaDB"),
    language: str = typer.Option("English", "--language", help="Filter conversations by language"),
    min_length: int = typer.Option(30, "--min-length", help="Minimum message length to include"),
    reset: bool = typer.Option(False, "--reset", help="Reset collection before loading (delete existing data)")
):
    """Load WildChat data to ChromaDB"""
    
    console.print("WildChat to ChromaDB Loader", style="bold blue")
    console.print("=" * 50)
    
    try:
        # Create client
        client = create_client(use_cloud=cloud)
        
        # Load data
        load_to_chromadb(
            client=client,
            collection_name=collection_name,
            limit=limit,
            batch_size=batch_size,
            filter_language=language,
            min_message_length=min_length,
            reset_collection=reset
        )
        
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app() 