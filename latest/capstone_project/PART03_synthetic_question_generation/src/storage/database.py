"""Database management for synthetic queries."""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
import json


class QueryDatabase:
    """Manage SQLite database for synthetic queries."""
    
    def __init__(self, db_path: Path):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS synthetic_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_hash TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    query TEXT NOT NULL,
                    chain_of_thought TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Create indexes for better query performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversation_hash 
                ON synthetic_queries(conversation_hash)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_version 
                ON synthetic_queries(prompt_version)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON synthetic_queries(created_at)
            """)
            
            # Create a conversations table to track processed conversations
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_conversations (
                    conversation_hash TEXT PRIMARY KEY,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    versions_processed TEXT
                )
            """)
            conn.commit()
    
    def insert_queries(self, queries: List[Tuple[str, str, str, str, Optional[Dict[str, Any]]]]):
        """Insert multiple queries into the database.
        
        Args:
            queries: List of tuples (conversation_hash, prompt_version, query, chain_of_thought, metadata)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO synthetic_queries 
                (conversation_hash, prompt_version, query, chain_of_thought, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                [(h, v, q, c, json.dumps(m) if m else None) for h, v, q, c, m in queries]
            )
            conn.commit()
    
    def get_queries(
        self, 
        limit: Optional[int] = None,
        version: Optional[str] = None,
        conversation_hash: Optional[str] = None
    ) -> List[Tuple[str, str, str]]:
        """Load queries from database.
        
        Args:
            limit: Maximum number of queries to return
            version: Filter by prompt version (v1 or v2)
            conversation_hash: Filter by specific conversation hash
            
        Returns:
            List of tuples (conversation_hash, prompt_version, query)
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT conversation_hash, prompt_version, query 
                FROM synthetic_queries
                WHERE 1=1
            """
            params = []
            
            if version:
                query += " AND prompt_version = ?"
                params.append(version)
            
            if conversation_hash:
                query += " AND conversation_hash = ?"
                params.append(conversation_hash)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def mark_conversation_processed(self, conversation_hash: str, versions: List[str]):
        """Mark a conversation as processed.
        
        Args:
            conversation_hash: Hash of the processed conversation
            versions: List of versions processed (e.g., ['v1', 'v2'])
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO processed_conversations 
                (conversation_hash, versions_processed)
                VALUES (?, ?)
                """,
                (conversation_hash, ','.join(versions))
            )
            conn.commit()
    
    def is_conversation_processed(self, conversation_hash: str, version: Optional[str] = None) -> bool:
        """Check if a conversation has been processed.
        
        Args:
            conversation_hash: Hash of the conversation
            version: Specific version to check (optional)
            
        Returns:
            True if processed, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT versions_processed FROM processed_conversations WHERE conversation_hash = ?",
                (conversation_hash,)
            )
            result = cursor.fetchone()
            
            if not result:
                return False
            
            if version:
                versions_processed = result[0].split(',')
                return version in versions_processed
            
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total queries
            cursor = conn.execute("SELECT COUNT(*) FROM synthetic_queries")
            stats['total_queries'] = cursor.fetchone()[0]
            
            # Queries by version
            cursor = conn.execute(
                "SELECT prompt_version, COUNT(*) FROM synthetic_queries GROUP BY prompt_version"
            )
            stats['queries_by_version'] = dict(cursor.fetchall())
            
            # Unique conversations
            cursor = conn.execute("SELECT COUNT(DISTINCT conversation_hash) FROM synthetic_queries")
            stats['unique_conversations'] = cursor.fetchone()[0]
            
            # Processed conversations
            cursor = conn.execute("SELECT COUNT(*) FROM processed_conversations")
            stats['processed_conversations'] = cursor.fetchone()[0]
            
            return stats