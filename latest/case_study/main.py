import asyncio
import typer
from pathlib import Path
from typing import List, Optional
from rich.console import Console

from core.db import get_engine, get_conversations_by_hashes, get_database_stats, Summary
from core.documents import load_wildchat_into_db
from core.summarization import ConversationSummary
from pipelines.generation import generate_questions_pipeline, generate_summaries_pipeline
from core.embeddings import generate_conversation_embeddings, generate_summary_embeddings, generate_full_conversation_embeddings
from core.evaluation import evaluate_questions
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
def load_wildchat(
    limit: int = typer.Option(10000, help="Number of conversations to load")
):
    """Load WildChat dataset into SQLite database"""
    load_wildchat_into_db(PATH_TO_DB, limit=limit)


@app.command()
def generate_questions(
    version: str = typer.Option("v1", help="Question generation version (v1, v2, v3, v5)"),
    limit: Optional[int] = typer.Option(None, help="Limit number of conversations to process"),
    experiment_id: Optional[str] = typer.Option(None, help="Experiment ID for tracking"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
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
    versions: str = typer.Option("v1", help="Comma-separated summary versions (e.g., 'v1,v2,v3' or 'all' for v1-v5)"),
    limit: Optional[int] = typer.Option(None, help="Limit number of conversations to process"),
    experiment_id: Optional[str] = typer.Option(None, help="Experiment ID for tracking"),
    concurrency: int = typer.Option(50, help="Max concurrent API requests"),
    conversation_hashes: Optional[List[str]] = typer.Option(None, help="Specific conversation hashes to process"),
):
    """Generate summaries for conversations using one or more versions"""
    
    # Parse versions
    valid_versions = ["v1", "v2", "v3", "v4", "v5"]
    if versions.lower() == "all":
        version_list = valid_versions
    else:
        version_list = [v.strip() for v in versions.split(",")]
    
    # Validate versions
    for version in version_list:
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
    
    console.print(f"[blue]Processing {len(hashes)} conversations with versions: {', '.join(version_list)}[/blue]")
    
    # Run the generation pipeline for each version
    all_results = {}
    
    async def run_all_versions():
        tasks = []
        for version in version_list:
            task = generate_summaries_pipeline(
                conversation_hashes=hashes,
                version=version,
                db_path=PATH_TO_DB,
                experiment_id=experiment_id,
                concurrency=concurrency // len(version_list),  # Divide concurrency among versions
                show_progress=len(version_list) == 1,  # Only show progress for single version
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Combine results
        for result in results:
            all_results.update(result)
        
        return all_results
    
    results = asyncio.run(run_all_versions())
    
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


@app.command()
def embed_conversations(
    embedding_model: str = typer.Option("text-embedding-3-large", help="Embedding model to use"),
    limit: Optional[int] = typer.Option(None, help="Limit number of conversations to embed"),
    batch_size: int = typer.Option(100, help="Batch size for embedding generation"),
    mode: str = typer.Option("first_message", help="Embedding mode: 'first_message' or 'full'"),
    max_tokens: int = typer.Option(8000, help="Max tokens for full conversation mode"),
):
    """Generate embeddings for conversations"""
    # Validate mode
    if mode not in ["first_message", "full"]:
        console.print(f"[red]Invalid mode '{mode}'. Must be 'first_message' or 'full'[/red]")
        raise typer.Exit(1)
    
    # Get conversations
    hashes = get_all_conversation_hashes(PATH_TO_DB, limit)
    
    if not hashes:
        console.print("[red]No conversations found in database[/red]")
        raise typer.Exit(1)
    
    # Load full conversation data
    conversations = get_conversations_by_hashes(hashes, PATH_TO_DB)
    console.print(f"[blue]Embedding {len(conversations)} conversations (mode: {mode})[/blue]")
    
    # Generate embeddings based on mode
    if mode == "first_message":
        output_dir = PATH_TO_DB.parent / "embeddings" / "conversations"
        output_path = asyncio.run(
            generate_conversation_embeddings(
                conversations,
                embedding_model=embedding_model,
                output_dir=output_dir,
                batch_size=batch_size
            )
        )
    else:  # full mode
        output_dir = PATH_TO_DB.parent / "embeddings" / "full_conversations"
        output_path = asyncio.run(
            generate_full_conversation_embeddings(
                conversations,
                embedding_model=embedding_model,
                output_dir=output_dir,
                batch_size=batch_size,
                max_tokens=max_tokens
            )
        )
    
    console.print(f"[green]Embeddings saved to: {output_path}[/green]")


@app.command()
def embed_summaries(
    technique: str = typer.Option("v1", help="Summary technique to embed (v1-v5)"),
    embedding_model: str = typer.Option("text-embedding-3-large", help="Embedding model to use"),
    limit: Optional[int] = typer.Option(None, help="Limit number of summaries to embed"),
    batch_size: int = typer.Option(100, help="Batch size for embedding generation"),
):
    """Generate embeddings for summaries"""
    engine = get_engine(PATH_TO_DB)
    
    # Get summaries
    with Session(engine) as session:
        statement = select(Summary).where(Summary.technique == technique)
        if limit:
            statement = statement.limit(limit)
        summaries = session.exec(statement).all()
    
    if not summaries:
        console.print(f"[red]No summaries found for technique {technique}[/red]")
        raise typer.Exit(1)
    
    # Convert to dict format
    # Note: We use conversation_hash as the ID for ChromaDB compatibility
    # The database ID has a suffix (e.g., "_v1") but we need just the hash for search
    summary_dicts = [
        {
            "id": s.id,  # This will be like "hash_v1" but won't be used for ChromaDB
            "conversation_hash": s.conversation_hash,  # This is what we'll use as the ChromaDB ID
            "technique": s.technique,
            "summary": s.summary,
            "experiment_id": s.experiment_id
        }
        for s in summaries
    ]
    
    console.print(f"[blue]Embedding {len(summaries)} {technique} summaries[/blue]")
    
    # Generate embeddings
    output_dir = PATH_TO_DB.parent / "embeddings" / "summaries"
    output_path = asyncio.run(
        generate_summary_embeddings(
            summary_dicts,
            embedding_model=embedding_model,
            output_dir=output_dir,
            batch_size=batch_size
        )
    )
    
    console.print(f"[green]Embeddings saved to: {output_path}[/green]")


@app.command()
def evaluate(
    question_version: str = typer.Option("v1", help="Question version to evaluate (v1, v2, v3, v5)"),
    embeddings_type: str = typer.Option("conversations", help="Type of embeddings to search: conversations, full_conversations, or summaries"),
    embedding_model: str = typer.Option("text-embedding-3-large", help="Embedding model name"),
    limit: Optional[int] = typer.Option(None, help="Limit number of questions to evaluate"),
    experiment_id: Optional[str] = typer.Option(None, help="Experiment ID for tracking"),
):
    """Evaluate question generation performance"""
    # Determine embeddings path
    if embeddings_type == "conversations":
        embeddings_path = PATH_TO_DB.parent / "embeddings" / "conversations" / f"{embedding_model.replace('/', '-')}.parquet"
    elif embeddings_type == "full_conversations":
        embeddings_path = PATH_TO_DB.parent / "embeddings" / "full_conversations" / f"{embedding_model.replace('/', '-')}.parquet"
    else:  # summaries
        # For summaries, need to specify which summary version
        summary_version = typer.prompt("Which summary version? (v1-v5)")
        embeddings_path = PATH_TO_DB.parent / "embeddings" / "summaries" / f"{summary_version}_{embedding_model.replace('/', '-')}.parquet"
    
    if not embeddings_path.exists():
        console.print(f"[red]Embeddings not found at {embeddings_path}[/red]")
        console.print("[yellow]Run embed-conversations or embed-summaries first[/yellow]")
        raise typer.Exit(1)
    
    # Run evaluation
    results, metrics = asyncio.run(
        evaluate_questions(
            question_version=question_version,
            embeddings_path=embeddings_path,
            db_path=PATH_TO_DB,
            embedding_model=embedding_model,
            limit=limit,
            experiment_id=experiment_id
        )
    )
    
    # Save report
    report_path = PATH_TO_DB.parent / "results" / f"eval_{question_version}_{embeddings_type}_{embedding_model.replace('/', '-')}.json"
    from core.evaluation import save_evaluation_report
    save_evaluation_report(
        results, 
        metrics,
        report_path,
        metadata={
            "question_version": question_version,
            "embeddings_type": embeddings_type,
            "embedding_model": embedding_model
        },
        db_path=PATH_TO_DB,
        experiment_id=experiment_id
    )


if __name__ == "__main__":
    app()
