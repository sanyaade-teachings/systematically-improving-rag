#!/usr/bin/env python3
"""
Load conversation summaries to ChromaDB

This script loads conversation summaries (instead of first messages) into
ChromaDB for improved RAG performance with V2 queries.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
import typer

# Add the src directory to path
sys.path.append(str(Path(__file__).parent))
from src.db import load_summaries_from_db, get_results_summary

# Add the utils directory to path for DAO access
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from dao.wildchat_dao import WildChatDocument
from dao.wildchat_dao_chromadb import WildChatDAOChromaDB

console = Console()
app = typer.Typer(help="Load conversation summaries to ChromaDB")

async def load_summaries_to_chromadb(
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
    
    # Create DAO instance
    dao = WildChatDAOChromaDB(table_name=collection_name, use_cloud=use_cloud)
    
    try:
        # Connect to ChromaDB
        await dao.connect()
        console.print(f"Connected to {'cloud' if use_cloud else 'local'} ChromaDB", style="green")
        
        # Handle collection reset
        if reset_collection:
            try:
                await dao.delete_table()
                console.print(f"Deleted existing collection: {collection_name}", style="yellow")
                # Reconnect after deletion
                await dao.connect()
            except Exception:
                pass  # Collection might not exist
        
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
                
                # Prepare batch data as WildChatDocument objects
                batch_documents = []
                
                for conv_hash, summary_version, summary_text, model in batch:
                    # Create unique ID for this summary
                    doc_id = f"{conv_hash}_{summary_version}"
                    
                    # Create WildChatDocument
                    doc = WildChatDocument(
                        id=doc_id,
                        text=summary_text,
                        conversation_string="",  # Not available for summaries
                        hash=conv_hash,
                        timestamp=datetime.now(),  # Use current time since we don't have original
                        language="Unknown",  # Not available for summaries
                        model_name=model,
                        conversation_length=0,  # Not available for summaries
                        country="Unknown",  # Not available for summaries
                        toxic=False,  # Assume summaries are not toxic
                        redacted=False,  # Assume summaries are not redacted
                        turn=1,  # Default turn
                    )
                    
                    batch_documents.append(doc)
                
                try:
                    # Write batch to ChromaDB
                    result = await dao.add(batch_documents)
                    total_added += result["added_count"]
                    total_skipped += result["skipped_count"]
                    total_processed += len(batch)
                    
                    progress.update(task, advance=len(batch))
                    
                except Exception as e:
                    console.print(f"Error writing batch: {e}", style="red")
                    raise
        
        # Get final statistics
        stats = await dao.get_stats()
        final_count = stats.get("total_documents", 0)
        
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
                from dao.wildchat_dao import SearchRequest, SearchType
                
                search_request = SearchRequest(
                    query="How to learn programming",
                    top_k=3,
                    search_type=SearchType.VECTOR,
                )
                
                results = await dao.search(search_request)
                
                console.print(f"Success: Query found {len(results.results)} similar summaries", style="green")
                console.print(f"   - Search time: {results.query_time_ms:.1f} ms")
                if results.results:
                    console.print(f"   Most similar: '{results.results[0].text[:100]}...'")
                    console.print(f"   Hash: {results.results[0].metadata.get('hash', 'N/A')}")
                    
            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")
    
    except Exception as e:
        console.print(f"Error during summary loading: {e}", style="red")
        raise
    
    finally:
        # Cleanup
        try:
            await dao.disconnect()
        except Exception:
            pass

@app.command()
def load(
    collection_name: str = typer.Option(
        "wildchat-summaries", "--collection-name", help="Name of the ChromaDB collection"
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
    full_collection_name = f"{collection_name}-{version}"
    
    try:
        # Load summaries
        asyncio.run(
            load_summaries_to_chromadb(
                db_path=db_path,
                collection_name=full_collection_name,
                version=version,
                limit=limit,
                batch_size=batch_size,
                reset_collection=reset,
                use_cloud=not local,
            )
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
        "wildchat-summaries-v2", "--collection-name", help="Name of the ChromaDB collection to delete"
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
    
    async def delete_collection_async():
        dao = WildChatDAOChromaDB(table_name=collection_name, use_cloud=not local)
        try:
            await dao.connect()
            console.print(f"Deleting collection: {collection_name}", style="red")
            result = await dao.delete_table()
            if result.get("success", False):
                console.print(f"Successfully deleted collection: {collection_name}", style="green")
            else:
                console.print(f"Error deleting collection: {result.get('error', 'Unknown error')}", style="red")
        except Exception as e:
            if "not found" in str(e).lower():
                console.print(f"Collection '{collection_name}' not found", style="yellow")
            else:
                console.print(f"Error deleting collection: {e}", style="red")
                sys.exit(1)
        finally:
            await dao.disconnect()
    
    try:
        asyncio.run(delete_collection_async())
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        sys.exit(1)

# Make load the default command
@app.command()
def main(
    collection_name: str = typer.Option(
        "wildchat-summaries", "--collection-name", help="Name of the ChromaDB collection"
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
    load(collection_name, version, limit, batch_size, reset, local)

if __name__ == "__main__":
    app() 