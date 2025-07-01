#!/usr/bin/env python3
"""
Load conversation summaries to Turbopuffer

This script loads conversation summaries (instead of first messages) into
Turbopuffer for improved RAG performance with V2 queries.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import turbopuffer
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
import typer

# Import our db module
sys.path.append(str(Path(__file__).parent.parent))
from src.db import load_summaries_from_db, get_summaries_by_hash

# Load environment variables
load_dotenv()

# Initialize console
console = Console()

# Database path
DB_PATH = Path(__file__).parent / "data" / "synthetic_summaries.db"

# Initialize embedding model
embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model"""
    global embedding_model
    if embedding_model is None:
        console.print("Loading embedding model...", style="cyan")
        embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        console.print("Embedding model loaded successfully", style="green")
    return embedding_model


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a list of texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return [embedding.tolist() for embedding in embeddings]


def create_client() -> turbopuffer.Turbopuffer:
    """Create Turbopuffer client"""
    api_key = os.getenv("TURBOPUFFER_API_KEY")
    if not api_key:
        raise ValueError("Missing required environment variable: TURBOPUFFER_API_KEY")

    # Default to GCP US Central region, but allow override
    region = os.getenv("TURBOPUFFER_REGION", "gcp-us-central1")

    console.print("Connecting to Turbopuffer...", style="blue")
    client = turbopuffer.Turbopuffer(api_key=api_key, region=region)
    console.print(f"Connected to Turbopuffer in region: {region}", style="green")

    return client


def load_summaries_to_turbopuffer(
    client: turbopuffer.Turbopuffer,
    summary_version: str,
    namespace_name: str = None,
    limit: int = None,
    batch_size: int = 25,
    reset_namespace: bool = False,
) -> None:
    """
    Load summaries to Turbopuffer with embeddings

    Args:
        client: Turbopuffer client instance
        summary_version: Which summary version to load (v1 or v2)
        namespace_name: Name of the namespace to create/use
        limit: Maximum number of summaries to load
        batch_size: Number of records to process in each batch
        reset_namespace: If True, delete existing namespace before loading
    """

    if namespace_name is None:
        namespace_name = f"wildchat-summaries-{summary_version}"

    console.print(f"\n[cyan]Loading summaries into Turbopuffer...[/cyan]")
    console.print(f"Namespace: {namespace_name}")
    console.print(f"Summary version: {summary_version}")
    console.print(
        f"Using embedding model: sentence-transformers/all-MiniLM-L6-v2", style="cyan"
    )

    # Load summaries from database
    summaries = load_summaries_from_db(DB_PATH, version=summary_version, limit=limit)

    if not summaries:
        console.print("[red]No summaries found in database[/red]")
        return

    console.print(f"[green]Found {len(summaries)} summaries to load[/green]")

    try:
        # Get namespace
        ns = client.namespace(namespace_name)

        # Handle namespace reset
        if reset_namespace:
            try:
                client.delete_namespace(namespace_name)
                console.print(
                    f"Deleted existing namespace: {namespace_name}", style="yellow"
                )
                ns = client.namespace(namespace_name)  # Recreate after deletion
            except Exception:
                pass  # Namespace might not exist

        # Batch processing variables
        batch_data = {
            "id": [],
            "vector": [],
            "text": [],
            "summary": [],
            "hash": [],
            "summary_version": [],
        }
        batch_texts = []
        total_added = 0
        duplicates_skipped = 0

        console.print("Loading summaries...", style="blue")

        # Start timing
        load_start_time = time.time()

        # Use rich progress bar
        with Progress() as progress:
            task = progress.add_task("Processing summaries...", total=len(summaries))

            for i, (conv_hash, version, summary) in enumerate(summaries):
                progress.update(task, advance=1)

                # Check for duplicates in current batch
                if conv_hash in batch_data["id"]:
                    duplicates_skipped += 1
                    continue

                # Add to batch
                batch_data["id"].append(conv_hash)
                batch_data["text"].append(summary)  # For search
                batch_data["summary"].append(summary)  # Full summary
                batch_data["hash"].append(conv_hash)
                batch_data["summary_version"].append(version)

                # Truncate for embeddings if needed
                batch_texts.append(summary[:2000] if len(summary) > 2000 else summary)

                # Process batch when full
                if len(batch_data["id"]) >= batch_size:
                    try:
                        # Generate embeddings for the batch
                        embeddings = create_embeddings(batch_texts)
                        batch_data["vector"] = embeddings

                        # Write batch to Turbopuffer
                        ns.write(
                            upsert_columns=batch_data,
                            distance_metric="cosine_distance",
                            schema={
                                "text": {
                                    "type": "string",
                                    "full_text_search": True,
                                },
                                "summary": {
                                    "type": "string",
                                    "full_text_search": True,
                                },
                                "hash": {"type": "string"},
                                "summary_version": {"type": "string"},
                            },
                        )

                        total_added += len(batch_data["id"])

                    except Exception as e:
                        if (
                            "duplicate" in str(e).lower()
                            or "already exists" in str(e).lower()
                        ):
                            console.print(
                                "Warning: Duplicate entries detected in batch, skipping",
                                style="yellow",
                            )
                            duplicates_skipped += len(batch_data["id"])
                        else:
                            console.print(f"Error writing batch: {e}", style="red")
                            raise

                    # Reset batch
                    batch_data = {key: [] for key in batch_data.keys()}
                    batch_texts = []

        # Write final batch
        if batch_data["id"]:
            try:
                embeddings = create_embeddings(batch_texts)
                batch_data["vector"] = embeddings

                ns.write(
                    upsert_columns=batch_data,
                    distance_metric="cosine_distance",
                    schema={
                        "text": {
                            "type": "string",
                            "full_text_search": True,
                        },
                        "summary": {
                            "type": "string",
                            "full_text_search": True,
                        },
                        "hash": {"type": "string"},
                        "summary_version": {"type": "string"},
                    },
                )

                total_added += len(batch_data["id"])
                console.print("Final batch written", style="green")

            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    console.print(
                        "Warning: Duplicate entries in final batch, skipping",
                        style="yellow",
                    )
                    duplicates_skipped += len(batch_data["id"])
                else:
                    console.print(f"Error writing final batch: {e}", style="red")

        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time

        # Get final statistics
        try:
            count_result = ns.query(aggregate_by={"document_count": ("Count", "id")})
            final_count = count_result.aggregations["document_count"]
        except Exception:
            final_count = "Unknown"

        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total summaries loaded: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Namespace size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")

        # Test query with timing
        if total_added > 0:
            console.print("\nTesting with sample query...", style="blue")
            test_query = "conversations about debugging Python code"

            try:
                # Test vector search
                search_start_time = time.time()
                test_embedding = create_embeddings([test_query])[0]
                results = ns.query(
                    rank_by=("vector", "ANN", test_embedding),
                    top_k=5,
                    include_attributes=["text", "hash"],
                )
                search_end_time = time.time()
                search_duration_ms = (search_end_time - search_start_time) * 1000

                console.print(f"Query: '{test_query}'")
                console.print(f"Found {len(results.rows)} results", style="green")
                console.print(f"Search time: {search_duration_ms:.1f} ms")

                for i, row in enumerate(results.rows[:3]):
                    console.print(
                        f"  {i + 1}. Hash: {row.hash[:16]}... - {row.text[:100]}..."
                    )

            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")

    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise


app = typer.Typer()


@app.command()
def main(
    summary_version: str = typer.Argument(
        ..., help="Summary version to load (v1 or v2)"
    ),
    namespace_name: str = typer.Option(
        None, help="TurboPuffer namespace (default: wildchat-summaries-{version})"
    ),
    limit: int = typer.Option(None, help="Limit number of summaries to load"),
    batch_size: int = typer.Option(25, help="Batch size for writing to Turbopuffer"),
    reset: bool = typer.Option(False, "--reset", help="Reset namespace before loading"),
):
    """Load conversation summaries to Turbopuffer"""

    console.print("[bold green]Summary to Turbopuffer Loader[/bold green]")
    console.print("=" * 50)

    try:
        # Create client
        client = create_client()

        # Load data
        load_summaries_to_turbopuffer(
            client=client,
            summary_version=summary_version,
            namespace_name=namespace_name,
            limit=limit,
            batch_size=batch_size,
            reset_namespace=reset,
        )

    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
