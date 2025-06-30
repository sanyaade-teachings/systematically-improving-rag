#!/usr/bin/env python3
"""
Turbopuffer implementation of WildChat DAO
"""

import os
import time
from typing import List, Dict, Any, Optional
import turbopuffer
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from .wildchat_dao import (
    WildChatDAOBase,
    WildChatDocument,
    SearchRequest,
    SearchResults,
    SearchResult,
    SearchType,
)


class WildChatDAOTurbopuffer(WildChatDAOBase):
    """Turbopuffer implementation of WildChat DAO"""

    def __init__(self, table_name: str = "wildchat_2k"):
        super().__init__(table_name)
        self.client = None
        self.namespace = None
        self.embedding_model = None

    def _get_embedding_model(self) -> SentenceTransformer:
        """Get or create the embedding model"""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
        return self.embedding_model

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        model = self._get_embedding_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        return [embedding.tolist() for embedding in embeddings]

    async def connect(self) -> None:
        """Establish connection to Turbopuffer"""
        load_dotenv()

        api_key = os.getenv("TURBOPUFFER_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing required environment variable: TURBOPUFFER_API_KEY"
            )

        # Default to GCP US Central region, but allow override
        region = os.getenv("TURBOPUFFER_REGION", "gcp-us-central1")

        self.client = turbopuffer.Turbopuffer(api_key=api_key, region=region)

        # Get namespace
        self.namespace = self.client.namespace(self.table_name)

    async def disconnect(self) -> None:
        """Close Turbopuffer connection"""
        # Turbopuffer doesn't require explicit disconnection
        self.client = None
        self.namespace = None
        self.embedding_model = None

    async def add(self, documents: List[WildChatDocument]) -> Dict[str, Any]:
        """Add documents to Turbopuffer namespace"""
        if not self.namespace:
            raise RuntimeError("Not connected to Turbopuffer. Call connect() first.")

        if not documents:
            return {"success": True, "added_count": 0, "skipped_count": 0}

        # Prepare batch data
        batch_data = {
            "id": [],
            "vector": [],
            "text": [],
            "conversation_string": [],
            "hash": [],
            "timestamp": [],
            "language": [],
            "model_name": [],
            "conversation_length": [],
            "country": [],
            "toxic": [],
            "redacted": [],
            "turn": [],
        }
        batch_texts = []
        added_count = 0
        skipped_count = 0

        for doc in documents:
            try:
                # Prepare document data
                batch_data["id"].append(doc.id)
                batch_data["text"].append(doc.text)
                batch_data["conversation_string"].append(doc.conversation_string)
                batch_data["hash"].append(doc.hash)
                batch_data["timestamp"].append(
                    doc.timestamp.isoformat() if doc.timestamp else ""
                )
                batch_data["language"].append(doc.language)
                batch_data["model_name"].append(doc.model_name)
                batch_data["conversation_length"].append(doc.conversation_length)
                batch_data["country"].append(doc.country)
                batch_data["toxic"].append(doc.toxic)
                batch_data["redacted"].append(doc.redacted)
                batch_data["turn"].append(doc.turn)

                # Truncate text for embedding
                text_for_embedding = doc.text[:2000] if doc.text else ""
                batch_texts.append(text_for_embedding)

            except Exception:
                skipped_count += 1
                continue

        try:
            # Generate embeddings
            embeddings = self._create_embeddings(batch_texts)
            batch_data["vector"] = embeddings

            # Write to Turbopuffer
            self.namespace.write(
                upsert_columns=batch_data,
                distance_metric="cosine_distance",
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
                    "turn": {"type": "int"},
                },
            )

            added_count = len(batch_data["id"])

        except Exception as e:
            if "duplicate" in str(e).lower():
                skipped_count = len(batch_data["id"])
            else:
                raise

        return {
            "success": True,
            "added_count": added_count,
            "skipped_count": skipped_count,
            "total_requested": len(documents),
        }

    async def delete(self, document_ids: List[str]) -> Dict[str, Any]:
        """Delete specific documents by ID"""
        if not self.namespace:
            raise RuntimeError("Not connected to Turbopuffer. Call connect() first.")

        try:
            # Turbopuffer doesn't have a direct delete by ID, so we use a filter-based delete
            deleted_count = 0
            for doc_id in document_ids:
                try:
                    self.namespace.delete(filters=("id", "Eq", doc_id))
                    deleted_count += 1
                except Exception:
                    pass  # Document might not exist

            return {"success": True, "deleted_count": deleted_count}
        except Exception as e:
            return {"success": False, "error": str(e), "deleted_count": 0}

    async def delete_table(self) -> Dict[str, Any]:
        """Delete the entire namespace"""
        if not self.client:
            raise RuntimeError("Not connected to Turbopuffer. Call connect() first.")

        try:
            self.client.delete_namespace(self.table_name)
            self.namespace = None
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_filters(self, request: SearchRequest) -> Optional[tuple]:
        """Convert SearchRequest filters to Turbopuffer filter format"""
        filters = []

        # Date range filter
        if request.date_range:
            start_date, end_date = request.date_range
            filters.append(("timestamp", "Gte", start_date.isoformat()))
            filters.append(("timestamp", "Lte", end_date.isoformat()))

        # Languages filter
        if request.languages:
            if len(request.languages) == 1:
                filters.append(("language", "Eq", request.languages[0]))
            else:
                filters.append(("language", "In", request.languages))

        # Combine filters with AND logic
        if len(filters) == 0:
            return None
        elif len(filters) == 1:
            return filters[0]
        else:
            # Turbopuffer uses AND logic by default when multiple filters are provided
            return ("And", filters)

    async def search(self, request: SearchRequest) -> SearchResults:
        """Execute search based on request parameters"""
        if not self.namespace:
            raise RuntimeError("Not connected to Turbopuffer. Call connect() first.")

        start_time = time.time()

        # Build filters
        filters = self._build_filters(request)

        try:
            if request.search_type == SearchType.VECTOR:
                # Vector similarity search
                query_embedding = self._create_embeddings([request.query])[0]

                results = self.namespace.query(
                    rank_by=("vector", "ANN", query_embedding),
                    top_k=request.top_k,
                    filters=filters,
                    include_attributes=[
                        "text",
                        "conversation_string",
                        "hash",
                        "timestamp",
                        "language",
                        "model_name",
                        "conversation_length",
                        "country",
                        "toxic",
                        "redacted",
                        "turn",
                    ],
                )

                # Convert to SearchResult objects
                search_results = []
                for row in results.rows:
                    metadata = {
                        "hash": getattr(row, "hash", ""),
                        "timestamp": getattr(row, "timestamp", ""),
                        "language": getattr(row, "language", ""),
                        "model_name": getattr(row, "model_name", ""),
                        "conversation_length": getattr(row, "conversation_length", 0),
                        "country": getattr(row, "country", ""),
                        "toxic": getattr(row, "toxic", False),
                        "redacted": getattr(row, "redacted", False),
                        "turn": getattr(row, "turn", 1),
                    }

                    search_result = SearchResult(
                        id=row.id,
                        text=getattr(row, "text", ""),
                        conversation_string=getattr(row, "conversation_string", ""),
                        score=row.similarity if hasattr(row, "similarity") else 1.0,
                        metadata=metadata,
                    )
                    search_results.append(search_result)

            elif request.search_type == SearchType.FULL_TEXT:
                # Full-text search
                results = self.namespace.query(
                    rank_by=("text", "BM25", request.query),
                    top_k=request.top_k,
                    filters=filters,
                    include_attributes=[
                        "text",
                        "conversation_string",
                        "hash",
                        "timestamp",
                        "language",
                        "model_name",
                        "conversation_length",
                        "country",
                        "toxic",
                        "redacted",
                        "turn",
                    ],
                )

                search_results = []
                for row in results.rows:
                    metadata = {
                        "hash": getattr(row, "hash", ""),
                        "timestamp": getattr(row, "timestamp", ""),
                        "language": getattr(row, "language", ""),
                        "model_name": getattr(row, "model_name", ""),
                        "conversation_length": getattr(row, "conversation_length", 0),
                        "country": getattr(row, "country", ""),
                        "toxic": getattr(row, "toxic", False),
                        "redacted": getattr(row, "redacted", False),
                        "turn": getattr(row, "turn", 1),
                    }

                    search_result = SearchResult(
                        id=row.id,
                        text=getattr(row, "text", ""),
                        conversation_string=getattr(row, "conversation_string", ""),
                        score=row.score if hasattr(row, "score") else 1.0,
                        metadata=metadata,
                    )
                    search_results.append(search_result)

            elif request.search_type == SearchType.HYBRID:
                # Hybrid search - combine vector and text search
                query_embedding = self._create_embeddings([request.query])[0]

                # Get vector results
                vector_results = self.namespace.query(
                    rank_by=("vector", "ANN", query_embedding),
                    top_k=request.top_k * 2,
                    filters=filters,
                    include_attributes=[
                        "text",
                        "conversation_string",
                        "hash",
                        "timestamp",
                        "language",
                        "model_name",
                        "conversation_length",
                        "country",
                        "toxic",
                        "redacted",
                        "turn",
                    ],
                )

                # Get text results
                text_results = self.namespace.query(
                    rank_by=("text", "BM25", request.query),
                    top_k=request.top_k * 2,
                    filters=filters,
                    include_attributes=[
                        "text",
                        "conversation_string",
                        "hash",
                        "timestamp",
                        "language",
                        "model_name",
                        "conversation_length",
                        "country",
                        "toxic",
                        "redacted",
                        "turn",
                    ],
                )

                # Combine and rerank results
                combined_results = {}

                # Add vector results with weight
                for row in vector_results.rows:
                    score = getattr(row, "similarity", 1.0) * request.vector_weight
                    metadata = {
                        "hash": getattr(row, "hash", ""),
                        "timestamp": getattr(row, "timestamp", ""),
                        "language": getattr(row, "language", ""),
                        "model_name": getattr(row, "model_name", ""),
                        "conversation_length": getattr(row, "conversation_length", 0),
                        "country": getattr(row, "country", ""),
                        "toxic": getattr(row, "toxic", False),
                        "redacted": getattr(row, "redacted", False),
                        "turn": getattr(row, "turn", 1),
                    }

                    combined_results[row.id] = SearchResult(
                        id=row.id,
                        text=getattr(row, "text", ""),
                        conversation_string=getattr(row, "conversation_string", ""),
                        score=score,
                        metadata=metadata,
                    )

                # Add/merge text results with weight
                for row in text_results.rows:
                    score = getattr(row, "score", 1.0) * request.text_weight

                    if row.id in combined_results:
                        # Combine scores
                        combined_results[row.id].score += score
                    else:
                        metadata = {
                            "hash": getattr(row, "hash", ""),
                            "timestamp": getattr(row, "timestamp", ""),
                            "language": getattr(row, "language", ""),
                            "model_name": getattr(row, "model_name", ""),
                            "conversation_length": getattr(
                                row, "conversation_length", 0
                            ),
                            "country": getattr(row, "country", ""),
                            "toxic": getattr(row, "toxic", False),
                            "redacted": getattr(row, "redacted", False),
                            "turn": getattr(row, "turn", 1),
                        }

                        combined_results[row.id] = SearchResult(
                            id=row.id,
                            text=getattr(row, "text", ""),
                            conversation_string=getattr(row, "conversation_string", ""),
                            score=score,
                            metadata=metadata,
                        )

                # Sort by combined score and take top_k
                search_results = sorted(
                    combined_results.values(), key=lambda x: x.score, reverse=True
                )[: request.top_k]

            else:
                raise ValueError(f"Unsupported search type: {request.search_type}")

            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000

            return SearchResults(
                results=search_results,
                total_count=len(search_results),
                query_time_ms=query_time_ms,
                search_type=request.search_type,
                request=request,
            )

        except Exception:
            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000

            return SearchResults(
                results=[],
                total_count=0,
                query_time_ms=query_time_ms,
                search_type=request.search_type,
                request=request,
            )

    async def get_stats(self) -> Dict[str, Any]:
        """Get namespace statistics"""
        if not self.namespace:
            raise RuntimeError("Not connected to Turbopuffer. Call connect() first.")

        try:
            # Get total count
            count_result = self.namespace.query(
                aggregate_by={"document_count": ("Count", "id")}
            )
            total_count = count_result.aggregations["document_count"]

            stats = {
                "total_documents": total_count,
                "namespace_name": self.table_name,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            }

            # Get language distribution
            try:
                lang_result = self.namespace.query(
                    aggregate_by={"languages": ("GroupBy", "language")}, top_k=10
                )
                if (
                    hasattr(lang_result, "aggregations")
                    and "languages" in lang_result.aggregations
                ):
                    stats["languages"] = lang_result.aggregations["languages"]
            except Exception:
                pass

            # Get model distribution
            try:
                model_result = self.namespace.query(
                    aggregate_by={"models": ("GroupBy", "model_name")}, top_k=10
                )
                if (
                    hasattr(model_result, "aggregations")
                    and "models" in model_result.aggregations
                ):
                    stats["models"] = model_result.aggregations["models"]
            except Exception:
                pass

            return stats

        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "namespace_name": self.table_name,
            }
