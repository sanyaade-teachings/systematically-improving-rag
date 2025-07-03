#!/usr/bin/env python3
"""
Verify Recall Script

This script loads synthetic queries from the SQLite database, performs searches
using ChromaDB or TurboPuffer, and verifies if the search results contain documents
with the same conversation hash as the original query.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
from datetime import datetime
import typer

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from src.cache import setup_cache, GenericCache, NoOpCache
from src.db import load_queries_from_db

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import DAOs
from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer
from utils.dao.wildchat_dao import SearchRequest, SearchType, WildChatDAOBase

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database and cache paths
DB_PATH = Path(__file__).parent / "data" / "synthetic_queries.db"
CACHE_DIR = Path(__file__).parent / "data" / ".cache"


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

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of metrics"""
        return {
            "total_queries": self.total_queries,
            "successful_searches": self.successful_searches,
            "recall@1": self.get_recall_at_k(1),
            "recall@5": self.get_recall_at_k(5),
            "recall@10": self.get_recall_at_k(10),
            "recall@20": self.get_recall_at_k(20),
            "recall@30": self.get_recall_at_k(30),
            "not_found": self.not_found,
            "search_errors": self.search_errors,
            "error_rate": self.search_errors / self.total_queries
            if self.total_queries > 0
            else 0,
        }


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
    
    # Create cache key with DAO type
    dao_type = dao.__class__.__name__
    cache_key = GenericCache.make_generic_key(
        "recall", dao_type, search_type.name, conversation_hash, query[:50]
    )

    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        start_time = time.time()
        
        # Create search request
        request = SearchRequest(query=query, top_k=top_k, search_type=search_type)

        # Perform search
        results = await dao.search(request)
        
        end_time = time.time()
        query_time_ms = (end_time - start_time) * 1000

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
            "query_time_ms": query_time_ms,
        }

        # Cache the result
        cache.set(cache_key, result)

        return result

    except Exception as e:
        console.print(f"[red]Search error for query '{query[:50]}...': {e}[/red]")
        error_result = {"success": False, "error": str(e), "position": -1}
        # Also cache errors to avoid retrying
        cache.set(cache_key, error_result)
        return error_result


async def process_query_with_metrics(
    dao: WildChatDAOBase,
    conversation_hash: str,
    query: str,
    metrics: RecallMetrics,
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
    *,
    search_type: SearchType = SearchType.VECTOR,
) -> None:
    """Process a single query and update metrics"""
    async with semaphore:
        result = await verify_single_query(
            dao, conversation_hash, query, cache, search_type=search_type
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


async def main(
    limit: int = typer.Option(None, help="Limit number of queries to process"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1 or v2)"
    ),
    backend: str = typer.Option(
        "chromadb", help="Backend to use (chromadb or turbopuffer)"
    ),
    search_type: str = typer.Option(
        "vector", help="Search type (vector, full_text, or hybrid)"
    ),
    no_cache: bool = typer.Option(False, help="Disable caching for fresh results"),
):
    """Verify recall of synthetic queries"""

    console.print("[bold green]Recall Verification Script[/bold green]")
    console.print("=" * 50)

    # Check if database exists
    if not DB_PATH.exists():
        console.print(f"[red]Database not found at {DB_PATH}[/red]")
        console.print("[yellow]Please run compute_synth_questions.py first[/yellow]")
        return

    # Set up disk cache
    if no_cache:
        console.print(f"\n[cyan]Cache disabled - running fresh queries[/cyan]")
        cache = NoOpCache()
    else:
        console.print(f"\n[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
        cache = setup_cache(CACHE_DIR)

    # Load queries
    console.print(f"\n[cyan]Loading {query_version} queries from database...[/cyan]")
    all_queries = load_queries_from_db(DB_PATH, limit=limit)

    # Filter for specified query version
    queries = [(h, v, q) for h, v, q in all_queries if v == query_version]

    if not queries:
        console.print(f"[red]No {query_version} queries found in database[/red]")
        return

    console.print(f"[green]Loaded {len(queries)} {query_version} queries[/green]")

    # Initialize DAO
    search_type_enum = SearchType.VECTOR
    if search_type.lower() == "full_text":
        search_type_enum = SearchType.FULL_TEXT
    elif search_type.lower() == "hybrid":
        search_type_enum = SearchType.HYBRID

    if backend.lower() == "chromadb":
        dao = WildChatDAOChromaDB()
        dao_name = "ChromaDB"
    elif backend.lower() == "turbopuffer":
        dao = WildChatDAOTurbopuffer()
        dao_name = "TurboPuffer"
    else:
        console.print(f"[red]Unknown backend: {backend}[/red]")
        return

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
        except Exception as e:
            console.print(f"[yellow]Could not get stats: {e}[/yellow]")

    except Exception as e:
        console.print(f"[red]Failed to connect to {dao_name}: {e}[/red]")
        return

    # Process queries
    console.print(
        f"\n[cyan]Testing {query_version} queries against {dao_name} ({search_type})...[/cyan]"
    )

    metrics = RecallMetrics()
    semaphore = asyncio.Semaphore(5)

    # Create tasks
    tasks = []
    for conversation_hash, _, query in queries:
        task = asyncio.create_task(
            process_query_with_metrics(
                dao,
                conversation_hash,
                query,
                metrics,
                cache,
                semaphore,
                search_type=search_type_enum,
            )
        )
        tasks.append(task)

    # Process with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing queries...", total=len(tasks))

        for coro in asyncio.as_completed(tasks):
            await coro
            progress.update(task, advance=1)

    await dao.disconnect()

    # Display results
    console.print("\n[bold]Results Summary:[/bold]")

    summary = metrics.get_summary()

    results_table = Table(
        title=f"{query_version} Queries vs {dao_name} ({search_type})"
    )
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="magenta", justify="right")

    results_table.add_row(
        f"Total {query_version} Queries", str(summary["total_queries"])
    )
    results_table.add_row("Successful Searches", str(summary["successful_searches"]))
    results_table.add_row("Recall@1", f"{summary['recall@1']:.2%}")
    results_table.add_row("Recall@5", f"{summary['recall@5']:.2%}")
    results_table.add_row("Recall@10", f"{summary['recall@10']:.2%}")
    results_table.add_row("Recall@20", f"{summary['recall@20']:.2%}")
    results_table.add_row("Recall@30", f"{summary['recall@30']:.2%}")
    results_table.add_row("Not Found", str(summary["not_found"]))
    results_table.add_row("Search Errors", str(summary["search_errors"]))

    console.print(results_table)

    # Save results
    results_file = Path(__file__).parent / f"recall_results_{backend}_{query_version}.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "query_version": query_version,
        "backend": backend,
        "search_type": search_type,
        "total_queries": len(queries),
        "metrics": summary,
    }

    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    console.print(f"\n[green]Results saved to:[/green] {results_file}")


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(None, help="Limit number of queries to process"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1 or v2)"
    ),
    backend: str = typer.Option(
        "chromadb", help="Backend to use (chromadb or turbopuffer)"
    ),
    search_type: str = typer.Option(
        "vector", help="Search type (vector, full_text, or hybrid)"
    ),
    no_cache: bool = typer.Option(False, help="Disable caching for fresh results"),
):
    """Verify recall of synthetic queries"""
    asyncio.run(main(limit, query_version, backend, search_type, no_cache))


if __name__ == "__main__":
    app()
