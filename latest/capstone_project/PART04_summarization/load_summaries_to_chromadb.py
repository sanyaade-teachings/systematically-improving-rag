#!/usr/bin/env python3
"""
Load conversation summaries to ChromaDB

This script loads conversation summaries (instead of first messages) into
ChromaDB for improved RAG performance with V2 queries.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
import typer

# Import our db module and DAO
sys.path.append(str(Path(__file__).parent.parent))
from src.db import load_summaries_from_db, get_summaries_by_hash
from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao import WildChatDocument

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database path
DB_PATH = Path(__file__).parent / "data" / "synthetic_summaries.db"


def convert_summary_to_document(
    conv_hash: str, version: str, summary: str, index: int
) -> WildChatDocument:
    """Convert a summary to a WildChatDocument"""
    return WildChatDocument(
        id=f"{conv_hash}_{version}",
        hash=conv_hash,
        text=summary,
        timestamp=datetime.now(),
        language="English",  # Assuming English summaries
        model_name="summary_model",
        conversation_length=1,  # Summaries are single items
        country="Unknown",
        toxic=False,
        redacted=False,
        turn=1,
        conversation_string=summary,  # Use summary as conversation string
    )


async def load_summaries_to_chromadb(
    dao: WildChatDAOChromaDB,
    summary_version: str,
    limit: int = None,
    batch_size: int = 25,
    reset_collection: bool = False,
) -> None:
    """
    Load summaries to ChromaDB with embeddings

    Args:
        dao: ChromaDB DAO instance
        summary_version: Which summary version to load (v1 or v2)
        limit: Maximum number of summaries to load
        batch_size: Number of records to process in each batch
        reset_collection: If True, delete existing collection before loading
    """

    console.print(f"\n[cyan]Loading summaries into ChromaDB...[/cyan]")
    console.print(f"Collection: {dao.table_name}")
    console.print(f"Summary version: {summary_version}")
    console.print(
        f"Using embedding model: sentence-transformers/all-MiniLM-L6-v2", style="cyan"
    )

    # Load summaries from database
    summaries = load_summaries_from_db(DB_PATH, version=summary_version, limit=limit)

    if not summaries:
        console.print("[red]No summaries found in database[/red]")
        return

    console.print(f"[green]Found {len(summaries)} summaries to load[/green]")

    try:
        # Handle collection reset
        if reset_collection:
            try:
                await dao.delete_table()
                console.print(
                    f"Deleted existing collection: {dao.table_name}", style="yellow"
                )
                # Reconnect to create new collection
                await dao.connect()
            except Exception as e:
                console.print(f"Warning: Could not delete collection: {e}", style="yellow")

        # Batch processing variables
        batch_documents = []
        total_added = 0
        duplicates_skipped = 0

        console.print("Loading summaries...", style="blue")

        # Start timing
        load_start_time = time.time()

        # Use rich progress bar
        with Progress() as progress:
            task = progress.add_task("Processing summaries...", total=len(summaries))

            for i, (conv_hash, version, summary, model) in enumerate(summaries):
                progress.update(task, advance=1)

                # Convert to WildChatDocument
                document = convert_summary_to_document(conv_hash, version, summary, i)
                batch_documents.append(document)

                # Process batch when full
                if len(batch_documents) >= batch_size:
                    try:
                        # Write batch to ChromaDB
                        result = await dao.add(batch_documents)
                        
                        total_added += result.get("added_count", 0)
                        duplicates_skipped += result.get("skipped_count", 0)

                        if not result.get("success", False):
                            console.print(f"Warning: Batch write had issues", style="yellow")

                    except Exception as e:
                        console.print(f"Error writing batch: {e}", style="red")
                        # Continue with next batch instead of failing completely
                        duplicates_skipped += len(batch_documents)

                    # Reset batch
                    batch_documents = []

        # Write final batch
        if batch_documents:
            try:
                result = await dao.add(batch_documents)
                total_added += result.get("added_count", 0)
                duplicates_skipped += result.get("skipped_count", 0)
                console.print("Final batch written", style="green")

            except Exception as e:
                console.print(f"Error writing final batch: {e}", style="red")
                duplicates_skipped += len(batch_documents)

        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time

        # Get final statistics
        try:
            stats = await dao.get_stats()
            final_count = stats.get("total_documents", "Unknown")
        except Exception:
            final_count = "Unknown"

        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total summaries loaded: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Collection size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")

        # Test query with timing
        if total_added > 0:
            console.print("\nTesting with sample query...", style="blue")
            test_query = "conversations about debugging Python code"

            try:
                from utils.dao.wildchat_dao import SearchRequest, SearchType
                
                # Test vector search
                search_start_time = time.time()
                search_request = SearchRequest(
                    query=test_query,
                    search_type=SearchType.VECTOR,
                    top_k=5
                )
                
                results = await dao.search(search_request)
                search_end_time = time.time()
                search_duration_ms = (search_end_time - search_start_time) * 1000

                console.print(f"Query: '{test_query}'")
                console.print(f"Found {len(results.results)} results", style="green")
                console.print(f"Search time: {search_duration_ms:.1f} ms")

                for i, result in enumerate(results.results[:3]):
                    console.print(
                        f"  {i + 1}. Hash: {result.metadata.get('hash', 'N/A')[:16]}... - {result.text[:100]}..."
                    )

            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")

    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise


app = typer.Typer()


@app.command()
def main(
    collection_name: str = typer.Option(
        None, help="ChromaDB collection name (default: wildchat-summaries-{version})"
    ),
    limit: int = typer.Option(None, help="Limit number of summaries to load"),
    batch_size: int = typer.Option(25, help="Batch size for writing to ChromaDB"),
    reset: bool = typer.Option(False, "--reset", help="Reset collection before loading"),
    use_cloud: bool = typer.Option(True, "--cloud/--local", help="Use ChromaDB cloud or local"),
):
    """Load conversation summaries to ChromaDB"""

    console.print("[bold green]Summary to ChromaDB Loader[/bold green]")
    console.print("=" * 50)

    async def async_main():
        try:
            for version in ["v1", "v2"]:
                # Create DAO instance
                table_name = collection_name or f"wildchat-summaries-{version}"
                dao = WildChatDAOChromaDB(table_name=table_name, use_cloud=False)
                
                console.print(f"\n[blue]Processing {version} summaries...[/blue]")
                
                try:
                    # Connect to ChromaDB
                    await dao.connect()
                    console.print(f"Connected to ChromaDB ({'cloud' if use_cloud else 'local'})", style="green")
                    
                    # Load summaries
                    await load_summaries_to_chromadb(
                        dao=dao,
                        summary_version=version,
                        limit=limit,
                        batch_size=batch_size,
                        reset_collection=reset,
                    )
                    
                finally:
                    # Always disconnect
                    await dao.disconnect()
                    console.print(f"Disconnected from ChromaDB", style="blue")

        except KeyboardInterrupt:
            console.print("\nOperation cancelled by user", style="yellow")
            sys.exit(1)
        except Exception as e:
            console.print(f"\nError: {e}", style="red")
            sys.exit(1)

    # Run the async main function
    asyncio.run(async_main())


if __name__ == "__main__":
    app() 