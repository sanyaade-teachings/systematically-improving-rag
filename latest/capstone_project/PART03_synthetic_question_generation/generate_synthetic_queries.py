#!/usr/bin/env python3
"""
Synthetic Query Generation Script

This script loads 1000 random conversations from WildChat dataset and generates
synthetic search queries using both v1 and v2 prompt versions. Results are saved
to a SQLite database.
"""

import asyncio
import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any
import instructor
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from diskcache import Cache
import argparse

# Import from our package - handles both direct execution and module import
try:
    # When run as a script directly
    from utils.dataloader import WildChatDataLoader
    from processor import synthetic_question_generation_v1, synthetic_question_generation_v2
except ImportError:
    # When imported as a module
    from ..utils.dataloader import WildChatDataLoader
    from .processor import synthetic_question_generation_v1, synthetic_question_generation_v2

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

# Database and cache setup
DB_PATH = Path(__file__).parent / "synthetic_queries.db"
CACHE_DIR = Path(__file__).parent / ".cache"

def setup_database():
    """Create SQLite table for storing results"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_queries (
            conversation_hash TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (conversation_hash, prompt_version, query)
        )
    """)
    
    # Create index for faster lookups on individual columns
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_hash 
        ON synthetic_queries(conversation_hash)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_prompt_version 
        ON synthetic_queries(prompt_version)
    """)
    
    conn.commit()
    conn.close()

def save_query_to_db(conversation_hash: str, prompt_version: str, query: str) -> bool:
    """Save a single query result to database immediately, ignore duplicates"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO synthetic_queries (conversation_hash, prompt_version, query)
            VALUES (?, ?, ?)
        """, (conversation_hash, prompt_version, query))
        
        conn.commit()
        # Return True if a new row was inserted
        return cursor.rowcount > 0
    except Exception as e:
        console.print(f"[red]Database error for {conversation_hash}: {e}[/red]")
        return False
    finally:
        conn.close()

def get_processed_conversations() -> set:
    """Get set of conversation hashes that have been fully processed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find conversations that have both v1 and v2 results
    cursor.execute("""
        SELECT conversation_hash 
        FROM synthetic_queries 
        GROUP BY conversation_hash 
        HAVING COUNT(DISTINCT prompt_version) = 2
    """)
    
    processed = {row[0] for row in cursor.fetchall()}
    conn.close()
    return processed

def conversation_cache_key(conversation_hash: str, prompt_version: str) -> str:
    """Generate cache key for conversation and version"""
    return f"{conversation_hash}_{prompt_version}"

async def process_conversation_version(
    client, 
    conversation: Dict[str, Any], 
    version: str,
    cache: Cache,
    semaphore: asyncio.Semaphore
) -> List[str]:
    """Process a single conversation with one version (v1 or v2)"""
    async with semaphore:
        conversation_hash = conversation['conversation_hash']
        messages = conversation['conversation']
        cache_key = conversation_cache_key(conversation_hash, version)
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            if version == "v1":
                result = await synthetic_question_generation_v1(client, messages)
            else:  # v2
                result = await synthetic_question_generation_v2(client, messages)
            
            queries = result.queries if hasattr(result, 'queries') else []
            
            # Cache the result
            cache.set(cache_key, queries)
            
            return queries
            
        except Exception as e:
            console.print(f"[red]Error processing {conversation_hash} {version}: {e}[/red]")
            return []

async def process_conversation(
    client, 
    conversation: Dict[str, Any], 
    cache: Cache,
    semaphore: asyncio.Semaphore,
    progress: Progress,
    task_id
) -> int:
    """Process a single conversation with both v1 and v2 generators and save immediately"""
    conversation_hash = conversation['conversation_hash']
    saved_count = 0
    
    try:
        # Process both versions concurrently
        v1_task = process_conversation_version(client, conversation, "v1", cache, semaphore)
        v2_task = process_conversation_version(client, conversation, "v2", cache, semaphore)
        
        v1_queries, v2_queries = await asyncio.gather(v1_task, v2_task)
        
        # Save v1 queries immediately
        for query in v1_queries:
            if save_query_to_db(conversation_hash, "v1", query):
                saved_count += 1
        
        # Save v2 queries immediately
        for query in v2_queries:
            if save_query_to_db(conversation_hash, "v2", query):
                saved_count += 1
            
        progress.update(task_id, advance=1)
        
    except Exception as e:
        console.print(f"[red]Failed to process conversation {conversation_hash}: {e}[/red]")
    
    return saved_count

async def main():
    """Main execution function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate synthetic queries from WildChat conversations")
    parser.add_argument("--limit", type=int, default=500, help="Number of conversations to process (default: 1000)")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache before starting")
    parser.add_argument("--concurrency", type=int, default=50, help="Max concurrent API requests (default: 50)")
    args = parser.parse_args()
    
    console.print("[bold green]Synthetic Query Generation[/bold green]")
    console.print("="*50)
    
    console.print("\n[cyan]Setting up database...[/cyan]")
    setup_database()
    
    # Set up disk cache
    cache = Cache(str(CACHE_DIR))
    console.print(f"[cyan]Using disk cache at: {CACHE_DIR}[/cyan]")
    
    if args.clear_cache:
        console.print("[yellow]Clearing cache...[/yellow]")
        cache.clear()
    else:
        cache_size = len(cache)
        if cache_size > 0:
            console.print(f"[yellow]Found {cache_size} cached query generation results[/yellow]")
    
    # Check for already processed conversations
    processed = get_processed_conversations()
    if processed:
        console.print(f"[yellow]Found {len(processed)} already processed conversations[/yellow]")
    
    console.print("\n[cyan]Loading conversations...[/cyan]")
    # Load conversations
    loader = WildChatDataLoader(limit=2000)  # Load more to ensure we get 1000 good ones
    conversations = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console
    ) as progress:
        load_task = progress.add_task("Loading conversations", total=args.limit)
        
        for conversation in loader.stream_conversations(
            limit=int(args.limit * 1.5),  # Load extra in case some are already processed
            min_message_length=50,
            filter_language="English",
            filter_toxic=True
        ):
            # Skip already processed conversations
            if conversation['conversation_hash'] not in processed:
                conversations.append(conversation)
                progress.update(load_task, advance=1)
                
            if len(conversations) >= args.limit:
                break
    
    console.print(f"[green]Loaded {len(conversations)} new conversations to process[/green]")
    
    # Set up OpenAI client with instructor
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    client = instructor.from_provider(model="openai/gpt-4.1-nano", async_client=True)
    
    # Control concurrency to avoid rate limits
    semaphore = asyncio.Semaphore(args.concurrency)
    
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
            process_conversation(client, conversation, cache, semaphore, progress, process_task)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT prompt_version, COUNT(*) FROM synthetic_queries GROUP BY prompt_version")
    counts = cursor.fetchall()
    
    console.print("\n[bold]Results summary:[/bold]")
    for version, count in counts:
        console.print(f"  [cyan]{version}:[/cyan] {count} queries")
    
    cursor.execute("SELECT COUNT(DISTINCT conversation_hash) FROM synthetic_queries")
    unique_conversations = cursor.fetchone()[0]
    console.print(f"  [cyan]Unique conversations:[/cyan] {unique_conversations}")
    
    conn.close()
    console.print(f"\n[green]Database saved to:[/green] {DB_PATH}")
    console.print(f"[green]Cache directory:[/green] {CACHE_DIR}")

if __name__ == "__main__":
    asyncio.run(main())