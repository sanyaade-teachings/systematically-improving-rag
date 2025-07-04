"""
Script to generate embeddings for all questions using three different models:
- sentence-transformers/all-MiniLM-L6-v2
- text-embedding-3-large
- text-embedding-3-small
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from sqlmodel import Session, select

from core.db import get_engine, Question
from core.embeddings import EmbeddingGenerator, save_embeddings_to_parquet
from config import PATH_TO_DB

console = Console()

# Define the three embedding models to use
EMBEDDING_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "text-embedding-3-large",
    "text-embedding-3-small"
]


async def generate_embeddings_for_questions(
    questions: List[Dict[str, Any]],
    embedding_model: str,
    output_dir: Path,
    batch_size: int = 100
) -> Path:
    """Generate embeddings for questions and save to parquet"""
    console.print(f"[bold green]Generating embeddings for {len(questions)} questions using {embedding_model}[/bold green]")
    
    # Initialize embedding generator
    generator = EmbeddingGenerator(embedding_model)
    
    # Extract texts and metadata
    texts = [q['question'] for q in questions]
    metadata = [
        {
            'id': q['id'],
            'conversation_hash': q['conversation_hash'],
            'version': q['version'],
            'experiment_id': q.get('experiment_id')
        }
        for q in questions
    ]
    
    # Generate embeddings
    embeddings = await generator.generate_embeddings(texts, batch_size)
    
    # Save to parquet with version info in filename
    versions = set(q['version'] for q in questions)
    version_str = "_".join(sorted(versions))
    output_path = output_dir / f"questions_{version_str}_{embedding_model.replace('/', '-')}.parquet"
    save_embeddings_to_parquet(embeddings, metadata, output_path, embedding_model)
    
    return output_path


async def main():
    """Main function to generate embeddings for all questions"""
    console.print("[bold blue]Starting question embedding generation[/bold blue]")
    
    # Get all questions from database
    engine = get_engine(PATH_TO_DB)
    
    with Session(engine) as session:
        statement = select(Question)
        questions = session.exec(statement).all()
    
    if not questions:
        console.print("[red]No questions found in database[/red]")
        return
    
    # Convert to dict format
    question_dicts = [
        {
            "id": q.id,
            "conversation_hash": q.conversation_hash,
            "version": q.version,
            "question": q.question,
            "experiment_id": q.experiment_id
        }
        for q in questions
    ]
    
    console.print(f"[blue]Found {len(question_dicts)} questions to embed[/blue]")
    
    # Group by version
    v1_questions = [q for q in question_dicts if q['version'] == 'v1']
    v2_questions = [q for q in question_dicts if q['version'] == 'v2']
    
    console.print(f"  - v1 questions: {len(v1_questions)}")
    console.print(f"  - v2 questions: {len(v2_questions)}")
    
    # Create output directory
    output_dir = PATH_TO_DB.parent / "embeddings" / "questions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate embeddings for each model
    for model in EMBEDDING_MODELS:
        console.print(f"\n[bold cyan]Processing embeddings with {model}[/bold cyan]")
        
        try:
            # Process all questions together
            output_path = await generate_embeddings_for_questions(
                question_dicts,
                model,
                output_dir,
                batch_size=100 if model.startswith("text-embedding") else 32
            )
            console.print(f"[green]✓ Saved embeddings to: {output_path}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Error with {model}: {e}[/red]")
            continue
    
    console.print("\n[bold green]✓ Embedding generation completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())