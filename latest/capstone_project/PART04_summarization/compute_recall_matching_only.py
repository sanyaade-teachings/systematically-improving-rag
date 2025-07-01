#!/usr/bin/env python3
"""
Compute Recall for V2 queries that have matching summaries

This script tests ONLY V2 queries for conversations that we have summaries for.
"""

import asyncio
import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import json
from datetime import datetime
import typer

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))

# Import DAOs
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer
from utils.dao.wildchat_dao import SearchRequest, SearchType, WildChatDAOBase

# Import cache from local src
from src.cache import setup_cache, GenericCache

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database paths
QUERIES_DB_PATH = (
    Path(__file__).parent.parent
    / "PART03_synthetic_question_generation"
    / "data"
    / "synthetic_queries.db"
)
SUMMARIES_DB_PATH = Path(__file__).parent / "data" / "synthetic_summaries.db"
CACHE_DIR = Path(__file__).parent / "data" / ".cache_recall"


@dataclass
class RecallMetrics:
    """Container for recall metrics"""

    total_queries: int = 0
    successful_searches: int = 0
    found_in_top_1: int = 0
    found_in_top_5: int = 0
    found_in_top_10: int = 0
    found_in_top_20: int = 0
    found_in_top_30: int = 0
    not_found: int = 0
    search_errors: int = 0

    def get_recall_at_k(self, k: int) -> float:
        """Calculate recall@k"""
        if self.total_queries == 0:
            return 0.0

        if k == 1:
            return self.found_in_top_1 / self.total_queries
        elif k == 5:
            return self.found_in_top_5 / self.total_queries
        elif k == 10:
            return self.found_in_top_10 / self.total_queries
        elif k == 20:
            return self.found_in_top_20 / self.total_queries
        elif k == 30:
            return self.found_in_top_30 / self.total_queries
        else:
            return 0.0


def get_conversations_with_summaries() -> Set[str]:
    """Get set of conversation hashes that have summaries"""
    conn = sqlite3.connect(SUMMARIES_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT conversation_hash FROM synthetic_summaries")
    hashes = {row[0] for row in cursor.fetchall()}
    conn.close()
    return hashes


def load_matching_v2_queries(limit: int = None) -> List[Tuple[str, str, str]]:
    """Load V2 queries only for conversations that have summaries"""

    # Get conversations with summaries
    summary_hashes = get_conversations_with_summaries()
    console.print(
        f"[cyan]Found {len(summary_hashes)} conversations with summaries[/cyan]"
    )

    # Load V2 queries
    conn = sqlite3.connect(QUERIES_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT conversation_hash, prompt_version, query 
        FROM synthetic_queries
        WHERE prompt_version = 'v2'
        ORDER BY created_at DESC
    """)

    # Filter for matching conversations
    matching_queries = []
    for row in cursor.fetchall():
        if row[0] in summary_hashes:
            matching_queries.append(row)
            if limit and len(matching_queries) >= limit:
                break

    conn.close()
    return matching_queries


async def verify_single_query(
    dao: WildChatDAOBase,
    conversation_hash: str,
    query: str,
    cache: GenericCache,
    *,
    search_type: SearchType = SearchType.VECTOR,
    top_k: int = 30,
) -> Dict[str, Any]:
    """Verify if search results contain the original conversation hash"""

    # Create cache key
    dao_type = dao.__class__.__name__
    cache_key = GenericCache.make_generic_key(
        "recall_summary_match",
        dao_type,
        search_type.name,
        conversation_hash,
        query[:50],
    )

    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        # Create search request
        request = SearchRequest(query=query, top_k=top_k, search_type=search_type)

        # Perform search
        results = await dao.search(request)

        # Check if conversation hash is in results
        position = -1
        for i, result in enumerate(results.results):
            # The hash is stored in metadata
            result_hash = result.metadata.get("hash", "")
            if result_hash == conversation_hash:
                position = i
                break

        result = {
            "success": True,
            "position": position,
            "total_results": len(results.results),
            "query_time_ms": results.query_time_ms,
        }

        # Cache the result
        cache.set(cache_key, result)

        return result

    except Exception as e:
        console.print(f"[red]Search error for query '{query[:50]}...': {e}[/red]")
        error_result = {"success": False, "error": str(e), "position": -1}
        cache.set(cache_key, error_result)
        return error_result


async def process_queries(
    dao: WildChatDAOBase,
    queries: List[Tuple[str, str, str]],
    cache: GenericCache,
) -> RecallMetrics:
    """Process queries and calculate metrics"""

    metrics = RecallMetrics()
    semaphore = asyncio.Semaphore(5)

    console.print(f"[cyan]Processing {len(queries)} queries...[/cyan]")

    async def process_single(query_data):
        conversation_hash, _, query = query_data
        async with semaphore:
            result = await verify_single_query(
                dao, conversation_hash, query, cache, search_type=SearchType.VECTOR
            )

            metrics.total_queries += 1

            if result["success"]:
                metrics.successful_searches += 1
                position = result["position"]

                if position == -1:
                    metrics.not_found += 1
                elif position == 0:
                    metrics.found_in_top_1 += 1
                    metrics.found_in_top_5 += 1
                    metrics.found_in_top_10 += 1
                    metrics.found_in_top_20 += 1
                    metrics.found_in_top_30 += 1
                elif position < 5:
                    metrics.found_in_top_5 += 1
                    metrics.found_in_top_10 += 1
                    metrics.found_in_top_20 += 1
                    metrics.found_in_top_30 += 1
                elif position < 10:
                    metrics.found_in_top_10 += 1
                    metrics.found_in_top_20 += 1
                    metrics.found_in_top_30 += 1
                elif position < 20:
                    metrics.found_in_top_20 += 1
                    metrics.found_in_top_30 += 1
                elif position < 30:
                    metrics.found_in_top_30 += 1
            else:
                metrics.search_errors += 1

    # Process all queries
    tasks = [process_single(q) for q in queries]

    # Show progress
    completed = 0
    with console.status("[cyan]Processing queries...[/cyan]") as status:
        for coro in asyncio.as_completed(tasks):
            await coro
            completed += 1
            if completed % 10 == 0:
                status.update(
                    f"[cyan]Processing queries... {completed}/{len(tasks)}[/cyan]"
                )

    return metrics


async def main(
    limit: int = typer.Option(None, help="Limit number of queries to test"),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
):
    """Test V2 queries against summary embeddings (only matching conversations)"""

    console.print(
        "[bold green]Recall Verification - Matching Conversations Only[/bold green]"
    )
    console.print("=" * 50)

    # Check if databases exist
    if not QUERIES_DB_PATH.exists():
        console.print(f"[red]Queries database not found at {QUERIES_DB_PATH}[/red]")
        return

    if not SUMMARIES_DB_PATH.exists():
        console.print(f"[red]Summaries database not found at {SUMMARIES_DB_PATH}[/red]")
        return

    # Set up cache
    console.print(f"\n[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
    cache = setup_cache(CACHE_DIR)

    # Load matching V2 queries
    console.print("\n[cyan]Loading V2 queries that have summaries...[/cyan]")
    matching_queries = load_matching_v2_queries(limit)

    if not matching_queries:
        console.print("[red]No matching V2 queries found[/red]")
        return

    console.print(
        f"[green]Found {len(matching_queries)} V2 queries with corresponding summaries[/green]"
    )

    # Initialize TurboPuffer DAO
    table_name = f"wildchat-summaries-{summary_version}"
    dao = WildChatDAOTurbopuffer(table_name=table_name)
    dao_name = f"TurboPuffer (summaries {summary_version})"

    console.print(f"\n[cyan]Connecting to {dao_name}...[/cyan]")
    try:
        await dao.connect()
        console.print(f"[green]Connected to {dao_name}[/green]")

        # Get stats
        try:
            stats = await dao.get_stats()
            if stats and "total_documents" in stats:
                console.print(
                    f"[cyan]Total documents: {stats['total_documents']:,}[/cyan]"
                )
        except Exception:
            pass

    except Exception as e:
        console.print(f"[red]Failed to connect to {dao_name}: {e}[/red]")
        return

    # Process queries
    console.print(
        f"\n[cyan]Testing V2 queries against {summary_version} summaries...[/cyan]"
    )

    metrics = await process_queries(dao, matching_queries, cache)

    await dao.disconnect()

    # Display results
    console.print("\n[bold]Results Summary:[/bold]")

    results_table = Table(
        title="V2 Queries vs Summary-based Embeddings (Matching Only)"
    )
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="magenta", justify="right")

    results_table.add_row("Total V2 Queries Tested", str(metrics.total_queries))
    results_table.add_row("Successful Searches", str(metrics.successful_searches))
    results_table.add_row("Recall@1", f"{metrics.get_recall_at_k(1):.2%}")
    results_table.add_row("Recall@5", f"{metrics.get_recall_at_k(5):.2%}")
    results_table.add_row("Recall@10", f"{metrics.get_recall_at_k(10):.2%}")
    results_table.add_row("Recall@20", f"{metrics.get_recall_at_k(20):.2%}")
    results_table.add_row("Recall@30", f"{metrics.get_recall_at_k(30):.2%}")
    results_table.add_row("Not Found", str(metrics.not_found))
    results_table.add_row("Search Errors", str(metrics.search_errors))

    console.print(results_table)

    # Compare with typical V2 performance on first-message-only
    console.print("\n[bold]Expected Improvement:[/bold]")
    console.print("Original V2 queries with first-message-only embeddings: ~2% recall")
    console.print(
        f"V2 queries with {summary_version} summaries: {metrics.get_recall_at_k(10):.2%} recall@10"
    )

    if metrics.get_recall_at_k(10) > 0.15:  # If we get more than 15% recall
        console.print(
            "\n[green]✓ Success! Summaries significantly improved V2 query recall![/green]"
        )
    else:
        console.print(
            "\n[yellow]⚠ Recall is lower than expected. Check summary quality.[/yellow]"
        )


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(None, help="Limit number of queries to test"),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
):
    """Test V2 queries against summary embeddings (matching conversations only)"""
    asyncio.run(main(limit, summary_version))


if __name__ == "__main__":
    app()
