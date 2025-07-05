#!/usr/bin/env python3
"""
Analyze Failed Queries

This script analyzes the failed queries to identify patterns and potential improvements.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import typer
from rich.console import Console
from rich.table import Table
from typing import Dict, List, Any

console = Console()
app = typer.Typer(help="Analyze failed queries from recall tests")


def load_failed_queries(file_path: Path) -> Dict[str, Any]:
    """Load failed queries from JSON file"""
    with open(file_path, "r") as f:
        return json.load(f)


def analyze_query_patterns(failed_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze patterns in failed queries"""

    # Extract common words/phrases
    word_counter = Counter()
    phrase_counter = Counter()

    for item in failed_queries:
        query = item["query"].lower()

        # Count individual words (excluding common words)
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "about",
        }
        words = [w for w in query.split() if w not in common_words]
        word_counter.update(words)

        # Count bi-grams
        words_full = query.split()
        for i in range(len(words_full) - 1):
            bigram = f"{words_full[i]} {words_full[i + 1]}"
            phrase_counter[bigram] += 1

    return {
        "common_words": word_counter.most_common(20),
        "common_phrases": phrase_counter.most_common(15),
    }


def analyze_top_results(failed_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze what was returned instead of the correct results"""

    summary_patterns = Counter()

    for item in failed_queries:
        for result in item.get("top_results", []):
            summary = result.get("summary", "")
            # Extract the conversation type from summary (if using v4 format)
            if summary.startswith("This is a"):
                parts = summary.split("conversation")
                if len(parts) > 0:
                    conv_type = parts[0].replace("This is a", "").strip()
                    summary_patterns[conv_type] += 1

    return {
        "common_result_types": summary_patterns.most_common(10),
    }


def group_by_conversation(failed_queries: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Group failed queries by conversation hash"""

    groups = defaultdict(list)
    for item in failed_queries:
        groups[item["conversation_hash"]].append(item["query"])

    # Sort by number of failed queries per conversation
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    return dict(sorted_groups[:10])  # Top 10 conversations with most failures


@app.command()
def analyze(
    query_version: str = typer.Option("v2", help="Query version (v1 or v2)"),
    summary_version: str = typer.Option(
        "v4", help="Summary version (v1, v2, v3, or v4)"
    ),
):
    """Analyze failed queries from recall tests"""

    # Load failed queries
    file_path = (
        Path(__file__).parent
        / f"failed_queries_q{query_version}_s{summary_version}.json"
    )

    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return

    data = load_failed_queries(file_path)
    failed_queries = data["failed_queries"]

    console.print("[bold]Failed Query Analysis[/bold]")
    console.print(f"Query Version: {query_version}")
    console.print(f"Summary Version: {summary_version}")
    console.print(f"Total Failed: {data['total_failed']}")
    console.print(f"Recall Rate: {data['recall_rate']:.2%}\n")

    # Analyze query patterns
    patterns = analyze_query_patterns(failed_queries)

    # Display common words
    console.print("[bold cyan]Most Common Words in Failed Queries:[/bold cyan]")
    word_table = Table()
    word_table.add_column("Word", style="green")
    word_table.add_column("Count", style="yellow")

    for word, count in patterns["common_words"][:10]:
        word_table.add_row(word, str(count))

    console.print(word_table)

    # Display common phrases
    console.print("\n[bold cyan]Most Common Phrases in Failed Queries:[/bold cyan]")
    phrase_table = Table()
    phrase_table.add_column("Phrase", style="green")
    phrase_table.add_column("Count", style="yellow")

    for phrase, count in patterns["common_phrases"][:10]:
        phrase_table.add_row(phrase, str(count))

    console.print(phrase_table)

    # Analyze top results
    result_analysis = analyze_top_results(failed_queries)

    if result_analysis["common_result_types"]:
        console.print(
            "\n[bold cyan]Common Types in Top Results (What was found instead):[/bold cyan]"
        )
        result_table = Table()
        result_table.add_column("Result Type", style="green")
        result_table.add_column("Count", style="yellow")

        for result_type, count in result_analysis["common_result_types"]:
            result_table.add_row(result_type, str(count))

        console.print(result_table)

    # Group by conversation
    grouped = group_by_conversation(failed_queries)

    console.print("\n[bold cyan]Conversations with Most Failed Queries:[/bold cyan]")
    conv_table = Table()
    conv_table.add_column("Conversation Hash", style="green")
    conv_table.add_column("Failed Count", style="yellow")
    conv_table.add_column("Example Queries", style="blue")

    for conv_hash, queries in list(grouped.items())[:5]:
        example_queries = "; ".join(queries[:2])
        if len(queries) > 2:
            example_queries += "..."
        conv_table.add_row(conv_hash, str(len(queries)), example_queries)

    console.print(conv_table)

    # Sample failed queries
    console.print("\n[bold cyan]Sample Failed Queries:[/bold cyan]")
    for i, item in enumerate(failed_queries[:5]):
        console.print(f"\n[yellow]Query {i + 1}:[/yellow] {item['query']}")
        console.print(f"[dim]Conv Hash:[/dim] {item['conversation_hash']}")
        if item["top_results"]:
            console.print("[dim]Top Result:[/dim]")
            top_result = item["top_results"][0]
            console.print(f"  [dim]Hash:[/dim] {top_result['hash']}")
            console.print(f"  [dim]Summary:[/dim] {top_result['summary']}")


if __name__ == "__main__":
    app()
