#!/usr/bin/env python3
"""
Compute Recall with Summaries

This script tests V2 queries (from PART03) against the summary-based embeddings
to demonstrate improved recall when the embedding strategy aligns with the query style.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
from datetime import datetime
import typer
import turbopuffer
from sentence_transformers import SentenceTransformer

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

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(
    str(Path(__file__).parent.parent / "PART03_synthetic_question_generation")
)

# Import cache from local src
from src.cache import setup_cache, GenericCache, NoOpCache

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


class SummaryTurboPufferClient:
    """Custom TurboPuffer client for summary data"""

    def __init__(self, namespace_name: str):
        self.namespace_name = namespace_name
        self.client = None
        self.namespace = None
        self.embedding_model = None

    def _get_embedding_model(self) -> SentenceTransformer:
        """Get or create the embedding model"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        return self.embedding_model

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        model = self._get_embedding_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        return [embedding.tolist() for embedding in embeddings]

    async def connect(self) -> None:
        """Connect to TurboPuffer"""
        api_key = os.getenv("TURBOPUFFER_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing required environment variable: TURBOPUFFER_API_KEY"
            )

        region = os.getenv("TURBOPUFFER_REGION", "gcp-us-central1")
        self.client = turbopuffer.Turbopuffer(api_key=api_key, region=region)
        self.namespace = self.client.namespace(self.namespace_name)

    async def disconnect(self) -> None:
        """Disconnect from TurboPuffer"""
        self.client = None
        self.namespace = None
        self.embedding_model = None

    async def search(self, query: str, top_k: int = 30) -> List[Dict[str, Any]]:
        """Search summaries and return results"""
        if not self.namespace:
            raise RuntimeError("Not connected to TurboPuffer. Call connect() first.")

        # Create embedding for query
        query_embedding = self._create_embeddings([query])[0]

        # Search with vector similarity
        results = self.namespace.query(
            rank_by=("vector", "ANN", query_embedding),
            top_k=top_k,
            include_attributes=["summary", "hash", "summary_version", "model"],
        )

        # Convert results to our format
        search_results = []
        for row in results.rows:
            result = {
                "id": row.id,
                "summary": getattr(row, "summary", ""),
                "hash": getattr(row, "hash", ""),
                "summary_version": getattr(row, "summary_version", ""),
                "model": getattr(row, "model", ""),
            }
            search_results.append(result)

        return search_results

    async def get_stats(self) -> Dict[str, Any]:
        """Get namespace statistics"""
        if not self.namespace:
            raise RuntimeError("Not connected to TurboPuffer. Call connect() first.")

        try:
            count_result = self.namespace.query(
                aggregate_by={"document_count": ("Count", "id")}
            )
            total_count = count_result.aggregations["document_count"]
            return {
                "total_documents": total_count,
                "namespace_name": self.namespace_name,
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "namespace_name": self.namespace_name,
            }


async def verify_single_query(
    client: SummaryTurboPufferClient,
    conversation_hash: str,
    query: str,
    cache: GenericCache,
    *,
    top_k: int = 30,
) -> Dict[str, Any]:
    """Verify if search results contain the original conversation hash"""

    # Create cache key
    cache_key = GenericCache.make_generic_key(
        "recall_summary", client.namespace_name, conversation_hash, query[:50]
    )

    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        start_time = time.time()

        # Perform search
        results = await client.search(query, top_k=top_k)

        end_time = time.time()
        query_time_ms = (end_time - start_time) * 1000

        # Check if conversation hash is in results
        position = -1

        # Check if target hash is in results
        if len(results) > 0:
            for i, result in enumerate(results):
                hash_value = result.get("hash", "")
                if hash_value == conversation_hash:
                    position = i  # Found it!
                    break

        result = {
            "success": True,
            "position": position,
            "total_results": len(results),
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
    client: SummaryTurboPufferClient,
    conversation_hash: str,
    query: str,
    metrics: RecallMetrics,
    cache: GenericCache,
    semaphore: asyncio.Semaphore,
) -> None:
    """Process a single query and update metrics"""
    async with semaphore:
        result = await verify_single_query(client, conversation_hash, query, cache)

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
    limit: int = typer.Option(None, help="Limit number of V2 queries to test"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1 or v2)"
    ),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
    no_cache: bool = typer.Option(False, help="Disable caching for fresh results"),
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
    if no_cache:
        console.print(f"\n[cyan]Cache disabled - running fresh queries[/cyan]")
        cache = NoOpCache()
    else:
        console.print(f"\n[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
        cache = setup_cache(CACHE_DIR)

    # Load V2 queries only
    console.print("\n[cyan]Loading V2 queries from database...[/cyan]")
    all_queries = load_queries_from_db(QUERIES_DB_PATH, limit=limit)

    # Filter for specified query version
    queries = [(h, v, q) for h, v, q in all_queries if v == query_version]

    if not queries:
        console.print(f"[red]No {query_version} queries found in database[/red]")
        return

    console.print(f"[green]Loaded {len(queries)} {query_version} queries[/green]")

    # Initialize custom TurboPuffer client
    namespace_name = f"wildchat-synthetic-summaries-{summary_version}"
    client = SummaryTurboPufferClient(namespace_name)

    console.print(
        f"\n[cyan]Connecting to TurboPuffer namespace: {namespace_name}[/cyan]"
    )
    try:
        await client.connect()
        console.print(f"[green]Connected to TurboPuffer[/green]")

        # Get stats
        try:
            stats = await client.get_stats()
            if stats and "total_documents" in stats:
                console.print(
                    f"[cyan]Total documents: {stats['total_documents']:,}[/cyan]"
                )
        except Exception as e:
            console.print(f"[yellow]Could not get stats: {e}[/yellow]")

    except Exception as e:
        console.print(f"[red]Failed to connect to TurboPuffer: {e}[/red]")
        return

    # Process queries
    console.print(
        f"\n[cyan]Testing {query_version} queries against {summary_version} summaries...[/cyan]"
    )

    metrics = RecallMetrics()
    semaphore = asyncio.Semaphore(5)

    # Create tasks
    tasks = []
    for conversation_hash, _, query in queries:
        task = asyncio.create_task(
            process_query_with_metrics(
                client,
                conversation_hash,
                query,
                metrics,
                cache,
                semaphore,
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

    await client.disconnect()

    # Display results
    console.print("\n[bold]Results Summary:[/bold]")

    summary = metrics.get_summary()

    results_table = Table(
        title=f"{query_version} Queries vs {summary_version} Summary Embeddings"
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
    results_file = (
        Path(__file__).parent / f"recall_results_summaries_{summary_version}.json"
    )
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "summary_version": summary_version,
        "query_version": query_version,
        "db_backend": "turbopuffer",
        "total_queries": len(queries),
        "metrics": summary,
        "comparison": {
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


app = typer.Typer()


@app.command()
def run(
    limit: int = typer.Option(None, help="Limit number of queries to test"),
    query_version: str = typer.Option(
        "v2", help="Which query version to test (v1 or v2)"
    ),
    summary_version: str = typer.Option(
        "v2", help="Which summary version to test (v1 or v2)"
    ),
    no_cache: bool = typer.Option(False, help="Disable caching for fresh results"),
):
    asyncio.run(main(limit, query_version, summary_version, no_cache))


if __name__ == "__main__":
    app()
