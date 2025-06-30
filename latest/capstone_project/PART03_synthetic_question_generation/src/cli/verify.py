"""Verify recall of synthetic queries CLI command."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao import SearchRequest, SearchType
from ..storage import QueryDatabase, CacheManager
from ..config import Config


console = Console()


@dataclass
class RecallMetrics:
    """Container for recall metrics."""
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
        """Calculate recall@k."""
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
        """Get summary of metrics."""
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
            "error_rate": self.search_errors / self.total_queries if self.total_queries > 0 else 0
        }


async def verify_single_query(
    dao: WildChatDAOChromaDB,
    conversation_hash: str,
    query: str,
    cache: CacheManager,
    top_k: int = 30
) -> Dict[str, Any]:
    """Verify if search results contain the original conversation hash."""
    # Create cache key
    cache_key = cache.create_recall_key(conversation_hash, query)
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    try:
        # Create search request
        request = SearchRequest(
            query=query,
            top_k=top_k,
            search_type=SearchType.VECTOR
        )
        
        # Perform search
        results = await dao.search(request)
        
        # Check if conversation hash is in results
        position = -1
        for i, result in enumerate(results.results):
            # The hash is stored in metadata
            result_hash = result.metadata.get('hash', '')
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
        error_result = {
            "success": False,
            "error": str(e),
            "position": -1
        }
        # Also cache errors to avoid retrying
        cache.set(cache_key, error_result)
        return error_result


async def process_query_with_metrics(
    dao: WildChatDAOChromaDB,
    conversation_hash: str,
    prompt_version: str,
    query: str,
    metrics: RecallMetrics,
    cache: CacheManager,
    semaphore: asyncio.Semaphore
) -> None:
    """Process a single query and update metrics."""
    async with semaphore:
        result = await verify_single_query(dao, conversation_hash, query, cache)
        
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


def create_metrics_table(metrics_by_version: Dict[str, RecallMetrics], title: str = "Recall Verification Results") -> Table:
    """Create a metrics table."""
    table = Table(title=title)
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    for version in sorted(metrics_by_version.keys()):
        table.add_column(version, style="magenta", justify="right")
    
    # Add rows
    metrics = list(metrics_by_version.values())
    metric_names = [
        ("Total Queries", lambda m: str(m.total_queries)),
        ("Successful Searches", lambda m: str(m.successful_searches)),
        ("Recall@1", lambda m: f"{m.get_recall_at_k(1):.2%}"),
        ("Recall@5", lambda m: f"{m.get_recall_at_k(5):.2%}"),
        ("Recall@10", lambda m: f"{m.get_recall_at_k(10):.2%}"),
        ("Recall@20", lambda m: f"{m.get_recall_at_k(20):.2%}"),
        ("Recall@30", lambda m: f"{m.get_recall_at_k(30):.2%}"),
        ("Not Found", lambda m: str(m.not_found)),
        ("Search Errors", lambda m: str(m.search_errors))
    ]
    
    for name, getter in metric_names:
        row = [name]
        for version in sorted(metrics_by_version.keys()):
            row.append(getter(metrics_by_version[version]))
        table.add_row(*row)
    
    return table


async def process_queries_with_live_updates(
    dao: WildChatDAOChromaDB,
    queries: List[Tuple[str, str, str]],
    cache: CacheManager,
    update_interval: int = 50,
    max_concurrent: int = 5
) -> Dict[str, RecallMetrics]:
    """Process queries with live rolling metrics updates."""
    # Metrics by prompt version
    metrics_by_version = defaultdict(RecallMetrics)
    
    # Control concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Create layout for live display
    def make_layout() -> Layout:
        """Create the display layout."""
        layout = Layout()
        return layout
    
    with Live(make_layout(), refresh_per_second=4, console=console) as live:
        # Create task queue
        tasks = []
        
        for i, (conversation_hash, prompt_version, query) in enumerate(queries):
            task = asyncio.create_task(
                process_query_with_metrics(
                    dao, conversation_hash, prompt_version, query,
                    metrics_by_version[prompt_version], cache, semaphore
                )
            )
            tasks.append(task)
            
            # Update display periodically
            if (i + 1) % update_interval == 0 or i == len(queries) - 1:
                # Wait for some tasks to complete
                completed, pending = await asyncio.wait(
                    tasks[:i+1], 
                    return_when=asyncio.ALL_COMPLETED
                )
                
                # Update live display
                metrics_table = create_metrics_table(
                    metrics_by_version, 
                    title=f"Rolling Metrics (after {i+1} queries)"
                )
                
                layout = Layout()
                layout.split_column(
                    Panel(metrics_table, title="Live Metrics")
                )
                live.update(layout)
        
        # Wait for all remaining tasks
        await asyncio.gather(*tasks)
    
    return dict(metrics_by_version)


async def verify_recall(
    config: Config,
    limit: int,
    version: str,
    update_interval: int,
    export_path: str = None
):
    """Verify recall of synthetic queries."""
    console.print("[bold green]Recall Verification[/bold green]")
    console.print("="*50)
    
    # Ensure directories exist
    config.ensure_dirs()
    
    # Initialize storage
    db = QueryDatabase(config.db_path)
    cache = CacheManager(config.recall_cache_dir)
    
    console.print(f"\n[cyan]Using recall cache at: {config.recall_cache_dir}[/cyan]")
    cache_size = cache.size()
    if cache_size > 0:
        console.print(f"[yellow]Found {cache_size} cached results[/yellow]")
    
    # Load queries
    console.print("\n[cyan]Loading queries from database...[/cyan]")
    queries = db.get_queries(limit=limit, version=version if version != "all" else None)
    
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
    
    # Initialize ChromaDB DAO
    console.print("\n[cyan]Connecting to ChromaDB...[/cyan]")
    dao = WildChatDAOChromaDB(use_cloud=config.use_cloud_chromadb)
    
    try:
        await dao.connect()
        console.print("[green]Connected to ChromaDB[/green]")
        
        # Get stats
        stats = await dao.get_stats()
        console.print(f"[cyan]Collection stats:[/cyan]")
        console.print(f"  Total documents: {stats.get('total_documents', 0):,}")
        console.print(f"  Collection name: {stats.get('collection_name', 'N/A')}")
        
    except Exception as e:
        console.print(f"[red]Failed to connect to ChromaDB: {e}[/red]")
        console.print("[yellow]Make sure ChromaDB environment variables are set[/yellow]")
        return
    
    # Process queries with live updates
    console.print("\n[cyan]Verifying recall with live metrics...[/cyan]")
    console.print(f"[dim]Metrics will update every {update_interval} queries[/dim]\n")
    
    # Process all queries with live updates
    metrics_by_version = await process_queries_with_live_updates(
        dao, queries, cache, 
        update_interval=update_interval,
        max_concurrent=config.max_concurrent
    )
    
    # Print final results
    console.print("\n")
    final_table = create_metrics_table(metrics_by_version)
    console.print(final_table)
    
    # Export results if requested
    if export_path:
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(queries),
            "metrics": {
                version: metrics.get_summary() 
                for version, metrics in metrics_by_version.items()
            }
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        console.print(f"\n[green]Results exported to:[/green] {export_path}")
    
    # Disconnect
    await dao.disconnect()
    console.print("\n[cyan]Done![/cyan]")
    
    # Close cache
    cache.close()


def verify_command(args):
    """Entry point for verify command."""
    # Create config
    config = Config.from_env()
    config.override_from_args(args)
    
    # Run async verification
    asyncio.run(verify_recall(
        config=config,
        limit=args.limit,
        version=args.version,
        update_interval=args.update_interval,
        export_path=args.export
    ))