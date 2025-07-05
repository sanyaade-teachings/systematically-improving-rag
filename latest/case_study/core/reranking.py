"""
Reranking functionality for improving retrieval performance.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import os
from tqdm import tqdm

from rich.console import Console

console = Console()


@dataclass
class RerankResult:
    """Result from reranking operation"""
    document_id: str
    original_rank: int
    reranked_rank: int
    original_score: float
    rerank_score: float
    latency_ms: float = 0.0


@dataclass
class RerankingMetrics:
    """Metrics from reranking operation"""
    total_queries: int
    total_latency_ms: float
    avg_latency_per_query_ms: float
    api_calls_made: int


class BaseReranker(ABC):
    """Abstract base class for rerankers"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def rerank(
        self, 
        query: str, 
        documents: List[Tuple[str, str, float]]  # [(doc_id, text, score), ...]
    ) -> List[RerankResult]:
        """
        Rerank documents for a given query
        
        Args:
            query: The search query
            documents: List of (document_id, document_text, similarity_score)
            
        Returns:
            List of RerankResult objects with reranking information
        """
        pass
    
    @abstractmethod
    def batch_rerank(
        self,
        queries_and_docs: List[Tuple[str, List[Tuple[str, str, float]]]]
    ) -> List[List[RerankResult]]:
        """
        Rerank multiple queries in batch
        
        Args:
            queries_and_docs: List of (query, documents) tuples
            
        Returns:
            List of lists containing RerankResult objects for each query
        """
        pass


class NoReranker(BaseReranker):
    """No-op reranker that preserves original ranking"""
    
    def __init__(self):
        super().__init__("none")
    
    def rerank(
        self, 
        query: str, 
        documents: List[Tuple[str, str, float]]
    ) -> List[RerankResult]:
        """Return documents in original order"""
        results = []
        for i, (doc_id, text, score) in enumerate(documents):
            results.append(RerankResult(
                document_id=doc_id,
                original_rank=i + 1,
                reranked_rank=i + 1,
                original_score=score,
                rerank_score=score
            ))
        return results
    
    def batch_rerank(
        self,
        queries_and_docs: List[Tuple[str, List[Tuple[str, str, float]]]]
    ) -> List[List[RerankResult]]:
        """Process multiple queries without reranking"""
        return [self.rerank(query, docs) for query, docs in queries_and_docs]


class SentenceTransformersReranker(BaseReranker):
    """Reranker using sentence-transformers cross-encoder models"""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        super().__init__(f"sentence-transformers/{model_name}")
        self.model_name = model_name
        self._model = None
        
    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                console.print(f"[yellow]Loading {self.model_name}...[/yellow]")
                self._model = CrossEncoder(self.model_name)
                console.print(f"[green]✓ Loaded {self.model_name}[/green]")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
    
    def rerank(
        self, 
        query: str, 
        documents: List[Tuple[str, str, float]]
    ) -> List[RerankResult]:
        """Rerank documents using cross-encoder"""
        self._load_model()
        
        if not documents:
            return []
        
        # Prepare input pairs for cross-encoder
        query_doc_pairs = [(query, doc_text) for doc_id, doc_text, score in documents]
        
        # Get reranking scores
        start_time = time.time()
        rerank_scores = self._model.predict(query_doc_pairs)
        latency_ms = (time.time() - start_time) * 1000
        
        # Create results with original and reranked positions
        results = []
        for i, ((doc_id, doc_text, orig_score), rerank_score) in enumerate(
            zip(documents, rerank_scores)
        ):
            results.append(RerankResult(
                document_id=doc_id,
                original_rank=i + 1,
                reranked_rank=0,  # Will be set after sorting
                original_score=orig_score,
                rerank_score=float(rerank_score)
            ))
        
        # Sort by rerank score (descending) and assign new ranks
        results.sort(key=lambda x: x.rerank_score, reverse=True)
        for i, result in enumerate(results):
            result.reranked_rank = i + 1
        
        # Store latency in results for analysis (no console spam)
        for result in results:
            result.latency_ms = latency_ms
        return results
    
    def batch_rerank(
        self,
        queries_and_docs: List[Tuple[str, List[Tuple[str, str, float]]]]
    ) -> List[List[RerankResult]]:
        """Process multiple queries with progress tracking"""
        if not queries_and_docs:
            return []
        
        results = []
        total_queries = len(queries_and_docs)
        total_latency = 0
        
        for query, docs in tqdm(queries_and_docs, desc="SentenceTransformers reranking"):
            result = self.rerank(query, docs)
            results.append(result)
            if result:
                total_latency += result[0].latency_ms
        
        avg_latency = total_latency / len(results) if results else 0
        console.print(f"[green]SentenceTransformers completed {total_queries} queries, avg latency: {avg_latency:.0f}ms[/green]")
        
        return results


class CohereReranker(BaseReranker):
    """Reranker using Cohere's reranking API"""
    
    def __init__(self, model_name: str = "rerank-english-v3.0"):
        super().__init__("cohere")
        self.model_name = model_name
        self._client = None
        
    def _get_client(self):
        """Lazy load the Cohere client"""
        if self._client is None:
            try:
                import cohere
                api_key = os.getenv("COHERE_API_KEY")
                if not api_key:
                    raise ValueError(
                        "COHERE_API_KEY environment variable not set. "
                        "Get an API key from https://dashboard.cohere.ai/"
                    )
                self._client = cohere.Client(api_key)
                console.print(f"[green]✓ Cohere client initialized[/green]")
            except ImportError:
                raise ImportError(
                    "cohere not installed. Install with: pip install cohere"
                )
        return self._client
    
    def rerank(
        self, 
        query: str, 
        documents: List[Tuple[str, str, float]]
    ) -> List[RerankResult]:
        """Rerank documents using Cohere API"""
        client = self._get_client()
        
        if not documents:
            return []
        
        # Prepare documents for Cohere API
        doc_texts = [doc_text for doc_id, doc_text, score in documents]
        
        # Call Cohere rerank API
        start_time = time.time()
        try:
            response = client.rerank(
                model=self.model_name,
                query=query,
                documents=doc_texts,
                top_n=len(documents),  # Rerank all documents (top_k is now top_n)
                return_documents=False  # We already have the documents
            )
            latency_ms = (time.time() - start_time) * 1000
        except Exception as e:
            console.print(f"[red]Cohere rerank API error: {e}[/red]")
            # Fall back to original ranking
            return self._fallback_to_original(documents)
        
        # Create results mapping
        results = []
        reranked_indices = [result.index for result in response.results]
        reranked_scores = [result.relevance_score for result in response.results]
        
        # Build mapping from original position to reranked position
        rank_mapping = {}
        for new_rank, (orig_idx, rerank_score) in enumerate(
            zip(reranked_indices, reranked_scores), 1
        ):
            doc_id, doc_text, orig_score = documents[orig_idx]
            results.append(RerankResult(
                document_id=doc_id,
                original_rank=orig_idx + 1,
                reranked_rank=new_rank,
                original_score=orig_score,
                rerank_score=rerank_score
            ))
        
        # Store latency in results for analysis (no console spam)
        for result in results:
            result.latency_ms = latency_ms
        
        return results
    
    def _fallback_to_original(
        self, 
        documents: List[Tuple[str, str, float]]
    ) -> List[RerankResult]:
        """Fallback to original ranking when API fails"""
        results = []
        for i, (doc_id, text, score) in enumerate(documents):
            results.append(RerankResult(
                document_id=doc_id,
                original_rank=i + 1,
                reranked_rank=i + 1,
                original_score=score,
                rerank_score=score
            ))
        return results
    
    def batch_rerank(
        self,
        queries_and_docs: List[Tuple[str, List[Tuple[str, str, float]]]]
    ) -> List[List[RerankResult]]:
        """Process multiple queries with progress tracking"""
        if not queries_and_docs:
            return []
        
        results = []
        total_queries = len(queries_and_docs)
        total_latency = 0
        
        for query, docs in tqdm(queries_and_docs, desc="Cohere reranking"):
            result = self.rerank(query, docs)
            results.append(result)
            if result:
                total_latency += result[0].latency_ms
        
        avg_latency = total_latency / len(results) if results else 0
        console.print(f"[green]Cohere completed {total_queries} queries, avg latency: {avg_latency:.0f}ms[/green]")
        
        return results


def get_reranker(reranker_spec: str) -> BaseReranker:
    """
    Factory function to get reranker by specification
    
    Args:
        reranker_spec: Reranker specification in format:
            - "none"
            - "sentence-transformers/<model_name>"
            - "cohere/<model_name>"
    
    Examples:
        - "sentence-transformers/cross-encoder/ms-marco-MiniLM-L-6-v2"
        - "cohere/rerank-english-v3.0"
    """
    if reranker_spec == "none":
        return NoReranker()
    
    if "/" not in reranker_spec:
        raise ValueError(
            f"Invalid reranker specification: {reranker_spec}. "
            f"Use format: provider/model_name or 'none'"
        )
    
    provider, model_name = reranker_spec.split("/", 1)
    
    if provider == "sentence-transformers":
        return SentenceTransformersReranker(model_name=model_name)
    elif provider == "cohere":
        return CohereReranker(model_name=model_name)
    else:
        raise ValueError(
            f"Unknown reranker provider: {provider}. "
            f"Available: sentence-transformers, cohere"
        )
