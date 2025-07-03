#!/usr/bin/env python3
"""
Load conversation summaries to Turbopuffer

This script loads conversation summaries (instead of first messages) into
Turbopuffer for improved RAG performance with V2 queries.
"""

import os
import sys
from pathlib import Path
from typing import List
import turbopuffer
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
import typer

# Add the src directory to path
sys.path.append(str(Path(__file__).parent))
from src.db import load_summaries_from_db, get_results_summary

console = Console()
app = typer.Typer(help="Load conversation summaries to Turbopuffer")

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

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a list of texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return [embedding.tolist() for embedding in embeddings]

def create_client() -> turbopuffer.Turbopuffer:
    """Create Turbopuffer client"""
    load_dotenv()
    
    api_key = os.getenv("TURBOPUFFER_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: TURBOPUFFER_API_KEY")
    
    region = os.getenv("TURBOPUFFER_REGION", "gcp-us-central1")
    
    console.print("Connecting to Turbopuffer...", style="blue")
    client = turbopuffer.Turbopuffer(api_key=api_key, region=region)
    console.print(f"Connected to Turbopuffer in region: {region}", style="green")
    
    return client

def load_summaries_to_turbopuffer(
    client: turbopuffer.Turbopuffer,
    db_path: Path,
    namespace_name: str,
    version: str = "v2",
    limit: int = None,
    batch_size: int = 50,
    reset_namespace: bool = False,
) -> None:
    """
    Load conversation summaries to Turbopuffer
    
    Args:
        client: Turbopuffer client instance
        db_path: Path to the summaries database
        namespace_name: Name of the namespace to create/use
        version: Summary version to load (v1 or v2)
        limit: Maximum number of summaries to load
        batch_size: Number of summaries to process in each batch
        reset_namespace: If True, delete existing namespace before loading
    """
    
    console.print(f"Starting summary load to namespace: {namespace_name}", style="blue")
    console.print(f"Config: version={version}, limit={limit}, batch_size={batch_size}")
    
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
        # Get namespace
        ns = client.namespace(namespace_name)
        
        # Handle namespace reset
        if reset_namespace:
            try:
                ns.delete_all()
                console.print(f"Deleted all data from namespace: {namespace_name}", style="yellow")
            except Exception:
                pass  # Namespace might not exist
        
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
        
        with Progress() as progress:
            task = progress.add_task("Processing summaries...", total=len(summaries))
            
            for i in range(0, len(summaries), batch_size):
                batch = summaries[i:i + batch_size]
                
                # Prepare batch data
                batch_texts = []
                batch_data = {
                    "id": [],
                    "vector": [],
                    "summary": [],
                    "hash": [],
                    "summary_version": [],
                    "model": [],
                }
                
                for conv_hash, summary_version, summary_text, model in batch:
                    # Create unique ID for this summary
                    doc_id = f"{conv_hash}_{summary_version}"
                    
                    batch_data["id"].append(doc_id)
                    batch_data["summary"].append(summary_text)
                    batch_data["hash"].append(conv_hash)
                    batch_data["summary_version"].append(summary_version)
                    batch_data["model"].append(model)
                    
                    batch_texts.append(summary_text)
                
                # Create embeddings for the batch
                embeddings = create_embeddings(batch_texts)
                batch_data["vector"] = embeddings
                
                try:
                    # Write batch to Turbopuffer
                    ns.write(
                        upsert_columns=batch_data,
                        distance_metric="cosine_distance",
                        schema={
                            "summary": {
                                "type": "string",
                                "full_text_search": True,
                            },
                            "hash": {"type": "string"},
                            "summary_version": {"type": "string"},
                            "model": {"type": "string"},
                        },
                    )
                    
                    total_added += len(batch_data["id"])
                    total_processed += len(batch)
                    
                    progress.update(task, advance=len(batch))
                    
                except Exception as e:
                    console.print(f"Error writing batch: {e}", style="red")
                    raise
        
        # Get final statistics
        try:
            count_result = ns.query(
                aggregate_by={"document_count": ("Count", "id")}
            )
            final_count = count_result.aggregations["document_count"]
        except Exception:
            final_count = "Unknown"
        
        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Namespace size: {final_count}")
        
        # Test query
        if total_added > 0:
            console.print("\nTesting namespace with sample query...", style="blue")
            try:
                test_embedding = create_embeddings(["How to learn programming"])[0]
                results = ns.query(
                    rank_by=("vector", "ANN", test_embedding),
                    top_k=3,
                    include_attributes=["text", "hash", "summary_version"],
                )
                
                console.print(f"Success: Query found {len(results.rows)} similar summaries", style="green")
                if results.rows:
                    console.print(f"   Most similar: '{results.rows[0].text[:100]}...'")
                    console.print(f"   Hash: {getattr(results.rows[0], 'hash', 'N/A')}")
                    
            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")
    
    except Exception as e:
        console.print(f"Error during summary loading: {e}", style="red")
        raise

@app.command()
def load(
    prefix: str = typer.Option(
        "wildchat-synthetic-summaries", "--prefix", help="Prefix for the Turbopuffer namespace"
    ),
    version: str = typer.Option(
        "v2", "--version", help="Summary version to load (v1 or v2)"
    ),
    limit: int = typer.Option(
        None, "--limit", help="Maximum number of summaries to load"
    ),
    batch_size: int = typer.Option(
        50, "--batch-size", help="Batch size for writing to Turbopuffer"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset namespace before loading (delete existing data)"
    ),
):
    """Load conversation summaries to Turbopuffer"""
    
    console.print("Summary to Turbopuffer Loader", style="bold blue")
    console.print("=" * 50)
    
    # Database path
    db_path = Path(__file__).parent / "data" / "synthetic_summaries.db"
    
    try:
        # Create client
        client = create_client()
        
        # Load summaries
        load_summaries_to_turbopuffer(
            client=client,
            db_path=db_path,
            namespace_name=f"{prefix}-{version}",
            version=version,
            limit=limit,
            batch_size=batch_size,
            reset_namespace=reset,
        )
        
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)

@app.command()
def delete_namespace(
    namespace_name: str = typer.Option(
        "wildchat-summaries-v2", "--namespace-name", help="Name of the Turbopuffer namespace to delete"
    ),
    confirm: bool = typer.Option(
        False, "--confirm", help="Confirm deletion without prompting"
    ),
):
    """Delete a Turbopuffer namespace"""
    
    console.print("Namespace Deletion Tool", style="bold red")
    console.print("=" * 50)
    
    if not confirm:
        response = typer.confirm(f"Are you sure you want to delete namespace '{namespace_name}'?")
        if not response:
            console.print("Operation cancelled", style="yellow")
            return
    
    try:
        # Create client
        client = create_client()
        
        # Delete namespace
        console.print(f"Deleting namespace: {namespace_name}", style="red")
        ns = client.namespace(namespace_name)
        ns.delete_all()
        console.print(f"Successfully deleted all data from namespace: {namespace_name}", style="green")
        
    except Exception as e:
        if "not found" in str(e).lower():
            console.print(f"Namespace '{namespace_name}' not found", style="yellow")
        else:
            console.print(f"Error deleting namespace: {e}", style="red")
            sys.exit(1)

# Make load the default command
@app.command()
def main(
    prefix: str = typer.Option(
        "wildchat-synthetic-summaries", "--prefix", help="Prefix for the Turbopuffer namespace"
    ),
    version: str = typer.Option(
        "v2", "--version", help="Summary version to load (v1 or v2)"
    ),
    limit: int = typer.Option(
        None, "--limit", help="Maximum number of summaries to load"
    ),
    batch_size: int = typer.Option(
        50, "--batch-size", help="Batch size for writing to Turbopuffer"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset namespace before loading (delete existing data)"
    ),
):
    """Load conversation summaries to Turbopuffer (default command)"""
    
    # Call the load function
    load(prefix, version, limit, batch_size, reset)

if __name__ == "__main__":
    app()