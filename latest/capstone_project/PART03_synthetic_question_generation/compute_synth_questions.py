#!/usr/bin/env python3
"""
Synthetic Query Generation Script

This script loads 1000 random conversations from WildChat dataset and generates
synthetic search queries using both v1 and v2 prompt versions. Results are saved
to a SQLite database.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Any
import instructor
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)

import typer

# Import from our package - handles both direct execution and module import
from src.dataloader import WildChatDataLoader
from src.generation_prompts import (
    synthetic_question_generation_v1,
    synthetic_question_generation_v2,
    synthetic_question_generation_v3,
    synthetic_question_generation_v5,
)
from src.db import (
    setup_database,
    save_query_to_db,
    get_processed_conversations,
    get_results_summary,
)
from src.cache import setup_cache, GenericCache

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

# Database and cache setup
DB_PATH = Path(__file__).parent / "data" / "synthetic_queries.db"
CACHE_DIR = Path(__file__).parent / "data" / ".cache"


async def process_conversation_version(
    client,
    conversation: Dict[str, Any],
    query_version: str,
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
) -> List[str]:
    """Process a single conversation with one version (v1 or v2)"""
    async with semaphore:
        conversation_hash = conversation["conversation_hash"]
        messages = conversation["conversation"]
        cache_key = GenericCache.make_conversation_key(conversation_hash, query_version)

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            if query_version == "v1":
                result = await synthetic_question_generation_v1(client, messages)
            elif query_version == "v2":
                result = await synthetic_question_generation_v2(client, messages)
            elif query_version == "v3":
                result = await synthetic_question_generation_v3(client, messages)
            elif query_version == "v5":
                result = await synthetic_question_generation_v5(client, messages)
            else:
                raise ValueError(f"Unknown query version: {query_version}")

            queries = result.queries if hasattr(result, "queries") else []

            # Cache the result
            cache.set(cache_key, queries)

            return queries

        except Exception as e:
            console.print(
                f"[red]Error processing {conversation_hash} {query_version}: {e}[/red]"
            )
            return []


async def process_conversation(
    client,
    conversation: Dict[str, Any],
    query_version: str,
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
    progress: Progress,
    task_id,
) -> int:
    """Process a single conversation with both v1 and v2 generators and save immediately"""
    conversation_hash = conversation["conversation_hash"]
    saved_count = 0

    try:
        # Process both versions concurrently
        v1_task = process_conversation_version(
            client, conversation, "v1", cache, semaphore
        )
        if query_version in ["v2", "v3", "v5"]:
            v2_task = process_conversation_version(
                client, conversation, query_version, cache, semaphore
            )
            v1_queries, v2_queries = await asyncio.gather(v1_task, v2_task)
        else:
            v2_task = None
            v1_queries = await v1_task
            v2_queries = []

        # Save v1 queries immediately
        for query in v1_queries:
            if save_query_to_db(DB_PATH, conversation_hash, "v1", query):
                saved_count += 1

        # Save v2/v3/v5 queries immediately
        for query in v2_queries:
            if save_query_to_db(DB_PATH, conversation_hash, query_version, query):
                saved_count += 1

        progress.update(task_id, advance=1)

    except Exception as e:
        console.print(
            f"[red]Failed to process conversation {conversation_hash}: {e}[/red]"
        )

    return saved_count


async def main(
    limit: int = typer.Option(500, help="Number of conversations to process"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1, v2, v3, or v5)"
    ),
    clear_cache: bool = typer.Option(False, help="Clear the cache before starting"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
):
    """Generate synthetic queries from WildChat conversations"""

    console.print("[bold green]Synthetic Query Generation[/bold green]")
    console.print("=" * 50)

    console.print("\n[cyan]Setting up database...[/cyan]")
    setup_database(DB_PATH)

    # Set up disk cache
    console.print(f"[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
    cache = setup_cache(CACHE_DIR, clear_cache=clear_cache)

    # Check for already processed conversations
    processed = get_processed_conversations(DB_PATH)
    if processed:
        console.print(
            f"[yellow]Found {len(processed)} already processed conversations[/yellow]"
        )

    console.print("\n[cyan]Loading conversations...[/cyan]")
    # Load conversations
    loader = WildChatDataLoader(limit=2000)  # Load more to ensure we get 1000 good ones
    conversations = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        load_task = progress.add_task("Loading conversations", total=limit)

        for conversation in loader.stream_conversations(
            limit=int(limit * 1.5),  # Load extra in case some are already processed
            min_message_length=50,
            filter_language="English",
            filter_toxic=True,
        ):
            # Skip already processed conversations
            if conversation["conversation_hash"] not in processed:
                conversations.append(conversation)
                progress.update(load_task, advance=1)

            if len(conversations) >= limit:
                break

    console.print(
        f"[green]Loaded {len(conversations)} new conversations to process[/green]"
    )

    # Set up OpenAI client with instructor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = instructor.from_provider(model="openai/gpt-4.1-nano", async_client=True)

    # Control concurrency to avoid rate limits
    semaphore = asyncio.Semaphore(concurrency)

    console.print("\n[cyan]Processing conversations...[/cyan]")

    # Process conversations with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        process_task = progress.add_task(
            "Processing conversations", total=len(conversations)
        )

        tasks = [
            process_conversation(
                client, conversation, query_version, cache, semaphore, progress, process_task
            )
            for conversation in conversations
        ]

        # Process all conversations concurrently
        total_saved = 0
        for coro in asyncio.as_completed(tasks):
            try:
                saved_count = await coro
                total_saved += saved_count
            except Exception as e:
                console.print(f"[red]Task failed: {e}[/red]")

    console.print(f"\n[green]Saved {total_saved} new queries to database[/green]")

    # Print summary
    summary = get_results_summary(DB_PATH)

    console.print("\n[bold]Results summary:[/bold]")
    for version, count in summary["version_counts"].items():
        console.print(f"  [cyan]{version}:[/cyan] {count} queries")

    console.print(
        f"  [cyan]Unique conversations:[/cyan] {summary['unique_conversations']}"
    )
    console.print(f"\n[green]Database saved to:[/green] {DB_PATH}")
    console.print(f"[green]Cache directory:[/green] {CACHE_DIR}")


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(500, help="Number of conversations to process"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1, v2, v3, or v5)"
    ),
    clear_cache: bool = typer.Option(False, help="Clear the cache before starting"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
):
    """Generate synthetic queries from WildChat conversations"""
    asyncio.run(main(limit, query_version, clear_cache, concurrency))


if __name__ == "__main__":
    app()
