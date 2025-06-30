#!/usr/bin/env python3
"""
Load WildChat data to LanceDB using DAO pattern

This script loads WildChat-1M data into LanceDB with options for:
- Local persistent storage
- Cloud storage
- Configurable batch size and limits
"""

import os
import sys
import time
import asyncio
from datetime import datetime
import typer
from rich.console import Console
from rich.progress import Progress

# Import from parent utils directory
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from dataloader import WildChatDataLoader
from dao.wildchat_dao import WildChatDocument, SearchRequest, SearchType
from dao.wildchat_dao_lancedb import WildChatDAOLanceDB

console = Console()
app = typer.Typer(help="Load WildChat data to LanceDB using DAO")


async def load_to_lancedb(
    use_cloud: bool = False,
    table_name: str = "wildchat_2k",
    limit: int = 2000,
    batch_size: int = 25,
    filter_language: str = "English",
    min_message_length: int = 30,
    reset_table: bool = False,
) -> None:
    """
    Load WildChat data to LanceDB using DAO pattern

    Args:
        use_cloud: If True, use cloud client. If False, use local persistent client.
        table_name: Name of the table to create/use
        limit: Maximum number of records to load
        batch_size: Number of records to process in each batch
        filter_language: Language filter for conversations
        min_message_length: Minimum message length to include
        reset_table: If True, delete existing table before loading
    """

    console.print(f"Starting data load to table: {table_name}", style="blue")
    console.print(
        f"Config: limit={limit}, batch_size={batch_size}, language={filter_language}"
    )
    console.print("Using DAO pattern with LanceDB", style="cyan")

    # Create DAO instance
    dao = WildChatDAOLanceDB(table_name=table_name, use_cloud=use_cloud)

    try:
        # Connect to database
        await dao.connect()
        console.print("Connected to LanceDB", style="green")

        # Reset table if requested
        if reset_table:
            try:
                await dao.delete_table()
                console.print(f"Deleted existing table: {table_name}", style="yellow")
            except Exception:
                pass  # Table might not exist

        # Initialize data loader
        loader = WildChatDataLoader()

        # Batch processing variables
        batch_documents = []
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
            filter_toxic=True,
        )

        # Use rich progress bar
        with Progress() as progress:
            task = progress.add_task("Processing conversations...", total=limit)

            for conversation in conversation_stream:
                total_processed += 1
                progress.update(task, advance=1)

                # Convert to WildChatDocument
                try:
                    doc = WildChatDocument(
                        id=conversation["conversation_hash"],
                        text=conversation["first_message"][
                            :2000
                        ],  # Truncate if too long
                        conversation_string=conversation["conversation_string"],
                        hash=conversation["conversation_hash"],
                        timestamp=conversation["timestamp"]
                        if conversation["timestamp"]
                        else datetime.now(),
                        language=conversation["language"],
                        model_name=conversation["model"],
                        conversation_length=conversation["conversation_length"],
                        country=conversation.get("country", "Unknown"),
                        toxic=conversation["toxic"],
                        redacted=conversation["redacted"],
                        turn=conversation["turn"],
                    )

                    # Check for duplicates in current batch
                    if any(
                        existing_doc.id == doc.id for existing_doc in batch_documents
                    ):
                        duplicates_skipped += 1
                        continue

                    batch_documents.append(doc)

                except Exception as e:
                    console.print(f"Error processing document: {e}", style="yellow")
                    continue

                # Process batch when full
                if len(batch_documents) >= batch_size:
                    try:
                        result = await dao.add(batch_documents)
                        total_added += result["added_count"]
                        duplicates_skipped += result["skipped_count"]

                    except Exception as e:
                        console.print(f"Error writing batch: {e}", style="red")
                        # For now, continue with LanceDB debugging issues
                        continue

                    # Reset batch
                    batch_documents = []

        # Write final batch
        if batch_documents:
            try:
                result = await dao.add(batch_documents)
                total_added += result["added_count"]
                duplicates_skipped += result["skipped_count"]
                console.print("Final batch written", style="green")

            except Exception as e:
                console.print(f"Error writing final batch: {e}", style="red")

        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time

        # Get final statistics
        stats = await dao.get_stats()
        final_count = stats.get("total_documents", 0)

        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Table size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")

        # Test query with vector search and timing
        if final_count > 0:
            console.print("\nTesting table with sample query...", style="blue")
            try:
                search_request = SearchRequest(
                    query="How to learn programming",
                    top_k=3,
                    search_type=SearchType.VECTOR,
                )

                search_start_time = time.time()
                results = await dao.search(search_request)
                search_end_time = time.time()
                search_duration_ms = (search_end_time - search_start_time) * 1000

                console.print(
                    f"Success: Query found {len(results.results)} similar conversations",
                    style="green",
                )
                console.print(f"   - Search time: {search_duration_ms:.1f} ms")
                if results.results:
                    console.print(
                        f"   Most similar: '{results.results[0].text[:100]}...'"
                    )

            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")

    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise
    finally:
        # Cleanup
        try:
            await dao.disconnect()
        except Exception:
            pass


@app.command()
def main(
    cloud: bool = typer.Option(
        False, "--cloud", help="Use LanceDB Cloud instead of local persistent storage"
    ),
    table_name: str = typer.Option(
        "wildchat_2k", "--table-name", help="Name of the LanceDB table"
    ),
    limit: int = typer.Option(
        2000, "--limit", help="Maximum number of records to load"
    ),
    batch_size: int = typer.Option(
        25, "--batch-size", help="Batch size for writing to LanceDB"
    ),
    language: str = typer.Option(
        "English", "--language", help="Filter conversations by language"
    ),
    min_length: int = typer.Option(
        30, "--min-length", help="Minimum message length to include"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset table before loading (delete existing data)"
    ),
):
    """Load WildChat data to LanceDB using DAO pattern"""

    console.print("WildChat to LanceDB Loader (DAO)", style="bold blue")
    console.print("=" * 50)

    try:
        # Run async function
        asyncio.run(
            load_to_lancedb(
                use_cloud=cloud,
                table_name=table_name,
                limit=limit,
                batch_size=batch_size,
                filter_language=language,
                min_message_length=min_length,
                reset_table=reset,
            )
        )

    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
