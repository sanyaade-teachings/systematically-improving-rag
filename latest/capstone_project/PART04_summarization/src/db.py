"""
Database operations for synthetic summaries
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime


def setup_database(db_path: Path) -> None:
    """Create the database schema for synthetic summaries"""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create synthetic_summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_summaries (
            conversation_hash TEXT NOT NULL,
            summary_version TEXT NOT NULL,
            summary TEXT NOT NULL,
            model TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (conversation_hash, summary_version)
        )
    """)

    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_hash 
        ON synthetic_summaries(conversation_hash)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_summary_version 
        ON synthetic_summaries(summary_version)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_model 
        ON synthetic_summaries(model)
    """)

    conn.commit()
    conn.close()


def save_summary_to_db(
    db_path: Path,
    conversation_hash: str,
    summary_version: str,
    summary: str,
    model: str,
) -> bool:
    """Save a summary to the database

    Returns:
        True if saved successfully, False if already exists
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT OR IGNORE INTO synthetic_summaries 
            (conversation_hash, summary_version, summary, model)
            VALUES (?, ?, ?, ?)
        """,
            (conversation_hash, summary_version, summary, model),
        )

        conn.commit()
        success = cursor.rowcount > 0

    except Exception as e:
        print(f"Error saving summary: {e}")
        success = False

    finally:
        conn.close()

    return success


def get_processed_conversations(db_path: Path, model: str) -> set:
    """Get set of conversation hashes that have been fully processed (both versions) for a specific model"""
    if not db_path.exists():
        return set()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get conversations that have both v1 and v2 summaries for the specific model
    cursor.execute(
        """
        SELECT conversation_hash 
        FROM synthetic_summaries
        WHERE model = ?
        GROUP BY conversation_hash
        HAVING COUNT(DISTINCT summary_version) >= 2
    """,
        (model,),
    )

    processed = {row[0] for row in cursor.fetchall()}
    conn.close()

    return processed


def get_existing_summaries(db_path: Path, model: str) -> set:
    """Get set of (conversation_hash, summary_version) tuples that already exist for a specific model"""
    if not db_path.exists():
        return set()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT conversation_hash, summary_version 
        FROM synthetic_summaries
        WHERE model = ?
    """,
        (model,),
    )

    existing = {(row[0], row[1]) for row in cursor.fetchall()}
    conn.close()

    return existing


def load_summaries_from_db(
    db_path: Path, version: str = None, limit: int = None
) -> List[Tuple[str, str, str, str]]:
    """Load summaries from database

    Returns:
        List of (conversation_hash, summary_version, summary, model) tuples
    """
    if not db_path.exists():
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT conversation_hash, summary_version, summary, model FROM synthetic_summaries"
    params = []

    if version:
        query += " WHERE summary_version = ?"
        params.append(version)

    query += " ORDER BY created_at DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    summaries = cursor.fetchall()

    conn.close()
    return summaries


def get_summaries_by_hash(db_path: Path, conversation_hash: str) -> Dict[str, str]:
    """Get all summaries for a specific conversation

    Returns:
        Dict mapping version to summary text
    """
    if not db_path.exists():
        return {}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT summary_version, summary 
        FROM synthetic_summaries
        WHERE conversation_hash = ?
    """,
        (conversation_hash,),
    )

    summaries = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return summaries


def get_results_summary(db_path: Path) -> Dict[str, Any]:
    """Get summary statistics about the database"""
    if not db_path.exists():
        return {
            "version_counts": {},
            "model_counts": {},
            "unique_conversations": 0,
            "total_summaries": 0,
        }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count by version
    cursor.execute("""
        SELECT summary_version, COUNT(*) 
        FROM synthetic_summaries 
        GROUP BY summary_version
    """)
    version_counts = dict(cursor.fetchall())

    # Count by model
    cursor.execute("""
        SELECT model, COUNT(*) 
        FROM synthetic_summaries 
        GROUP BY model
    """)
    model_counts = dict(cursor.fetchall())

    # Count unique conversations
    cursor.execute("""
        SELECT COUNT(DISTINCT conversation_hash) 
        FROM synthetic_summaries
    """)
    unique_conversations = cursor.fetchone()[0]

    # Total summaries
    cursor.execute("SELECT COUNT(*) FROM synthetic_summaries")
    total_summaries = cursor.fetchone()[0]

    conn.close()

    return {
        "version_counts": version_counts,
        "model_counts": model_counts,
        "unique_conversations": unique_conversations,
        "total_summaries": total_summaries,
    }
