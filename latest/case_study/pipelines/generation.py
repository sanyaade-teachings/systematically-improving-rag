"""
Generation pipelines for questions and summaries
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, TaskID

from core.db import (
    get_conversations_by_hashes,
    save_questions_to_sqlite,
    save_summaries_to_sqlite,
)
from core.synthetic_queries import (
    synthetic_question_generation_v1,
    synthetic_question_generation_v2,
    synthetic_question_generation_v3,
    synthetic_question_generation_v5,
    SearchQueries,
)
from core.summarization import (
    conversation_summary_v1,
    conversation_summary_v2,
    conversation_summary_v3,
    conversation_summary_v4,
    conversation_summary_v5,
    ConversationSummary,
)

console = Console()

fn_query = {
    "v1": synthetic_question_generation_v1,
    "v2": synthetic_question_generation_v2,
    "v3": synthetic_question_generation_v3,
    "v5": synthetic_question_generation_v5,
}

fn_summary = {
    "v1": conversation_summary_v1,
    "v2": conversation_summary_v2,
    "v3": conversation_summary_v3,
    "v4": conversation_summary_v4,
    "v5": conversation_summary_v5,
}


async def generate_questions_pipeline(
    conversation_hashes: List[str],
    version: str,
    db_path: Path,
    experiment_id: Optional[str] = None,
    concurrency: int = 10,
) -> Dict[str, int]:
    """
    Generate questions for conversations using specified techniques

    Args:
        conversation_hashes: List of conversation hashes to process
        versions: List of question generation versions
        db_path: Path to SQLite database
        experiment_id: Optional experiment ID for tracking
        concurrency: Max concurrent API requests

    Returns:
        Dict with generated counts per technique
    """
    console.print(
        f"[bold green]Generating questions with version: {version}[/bold green]"
    )

    # Load conversations
    conversations = get_conversations_by_hashes(conversation_hashes, db_path)
    console.print(f"Loaded {len(conversations)} conversations")

    results = {}

    questions = []
    semaphore = asyncio.Semaphore(concurrency)

    with Progress() as progress:
        task = progress.add_task(
            f"Generating {version} questions", total=len(conversations)
        )

        async def process_conversation(conv: Dict[str, Any]) -> SearchQueries | None:
            async with semaphore:
                try:
                    # Generate questions using the version
                    generated = await fn_query[version](conv, experiment_id)
                    progress.advance(task)
                    return generated
                except Exception as e:
                    console.print(
                        f"[red]Error processing {conv['conversation_hash']}: {e}[/red]"
                    )
                    progress.advance(task)
                    return None

        # Process all conversations concurrently
        tasks = [process_conversation(conv) for conv in conversations]
        questions = await asyncio.gather(*tasks)
        questions = [q for q in questions if q is not None]
        # Save to database
        saved_count = save_questions_to_sqlite(questions, db_path)
        results[version] = saved_count
        console.print(f"[green]Saved {saved_count} {version} questions[/green]")

    return results


async def generate_summaries_pipeline(
    conversation_hashes: List[str],
    version: str,
    db_path: Path,
    experiment_id: Optional[str] = None,
    concurrency: int = 10,
) -> Dict[str, int]:
    """
    Generate summaries for conversations using specified techniques
    """
    console.print(
        f"[bold green]Generating summaries with version: {version}[/bold green]"
    )

    # Load conversations
    conversations = get_conversations_by_hashes(conversation_hashes, db_path)
    console.print(f"Loaded {len(conversations)} conversations")

    results = {}

    summaries = []
    semaphore = asyncio.Semaphore(concurrency)

    with Progress() as progress:
        task = progress.add_task(
            f"Generating {version} summaries", total=len(conversations)
        )

        async def process_conversation(
            conv: Dict[str, Any],
        ) -> ConversationSummary | None:
            async with semaphore:
                try:
                    # Generate summary using the version
                    generated = await fn_summary[version](conv, experiment_id)
                    progress.advance(task)
                    return generated
                except Exception as e:
                    console.print(
                        f"[red]Error processing {conv['conversation_hash']}: {e}[/red]"
                    )
                    progress.advance(task)
                    return None

        # Process all conversations concurrently
        tasks = [process_conversation(conv) for conv in conversations]
        summaries = await asyncio.gather(*tasks)

        # Filter out None results
        summaries = [s for s in summaries if s is not None]

    # Save to database
    saved_count = save_summaries_to_sqlite(summaries, db_path, experiment_id)
    results[version] = saved_count
    console.print(f"[green]Saved {saved_count} {version} summaries[/green]")

    return results
