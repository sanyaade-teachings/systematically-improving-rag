import asyncio
import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console

from core.db import get_engine, get_conversations_by_hashes, get_database_stats
from core.documents import load_wildchat_into_db
from core.summarization import ConversationSummary
from pipelines.generation import generate_questions_pipeline, generate_summaries_pipeline
from config import PATH_TO_DB
from sqlmodel import Session, select
from core.db import Conversation

console = Console()
app = typer.Typer()


def get_all_conversation_hashes(db_path: Path, limit: Optional[int] = None) -> List[str]:
    """Get all conversation hashes from the database"""
    engine = get_engine(db_path)
    
    with Session(engine) as session:
        statement = select(Conversation.conversation_hash)
        if limit:
            statement = statement.limit(limit)
        
        results = session.exec(statement).all()
        return list(results)


@app.command()
def load_wildchat():
    """Load WildChat dataset into SQLite database"""
    load_wildchat_into_db(PATH_TO_DB)


@app.command()
def generate_questions(
    version: str = typer.Option("v1", help="Question generation version (v1, v2, v3, v5)"),
    limit: Optional[int] = typer.Option(None, help="Limit number of conversations to process"),
    experiment_id: Optional[str] = typer.Option(None, help="Experiment ID for tracking"),
    concurrency: int = typer.Option(10, help="Max concurrent API requests"),
    conversation_hashes: Optional[List[str]] = typer.Option(None, help="Specific conversation hashes to process"),
):
    """Generate synthetic questions for conversations"""
    
    # Validate version
    valid_versions = ["v1", "v2", "v3", "v5"]
    if version not in valid_versions:
        console.print(f"[red]Error: Invalid version '{version}'. Must be one of: {valid_versions}[/red]")
        raise typer.Exit(1)
    
    # Get conversation hashes
    if conversation_hashes:
        hashes = conversation_hashes
    else:
        hashes = get_all_conversation_hashes(PATH_TO_DB, limit)
    
    if not hashes:
        console.print("[red]No conversations found in database[/red]")
        raise typer.Exit(1)
    
    console.print(f"[blue]Processing {len(hashes)} conversations with version {version}[/blue]")
    
    # Run the generation pipeline
    results = asyncio.run(
        generate_questions_pipeline(
            conversation_hashes=hashes,
            version=version,
            db_path=PATH_TO_DB,
            experiment_id=experiment_id,
            concurrency=concurrency,
        )
    )
    
    console.print(f"[green]Generation completed: {results}[/green]")


@app.command()
def generate_summaries(
    version: str = typer.Option("v1", help="Summary generation version (v1, v2, v3, v4, v5)"),
    limit: Optional[int] = typer.Option(None, help="Limit number of conversations to process"),
    experiment_id: Optional[str] = typer.Option(None, help="Experiment ID for tracking"),
    concurrency: int = typer.Option(10, help="Max concurrent API requests"),
    conversation_hashes: Optional[List[str]] = typer.Option(None, help="Specific conversation hashes to process"),
):
    """Generate summaries for conversations"""
    
    # Validate version
    valid_versions = ["v1", "v2", "v3", "v4", "v5"]
    if version not in valid_versions:
        console.print(f"[red]Error: Invalid version '{version}'. Must be one of: {valid_versions}[/red]")
        raise typer.Exit(1)
    
    # Get conversation hashes
    if conversation_hashes:
        hashes = conversation_hashes
    else:
        hashes = get_all_conversation_hashes(PATH_TO_DB, limit)
    
    if not hashes:
        console.print("[red]No conversations found in database[/red]")
        raise typer.Exit(1)
    
    console.print(f"[blue]Processing {len(hashes)} conversations with version {version}[/blue]")
    
    # Run the generation pipeline
    results = asyncio.run(
        generate_summaries_pipeline(
            conversation_hashes=hashes,
            version=version,
            db_path=PATH_TO_DB,
            experiment_id=experiment_id,
            concurrency=concurrency,
        )
    )
    
    console.print(f"[green]Generation completed: {results}[/green]")


@app.command()
def stats():
    """Show database statistics"""
    stats = get_database_stats(PATH_TO_DB)
    
    if not stats:
        console.print("[red]Database not found or empty[/red]")
        return
    
    console.print("[bold blue]Database Statistics:[/bold blue]")
    for key, value in stats.items():
        console.print(f"  {key.capitalize()}: {value:,}")


if __name__ == "__main__":
    app()
