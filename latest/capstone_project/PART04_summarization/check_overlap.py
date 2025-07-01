#!/usr/bin/env python3
"""Check overlap between summaries and V2 queries"""

import sqlite3
from pathlib import Path

# Database paths
summaries_db = Path("data/synthetic_summaries.db")
queries_db = Path("../PART03_synthetic_question_generation/data/synthetic_queries.db")

# Get conversation hashes from summaries
conn_summaries = sqlite3.connect(summaries_db)
cursor_summaries = conn_summaries.cursor()
cursor_summaries.execute("SELECT DISTINCT conversation_hash FROM synthetic_summaries")
summary_hashes = {row[0] for row in cursor_summaries.fetchall()}
conn_summaries.close()

print(f"Total conversations with summaries: {len(summary_hashes)}")

# Get V2 queries
conn_queries = sqlite3.connect(queries_db)
cursor_queries = conn_queries.cursor()

# Count total V2 queries
cursor_queries.execute(
    "SELECT COUNT(*) FROM synthetic_queries WHERE prompt_version='v2'"
)
total_v2 = cursor_queries.fetchone()[0]
print(f"Total V2 queries: {total_v2}")

# Get V2 queries for conversations that have summaries
cursor_queries.execute("""
    SELECT conversation_hash, query 
    FROM synthetic_queries 
    WHERE prompt_version='v2'
""")

overlap_count = 0
overlap_queries = []
for hash, query in cursor_queries.fetchall():
    if hash in summary_hashes:
        overlap_count += 1
        overlap_queries.append((hash, query))

conn_queries.close()

print(f"V2 queries for conversations with summaries: {overlap_count}")
print(f"That's {overlap_count / total_v2 * 100:.1f}% of all V2 queries")

# Show a few examples
print("\nExample overlapping queries:")
for hash, query in overlap_queries[:5]:
    print(f"  {hash[:16]}...: {query[:80]}...")
