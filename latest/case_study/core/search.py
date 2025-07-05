"""
Search functionality for finding similar conversations using embeddings with ChromaDB.
"""

import numpy as np
import chromadb
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import pandas as pd

from core.embeddings import EmbeddingGenerator, load_embeddings_from_parquet
from rich.console import Console

console = Console()


@dataclass
class SearchResult:
    """Single search result"""
    id: str
    score: float
    metadata: Dict[str, Any]
    rank: int


@dataclass
class SearchResults:
    """Container for search results"""
    query: str
    results: List[SearchResult]
    total_results: int
    embedding_model: str


class ChromaSearchEngine:
    """Vector search engine using ChromaDB"""
    
    def __init__(
        self,
        collection_name: str,
        embedding_model: str = "text-embedding-3-large",
        persist_directory: Optional[Path] = None
    ):
        """
        Initialize search engine with ChromaDB
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Model used for query embedding
            persist_directory: Directory to persist ChromaDB data
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize ChromaDB client
        if persist_directory:
            self.client = chromadb.PersistentClient(path=str(persist_directory))
        else:
            self.client = chromadb.Client()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"embedding_model": embedding_model}
        )
        
        # Initialize query embedder
        self.query_embedder = EmbeddingGenerator(embedding_model)
        
        console.print(f"[green]ChromaDB search engine initialized for collection: {collection_name}[/green]")
    
    def load_embeddings_from_parquet(self, embeddings_path: Path):
        """Load embeddings from parquet file into ChromaDB"""
        console.print(f"[cyan]Loading embeddings from {embeddings_path}[/cyan]")
        
        # Load embeddings and metadata
        embeddings, metadata_df = load_embeddings_from_parquet(
            embeddings_path, return_metadata=True
        )
        
        # Prepare data for ChromaDB
        ids = metadata_df['id'].tolist()
        embeddings_list = embeddings.tolist()
        
        # Convert metadata to ChromaDB-compatible format
        metadatas = []
        for _, row in metadata_df.iterrows():
            meta = {}
            for key, value in row.items():
                # Convert timestamps to strings
                if hasattr(value, 'isoformat'):
                    meta[key] = value.isoformat()
                # Convert numpy types to Python types
                elif hasattr(value, 'item'):
                    meta[key] = value.item()
                # Keep None, str, int, float, bool as is
                elif value is None or isinstance(value, (str, int, float, bool)):
                    meta[key] = value
                else:
                    # Convert everything else to string
                    meta[key] = str(value)
            metadatas.append(meta)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings_list[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        console.print(f"[green]Loaded {len(ids)} documents into ChromaDB[/green]")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> SearchResults:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            where: Optional filter conditions
            
        Returns:
            SearchResults object
        """
        import time
        
        # Generate query embedding
        embed_start = time.time()
        query_embedding = await self.query_embedder.generate_embeddings(
            [query], show_progress=False
        )
        query_embedding = query_embedding[0].tolist()
        embed_time = (time.time() - embed_start) * 1000
        
        # Search in ChromaDB
        search_start = time.time()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        search_time = (time.time() - search_start) * 1000
        
        # Store timing info for analysis
        self._last_embed_time = embed_time
        self._last_search_time = search_time
        
        # Convert to SearchResult objects
        search_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for rank, (id_, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                # Convert distance to similarity score (1 - distance for cosine)
                score = 1.0 - distance
                
                result = SearchResult(
                    id=id_,
                    score=float(score),
                    metadata=metadata,
                    rank=rank + 1
                )
                search_results.append(result)
        
        return SearchResults(
            query=query,
            results=search_results,
            total_results=len(search_results),
            embedding_model=self.embedding_model
        )
    
    async def batch_search(
        self,
        queries: List[str],
        top_k: int = 10,
        where: Optional[Dict[str, Any]] = None,
        show_progress: bool = True
    ) -> List[SearchResults]:
        """
        Search for multiple queries
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            where: Optional filter conditions
            show_progress: Whether to show progress
            
        Returns:
            List of SearchResults
        """
        # Generate all query embeddings at once
        query_embeddings = await self.query_embedder.generate_embeddings(
            queries, show_progress=show_progress
        )
        query_embeddings_list = query_embeddings.tolist()
        
        # Search for all queries
        results = self.collection.query(
            query_embeddings=query_embeddings_list,
            n_results=top_k,
            where=where
        )
        
        # Convert to SearchResults objects
        all_results = []
        for i, query in enumerate(queries):
            search_results = []
            
            if results['ids'][i]:
                for rank, (id_, distance, metadata) in enumerate(zip(
                    results['ids'][i],
                    results['distances'][i],
                    results['metadatas'][i]
                )):
                    # Convert distance to similarity score
                    score = 1.0 - distance
                    
                    result = SearchResult(
                        id=id_,
                        score=float(score),
                        metadata=metadata,
                        rank=rank + 1
                    )
                    search_results.append(result)
            
            all_results.append(SearchResults(
                query=query,
                results=search_results,
                total_results=len(search_results),
                embedding_model=self.embedding_model
            ))
        
        return all_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "embedding_model": self.embedding_model
        }


class VectorSearchEngine:
    """Legacy compatibility wrapper for ChromaSearchEngine"""
    
    def __init__(
        self,
        embeddings_path: Path,
        embedding_model: str = "text-embedding-3-large"
    ):
        """Initialize with ChromaDB backend"""
        # Extract collection name from embeddings path
        collection_name = embeddings_path.stem.replace('-', '_')
        persist_dir = embeddings_path.parent.parent / "chromadb"
        
        self.engine = ChromaSearchEngine(
            collection_name=collection_name,
            embedding_model=embedding_model,
            persist_directory=persist_dir
        )
        
        # Check if we need to load embeddings
        if self.engine.collection.count() == 0:
            self.engine.load_embeddings_from_parquet(embeddings_path)
    
    async def search(self, query: str, top_k: int = 10, min_score: Optional[float] = None) -> SearchResults:
        """Search compatibility method"""
        results = await self.engine.search(query, top_k)
        
        # Filter by min_score if provided
        if min_score is not None:
            filtered_results = [r for r in results.results if r.score >= min_score]
            results.results = filtered_results
            results.total_results = len(filtered_results)
        
        return results
    
    async def batch_search(
        self,
        queries: List[str],
        top_k: int = 10,
        min_score: Optional[float] = None,
        show_progress: bool = True
    ) -> List[SearchResults]:
        """Batch search compatibility method"""
        all_results = await self.engine.batch_search(queries, top_k, show_progress=show_progress)
        
        # Filter by min_score if provided
        if min_score is not None:
            for results in all_results:
                filtered_results = [r for r in results.results if r.score >= min_score]
                results.results = filtered_results
                results.total_results = len(filtered_results)
        
        return all_results


async def vector_search(
    query: str,
    embeddings_path: Path,
    top_k: int = 10,
    embedding_model: str = "text-embedding-3-large"
) -> SearchResults:
    """
    Convenience function for one-off vector search
    
    Args:
        query: Search query
        embeddings_path: Path to embeddings parquet file
        top_k: Number of results
        embedding_model: Model for query embedding
        
    Returns:
        SearchResults
    """
    engine = VectorSearchEngine(embeddings_path, embedding_model)
    return await engine.search(query, top_k)