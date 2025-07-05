"""
Script to verify the generated embeddings
"""

import pandas as pd
from rich.console import Console
from rich.table import Table

from config import PATH_TO_DB

console = Console()


def verify_embeddings():
    """Verify all generated embeddings"""
    embeddings_dir = PATH_TO_DB.parent / "embeddings" / "questions"

    console.print("[bold blue]Verifying Generated Embeddings[/bold blue]\n")

    # Create a table for summary
    table = Table(title="Question Embeddings Summary")
    table.add_column("Model", style="cyan")
    table.add_column("File Size (MB)", justify="right", style="green")
    table.add_column("# Embeddings", justify="right", style="yellow")
    table.add_column("Embedding Dim", justify="right", style="magenta")
    table.add_column("Versions", style="blue")

    for parquet_file in sorted(embeddings_dir.glob("*.parquet")):
        # Load the parquet file
        df = pd.read_parquet(parquet_file)

        # Get file size
        file_size_mb = parquet_file.stat().st_size / 1024 / 1024

        # Get embedding dimension
        first_embedding = df.iloc[0]["embedding"]
        embedding_dim = len(first_embedding)

        # Get unique versions
        versions = sorted(df["version"].unique())

        # Extract model name from filename
        model_name = parquet_file.stem.replace("questions_v1_v2_", "")

        table.add_row(
            model_name,
            f"{file_size_mb:.1f}",
            f"{len(df):,}",
            str(embedding_dim),
            ", ".join(versions),
        )

        # Show version breakdown
        console.print(f"\n[cyan]{model_name}:[/cyan]")
        for version in versions:
            count = len(df[df["version"] == version])
            console.print(f"  - {version}: {count:,} questions")

    console.print()
    console.print(table)

    # Show sample questions
    console.print("\n[bold yellow]Sample Questions:[/bold yellow]")

    # Load one file to show samples
    sample_file = embeddings_dir / "questions_v1_v2_text-embedding-3-large.parquet"
    df = pd.read_parquet(sample_file)

    # Show 3 v1 and 3 v2 questions
    for version in ["v1", "v2"]:
        console.print(f"\n[green]{version} samples:[/green]")
        version_df = df[df["version"] == version]
        samples = version_df.sample(min(3, len(version_df)))

        for idx, row in samples.iterrows():
            # Get question from the database
            from sqlmodel import Session, select
            from core.db import get_engine, Question

            engine = get_engine(PATH_TO_DB)
            with Session(engine) as session:
                statement = select(Question).where(Question.id == row["id"])
                question = session.exec(statement).first()

                if question:
                    console.print(f"  • {question.question[:100]}...")


if __name__ == "__main__":
    verify_embeddings()
