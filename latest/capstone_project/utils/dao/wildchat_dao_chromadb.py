#!/usr/bin/env python3
"""
ChromaDB implementation of WildChat DAO
"""

import os
import time
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

from .wildchat_dao import (
    WildChatDAOBase, 
    WildChatDocument, 
    SearchRequest, 
    SearchResults, 
    SearchResult, 
    SearchType
)


class WildChatDAOChromaDB(WildChatDAOBase):
    """ChromaDB implementation of WildChat DAO"""
    
    def __init__(self, table_name: str = "wildchat_2k", use_cloud: bool = True):
        super().__init__(table_name)
        self.use_cloud = use_cloud
        self.client = None
        self.collection = None
        self.embedding_function = None
    
    async def connect(self) -> None:
        """Establish connection to ChromaDB"""
        load_dotenv()
        
        if self.use_cloud:
            # Cloud connection
            required_env_vars = ['CHROMA_API_KEY', 'CHROMA_TENANT', 'CHROMA_DATABASE']
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(f"Missing required environment variables for ChromaDB cloud: {missing_vars}")
            
            self.client = chromadb.CloudClient(
                api_key=os.getenv('CHROMA_API_KEY'),
                tenant=os.getenv('CHROMA_TENANT'),
                database=os.getenv('CHROMA_DATABASE')
            )
        else:
            # Local persistent client
            db_path = "./chroma_db"
            self.client = chromadb.PersistentClient(path=db_path)
        
        # Create embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.table_name,
            embedding_function=self.embedding_function,
            metadata={
                "description": "WildChat-1M conversations",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        )
    
    async def disconnect(self) -> None:
        """Close ChromaDB connection"""
        # ChromaDB doesn't require explicit disconnection
        self.client = None
        self.collection = None
        self.embedding_function = None
    
    async def add(self, documents: List[WildChatDocument]) -> Dict[str, Any]:
        """Add documents to ChromaDB collection"""
        if not self.collection:
            raise RuntimeError("Not connected to ChromaDB. Call connect() first.")
        
        if not documents:
            return {"success": True, "added_count": 0, "skipped_count": 0}
        
        # Prepare data for ChromaDB
        doc_texts = []
        metadatas = []
        ids = []
        added_count = 0
        skipped_count = 0
        
        for doc in documents:
            try:
                # Prepare metadata (ChromaDB doesn't accept None values)
                metadata = {
                    "hash": doc.hash or "",
                    "timestamp": doc.timestamp.isoformat() if doc.timestamp else "",
                    "language": doc.language or "Unknown",
                    "model_name": doc.model_name or "Unknown",
                    "conversation_length": doc.conversation_length or 0,
                    "country": doc.country or "Unknown",
                    "toxic": bool(doc.toxic),
                    "redacted": bool(doc.redacted),
                    "turn": doc.turn or 1
                }
                
                # Truncate text if too long
                text = doc.text[:2000] if doc.text else ""
                
                doc_texts.append(text)
                metadatas.append(metadata)
                ids.append(doc.id)
                
            except Exception:
                skipped_count += 1
                continue
        
        try:
            # Add to collection
            self.collection.add(
                documents=doc_texts,
                metadatas=metadatas,
                ids=ids
            )
            added_count = len(doc_texts)
            
        except Exception as e:
            if "Expected IDs to be unique" in str(e):
                # Handle duplicates by trying to add one by one
                for i, (text, metadata, doc_id) in enumerate(zip(doc_texts, metadatas, ids)):
                    try:
                        self.collection.add(
                            documents=[text],
                            metadatas=[metadata],
                            ids=[doc_id]
                        )
                        added_count += 1
                    except:
                        skipped_count += 1
            else:
                raise
        
        return {
            "success": True,
            "added_count": added_count,
            "skipped_count": skipped_count,
            "total_requested": len(documents)
        }
    
    async def delete(self, document_ids: List[str]) -> Dict[str, Any]:
        """Delete specific documents by ID"""
        if not self.collection:
            raise RuntimeError("Not connected to ChromaDB. Call connect() first.")
        
        try:
            self.collection.delete(ids=document_ids)
            return {
                "success": True,
                "deleted_count": len(document_ids)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            }
    
    async def delete_table(self) -> Dict[str, Any]:
        """Delete the entire collection"""
        if not self.client:
            raise RuntimeError("Not connected to ChromaDB. Call connect() first.")
        
        try:
            self.client.delete_collection(self.table_name)
            self.collection = None
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _apply_filters(self, request: SearchRequest) -> Optional[Dict[str, Any]]:
        """Convert SearchRequest filters to ChromaDB where clause"""
        where_conditions = []
        
        # Date range filter
        if request.date_range:
            start_date, end_date = request.date_range
            where_conditions.append({
                "$and": [
                    {"timestamp": {"$gte": start_date.isoformat()}},
                    {"timestamp": {"$lte": end_date.isoformat()}}
                ]
            })
        
        # Conversation length range
        if request.conversation_length_range:
            min_len, max_len = request.conversation_length_range
            where_conditions.append({
                "$and": [
                    {"conversation_length": {"$gte": min_len}},
                    {"conversation_length": {"$lte": max_len}}
                ]
            })
        
        # Model names filter
        if request.model_names:
            where_conditions.append({"model_name": {"$in": request.model_names}})
        
        # Languages filter
        if request.languages:
            where_conditions.append({"language": {"$in": request.languages}})
        
        # Countries filter
        if request.countries:
            where_conditions.append({"country": {"$in": request.countries}})
        
        # Toxic filter
        if request.exclude_toxic:
            where_conditions.append({"toxic": {"$eq": False}})
        
        # Redacted filter
        if request.exclude_redacted:
            where_conditions.append({"redacted": {"$eq": False}})
        
        # Turn range filter
        if request.turn_range:
            min_turn, max_turn = request.turn_range
            where_conditions.append({
                "$and": [
                    {"turn": {"$gte": min_turn}},
                    {"turn": {"$lte": max_turn}}
                ]
            })
        
        # Combine all conditions with AND
        if where_conditions:
            if len(where_conditions) == 1:
                return where_conditions[0]
            else:
                return {"$and": where_conditions}
        
        return None
    
    async def search(self, request: SearchRequest) -> SearchResults:
        """Execute search based on request parameters"""
        if not self.collection:
            raise RuntimeError("Not connected to ChromaDB. Call connect() first.")
        
        start_time = time.time()
        
        # Apply filters
        where_clause = self._apply_filters(request)
        
        try:
            if request.search_type == SearchType.VECTOR:
                # Vector similarity search
                results = self.collection.query(
                    query_texts=[request.query],
                    n_results=request.top_k,
                    where=where_clause,
                    include=['documents', 'metadatas', 'distances']
                )
                
                # Convert to SearchResult objects
                search_results = []
                if results['documents'] and results['documents'][0]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        search_result = SearchResult(
                            id=results['ids'][0][i],
                            text=doc,
                            conversation_string=metadata.get('conversation_string', ''),
                            score=1.0 - distance,  # Convert distance to similarity score
                            metadata=metadata
                        )
                        search_results.append(search_result)
            
            elif request.search_type == SearchType.FULL_TEXT:
                # ChromaDB doesn't have native full-text search, so we use vector search with a note
                results = self.collection.query(
                    query_texts=[request.query],
                    n_results=request.top_k,
                    where=where_clause,
                    include=['documents', 'metadatas', 'distances']
                )
                
                # Convert to SearchResult objects (same as vector search)
                search_results = []
                if results['documents'] and results['documents'][0]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        search_result = SearchResult(
                            id=results['ids'][0][i],
                            text=doc,
                            conversation_string=metadata.get('conversation_string', ''),
                            score=1.0 - distance,
                            metadata=metadata
                        )
                        search_results.append(search_result)
            
            elif request.search_type == SearchType.HYBRID:
                # For hybrid, use vector search (ChromaDB limitation)
                results = self.collection.query(
                    query_texts=[request.query],
                    n_results=request.top_k,
                    where=where_clause,
                    include=['documents', 'metadatas', 'distances']
                )
                
                search_results = []
                if results['documents'] and results['documents'][0]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        search_result = SearchResult(
                            id=results['ids'][0][i],
                            text=doc,
                            conversation_string=metadata.get('conversation_string', ''),
                            score=1.0 - distance,
                            metadata=metadata
                        )
                        search_results.append(search_result)
            
            else:
                raise ValueError(f"Unsupported search type: {request.search_type}")
            
            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000
            
            return SearchResults(
                results=search_results,
                total_count=len(search_results),
                query_time_ms=query_time_ms,
                search_type=request.search_type,
                request=request
            )
            
        except Exception:
            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000
            
            return SearchResults(
                results=[],
                total_count=0,
                query_time_ms=query_time_ms,
                search_type=request.search_type,
                request=request
            )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.collection:
            raise RuntimeError("Not connected to ChromaDB. Call connect() first.")
        
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand data distribution
            sample_results = self.collection.query(
                query_texts=["sample"],
                n_results=min(100, count) if count > 0 else 1,
                include=['metadatas']
            )
            
            stats = {
                "total_documents": count,
                "collection_name": self.table_name,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            
            # Analyze metadata if we have results
            if sample_results['metadatas'] and sample_results['metadatas'][0]:
                metadatas = sample_results['metadatas'][0]
                
                # Language distribution
                languages = {}
                models = {}
                countries = {}
                
                for metadata in metadatas:
                    lang = metadata.get('language', 'Unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    model = metadata.get('model_name', 'Unknown')
                    models[model] = models.get(model, 0) + 1
                    
                    country = metadata.get('country', 'Unknown')
                    countries[country] = countries.get(country, 0) + 1
                
                stats.update({
                    "languages": dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "models": dict(sorted(models.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "countries": dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "sample_size": len(metadatas)
                })
            
            return stats
            
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": 0,
                "collection_name": self.table_name
            }
