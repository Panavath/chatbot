"""
Vector Store Service for RAG Chatbot
Handles document storage and similarity search using ChromaDB
"""

import logging
import os
from typing import List, Optional, Tuple
import chromadb
from chromadb.config import Settings
from embedding import EmbeddingService
from config import Config

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store using ChromaDB with Gemini embeddings"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.client = None
        self.collection = None
        self._setup()
    
    def _setup(self) -> None:
        """Setup ChromaDB"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(Config.CHROMADB_DIR, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=Config.CHROMADB_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ ChromaDB vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Vector store setup failed: {e}")
            raise
    
    def add_documents(self, documents: List[str]) -> bool:
        """Add documents to vector store"""
        if not self.collection or not documents:
            return False
        
        try:
            # Clear existing documents - get all IDs first
            try:
                results = self.collection.get()
                if results and results['ids']:
                    self.collection.delete(ids=results['ids'])
            except Exception:
                # If no documents exist, that's fine
                pass
            
            # Prepare documents for insertion
            valid_documents = []
            valid_embeddings = []
            valid_ids = []
            
            for i, doc in enumerate(documents):
                embedding = self.embedding_service.get_embedding(doc)
                if embedding:
                    valid_documents.append(doc)
                    valid_embeddings.append(embedding)
                    valid_ids.append(str(i))
            
            if not valid_documents:
                logger.warning("⚠️ No valid documents to add to vector store")
                return False
            
            # Add documents to collection
            self.collection.add(
                documents=valid_documents,
                embeddings=valid_embeddings,
                ids=valid_ids
            )
            
            logger.info(f"✅ Added {len(valid_documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, n_results: int = None) -> List[str]:
        """Search for similar documents"""
        if not self.collection or not query.strip():
            return []
        
        if n_results is None:
            n_results = Config.MAX_RETRIEVAL_DOCS
        
        try:
            # Get query embedding
            query_embedding = self.embedding_service.get_embedding(query)
            if not query_embedding:
                logger.warning("⚠️ Failed to get query embedding")
                return []
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "distances"]
            )
            
            if results and results['documents']:
                documents = results['documents'][0]
                distances = results['distances'][0]
                
                # Filter by similarity threshold
                filtered_docs = []
                logger.info(f"🔍 Raw search results: {len(documents)} documents found")
                for i, (doc, distance) in enumerate(zip(documents, distances)):
                    similarity = 1 - distance  # Convert distance to similarity
                    logger.info(f"🔍 Document {i+1}: similarity={similarity:.3f}, distance={distance:.3f}")
                    if similarity >= Config.SIMILARITY_THRESHOLD:
                        filtered_docs.append(doc)
                
                logger.info(f"🔍 Found {len(filtered_docs)} relevant documents (similarity >= {Config.SIMILARITY_THRESHOLD})")
                return filtered_docs
            else:
                logger.info("🔍 No relevant documents found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error searching vector store: {e}")
            return []
    
    def search_with_scores(self, query: str, n_results: int = None) -> List[Tuple[str, float]]:
        """Search for similar documents with similarity scores"""
        if not self.collection or not query.strip():
            return []
        
        if n_results is None:
            n_results = Config.MAX_RETRIEVAL_DOCS
        
        try:
            # Get query embedding
            query_embedding = self.embedding_service.get_embedding(query)
            if not query_embedding:
                logger.warning("⚠️ Failed to get query embedding")
                return []
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "distances"]
            )
            
            if results and results['documents']:
                documents = results['documents'][0]
                distances = results['distances'][0]
                
                # Convert distances to similarities and filter
                doc_scores = []
                for doc, distance in zip(documents, distances):
                    similarity = 1 - distance
                    if similarity >= Config.SIMILARITY_THRESHOLD:
                        doc_scores.append((doc, similarity))
                
                # Sort by similarity (highest first)
                doc_scores.sort(key=lambda x: x[1], reverse=True)
                
                logger.info(f"🔍 Found {len(doc_scores)} relevant documents with scores")
                return doc_scores
            else:
                logger.info("🔍 No relevant documents found")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error searching vector store: {e}")
            return []
    
    def get_collection_info(self) -> dict:
        """Get information about the collection"""
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "name": Config.COLLECTION_NAME,
                "document_count": count,
                "embedding_cache_size": self.embedding_service.get_cache_size()
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection info: {e}")
            return {"error": str(e)}
    
    def reset_collection(self) -> bool:
        """Reset the collection (delete all documents)"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(where={})
            logger.info("🗑️ Vector store collection reset")
            return True
        except Exception as e:
            logger.error(f"❌ Error resetting collection: {e}")
            return False 