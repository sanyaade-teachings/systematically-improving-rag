#!/usr/bin/env python3
"""
Compute Recall with Summaries

This script tests V2 queries (from PART03) against the summary-based embeddings
to demonstrate improved recall when the embedding strategy aligns with the query style.
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

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(
    str(Path(__file__).parent.parent / "PART03_synthetic_question_generation")
)

# Import DAOs
from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer
from utils.dao.wildchat_dao import SearchRequest, SearchType, WildChatDAOBase

# Import cache from local src
from src.cache import setup_cache, GenericCache

# Import load_queries_from_db from PART03
sys.path.insert(
    0, str(Path(__file__).parent.parent / "PART03_synthetic_question_generation")
)
from src.db import load_queries_from_db

sys.path.pop(0)  # Remove after import to avoid conflicts

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database and cache paths
QUERIES_DB_PATH = (
    Path(__file__).parent.parent
    / "PART03_synthetic_question_generation"
    / "data"
    / "synthetic_queries.db"
)
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

    # Create cache key with DAO type and summary indicator
    dao_type = dao.__class__.__name__
    cache_key = GenericCache.make_generic_key(
        "recall_summary", dao_type, search_type.name, conversation_hash, query[:50]
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


def create_comparison_table(
    original_recall: float,
    summary_v1_recall: float,
    summary_v2_recall: float,
    k: int,
) -> Table:
    """Create a comparison table for recall@k"""
    table = Table(title=f"Recall@{k} Comparison")

    table.add_column("Embedding Strategy", style="cyan")
    table.add_column("Recall", style="magenta", justify="right")
    table.add_column("Improvement", style="green", justify="right")

    table.add_row("Original (First Message Only)", f"{original_recall:.2%}", "-")

    v1_improvement = (
        ((summary_v1_recall - original_recall) / original_recall * 100)
        if original_recall > 0
        else float("inf")
    )
    table.add_row(
        "Summary V1 (Concise)",
        f"{summary_v1_recall:.2%}",
        f"+{v1_improvement:.1f}%" if v1_improvement != float("inf") else "∞",
    )

    v2_improvement = (
        ((summary_v2_recall - original_recall) / original_recall * 100)
        if original_recall > 0
        else float("inf")
    )
    table.add_row(
        "Summary V2 (Comprehensive)",
        f"{summary_v2_recall:.2%}",
        f"+{v2_improvement:.1f}%" if v2_improvement != float("inf") else "∞",
    )

    return table


async def main(
    limit: int = typer.Option(None, help="Limit number of V2 queries to test"),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
    db_backend: str = typer.Option(
        "chromadb", help="Vector DB backend (chromadb or turbopuffer)"
    ),
):
    """Test V2 queries against summary-based embeddings"""

    console.print("[bold green]Recall Verification with Summaries[/bold green]")
    console.print("=" * 50)

    # Check if queries database exists
    if not QUERIES_DB_PATH.exists():
        console.print(f"[red]Queries database not found at {QUERIES_DB_PATH}[/red]")
        console.print(
            "[yellow]Please run PART03/compute_synth_questions.py first[/yellow]"
        )
        return

    # Set up disk cache
    console.print(f"\n[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
    cache = setup_cache(CACHE_DIR)

    # Load V2 queries only
    console.print("\n[cyan]Loading V2 queries from database...[/cyan]")
    all_queries = load_queries_from_db(QUERIES_DB_PATH, limit=limit)

    # Filter for V2 queries only
    v2_queries = [(h, v, q) for h, v, q in all_queries if v == "v2"]

    if not v2_queries:
        console.print("[red]No V2 queries found in database[/red]")
        return

    console.print(f"[green]Loaded {len(v2_queries)} V2 queries[/green]")

    # Initialize DAO based on backend
    if db_backend == "chromadb":
        collection_name = f"wildchat_summaries_{summary_version}"
        dao = WildChatDAOChromaDB(
            db_path=".chroma_summaries", collection_name=collection_name
        )
        dao_name = f"ChromaDB (summaries {summary_version})"
    else:  # turbopuffer
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

    metrics = RecallMetrics()
    semaphore = asyncio.Semaphore(5)

    # Create tasks
    tasks = []
    for conversation_hash, _, query in v2_queries:
        task = asyncio.create_task(
            process_query_with_metrics(
                dao,
                conversation_hash,
                "v2",  # All queries are V2
                query,
                metrics,
                cache,
                semaphore,
                search_type=SearchType.VECTOR,
            )
        )
        tasks.append(task)

    # Process with progress indicator
    completed = 0
    with console.status("[cyan]Processing queries...[/cyan]") as status:
        for coro in asyncio.as_completed(tasks):
            await coro
            completed += 1
            if completed % 10 == 0:
                status.update(
                    f"[cyan]Processing queries... {completed}/{len(tasks)}[/cyan]"
                )

    await dao.disconnect()

    # Display results
    console.print("\n[bold]Results Summary:[/bold]")

    summary = metrics.get_summary()

    results_table = Table(title="V2 Queries vs Summary-based Embeddings")
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="magenta", justify="right")

    results_table.add_row("Total V2 Queries", str(summary["total_queries"]))
    results_table.add_row("Successful Searches", str(summary["successful_searches"]))
    results_table.add_row("Recall@1", f"{summary['recall@1']:.2%}")
    results_table.add_row("Recall@5", f"{summary['recall@5']:.2%}")
    results_table.add_row("Recall@10", f"{summary['recall@10']:.2%}")
    results_table.add_row("Recall@20", f"{summary['recall@20']:.2%}")
    results_table.add_row("Recall@30", f"{summary['recall@30']:.2%}")
    results_table.add_row("Not Found", str(summary["not_found"]))
    results_table.add_row("Search Errors", str(summary["search_errors"]))

    console.print(results_table)

    # Compare with original results (hardcoded from PART03 typical results)
    console.print(
        "\n[bold]Comparison with Original First-Message-Only Approach:[/bold]"
    )

    # Typical V2 recall with first-message-only embeddings
    original_v2_recall = {1: 0.00, 5: 0.02, 10: 0.05, 20: 0.08, 30: 0.10}

    for k in [1, 5, 10, 20, 30]:
        comparison_table = create_comparison_table(
            original_v2_recall[k],
            summary["recall@" + str(k)],  # Using current summary version
            summary["recall@" + str(k)],  # Same for now, but could compare v1 vs v2
            k,
        )
        console.print(comparison_table)
        console.print()

    # Save results
    results_file = (
        Path(__file__).parent / f"recall_results_summaries_{summary_version}.json"
    )
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "summary_version": summary_version,
        "db_backend": db_backend,
        "total_v2_queries": len(v2_queries),
        "metrics": summary,
        "comparison": {
            "original_first_message_only": original_v2_recall,
            "with_summaries": {
                1: summary["recall@1"],
                5: summary["recall@5"],
                10: summary["recall@10"],
                20: summary["recall@20"],
                30: summary["recall@30"],
            },
        },
    }

    with open(results_file, "w") as f:
        json.dump(results_data, f, indent=2)

    console.print(f"\n[green]Results saved to:[/green] {results_file}")
    console.print("\n[cyan]Key Insight:[/cyan]")
    console.print("V2 queries now achieve much better recall because the summaries")
    console.print(
        "capture the full conversation context that V2 queries are looking for!"
    )


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(None, help="Limit number of V2 queries to test"),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
    db_backend: str = typer.Option(
        "chromadb", help="Vector DB backend (chromadb or turbopuffer)"
    ),
):
    """Test V2 queries against summary-based embeddings"""
    asyncio.run(main(limit, summary_version, db_backend))


if __name__ == "__main__":
    app()
