"""Generate synthetic queries CLI command."""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import instructor
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from utils.dataloader import WildChatDataLoader
from ..processors import SearchFocusedProcessor, PatternFocusedProcessor
from ..storage import QueryDatabase, CacheManager
from ..config import Config


console = Console()


async def process_conversation_version(
    processor,
    conversation: Dict[str, Any],
    cache: CacheManager,
    semaphore: asyncio.Semaphore
) -> List[str]:
    """Process a single conversation with one processor version."""
    async with semaphore:
        conversation_hash = conversation['conversation_hash']
        messages = conversation['conversation']
        cache_key = cache.create_query_key(conversation_hash, processor.version)
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            result = await processor.process(messages)
            queries = result.queries if hasattr(result, 'queries') else []
            
            # Cache the result
            cache.set(cache_key, queries)
            
            return queries
            
        except Exception as e:
            console.print(f"[red]Error processing {conversation_hash} {processor.version}: {e}[/red]")
            return []


async def process_conversation(
    processors: List,
    conversation: Dict[str, Any],
    db: QueryDatabase,
    cache: CacheManager,
    semaphore: asyncio.Semaphore,
    progress: Progress,
    task_id,
    dry_run: bool = False
) -> int:
    """Process a single conversation with all processors and save immediately."""
    conversation_hash = conversation['conversation_hash']
    saved_count = 0
    
    try:
        # Process all versions concurrently
        tasks = [
            process_conversation_version(processor, conversation, cache, semaphore)
            for processor in processors
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Save results immediately
        if not dry_run:
            for processor, queries in zip(processors, results):
                # Prepare batch for this processor
                batch = [
                    (conversation_hash, processor.version, query, "", None)
                    for query in queries
                ]
                if batch:
                    db.insert_queries(batch)
                    saved_count += len(batch)
                    
            # Mark conversation as processed
            db.mark_conversation_processed(
                conversation_hash, 
                [p.version for p in processors]
            )
        else:
            # In dry-run mode, just count what would be saved
            for queries in results:
                saved_count += len(queries)
            
        progress.update(task_id, advance=1)
        
    except Exception as e:
        console.print(f"[red]Failed to process conversation {conversation_hash}: {e}[/red]")
    
    return saved_count


async def generate_queries(
    config: Config,
    limit: int,
    versions: List[str],
    dry_run: bool,
    clear_cache: bool,
    sample: bool = False
):
    """Generate synthetic queries from conversations."""
    console.print("[bold green]Synthetic Query Generation[/bold green]")
    console.print("="*50)
    
    # Ensure directories exist
    config.ensure_dirs()
    
    # Initialize storage
    db = QueryDatabase(config.db_path)
    cache = CacheManager(config.cache_dir)
    
    if clear_cache:
        console.print("[yellow]Clearing cache...[/yellow]")
        cache.clear()
    else:
        cache_size = cache.size()
        if cache_size > 0:
            console.print(f"[yellow]Found {cache_size} cached query generation results[/yellow]")
    
    # Check for already processed conversations (only if not in sample mode)
    processed = set()
    if not sample:
        stats = db.get_statistics()
        processed_count = stats.get('processed_conversations', 0)
        if processed_count > 0:
            console.print(f"[yellow]Found {processed_count} already processed conversations[/yellow]")
            # Get the actual hashes of processed conversations
            # Note: This is a simplified version - you might want to add a method to get processed hashes
    
    # Set up OpenAI client with instructor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = instructor.from_provider(model=config.model_name, async_client=True)
    
    # Initialize processors based on versions
    processors = []
    if "v1" in versions or "all" in versions:
        processors.append(SearchFocusedProcessor(client))
    if "v2" in versions or "all" in versions:
        processors.append(PatternFocusedProcessor(client))
    
    if not processors:
        console.print("[red]No valid processor versions specified[/red]")
        return
    
    console.print(f"\n[cyan]Using processors: {', '.join(p.version for p in processors)}[/cyan]")
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No data will be saved[/yellow]")
    
    # Load conversations
    console.print("\n[cyan]Loading conversations...[/cyan]")
    loader = WildChatDataLoader(limit=int(limit * 1.5))  # Load extra to account for filtering
    conversations = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console
    ) as progress:
        load_task = progress.add_task("Loading conversations", total=limit)
        
        for conversation in loader.stream_conversations(
            limit=int(limit * 1.5),
            min_message_length=50,
            filter_language="English",
            filter_toxic=True
        ):
            # Skip already processed conversations unless in sample mode
            if sample or conversation['conversation_hash'] not in processed:
                conversations.append(conversation)
                progress.update(load_task, advance=1)
                
            if len(conversations) >= limit:
                break
    
    console.print(f"[green]Loaded {len(conversations)} conversations to process[/green]")
    
    # Control concurrency
    semaphore = asyncio.Semaphore(config.max_concurrent)
    
    console.print("\n[cyan]Processing conversations...[/cyan]")
    
    # Process conversations with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        process_task = progress.add_task("Processing conversations", total=len(conversations))
        
        tasks = [
            process_conversation(
                processors, conversation, db, cache, semaphore, 
                progress, process_task, dry_run
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
    
    # Print summary
    if dry_run:
        console.print(f"\n[green]Would have saved {total_saved} queries (DRY RUN)[/green]")
    else:
        console.print(f"\n[green]Saved {total_saved} new queries to database[/green]")
        
        # Show database statistics
        stats = db.get_statistics()
        console.print("\n[bold]Database statistics:[/bold]")
        console.print(f"  [cyan]Total queries:[/cyan] {stats['total_queries']}")
        for version, count in stats['queries_by_version'].items():
            console.print(f"  [cyan]{version}:[/cyan] {count} queries")
        console.print(f"  [cyan]Unique conversations:[/cyan] {stats['unique_conversations']}")
        console.print(f"\n[green]Database location:[/green] {config.db_path}")
    
    # Close cache
    cache.close()


def generate_command(args):
    """Entry point for generate command."""
    # Create config
    config = Config.from_env()
    config.override_from_args(args)
    
    # Determine which versions to process
    versions = []
    if args.version:
        versions = [args.version]
    else:
        versions = ["all"]
    
    # Run async generation
    asyncio.run(generate_queries(
        config=config,
        limit=args.limit,
        versions=versions,
        dry_run=args.dry_run,
        clear_cache=args.clear_cache,
        sample=args.sample
    ))