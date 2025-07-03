#!/usr/bin/env python3
"""
Load conversation summaries to ChromaDB

This script loads conversation summaries (instead of first messages) into
ChromaDB for improved RAG performance with V2 queries.
"""

import os
import sys
from pathlib import Path
from typing import List
from datetime import datetime
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
import typer

# Add the src directory to path
sys.path.append(str(Path(__file__).parent))
from src.db import load_summaries_from_db, get_results_summary

console = Console()
app = typer.Typer(help="Load conversation summaries to ChromaDB")

# Global embedding model
embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model"""
    global embedding_model
    if embedding_model is None:
        console.print("Loading embedding model...", style="cyan")
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        console.print("Embedding model loaded successfully", style="green")
    return embedding_model

def create_chromadb_client(use_cloud: bool = True):
    """Create ChromaDB client"""
    load_dotenv()
    
    if use_cloud:
        # Cloud connection
        required_env_vars = ["CHROMA_API_KEY", "CHROMA_TENANT", "CHROMA_DATABASE"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables for ChromaDB cloud: {missing_vars}")
        
        console.print("Connecting to ChromaDB Cloud...", style="blue")
        client = chromadb.CloudClient(
            api_key=os.getenv("CHROMA_API_KEY"),
            tenant=os.getenv("CHROMA_TENANT"),
            database=os.getenv("CHROMA_DATABASE"),
        )
        console.print("Connected to ChromaDB Cloud", style="green")
    else:
        # Local persistent client
        db_path = "./chroma_db"
        console.print(f"Connecting to local ChromaDB at {db_path}...", style="blue")
        client = chromadb.PersistentClient(path=db_path)
        console.print("Connected to local ChromaDB", style="green")
    
    return client

def load_summaries_to_chromadb(
    db_path: Path,
    collection_name: str,
    version: str = "v2",
    limit: int = None,
    batch_size: int = 50,
    reset_collection: bool = False,
    use_cloud: bool = True,
) -> None:
    """
    Load conversation summaries to ChromaDB
    
    Args:
        db_path: Path to the summaries database
        collection_name: Name of the collection to create/use
        version: Summary version to load (v1 or v2)
        limit: Maximum number of summaries to load
        batch_size: Number of summaries to process in each batch
        reset_collection: If True, delete existing collection before loading
        use_cloud: If True, use ChromaDB cloud, otherwise local
    """
    
    console.print(f"Starting summary load to collection: {collection_name}", style="blue")
    console.print(f"Config: version={version}, limit={limit}, batch_size={batch_size}")
    console.print(f"Using {'cloud' if use_cloud else 'local'} ChromaDB", style="cyan")
    
    # Check if SQLite database exists
    if not db_path.exists():
        console.print(f"[red]SQLite database not found at {db_path}[/red]")
        console.print("[yellow]Please run compute_summaries.py first[/yellow]")
        return
    
    # Get SQLite database statistics
    stats = get_results_summary(db_path)
    console.print(f"SQLite database contains {stats['total_summaries']} summaries")
    console.print(f"Version counts: {stats['version_counts']}")
    
    try:
        # Create ChromaDB client
        client = create_chromadb_client(use_cloud)
        
        # Create embedding function
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Handle collection reset
        if reset_collection:
            try:
                client.delete_collection(collection_name)
                console.print(f"Deleted existing collection: {collection_name}", style="yellow")
            except Exception:
                pass  # Collection might not exist
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={
                "description": f"WildChat conversation summaries ({version})",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "summary_version": version,
            },
        )
        
        # Load summaries from database
        console.print(f"Loading {version} summaries from database...", style="cyan")
        summaries = load_summaries_from_db(db_path, version=version, limit=limit)
        
        if not summaries:
            console.print(f"[red]No {version} summaries found in database[/red]")
            return
        
        console.print(f"Loaded {len(summaries)} summaries", style="green")
        
        # Process summaries in batches
        total_processed = 0
        total_added = 0
        total_skipped = 0
        
        with Progress() as progress:
            task = progress.add_task("Processing summaries...", total=len(summaries))
            
            for i in range(0, len(summaries), batch_size):
                batch = summaries[i:i + batch_size]
                
                # Prepare batch data
                batch_texts = []
                batch_metadatas = []
                batch_ids = []
                
                for conv_hash, summary_version, summary_text, model in batch:
                    # Create unique ID for this summary
                    doc_id = f"{conv_hash}_{summary_version}"
                    
                    # Prepare metadata
                    metadata = {
                        "hash": conv_hash,
                        "summary_version": summary_version,
                        "model": model,
                        "timestamp": datetime.now().isoformat(),
                        "text_length": len(summary_text),
                    }
                    
                    batch_texts.append(summary_text)
                    batch_metadatas.append(metadata)
                    batch_ids.append(doc_id)
                
                try:
                    # Add batch to collection
                    collection.add(
                        documents=batch_texts,
                        metadatas=batch_metadatas,
                        ids=batch_ids
                    )
                    
                    total_added += len(batch_texts)
                    total_processed += len(batch)
                    
                    progress.update(task, advance=len(batch))
                    
                except Exception as e:
                    if "Expected IDs to be unique" in str(e):
                        # Handle duplicates by trying to add one by one
                        for text, metadata, doc_id in zip(batch_texts, batch_metadatas, batch_ids):
                            try:
                                collection.add(
                                    documents=[text],
                                    metadatas=[metadata],
                                    ids=[doc_id]
                                )
                                total_added += 1
                            except Exception:
                                total_skipped += 1
                        total_processed += len(batch)
                        progress.update(task, advance=len(batch))
                    else:
                        console.print(f"Error writing batch: {e}", style="red")
                        raise
        
        # Get final statistics
        final_count = collection.count()
        
        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Total skipped: {total_skipped}")
        console.print(f"   - Collection size: {final_count}")
        
        # Test query
        if total_added > 0:
            console.print("\nTesting collection with sample query...", style="blue")
            try:
                results = collection.query(
                    query_texts=["How to learn programming"],
                    n_results=3,
                    include=["documents", "metadatas", "distances"]
                )
                
                console.print(f"Success: Query found {len(results['documents'][0])} similar summaries", style="green")
                if results['documents'][0]:
                    console.print(f"   Most similar: '{results['documents'][0][0][:100]}...'")
                    console.print(f"   Hash: {results['metadatas'][0][0].get('hash', 'N/A')}")
                    console.print(f"   Distance: {results['distances'][0][0]:.4f}")
                    
            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")
    
    except Exception as e:
        console.print(f"Error during summary loading: {e}", style="red")
        raise

@app.command()
def load(
    prefix: str = typer.Option(
        "wildchat-synthetic-summaries", "--prefix", help="Prefix for the ChromaDB collection"
    ),
    version: str = typer.Option(
        "v2", "--version", help="Summary version to load (v1 or v2)"
    ),
    limit: int = typer.Option(
        None, "--limit", help="Maximum number of summaries to load"
    ),
    batch_size: int = typer.Option(
        50, "--batch-size", help="Batch size for writing to ChromaDB"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset collection before loading (delete existing data)"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use local ChromaDB instead of cloud"
    ),
):
    """Load conversation summaries to ChromaDB"""
    
    console.print("Summary to ChromaDB Loader", style="bold blue")
    console.print("=" * 50)
    
    # Database path
    db_path = Path(__file__).parent / "data" / "synthetic_summaries.db"
    
    # Add version suffix to collection name
    full_collection_name = f"{prefix}-{version}"
    
    try:
        # Load summaries
        load_summaries_to_chromadb(
            db_path=db_path,
            collection_name=full_collection_name,
            version=version,
            limit=limit,
            batch_size=batch_size,
            reset_collection=reset,
            use_cloud=not local,
        )
        
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)

@app.command()
def delete_collection(
    collection_name: str = typer.Option(
        "wildchat-synthetic-summaries-v2", "--collection-name", help="Name of the ChromaDB collection to delete"
    ),
    confirm: bool = typer.Option(
        False, "--confirm", help="Confirm deletion without prompting"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use local ChromaDB instead of cloud"
    ),
):
    """Delete a ChromaDB collection"""
    
    console.print("Collection Deletion Tool", style="bold red")
    console.print("=" * 50)
    
    if not confirm:
        response = typer.confirm(f"Are you sure you want to delete collection '{collection_name}'?")
        if not response:
            console.print("Operation cancelled", style="yellow")
            return
    
    try:
        # Create client
        client = create_chromadb_client(use_cloud=not local)
        
        # Delete collection
        console.print(f"Deleting collection: {collection_name}", style="red")
        client.delete_collection(collection_name)
        console.print(f"Successfully deleted collection: {collection_name}", style="green")
        
    except Exception as e:
        if "not found" in str(e).lower():
            console.print(f"Collection '{collection_name}' not found", style="yellow")
        else:
            console.print(f"Error deleting collection: {e}", style="red")
            sys.exit(1)

@app.command()
def list_collections(
    local: bool = typer.Option(
        False, "--local", help="Use local ChromaDB instead of cloud"
    ),
):
    """List all ChromaDB collections"""
    
    console.print("ChromaDB Collections", style="bold blue")
    console.print("=" * 50)
    
    try:
        # Create client
        client = create_chromadb_client(use_cloud=not local)
        
        # List collections
        collections = client.list_collections()
        
        if not collections:
            console.print("No collections found", style="yellow")
            return
        
        console.print(f"Found {len(collections)} collections:", style="green")
        for collection in collections:
            console.print(f"  - {collection.name} (count: {collection.count()})")
            if collection.metadata:
                for key, value in collection.metadata.items():
                    console.print(f"    {key}: {value}")
        
    except Exception as e:
        console.print(f"Error listing collections: {e}", style="red")
        sys.exit(1)

# Make load the default command
@app.command()
def main(
    prefix: str = typer.Option(
        "wildchat-synthetic-summaries", "--prefix", help="Prefix for the ChromaDB collection"
    ),
    version: str = typer.Option(
        "v2", "--version", help="Summary version to load (v1 or v2)"
    ),
    limit: int = typer.Option(
        None, "--limit", help="Maximum number of summaries to load"
    ),
    batch_size: int = typer.Option(
        50, "--batch-size", help="Batch size for writing to ChromaDB"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset collection before loading (delete existing data)"
    ),
    local: bool = typer.Option(
        False, "--local", help="Use local ChromaDB instead of cloud"
    ),
):
    """Load conversation summaries to ChromaDB (default command)"""
    
    # Call the load function
    load(prefix, version, limit, batch_size, reset, local)

if __name__ == "__main__":
    app() 