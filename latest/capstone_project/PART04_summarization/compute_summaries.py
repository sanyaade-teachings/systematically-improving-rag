#!/usr/bin/env python3
"""
Synthetic Summary Generation Script

This script loads conversations from WildChat dataset and generates
synthetic summaries using both v1 and v2 prompt versions. Results are saved
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

# Import from our package
from src.dataloader import WildChatDataLoader
from src.summarization_prompts import (
    conversation_summary_v1,
    conversation_summary_v2,
)
from src.db import (
    setup_database,
    save_summary_to_db,
    get_processed_conversations,
    get_existing_summaries,
    get_results_summary,
)
from src.cache import setup_cache, GenericCache

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

# Database and cache setup
DB_PATH = Path(__file__).parent / "data" / "synthetic_summaries.db"
CACHE_DIR = Path(__file__).parent / "data" / ".cache"


async def process_conversation_version(
    client,
    conversation: Dict[str, Any],
    version: str,
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
) -> str:
    """Process a single conversation with one version (v1 or v2)"""
    async with semaphore:
        conversation_hash = conversation["conversation_hash"]
        messages = conversation["conversation"]
        cache_key = GenericCache.make_conversation_key(
            conversation_hash, f"summary_{version}"
        )

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        try:
            if version == "v1":
                result = await conversation_summary_v1(client, messages)
            else:  # v2
                result = await conversation_summary_v2(client, messages)

            summary = result.summary if hasattr(result, "summary") else ""

            # Cache the result
            cache.set(cache_key, summary)

            return summary

        except Exception as e:
            console.print(
                f"[red]Error processing {conversation_hash} {version}: {e}[/red]"
            )
            return ""


async def process_conversation(
    client,
    conversation: Dict[str, Any],
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
    progress: Progress,
    task_id,
    model: str,
    existing_summaries: set,
) -> int:
    """Process a single conversation with both v1 and v2 generators and save immediately"""
    conversation_hash = conversation["conversation_hash"]
    saved_count = 0

    try:
        # Check which versions need to be processed
        need_v1 = (conversation_hash, "v1") not in existing_summaries
        need_v2 = (conversation_hash, "v2") not in existing_summaries

        tasks = []
        if need_v1:
            tasks.append(
                (
                    "v1",
                    process_conversation_version(
                        client, conversation, "v1", cache, semaphore
                    ),
                )
            )
        if need_v2:
            tasks.append(
                (
                    "v2",
                    process_conversation_version(
                        client, conversation, "v2", cache, semaphore
                    ),
                )
            )

        # Process only needed versions
        if tasks:
            results = await asyncio.gather(*[task[1] for task in tasks])

            for i, (version, _) in enumerate(tasks):
                summary = results[i]
                if summary and save_summary_to_db(
                    DB_PATH, conversation_hash, version, summary, model
                ):
                    saved_count += 1

        progress.update(task_id, advance=1)

    except Exception as e:
        console.print(
            f"[red]Failed to process conversation {conversation_hash}: {e}[/red]"
        )

    return saved_count


async def main(
    limit: int = typer.Option(500, help="Number of conversations to process"),
    clear_cache: bool = typer.Option(False, help="Clear the cache before starting"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
):
    """Generate synthetic summaries from WildChat conversations"""

    console.print("[bold green]Synthetic Summary Generation[/bold green]")
    console.print("=" * 50)

    console.print(f"\n[cyan]Setting up database at {DB_PATH}[/cyan]")
    setup_database(DB_PATH)

    # Set up disk cache
    console.print(f"[cyan]Setting up disk cache at {CACHE_DIR}[/cyan]")
    cache = setup_cache(CACHE_DIR, clear_cache=clear_cache)

    MODEL = "openai/gpt-4.1-nano"

    # Check for already existing summaries for this model
    existing_summaries = get_existing_summaries(DB_PATH, MODEL)
    if existing_summaries:
        console.print(
            f"[yellow]Found {len(existing_summaries)} existing summaries for model {MODEL}[/yellow]"
        )

    console.print(f"\n[cyan]Loading {limit} conversations[/cyan]")
    # Load conversations
    loader = (
        WildChatDataLoader()
    )  # No limit on dataset loader - let stream_conversations handle filtering
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
            # Skip conversations that already have both v1 and v2 summaries for this model
            conversation_hash = conversation["conversation_hash"]
            has_v1 = (conversation_hash, "v1") in existing_summaries
            has_v2 = (conversation_hash, "v2") in existing_summaries

            if not (has_v1 and has_v2):
                conversations.append(conversation)
                progress.update(load_task, advance=1)

            if len(conversations) >= limit:
                break

    console.print(
        f"[green]Loaded {len(conversations)} new conversations to process[/green]"
    )

    client = instructor.from_provider(model=MODEL, async_client=True)

    # Control concurrency to avoid rate limits
    console.print(
        f"\n[cyan]Processing conversations with {concurrency} concurrency[/cyan]"
    )
    semaphore = asyncio.Semaphore(concurrency)

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
                client,
                conversation,
                cache,
                semaphore,
                progress,
                process_task,
                MODEL,
                existing_summaries,
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

    console.print(f"\n[green]Saved {total_saved} new summaries to database[/green]")

    # Print summary
    summary = get_results_summary(DB_PATH)

    console.print("\n[bold]Results summary:[/bold]")
    for version, count in summary["version_counts"].items():
        console.print(f"  [cyan]{version}:[/cyan] {count} summaries")

    console.print("\n[bold]By model:[/bold]")
    for model, count in summary["model_counts"].items():
        console.print(f"  [cyan]{model}:[/cyan] {count} summaries")

    console.print(
        f"\n[cyan]Unique conversations:[/cyan] {summary['unique_conversations']}"
    )
    console.print(f"\n[green]Database saved to:[/green] {DB_PATH}")
    console.print(f"[green]Cache directory:[/green] {CACHE_DIR}")


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(500, help="Number of conversations to process"),
    clear_cache: bool = typer.Option(False, help="Clear the cache before starting"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
):
    """Generate synthetic summaries from WildChat conversations"""
    asyncio.run(main(limit, clear_cache, concurrency))


if __name__ == "__main__":
    app()
