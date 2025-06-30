#!/usr/bin/env python3
"""
Load WildChat data to Turbopuffer

This script loads WildChat-1M data into Turbopuffer with options for:
- Configurable batch size and limits
- Full-text search capabilities
- Vector search with embeddings
- Formatted conversation history
"""

import os
import sys
import time
from typing import List
import turbopuffer
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import typer
from rich.console import Console
from rich.progress import Progress

# Import from the same directory since we're in utils/
from dataloader import WildChatDataLoader

console = Console()
app = typer.Typer(help="Load WildChat data to Turbopuffer")

# Initialize embedding model
embedding_model = None

def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model"""
    global embedding_model
    if embedding_model is None:
        console.print("Loading embedding model...", style="cyan")
        embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        console.print("Embedding model loaded successfully", style="green")
    return embedding_model

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings for a list of texts"""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return [embedding.tolist() for embedding in embeddings]

def format_conversation_history(conversation: List[dict]) -> str:
    """
    Format the conversation history into a readable text format
    
    Args:
        conversation: List of message dictionaries with 'content' and optionally 'role'
        
    Returns:
        Formatted conversation string
    """
    if not conversation or len(conversation) == 0:
        return ""
    
    formatted_messages = []
    
    for i, message in enumerate(conversation):
        # Extract content
        content = message.get('content', '').strip()
        if not content:
            continue
            
        # Try to determine role (user vs assistant)
        role = message.get('role', '')
        
        # If no role provided, alternate between user and assistant
        # Assume first message is from user
        if not role:
            role = 'user' if i % 2 == 0 else 'assistant'
        
        # Format the message
        role_label = "User" if role.lower() in ['user', 'human'] else "Assistant"
        formatted_messages.append(f"{role_label}: {content}")
    
    return "\n\n".join(formatted_messages)

def create_conversation_summary(conversation: List[dict]) -> str:
    """
    Create a brief summary of the conversation for better searchability
    
    Args:
        conversation: List of message dictionaries
        
    Returns:
        Summary string combining first user message and key topics
    """
    if not conversation or len(conversation) == 0:
        return ""
    
    # Get first message (user query)
    first_message = conversation[0].get('content', '').strip()
    
    # For longer conversations, add context about the interaction
    if len(conversation) > 2:
        summary = f"User Query: {first_message}\n\nThis was a {len(conversation)}-turn conversation"
        
        # Add snippet of assistant's response if available
        if len(conversation) > 1:
            assistant_response = conversation[1].get('content', '').strip()
            if assistant_response:
                # Truncate long responses
                if len(assistant_response) > 200:
                    assistant_response = assistant_response[:200] + "..."
                summary += f" where the assistant responded: {assistant_response}"
        
        return summary
    else:
        return f"User Query: {first_message}"

def create_client() -> turbopuffer.Turbopuffer:
    """
    Create Turbopuffer client
    
    Returns:
        Turbopuffer client instance
    """
    load_dotenv()
    
    api_key = os.getenv('TURBOPUFFER_API_KEY')
    if not api_key:
        raise ValueError("Missing required environment variable: TURBOPUFFER_API_KEY")
    
    # Default to GCP US Central region, but allow override
    region = os.getenv('TURBOPUFFER_REGION', 'gcp-us-central1')
    
    console.print("Connecting to Turbopuffer...", style="blue")
    client = turbopuffer.Turbopuffer(
        api_key=api_key,
        region=region
    )
    console.print(f"Connected to Turbopuffer in region: {region}", style="green")
    
    return client

def load_to_turbopuffer(
    client: turbopuffer.Turbopuffer,
    namespace_name: str = "wildchat_2k",
    limit: int = 2000,
    batch_size: int = 25,
    filter_language: str = "English",
    min_message_length: int = 30,
    reset_namespace: bool = False
) -> None:
    """
    Load WildChat data to Turbopuffer using streaming approach with embeddings
    
    Args:
        client: Turbopuffer client instance
        namespace_name: Name of the namespace to create/use
        limit: Maximum number of records to load
        batch_size: Number of records to process in each batch
        filter_language: Language filter for conversations
        min_message_length: Minimum message length to include
        reset_namespace: If True, delete existing namespace before loading
    """
    
    console.print(f"Starting data load to namespace: {namespace_name}", style="blue")
    console.print(f"Config: limit={limit}, batch_size={batch_size}, language={filter_language}")
    console.print("Using embedding model: sentence-transformers/all-MiniLM-L6-v2", style="cyan")
    
    try:
        # Get namespace
        ns = client.namespace(namespace_name)
        
        # Handle namespace reset
        if reset_namespace:
            try:
                client.delete_namespace(namespace_name)
                console.print(f"Deleted existing namespace: {namespace_name}", style="yellow")
                ns = client.namespace(namespace_name)  # Recreate after deletion
            except Exception:
                pass  # Namespace might not exist
        
        # Initialize data loader
        loader = WildChatDataLoader()
        
        # Batch processing variables
        batch_data = {
            'id': [],
            'vector': [],
            'text': [],
            'conversation_string': [],
            'hash': [],
            'timestamp': [],
            'language': [],
            'model_name': [],
            'conversation_length': [],
            'country': [],
            'toxic': [],
            'redacted': [],
            'turn': []
        }
        batch_texts = []
        total_processed = 0
        total_added = 0
        duplicates_skipped = 0
        
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
                if doc_id in batch_data['id']:
                    duplicates_skipped += 1
                    continue
                
                # Get original conversation data for formatting
                original_conversation = conversation.get('conversation', [])
                
                # Format conversation history and create summary
                formatted_history = format_conversation_history(original_conversation)
                
                # Use first message as main text (for embeddings)
                message_text = conversation['first_message'] # we dont truncate the message, only truncate for embeddings
                
                # Add to batch
                batch_data['id'].append(doc_id)
                batch_data['text'].append(message_text)
                batch_data['conversation_string'].append(formatted_history)
                batch_data['hash'].append(conversation['conversation_hash'])
                batch_data['timestamp'].append(str(conversation['timestamp']))
                batch_data['language'].append(conversation['language'])
                batch_data['model_name'].append(conversation['model'])
                batch_data['conversation_length'].append(conversation['conversation_length'])
                batch_data['country'].append(conversation.get('country', 'Unknown'))
                batch_data['toxic'].append(conversation['toxic'])
                batch_data['redacted'].append(conversation['redacted'])
                batch_data['turn'].append(conversation['turn'])
                
                batch_texts.append(message_text)
                
                # Process batch when full
                if len(batch_data['id']) >= batch_size:
                    try:
                        # Generate embeddings for the batch
                        console.print(f"Generating embeddings for batch of {len(batch_texts)} documents...", style="blue")
                        embeddings = create_embeddings([
                            text[:2000] for text in batch_texts # truncate the text to 2000 characters for embeddings
                        ])
                        batch_data['vector'] = embeddings
                        
                        # Write batch to Turbopuffer
                        ns.write(
                            upsert_columns=batch_data,
                            distance_metric='cosine_distance',
                            schema={
                                "text": {
                                    "type": "string",
                                    "full_text_search": True,
                                },
                                "conversation_string": {
                                    "type": "string",
                                    "full_text_search": True,
                                },
                                "hash": {"type": "string"},
                                "timestamp": {"type": "string"},
                                "language": {"type": "string"},
                                "model_name": {"type": "string"},
                                "conversation_length": {"type": "int"},
                                "country": {"type": "string"},
                                "toxic": {"type": "bool"},
                                "redacted": {"type": "bool"},
                                "turn": {"type": "int"}
                            }
                        )
                        
                        total_added += len(batch_data['id'])
                        console.print(f"Batch written: {total_added} documents added so far (with embeddings)", style="green")
                        
                    except Exception as e:
                        if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                            console.print("Warning: Duplicate entries detected in batch, skipping", style="yellow")
                            duplicates_skipped += len(batch_data['id'])
                        else:
                            console.print(f"Error writing batch: {e}", style="red")
                            raise
                    
                    # Reset batch
                    batch_data = {key: [] for key in batch_data.keys()}
                    batch_texts = []
        
        # Write final batch
        if batch_data['id']:
            try:
                console.print(f"Generating embeddings for final batch of {len(batch_texts)} documents...", style="blue")
                embeddings = create_embeddings(batch_texts)
                batch_data['vector'] = embeddings
                
                ns.write(
                    upsert_columns=batch_data,
                    distance_metric='cosine_distance',
                    schema={
                        "text": {
                            "type": "string",
                            "full_text_search": True,
                        },
                        "hash": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "language": {"type": "string"},
                        "model_name": {"type": "string"},
                        "conversation_length": {"type": "int"},
                        "country": {"type": "string"},
                        "toxic": {"type": "bool"},
                        "redacted": {"type": "bool"},
                        "turn": {"type": "int"}
                    }
                )
                
                total_added += len(batch_data['id'])
                console.print("Final batch written", style="green")
                
            except Exception as e:
                if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                    console.print("Warning: Duplicate entries in final batch, skipping", style="yellow")
                    duplicates_skipped += len(batch_data['id'])
                else:
                    console.print(f"Error writing final batch: {e}", style="red")
        
        # Calculate load time
        load_end_time = time.time()
        load_duration = load_end_time - load_start_time
        
        # Get final statistics - approximate count via query
        try:
            count_result = ns.query(
                aggregate_by={'document_count': ('Count', 'id')},
                filters=('language', 'Eq', filter_language)  # Count documents with our language filter
            )
            final_count = count_result.aggregations['document_count']
        except Exception:
            # Fallback: try to count all documents
            try:
                count_result = ns.query(
                    aggregate_by={'document_count': ('Count', 'id')}
                )
                final_count = count_result.aggregations['document_count']
            except Exception:
                final_count = "Unknown"
        
        console.print("\nLoad completed!", style="green bold")
        console.print("Statistics:")
        console.print(f"   - Total processed: {total_processed}")
        console.print(f"   - Total added: {total_added}")
        console.print(f"   - Duplicates skipped: {duplicates_skipped}")
        console.print(f"   - Namespace size: {final_count}")
        console.print(f"   - Load time: {load_duration:.2f} seconds")
        
        # Test query with timing
        if total_added > 0:
            console.print("\nTesting namespace with sample query...", style="blue")
            try:
                # Test vector search
                search_start_time = time.time()
                test_embedding = create_embeddings(["How to learn programming"])[0]
                results = ns.query(
                    rank_by=("vector", "ANN", test_embedding),
                    top_k=3,
                    include_attributes=['text', 'language']
                )
                search_end_time = time.time()
                search_duration_ms = (search_end_time - search_start_time) * 1000
                
                console.print(f"Success: Query found {len(results.rows)} similar conversations", style="green")
                console.print(f"   - Search time: {search_duration_ms:.1f} ms")
                if results.rows:
                    console.print(f"   Most similar: '{results.rows[0].text[:100]}...'")
                    
            except Exception as e:
                console.print(f"Warning: Query error: {e}", style="yellow")
                
                # Try a simple aggregation instead
                try:
                    simple_result = ns.query(
                        aggregate_by={'sample_count': ('Count', 'id')},
                        filters=('language', 'Eq', filter_language)
                    )
                    console.print(f"Success: Namespace accessible - found {simple_result.aggregations['sample_count']} documents", style="green")
                except Exception as e2:
                    console.print(f"Error accessing namespace: {e2}", style="red")
        
    except Exception as e:
        console.print(f"Error during data loading: {e}", style="red")
        raise


@app.command()
def main(
    namespace_name: str = typer.Option(
        "wildchat_2k",
        "--namespace-name",
        help="Name of the Turbopuffer namespace"
    ),
    limit: int = typer.Option(
        2000,
        "--limit",
        help="Maximum number of records to load"
    ),
    batch_size: int = typer.Option(
        25,
        "--batch-size",
        help="Batch size for writing to Turbopuffer"
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
        help="Reset namespace before loading (delete existing data)"
    )
):
    """Load WildChat data to Turbopuffer"""
    
    console.print("WildChat to Turbopuffer Loader", style="bold blue")
    console.print("=" * 50)
    
    try:
        # Create client
        client = create_client()
        
        # Load data
        load_to_turbopuffer(
            client=client,
            namespace_name=namespace_name,
            limit=limit,
            batch_size=batch_size,
            filter_language=language,
            min_message_length=min_length,
            reset_namespace=reset
        )
        
    except KeyboardInterrupt:
        console.print("\nOperation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"\nError: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
