#!/usr/bin/env python3
"""
Verify Recall Script

This script loads synthetic queries from the SQLite database, performs searches
using ChromaDB, and verifies if the search results contain documents with the
same conversation hash as the original query.
"""

import asyncio

import sys
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
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from src.cache import setup_cache, GenericCache
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
    top_k: int = 30,  # Increased to 30 to capture all recall levels
) -> Dict[str, Any]:
    """Verify if search results contain the original conversation hash

    Returns:
        Dict with search results and position of matching hash (if found)
    """
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
            # Don't cache the full results to save space
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
    prompt_version: str,
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


async def process_queries_with_live_updates(
    dao: WildChatDAOBase,
    queries: List[Tuple[str, str, str]],
    cache: GenericCache,
    update_interval: int = 50,
    *,
    search_type: SearchType = SearchType.VECTOR,
) -> Dict[str, RecallMetrics]:
    """Process queries with live rolling metrics updates"""

    # Metrics by prompt version
    metrics_by_version = {"v1": RecallMetrics(), "v2": RecallMetrics()}

    # Control concurrency
    semaphore = asyncio.Semaphore(5)

    # Create layout for live display
    def make_layout() -> Layout:
        """Create the display layout"""
        layout = Layout()
        return layout

    with Live(make_layout(), refresh_per_second=4, console=console) as live:
        # Create task queue
        tasks = []

        for i, (conversation_hash, prompt_version, query) in enumerate(queries):
            task = asyncio.create_task(
                process_query_with_metrics(
                    dao,
                    conversation_hash,
                    prompt_version,
                    query,
                    metrics_by_version[prompt_version],
                    cache,
                    semaphore,
                    search_type=search_type,
                )
            )
            tasks.append(task)

            # Update display periodically
            if (i + 1) % update_interval == 0 or i == len(queries) - 1:
                # Wait for some tasks to complete
                completed, pending = await asyncio.wait(
                    tasks[: i + 1], return_when=asyncio.ALL_COMPLETED
                )

                # Update live display
                metrics_table = create_metrics_table(
                    metrics_by_version, title=f"Rolling Metrics (after {i + 1} queries)"
                )

                layout = Layout()
                layout.split_column(Panel(metrics_table, title="Live Metrics"))
                live.update(layout)

        # Wait for all remaining tasks
        await asyncio.gather(*tasks)

    return metrics_by_version


def create_metrics_table(
    metrics_by_version: Dict[str, RecallMetrics],
    title: str = "Recall Verification Results",
) -> Table:
    """Create a metrics table (used for both live updates and final results)"""
    table = Table(title=title)

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("v1", style="magenta", justify="right")
    table.add_column("v2", style="magenta", justify="right")

    # Add rows
    v1_metrics = metrics_by_version.get("v1", RecallMetrics())
    v2_metrics = metrics_by_version.get("v2", RecallMetrics())

    table.add_row(
        "Total Queries", str(v1_metrics.total_queries), str(v2_metrics.total_queries)
    )
    table.add_row(
        "Successful Searches",
        str(v1_metrics.successful_searches),
        str(v2_metrics.successful_searches),
    )
    table.add_row(
        "Recall@1",
        f"{v1_metrics.get_recall_at_k(1):.2%}",
        f"{v2_metrics.get_recall_at_k(1):.2%}",
    )
    table.add_row(
        "Recall@5",
        f"{v1_metrics.get_recall_at_k(5):.2%}",
        f"{v2_metrics.get_recall_at_k(5):.2%}",
    )
    table.add_row(
        "Recall@10",
        f"{v1_metrics.get_recall_at_k(10):.2%}",
        f"{v2_metrics.get_recall_at_k(10):.2%}",
    )
    table.add_row(
        "Recall@20",
        f"{v1_metrics.get_recall_at_k(20):.2%}",
        f"{v2_metrics.get_recall_at_k(20):.2%}",
    )
    table.add_row(
        "Recall@30",
        f"{v1_metrics.get_recall_at_k(30):.2%}",
        f"{v2_metrics.get_recall_at_k(30):.2%}",
    )
    table.add_row("Not Found", str(v1_metrics.not_found), str(v2_metrics.not_found))
    table.add_row(
        "Search Errors", str(v1_metrics.search_errors), str(v2_metrics.search_errors)
    )

    return table


def print_results_table(metrics_by_version: Dict[str, RecallMetrics]):
    """Print results in a nice table format"""
    table = create_metrics_table(metrics_by_version)
    console.print(table)


def merge_version_metrics(metrics_by_version: Dict[str, RecallMetrics]) -> RecallMetrics:
    """Merge v1/v2 RecallMetrics into an aggregate RecallMetrics instance."""
    agg = RecallMetrics()
    for metrics in metrics_by_version.values():
        agg.total_queries += metrics.total_queries
        agg.successful_searches += metrics.successful_searches
        agg.found_in_top_1 += metrics.found_in_top_1
        agg.found_in_top_5 += metrics.found_in_top_5
        agg.found_in_top_10 += metrics.found_in_top_10
        agg.found_in_top_20 += metrics.found_in_top_20
        agg.found_in_top_30 += metrics.found_in_top_30
        agg.not_found += metrics.not_found
        agg.search_errors += metrics.search_errors
    return agg


def create_multi_dao_table(metrics_by_dao: Dict[str, RecallMetrics]) -> Table:
    """Create a rich Table comparing multiple DAO recall metrics."""
    table = Table(title="Recall Metrics Across Backends")
    table.add_column("Backend", style="cyan", no_wrap=True)
    table.add_column("Queries", style="magenta", justify="right")
    table.add_column("Recall@1", style="green", justify="right")
    table.add_column("Recall@5", style="green", justify="right")
    table.add_column("Recall@10", style="green", justify="right")
    table.add_column("Recall@20", style="green", justify="right")
    table.add_column("Recall@30", style="green", justify="right")

    for backend, metrics in metrics_by_dao.items():
        table.add_row(
            backend,
            f"{metrics.total_queries:,}",
            f"{metrics.get_recall_at_k(1):.2%}",
            f"{metrics.get_recall_at_k(5):.2%}",
            f"{metrics.get_recall_at_k(10):.2%}",
            f"{metrics.get_recall_at_k(20):.2%}",
            f"{metrics.get_recall_at_k(30):.2%}",
        )
    return table


def create_multi_dao_table_split(metrics_by_dao_version: Dict[str, Dict[str, RecallMetrics]]) -> Table:
    """Create table with separate rows for v1 and v2 per backend."""
    table = Table(title="Recall Metrics per Backend and Version")
    table.add_column("Backend / Version", style="cyan", no_wrap=True)
    table.add_column("Queries", style="magenta", justify="right")
    table.add_column("Recall@1", style="green", justify="right")
    table.add_column("Recall@5", style="green", justify="right")
    table.add_column("Recall@10", style="green", justify="right")
    table.add_column("Recall@20", style="green", justify="right")
    table.add_column("Recall@30", style="green", justify="right")

    for backend, metrics_map in metrics_by_dao_version.items():
        for version in ("v1", "v2"):
            if version not in metrics_map:
                continue
            m = metrics_map[version]
            row_label = f"{backend} ({version})"
            table.add_row(
                row_label,
                f"{m.total_queries:,}",
                f"{m.get_recall_at_k(1):.2%}",
                f"{m.get_recall_at_k(5):.2%}",
                f"{m.get_recall_at_k(10):.2%}",
                f"{m.get_recall_at_k(20):.2%}",
                f"{m.get_recall_at_k(30):.2%}",
            )
    return table


async def main(
    limit: int = typer.Option(None, help="Limit number of queries to process"),
    update_interval: int = typer.Option(50, help="Update metrics every N queries"),
):
    """Verify recall of synthetic queries"""

    console.print("[bold green]Recall Verification Script[/bold green]")
    console.print("=" * 50)

    # Check if database exists
    if not DB_PATH.exists():
        console.print(f"[red]Database not found at {DB_PATH}[/red]")
        console.print("[yellow]Please run generate_synthetic_queries.py first[/yellow]")
        return

    # Set up disk cache
    console.print(f"\n[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
    cache = setup_cache(CACHE_DIR)

    # Load queries
    console.print("\n[cyan]Loading queries from database...[/cyan]")
    queries = load_queries_from_db(DB_PATH, limit=limit)

    if not queries:
        console.print("[red]No queries found in database[/red]")
        return

    console.print(f"[green]Loaded {len(queries)} queries[/green]")

    # Group by version for summary
    queries_by_version = defaultdict(int)
    for _, version, _ in queries:
        queries_by_version[version] += 1

    console.print("\n[cyan]Query distribution:[/cyan]")
    for version, count in queries_by_version.items():
        console.print(f"  {version}: {count} queries")

    # --------------------------------------------------
    # Build DAO configurations to evaluate
    # --------------------------------------------------

    dao_configs = []

    # ChromaDB (cloud/local)
    chroma_name = f"ChromaDB"
    chroma_dao = WildChatDAOChromaDB()
    dao_configs.append({"name": chroma_name, "dao": chroma_dao, "search_type": SearchType.VECTOR})

    # TurboPuffer variants (vector and full-text). Hybrid omitted for current evaluation.
    turbo_variants = [
        ("TurboPuffer ‑ Vector", SearchType.VECTOR),
        ("TurboPuffer ‑ FullText", SearchType.FULL_TEXT),
    ]

    for variant_name, stype in turbo_variants:
        dao_configs.append({
            "name": variant_name,
            "dao": WildChatDAOTurbopuffer(),
            "search_type": stype,
        })

    metrics_by_dao: Dict[str, RecallMetrics] = {}
    metrics_by_dao_version: Dict[str, Dict[str, RecallMetrics]] = {}

    for cfg in dao_configs:
        dao = cfg["dao"]
        dao_name = cfg["name"]
        stype = cfg["search_type"]

        console.print(f"\n[cyan]Connecting to {dao_name}...[/cyan]")
        try:
            await dao.connect()
            console.print(f"[green]Connected to {dao_name}[/green]")

            # Optional stats
            try:
                stats = await dao.get_stats()
                if stats:
                    console.print("[cyan]Collection stats:[/cyan]")
                    if "total_documents" in stats:
                        console.print(f"  Total documents: {stats.get('total_documents', 0):,}")
            except Exception:
                pass

        except Exception as e:
            console.print(f"[red]Failed to connect to {dao_name}: {e}[/red]")
            metrics_by_dao[dao_name] = RecallMetrics(total_queries=len(queries), search_errors=len(queries))
            continue

        console.print(
            f"\n[cyan]Verifying recall with live metrics using {dao_name} (search={stype.name})...[/cyan]"
        )
        console.print(f"[dim]Metrics will update every {update_interval} queries[/dim]\n")

        metrics_by_version = await process_queries_with_live_updates(
            dao,
            queries,
            cache,
            update_interval=update_interval,
            search_type=stype,
        )

        # Store per-version metrics
        metrics_by_dao_version[dao_name] = metrics_by_version

        # Merge v1/v2 into one aggregate for this DAO config
        metrics_by_dao[dao_name] = merge_version_metrics(metrics_by_version)

        await dao.disconnect()

    # Print combined results
    console.print("\n")
    all_dao_table   = create_multi_dao_table_split(metrics_by_dao_version)
    console.print(all_dao_table)

    # Save detailed results per DAO
    results_file = Path(__file__).parent / "recall_results.json"
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(queries),
        "dao_metrics": {
            name: metrics.get_summary() for name, metrics in metrics_by_dao.items()
        },
    }

    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    console.print(f"\n[green]Detailed results saved to:[/green] {results_file}")

    console.print("\n[cyan]Done![/cyan]")


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(None, help="Limit number of queries to process"),
    update_interval: int = typer.Option(50, help="Update metrics every N queries"),
):
    """Verify recall of synthetic queries"""
    asyncio.run(main(limit, update_interval))


if __name__ == "__main__":
    app()

# helper functions relocated above
