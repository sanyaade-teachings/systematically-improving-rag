"""
Embedding generation and management for conversations and summaries.
"""

import asyncio
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI
from rich.console import Console
from rich.progress import Progress, TaskID
import pyarrow.parquet as pq
import pyarrow as pa
import os

console = Console()


class EmbeddingGenerator:
    """Handles embedding generation using different models"""
    
    def __init__(self, model_name: str = "text-embedding-3-large"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Either an OpenAI model name or a sentence-transformers model
        """
        self.model_name = model_name
        self.is_openai = model_name.startswith("text-embedding")
        
        if not self.is_openai:
            # Load sentence-transformers model
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
        else:
            # OpenAI models
            self.model = None
            if model_name == "text-embedding-ada-002":
                self.dimension = 1536
            elif model_name == "text-embedding-3-large":
                self.dimension = 3072
            elif model_name == "text-embedding-3-small":
                self.dimension = 1536
            else:
                raise ValueError(f"Unknown OpenAI model: {model_name}")
    
    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if self.is_openai:
            return await self._generate_openai_embeddings(texts, batch_size, show_progress)
        else:
            return self._generate_sentence_transformer_embeddings(texts, batch_size, show_progress)
    
    async def _generate_openai_embeddings(
        self,
        texts: List[str],
        batch_size: int,
        show_progress: bool
    ) -> np.ndarray:
        """Generate embeddings using OpenAI API"""
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        embeddings = []
        
        if show_progress:
            with Progress() as progress:
                task = progress.add_task(
                    f"Generating {self.model_name} embeddings",
                    total=len(texts)
                )
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    response = await client.embeddings.create(
                        model=self.model_name,
                        input=batch
                    )
                    batch_embeddings = [e.embedding for e in response.data]
                    embeddings.extend(batch_embeddings)
                    progress.update(task, advance=len(batch))
        else:
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = await client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                batch_embeddings = [e.embedding for e in response.data]
                embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def _generate_sentence_transformer_embeddings(
        self,
        texts: List[str],
        batch_size: int,
        show_progress: bool
    ) -> np.ndarray:
        """Generate embeddings using sentence-transformers"""
        if show_progress:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
        else:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True
            )
        
        return embeddings


def save_embeddings_to_parquet(
    embeddings: np.ndarray,
    metadata: List[Dict[str, Any]],
    output_path: Path,
    embedding_model: str
) -> None:
    """
    Save embeddings and metadata to a parquet file
    
    Args:
        embeddings: Numpy array of embeddings
        metadata: List of metadata dicts (must include 'id' field)
        output_path: Path to save the parquet file
        embedding_model: Name of the embedding model used
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create dataframe
    df_data = []
    for i, meta in enumerate(metadata):
        row = {
            'id': meta['id'],
            'embedding': embeddings[i].tolist(),
            'embedding_model': embedding_model,
            **{k: v for k, v in meta.items() if k != 'id'}
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Save to parquet
    df.to_parquet(output_path, index=False)
    console.print(f"[green]Saved {len(df)} embeddings to {output_path}[/green]")


def load_embeddings_from_parquet(
    parquet_path: Path,
    return_metadata: bool = True
) -> tuple[np.ndarray, Optional[pd.DataFrame]]:
    """
    Load embeddings from a parquet file
    
    Args:
        parquet_path: Path to the parquet file
        return_metadata: Whether to return metadata DataFrame
        
    Returns:
        Tuple of (embeddings array, metadata DataFrame or None)
    """
    df = pd.read_parquet(parquet_path)
    
    # Convert embedding column to numpy array
    embeddings = np.array(df['embedding'].tolist())
    
    if return_metadata:
        # Return all columns except embedding as metadata
        metadata_df = df.drop(columns=['embedding'])
        return embeddings, metadata_df
    else:
        return embeddings, None


async def generate_conversation_embeddings(
    conversations: List[Dict[str, Any]],
    embedding_model: str = "text-embedding-3-large",
    output_dir: Path = Path("data/embeddings/conversations"),
    batch_size: int = 100
) -> Path:
    """
    Generate embeddings for conversations and save to parquet
    
    Args:
        conversations: List of conversation dicts (must have 'conversation_hash' and 'text')
        embedding_model: Name of the embedding model to use
        output_dir: Directory to save embeddings
        batch_size: Batch size for embedding generation
        
    Returns:
        Path to the saved parquet file
    """
    console.print(f"[bold green]Generating embeddings for {len(conversations)} conversations[/bold green]")
    
    # Initialize embedding generator
    generator = EmbeddingGenerator(embedding_model)
    
    # Extract texts and metadata, filtering out empty texts
    texts = []
    metadata = []
    skipped = 0
    for conv in conversations:
        if conv['text'] and conv['text'].strip():  # Skip empty texts
            texts.append(conv['text'])
            meta = {
                'id': conv['conversation_hash'],
                'conversation_hash': conv['conversation_hash'],
                'language': conv.get('language', 'English'),
            }
            # Only add non-None values
            if conv.get('country') is not None:
                meta['country'] = conv['country']
            if conv.get('timestamp') is not None:
                meta['timestamp'] = conv['timestamp']
            metadata.append(meta)
        else:
            skipped += 1
    
    if skipped > 0:
        console.print(f"[yellow]Skipped {skipped} conversations with empty text[/yellow]")
    
    # Generate embeddings
    embeddings = await generator.generate_embeddings(texts, batch_size)
    
    # Save to parquet
    output_path = output_dir / f"{embedding_model.replace('/', '-')}.parquet"
    save_embeddings_to_parquet(embeddings, metadata, output_path, embedding_model)
    
    return output_path


async def generate_summary_embeddings(
    summaries: List[Dict[str, Any]],
    embedding_model: str = "text-embedding-3-large",
    output_dir: Path = Path("data/embeddings/summaries"),
    batch_size: int = 100
) -> Path:
    """
    Generate embeddings for summaries and save to parquet
    
    Args:
        summaries: List of summary dicts (must have 'id', 'summary', 'technique')
        embedding_model: Name of the embedding model to use
        output_dir: Directory to save embeddings
        batch_size: Batch size for embedding generation
        
    Returns:
        Path to the saved parquet file
    """
    console.print(f"[bold green]Generating embeddings for {len(summaries)} summaries[/bold green]")
    
    # Initialize embedding generator
    generator = EmbeddingGenerator(embedding_model)
    
    # Extract texts and metadata, filtering out None values
    texts = [s['summary'] for s in summaries]
    metadata = []
    for s in summaries:
        # IMPORTANT: ChromaDB document IDs must match what we search for in evaluation
        # The summary table uses IDs like "hash_v1" for uniqueness, but we search by
        # conversation_hash alone. So we use conversation_hash as the ChromaDB document ID.
        # This ensures that when we search for a conversation_hash, we find the right document.
        meta = {
            'id': s['conversation_hash'],  # Use conversation_hash as ChromaDB doc ID (NOT the database ID with suffix!)
            'conversation_hash': s['conversation_hash'],
            'technique': s['technique'],
        }
        # Only add experiment_id if it's not None
        if s.get('experiment_id') is not None:
            meta['experiment_id'] = s['experiment_id']
        metadata.append(meta)
    
    # Generate embeddings
    embeddings = await generator.generate_embeddings(texts, batch_size)
    
    # Save to parquet
    technique = summaries[0]['technique'] if summaries else 'unknown'
    output_path = output_dir / f"{technique}_{embedding_model.replace('/', '-')}.parquet"
    save_embeddings_to_parquet(embeddings, metadata, output_path, embedding_model)
    
    return output_path


def truncate_text_to_tokens(text: str, max_tokens: int = 8000, model: str = "text-embedding-3-large") -> str:
    """
    Truncate text to approximately max_tokens.
    
    For simplicity, we use character-based truncation with a rough estimate:
    - Average English word is ~5 characters
    - Average token is ~4 characters (0.75 tokens per word)
    
    Args:
        text: Text to truncate
        max_tokens: Maximum number of tokens
        model: Model name (for future token counting improvements)
        
    Returns:
        Truncated text
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text
    
    # Truncate and add ellipsis
    return text[:max_chars - 3] + "..."


async def generate_full_conversation_embeddings(
    conversations: List[Dict[str, Any]],
    embedding_model: str = "text-embedding-3-large",
    output_dir: Path = Path("data/embeddings/full_conversations"),
    batch_size: int = 100,
    max_tokens: int = 8000
) -> Path:
    """
    Generate embeddings for full conversations (not just first message) and save to parquet
    
    Args:
        conversations: List of conversation dicts (must have 'conversation_hash' and 'conversation_full')
        embedding_model: Name of the embedding model to use
        output_dir: Directory to save embeddings
        batch_size: Batch size for embedding generation
        max_tokens: Maximum tokens per conversation (will truncate if longer)
        
    Returns:
        Path to the saved parquet file
    """
    console.print(f"[bold green]Generating full conversation embeddings for {len(conversations)} conversations[/bold green]")
    console.print(f"[yellow]Max tokens per conversation: {max_tokens}[/yellow]")
    
    # Initialize embedding generator
    generator = EmbeddingGenerator(embedding_model)
    
    # Extract texts and metadata, filtering out empty conversations
    texts = []
    metadata = []
    skipped = 0
    truncated = 0
    
    for conv in conversations:
        # Parse conversation_full JSON string if needed
        if isinstance(conv.get('conversation_full'), str):
            try:
                import json
                conversation_data = json.loads(conv['conversation_full'])
            except:
                # If not JSON, use as is
                conversation_data = conv.get('conversation_full', '')
        else:
            conversation_data = conv.get('conversation_full', [])
        
        # Convert conversation to text
        if isinstance(conversation_data, list):
            # Format as "role: content" for each message
            full_text = "\n\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in conversation_data
                if msg.get('content')
            ])
        else:
            full_text = str(conversation_data)
        
        if full_text and full_text.strip():  # Skip empty conversations
            # Truncate if needed
            original_len = len(full_text)
            truncated_text = truncate_text_to_tokens(full_text, max_tokens, embedding_model)
            if len(truncated_text) < original_len:
                truncated += 1
            
            texts.append(truncated_text)
            meta = {
                'id': conv['conversation_hash'],
                'conversation_hash': conv['conversation_hash'],
                'language': conv.get('language', 'English'),
                'original_length': str(original_len),  # Convert to string for ChromaDB
                'truncated': str(len(truncated_text) < original_len)  # Convert bool to string
            }
            # Only add non-None values
            if conv.get('country') is not None:
                meta['country'] = conv['country']
            if conv.get('timestamp') is not None:
                meta['timestamp'] = conv['timestamp']
            metadata.append(meta)
        else:
            skipped += 1
    
    if skipped > 0:
        console.print(f"[yellow]Skipped {skipped} conversations with empty text[/yellow]")
    if truncated > 0:
        console.print(f"[yellow]Truncated {truncated} conversations to {max_tokens} tokens[/yellow]")
    
    # Generate embeddings
    embeddings = await generator.generate_embeddings(texts, batch_size)
    
    # Save to parquet
    output_path = output_dir / f"{embedding_model.replace('/', '-')}.parquet"
    save_embeddings_to_parquet(embeddings, metadata, output_path, embedding_model)
    
    return output_path