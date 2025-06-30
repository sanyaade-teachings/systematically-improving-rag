#!/usr/bin/env python3
"""
Synthetic Query Generation CLI

A unified command-line interface for generating and verifying synthetic queries
from the WildChat dataset.
"""

import sys
from pathlib import Path
from typing import Optional, Literal
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import generate_command, verify_command

# Create the typer app
app = typer.Typer(
    name="synthetic-query-gen",
    help="Generate and verify synthetic search queries from conversations",
    epilog="Run 'main.py COMMAND --help' for more information on a command.",
    rich_markup_mode="rich",
)

console = Console()


class VersionChoice(str, Enum):
    v1 = "v1"
    v2 = "v2"
    all = "all"


@app.command()
def generate(
    limit: int = typer.Option(
        500,
        "--limit", "-l",
        help="Number of conversations to process"
    ),
    version: VersionChoice = typer.Option(
        VersionChoice.all,
        "--version", "-v",
        help="Which processor version to use"
    ),
    batch_size: int = typer.Option(
        100,
        "--batch-size", "-b",
        help="Batch size for database inserts"
    ),
    max_concurrent: int = typer.Option(
        10,
        "--max-concurrent", "-c",
        help="Maximum concurrent API requests"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model", "-m",
        help="Model to use for generation (default: openai/gpt-4o-mini)"
    ),
    clear_cache: bool = typer.Option(
        False,
        "--clear-cache",
        help="Clear the cache before starting"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run without saving to database"
    ),
    sample: bool = typer.Option(
        False,
        "--sample",
        help="Generate sample queries (ignores already processed conversations)"
    ),
    data_dir: Optional[Path] = typer.Option(
        None,
        "--data-dir", "-d",
        help="Override data directory location"
    ),
):
    """
    Generate synthetic queries from conversations.
    
    Examples:
    
        # Generate queries for 100 conversations using both v1 and v2
        ./main.py generate --limit 100
        
        # Generate only v1 queries with dry run
        ./main.py generate --limit 50 --version v1 --dry-run
        
        # Generate sample queries for testing
        ./main.py generate --limit 10 --sample
    """
    # Create args-like object for backward compatibility
    class Args:
        pass
    
    args = Args()
    args.limit = limit
    args.version = version.value
    args.batch_size = batch_size
    args.max_concurrent = max_concurrent
    args.model = model
    args.clear_cache = clear_cache
    args.dry_run = dry_run
    args.sample = sample
    args.data_dir = data_dir
    
    generate_command(args)


@app.command()
def verify(
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-l",
        help="Limit number of queries to verify"
    ),
    version: VersionChoice = typer.Option(
        VersionChoice.all,
        "--version", "-v",
        help="Which version queries to verify"
    ),
    update_interval: int = typer.Option(
        50,
        "--update-interval", "-u",
        help="Update metrics every N queries"
    ),
    use_local: bool = typer.Option(
        False,
        "--use-local",
        help="Use local ChromaDB instead of cloud"
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export", "-e",
        help="Export results to JSON file"
    ),
    data_dir: Optional[Path] = typer.Option(
        None,
        "--data-dir", "-d",
        help="Override data directory location"
    ),
):
    """
    Verify recall of generated queries.
    
    Examples:
    
        # Verify recall for all queries
        ./main.py verify
        
        # Verify recall for v1 queries only and export results
        ./main.py verify --version v1 --export results.json
        
        # Verify first 100 queries
        ./main.py verify --limit 100
    """
    # Create args-like object for backward compatibility
    class Args:
        pass
    
    args = Args()
    args.limit = limit
    args.version = version.value
    args.update_interval = update_interval
    args.use_local = use_local
    args.export = str(export) if export else None
    args.data_dir = data_dir
    
    verify_command(args)


@app.command()
def stats(
    data_dir: Optional[Path] = typer.Option(
        None,
        "--data-dir", "-d",
        help="Override data directory location"
    ),
):
    """
    Show database statistics.
    
    Displays the number of queries, conversations, and other metrics
    from the synthetic query database.
    """
    from src.config import Config
    from src.storage import QueryDatabase
    
    # Create config
    config = Config.from_env()
    if data_dir:
        config.data_dir = Path(data_dir)
        config.db_path = config.data_dir / "databases" / "synthetic_queries.db"
    
    # Check if database exists
    if not config.db_path.exists():
        console.print(f"[red]Database not found at {config.db_path}[/red]")
        console.print("[yellow]Run 'generate' command first to create queries[/yellow]")
        raise typer.Exit(1)
    
    # Get statistics
    db = QueryDatabase(config.db_path)
    stats = db.get_statistics()
    
    # Display statistics
    console.print("\n[bold green]Synthetic Query Database Statistics[/bold green]")
    console.print("="*50)
    
    table = Table(title="Query Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta", justify="right")
    
    table.add_row("Total Queries", f"{stats['total_queries']:,}")
    table.add_row("Unique Conversations", f"{stats['unique_conversations']:,}")
    table.add_row("Processed Conversations", f"{stats['processed_conversations']:,}")
    
    console.print(table)
    
    # Show breakdown by version
    if stats['queries_by_version']:
        version_table = Table(title="\nQueries by Version")
        version_table.add_column("Version", style="cyan")
        version_table.add_column("Count", style="magenta", justify="right")
        version_table.add_column("Percentage", style="yellow", justify="right")
        
        total = stats['total_queries']
        for version, count in sorted(stats['queries_by_version'].items()):
            percentage = (count / total * 100) if total > 0 else 0
            version_table.add_row(version, f"{count:,}", f"{percentage:.1f}%")
        
        console.print(version_table)
    
    console.print(f"\n[dim]Database location: {config.db_path}[/dim]")


# Add a callback to show version information
def version_callback(value: bool):
    if value:
        console.print("[bold green]Synthetic Query Generation v0.1.0[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    ),
):
    """
    Synthetic Query Generation - Generate and verify search queries from conversations.
    
    This tool processes conversations from the WildChat dataset to generate
    synthetic search queries using different prompting strategies. It can then
    verify the recall of these queries against the original conversations.
    """
    pass


if __name__ == "__main__":
    app()