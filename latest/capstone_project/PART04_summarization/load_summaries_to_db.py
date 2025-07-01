#!/usr/bin/env python3
"""
Load summaries into vector databases

This script loads conversation summaries (instead of first messages) into 
various vector databases for improved RAG performance with V2 queries.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple
import time
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import chromadb
from chromadb.config import Settings
import typer

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import DAOs
from utils.dao.wildchat_dao_chromadb import WildChatDAOChromaDB
from utils.dao.wildchat_dao_turbopuffer import WildChatDAOTurbopuffer
from utils.dao.wildchat_dao import SearchRequest, SearchType

# Import our db module
from src.db import load_summaries_from_db, get_summaries_by_hash
from src.dataloader import WildChatDataLoader

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database paths
DB_PATH = Path(__file__).parent / "data" / "synthetic_summaries.db"
WILDCHAT_DB_PATH = Path(__file__).parent.parent / "PART01_eda" / "data" / "wildchat.db"


def load_summaries_chromadb(
    summary_version: str,
    db_path: str = ".chroma_summaries",
    collection_name: str = None,
    drop_existing: bool = False,
    limit: int = None,
):
    """Load summaries into ChromaDB"""
    
    if collection_name is None:
        collection_name = f"wildchat_summaries_{summary_version}"
    
    console.print(f"\n[cyan]Loading summaries into ChromaDB...[/cyan]")
    console.print(f"Database path: {db_path}")
    console.print(f"Collection name: {collection_name}")
    console.print(f"Summary version: {summary_version}")
    
    # Load summaries from database
    summaries = load_summaries_from_db(DB_PATH, version=summary_version, limit=limit)
    
    if not summaries:
        console.print("[red]No summaries found in database[/red]")
        return
    
    console.print(f"[green]Found {len(summaries)} summaries to load[/green]")
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False),
    )
    
    # Drop existing collection if requested
    if drop_existing:
        try:
            client.delete_collection(name=collection_name)
            console.print(f"[yellow]Dropped existing collection: {collection_name}[/yellow]")
        except Exception:
            pass
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    
    # Process in batches
    batch_size = 100
    total_loaded = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading summaries", total=len(summaries))
        
        for i in range(0, len(summaries), batch_size):
            batch = summaries[i:i + batch_size]
            
            # Prepare batch data
            ids = []
            documents = []
            metadatas = []
            
            for conv_hash, version, summary in batch:
                ids.append(conv_hash)
                documents.append(summary)
                metadatas.append({
                    "hash": conv_hash,
                    "summary_version": version,
                    "indexed_at": datetime.now().isoformat(),
                })
            
            # Add to collection
            try:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                )
                total_loaded += len(batch)
                progress.update(task, advance=len(batch))
            except Exception as e:
                console.print(f"[red]Error loading batch: {e}[/red]")
    
    console.print(f"\n[green]Successfully loaded {total_loaded} summaries[/green]")
    
    # Test with a sample query
    console.print("\n[cyan]Testing with sample query...[/cyan]")
    test_query = "conversations about debugging Python code"
    
    results = collection.query(
        query_texts=[test_query],
        n_results=5,
    )
    
    console.print(f"Query: '{test_query}'")
    console.print(f"Found {len(results['ids'][0])} results")
    
    for i, (id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
        console.print(f"  {i+1}. Hash: {id[:16]}... (distance: {distance:.4f})")


async def load_summaries_turbopuffer(
    summary_version: str,
    namespace: str = None,
    drop_existing: bool = False,
    limit: int = None,
):
    """Load summaries into TurboPuffer"""
    
    if namespace is None:
        namespace = f"wildchat-summaries-{summary_version}"
    
    console.print(f"\n[cyan]Loading summaries into TurboPuffer...[/cyan]")
    console.print(f"Namespace: {namespace}")
    console.print(f"Summary version: {summary_version}")
    
    # Load summaries from database
    summaries = load_summaries_from_db(DB_PATH, version=summary_version, limit=limit)
    
    if not summaries:
        console.print("[red]No summaries found in database[/red]")
        return
    
    console.print(f"[green]Found {len(summaries)} summaries to load[/green]")
    
    # Initialize TurboPuffer DAO
    dao = WildChatDAOTurbopuffer(namespace=namespace)
    await dao.connect()
    
    # Drop existing if requested
    if drop_existing:
        console.print(f"[yellow]TurboPuffer doesn't support collection deletion via API[/yellow]")
    
    # Process in batches
    batch_size = 100
    total_loaded = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading summaries", total=len(summaries))
        
        for i in range(0, len(summaries), batch_size):
            batch = summaries[i:i + batch_size]
            
            # Create documents in DAO format
            documents = []
            for conv_hash, version, summary in batch:
                documents.append({
                    "id": conv_hash,
                    "text": summary,
                    "metadata": {
                        "hash": conv_hash,
                        "summary_version": version,
                    }
                })
            
            # Add documents
            try:
                await dao.add_documents(documents)
                total_loaded += len(batch)
                progress.update(task, advance=len(batch))
            except Exception as e:
                console.print(f"[red]Error loading batch: {e}[/red]")
    
    console.print(f"\n[green]Successfully loaded {total_loaded} summaries[/green]")
    
    # Test with a sample query
    console.print("\n[cyan]Testing with sample query...[/cyan]")
    test_query = "conversations about debugging Python code"
    
    request = SearchRequest(
        query=test_query,
        top_k=5,
        search_type=SearchType.VECTOR
    )
    
    results = await dao.search(request)
    
    console.print(f"Query: '{test_query}'")
    console.print(f"Found {len(results.results)} results")
    console.print(f"Query time: {results.query_time_ms:.2f}ms")
    
    for i, result in enumerate(results.results):
        console.print(f"  {i+1}. Hash: {result.id[:16]}... (score: {result.score:.4f})")
    
    await dao.disconnect()


app = typer.Typer()


@app.command()
def chromadb(
    summary_version: str = typer.Argument(..., help="Summary version to load (v1 or v2)"),
    db_path: str = typer.Option(".chroma_summaries", help="ChromaDB directory path"),
    collection_name: str = typer.Option(None, help="Collection name (default: wildchat_summaries_{version})"),
    drop: bool = typer.Option(False, "--drop", help="Drop existing collection before loading"),
    limit: int = typer.Option(None, help="Limit number of summaries to load"),
):
    """Load summaries into ChromaDB"""
    load_summaries_chromadb(
        summary_version=summary_version,
        db_path=db_path,
        collection_name=collection_name,
        drop_existing=drop,
        limit=limit
    )


@app.command()
def turbopuffer(
    summary_version: str = typer.Argument(..., help="Summary version to load (v1 or v2)"),
    namespace: str = typer.Option(None, help="TurboPuffer namespace (default: wildchat-summaries-{version})"),
    drop: bool = typer.Option(False, "--drop", help="Drop existing data before loading"),
    limit: int = typer.Option(None, help="Limit number of summaries to load"),
):
    """Load summaries into TurboPuffer"""
    asyncio.run(load_summaries_turbopuffer(
        summary_version=summary_version,
        namespace=namespace,
        drop_existing=drop,
        limit=limit
    ))


@app.command()
def all(
    summary_version: str = typer.Argument(..., help="Summary version to load (v1 or v2)"),
    drop: bool = typer.Option(False, "--drop", help="Drop existing data before loading"),
    limit: int = typer.Option(None, help="Limit number of summaries to load"),
):
    """Load summaries into all supported vector databases"""
    
    async def load_all():
        console.print("[bold green]Loading summaries into all vector databases[/bold green]")
        console.print("=" * 50)
        
        # Load into ChromaDB
        await load_summaries_chromadb(
            summary_version=summary_version,
            drop_existing=drop,
            limit=limit
        )
        
        console.print("\n" + "=" * 50 + "\n")
        
        # Load into TurboPuffer
        await load_summaries_turbopuffer(
            summary_version=summary_version,
            drop_existing=drop,
            limit=limit
        )
        
        console.print("\n[green]All databases loaded successfully![/green]")
    
    asyncio.run(load_all())


if __name__ == "__main__":
    app()