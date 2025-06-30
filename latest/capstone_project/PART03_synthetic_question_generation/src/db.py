#!/usr/bin/env python3
"""
Database operations for synthetic query generation.

This module contains all SQLite database operations including setup,
data insertion, and querying.
"""

import sqlite3
from pathlib import Path
from typing import Set

def setup_database(db_path: Path) -> None:
    """Create SQLite table for storing results"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_queries (
            conversation_hash TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            query TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (conversation_hash, prompt_version, query)
        )
    """)
    
    # Create index for faster lookups on individual columns
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_hash 
        ON synthetic_queries(conversation_hash)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_prompt_version 
        ON synthetic_queries(prompt_version)
    """)
    
    conn.commit()
    conn.close()

def save_query_to_db(db_path: Path, conversation_hash: str, prompt_version: str, query: str) -> bool:
    """Save a single query result to database immediately, ignore duplicates"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO synthetic_queries (conversation_hash, prompt_version, query)
            VALUES (?, ?, ?)
        """, (conversation_hash, prompt_version, query))
        
        conn.commit()
        # Return True if a new row was inserted
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Database error for {conversation_hash}: {e}")
        return False
    finally:
        conn.close()

def get_processed_conversations(db_path: Path) -> Set[str]:
    """Get set of conversation hashes that have been fully processed"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find conversations that have both v1 and v2 results
    cursor.execute("""
        SELECT conversation_hash 
        FROM synthetic_queries 
        GROUP BY conversation_hash 
        HAVING COUNT(DISTINCT prompt_version) = 2
    """)
    
    processed = {row[0] for row in cursor.fetchall()}
    conn.close()
    return processed

def get_results_summary(db_path: Path) -> dict:
    """Get summary of results in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT prompt_version, COUNT(*) FROM synthetic_queries GROUP BY prompt_version")
    counts = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(DISTINCT conversation_hash) FROM synthetic_queries")
    unique_conversations = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'version_counts': dict(counts),
        'unique_conversations': unique_conversations
    }
