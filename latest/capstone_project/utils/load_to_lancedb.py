#!/usr/bin/env python3
"""
Load WildChat data to LanceDB

This script loads WildChat-1M data into LanceDB with options for:
- Local persistent storage
- Cloud storage  
- Configurable batch size and limits
"""

import os
import sys
import time
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from dotenv import load_dotenv
import typer
from rich.console import Console
from rich.progress import Progress

# Import from the same directory since we're in utils/
from dataloader import WildChatDataLoader

console = Console()
app = typer.Typer(help="Load WildChat data to LanceDB")

model = get_registry().get("sentence-transformers").create(
            name="sentence-transformers/all-MiniLM-L6-v2", 
            device="cpu")

class WildChatConversation(LanceModel):
    """LanceDB schema for WildChat conversations with embeddings"""
    id: str
    text: str = model.SourceField()
    vector: Vector(384) = model.VectorField()  # BAAI/bge-small-en-v1.5 has 384 dimensions
    hash: str
    timestamp: str
    language: str
    model_name: str
    conversation_length: int
    conversation_string: str
    country: str
    toxic: bool
    redacted: bool
    turn: int


def create_client(use_cloud: bool = False) -> lancedb.DBConnection:
    """
    Create LanceDB client - either local persistent or cloud
    
    Args:
        use_cloud: If True, use cloud client. If False, use local persistent client.
        
    Returns:
        LanceDB connection instance
    """
    if use_cloud:
        # Load environment variables for cloud connection
        load_dotenv()
        
        required_env_vars = ['LANCEDB_API_KEY', 'LANCEDB_URI']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables for cloud: {missing_vars}")
        
        console.print("Connecting to LanceDB Cloud...", style="blue")
        db = lancedb.connect(
            uri=os.getenv('LANCEDB_URI'),
            api_key=os.getenv('LANCEDB_API_KEY')
        )
        console.print(f"Connected to cloud database: {os.getenv('LANCEDB_URI')}", style="green")
        
    else:
        # Use local persistent client
        db_path = "./lance_db"
        console.print(f"Using local persistent LanceDB at: {db_path}", style="blue")
        db = lancedb.connect(db_path)
        console.print("Connected to local persistent LanceDB", style="green")
    
    return db


def load_to_lancedb(
    db: lancedb.DBConnection,
    table_name: str = "wildchat_2k",
    limit: int = 2000,
    batch_size: int = 25,
    filter_language: str = "English",
    min_message_length: int = 30,
    reset_table: bool = False
) -> None:
    """
    Load WildChat data to LanceDB using streaming approach with embeddings
    
    Args:
        db: LanceDB connection instance
        table_name: Name of the table to create/use
        limit: Maximum number of records to load
        batch_size: Number of records to process in each batch
        filter_language: Language filter for conversations
        min_message_length: Minimum message length to include
        reset_table: If True, delete existing table before loading
    """
    
    console.print(f"Starting data load to table: {table_name}", style="blue")
    console.print(f"Config: limit={limit}, batch_size={batch_size}, language={filter_language}")
    console.print("Using embedding model: sentence-transformers/all-MiniLM-L6-v2", style="cyan")
    
    try:
        # Handle table creation/reset
        if reset_table:
            try:
                db.drop_table(table_name)
                console.print(f"Deleted existing table: {table_name}", style="yellow")
            except Exception:
                pass  # Table might not exist
        
        # Initialize data loader
        loader = WildChatDataLoader()
        
        # Batch processing variables
        batch_data = []
        total_processed = 0
        total_added = 0
        duplicates_skipped = 0
        table = None
        
        console.print("Loading conversations...", style="blue")
        
        # Start timing the data load
        load_start_time = time.time()
        
        conversation_stream = loader.stream_conversations(
            limit=limit,
            min_message_length=min_message_length,
            filter_language=filter_language,
            filter_toxic=True
        )
        
        # Use rich progress bar
        with Progress() as progress:
            task = progress.add_task("Processing conversations...", total=limit)
            
            for conversation in conversation_stream:
                total_processed += 1
                progress.update(task, advance=1)
                
                # Prepare document data
                doc_id = conversation['conversation_hash']
                
                # Check for duplicates in current batch
                if any(row['id'] == doc_id for row in batch_data):
                    duplicates_skipped += 1
                    continue
                
                # Truncate message if too long
                message_text = conversation['first_message'][:2000]
                
                # Prepare row data matching the schema
                row_data = {
                    'id': doc_id,
                    'text': message_text,  # This will be automatically embedded
                    'hash': conversation['conversation_hash'],
                    'timestamp': str(conversation['timestamp']),
                    'language': conversation['language'],
                    'model_name': conversation['model'],  # Note: renamed from 'model' to avoid conflicts
                    'conversation_length': conversation['conversation_length'],
                    'country': conversation.get('country', 'Unknown'),
                    'toxic': conversation['toxic'],
                    'redacted': conversation['redacted'],
                    'turn': conversation['turn'],
                    'conversation_string': conversation['conversation_string']
                }
                
                # Add to batch
                batch_data.append(row_data)
                
                # Process batch when full
                if len(batch_data) >= batch_size:
                    try:
                        if table is None:
                            # Create table with schema and first batch
                            table = db.create_table(table_name, schema=WildChatConversation)
                            table.create_fts_index("text") # Create full-text search index on text field
                            table.create_fts_index("conversation_string") # Create full-text search index on conversation_string field
                            console.print(f"Created table: {table_name} with embedding schema", style="green")
                        
                        # Add batch data - embeddings will be computed automatically
                        table.add(batch_data)
                        
                        total_added += len(batch_data)
                        
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                            console.print("Warning: Duplicate entries detected in batch, skipping", style="yellow")
                            duplicates_skipped += len(batch_data)
                        else:
                            console.print(f"Error writing batch: {e}", style="red")
                            raise
                    
                    # Reset batch
                    batch_data = []
        
        # Write final batch
        if batch_data:
            try:
                if table is None:
                    # Create table with schema and final batch if no batches were processed
                    table = db.create_table(table_name, schema=WildChatConversation)
                    table.create_fts_index("text") # Create full-text search index on text field
                    table.create_fts_index("conversation_string") # Create full-text search index on conversation_string field
                    console.print(f"Created table: {table_name} with embedding schema", style="green")
                
                # Add final batch data
                table.add(batch_data)
                
                total_added += len(batch_data)
                console.print("Final batch written", style="green")
                
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    console.print("Warning: Duplicate entries in final batch, skipping", style="yellow")
                    duplicates_skipped += len(batch_data)
                else:
                    console.print(f"Error writing final batch: {e}", style="red")
        
        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time
        
        # Get final statistics
        if table is not None:
            final_count = table.count_rows()
        else:
            final_count = 0
            
        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Table size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")
        
        # Test query with vector search and timing
        if table is not None and final_count > 0:
            console.print("\nTesting table with sample query...", style="blue")
            try:
                search_start_time = time.time()
                results = table.search("How to learn programming").limit(3).to_pydantic(WildChatConversation)
                search_end_time = time.time()
                search_duration_ms = (search_end_time - search_start_time) * 1000
                
                console.print(f"Success: Query found {len(results)} similar conversations", style="green")
                console.print(f"   - Search time: {search_duration_ms:.1f} ms")
                if results:
                    console.print(f"   Most similar: '{results[0].text[:100]}...'")
            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")
                
                # Try a simple query instead
                try:
                    sample_results = table.to_pandas().head(3)
                    console.print(f"Success: Table accessible - showing {len(sample_results)} sample records", style="green")
                except Exception as e2:
                    console.print(f"Error accessing table: {e2}", style="red")
        
    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise


@app.command()
def main(
    cloud: bool = typer.Option(
        False, 
        "--cloud",
        help="Use LanceDB Cloud instead of local persistent storage"
    ),
    table_name: str = typer.Option(
        "wildchat_2k",
        "--table-name",
        help="Name of the LanceDB table"
    ),
    limit: int = typer.Option(
        2000,
        "--limit",
        help="Maximum number of records to load"
    ),
    batch_size: int = typer.Option(
        25,
        "--batch-size",
        help="Batch size for writing to LanceDB"
    ),
    language: str = typer.Option(
        "English",
        "--language",
        help="Filter conversations by language"
    ),
    min_length: int = typer.Option(
        30,
        "--min-length",
        help="Minimum message length to include"
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset table before loading (delete existing data)"
    )
):
    """Load WildChat data to LanceDB"""
    
    console.print("WildChat to LanceDB Loader", style="bold blue")
    console.print("=" * 50)
    
    try:
        # Create client
        db = create_client(use_cloud=cloud)
        
        # Load data
        load_to_lancedb(
            db=db,
            table_name=table_name,
            limit=limit,
            batch_size=batch_size,
            filter_language=language,
            min_message_length=min_length,
            reset_table=reset
        )
        
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
