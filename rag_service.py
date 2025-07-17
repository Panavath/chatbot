"""
RAG Service for Database Agent
Handles document processing, vector storage, and response generation for sub_org database
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import our modular services
from config import Config
from database import DatabaseService
from embedding import EmbeddingService
from vectorstore import VectorStore
from llm import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """RAG service for sub_org database with fallback support"""
    
    def __init__(self):
        self.database_service = None
        self.embedding_service = None
        self.vector_store = None
        self.llm_service = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize all RAG components"""
        try:
            Config.validate()
            
            # Initialize services
            logger.info("🚀 Initializing RAG Service...")
            
            # 1. Initialize database service
            self.database_service = DatabaseService()
            logger.info(f"📊 Database service initialized with {self.database_service.get_document_count()} documents")
            
            # 2. Initialize embedding service
            self.embedding_service = EmbeddingService()
            logger.info("🧠 Embedding service initialized")
            
            # 3. Initialize vector store
            self.vector_store = VectorStore(self.embedding_service)
            logger.info("🗄️ Vector store initialized")
            
            # 4. Initialize LLM service
            self.llm_service = LLMService()
            logger.info("🤖 LLM service initialized")
            
            # 5. Load documents into vector store
            documents = self.database_service.get_documents()
            if documents:
                success = self.vector_store.add_documents(documents)
                if success:
                    logger.info(f"✅ Successfully loaded {len(documents)} documents into vector store")
                else:
                    logger.error("❌ Failed to load documents into vector store")
                    return False
            else:
                logger.warning("⚠️ No documents to load into vector store")
            
            self._initialized = True
            logger.info("🎉 RAG Service initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG Service: {e}")
            return False
    
    def query(self, question: str, language: str = "auto") -> Dict[str, Any]:
        """Process a query and return response"""
        if not self._initialized:
            return {
                "response": "Service not initialized. Please try again.",
                "sources": 0,
                "error": "Service not initialized"
            }
        
        try:
            # 1. Search for relevant documents
            relevant_docs = self.vector_store.search(question)
            
            # 2. Generate response
            response = self.llm_service.generate_response(question, relevant_docs, language)
            
            # 3. Return result
            return {
                "response": response,
                "sources": len(relevant_docs),
                "timestamp": datetime.now().isoformat(),
                "language": language
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}")
            return {
                "response": "An error occurred while processing your request. Please try again.",
                "sources": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def query_with_scores(self, question: str, language: str = "auto") -> Dict[str, Any]:
        """Process a query and return response with similarity scores"""
        if not self._initialized:
            return {
                "response": "Service not initialized. Please try again.",
                "sources": 0,
                "error": "Service not initialized"
            }
        
        try:
            # 1. Search for relevant documents with scores
            relevant_docs_with_scores = self.vector_store.search_with_scores(question)
            
            # 2. Extract just the documents for LLM
            relevant_docs = [doc for doc, score in relevant_docs_with_scores]
            
            # 3. Generate response
            response = self.llm_service.generate_response(question, relevant_docs, language)
            
            # 4. Return result with scores
            return {
                "response": response,
                "sources": len(relevant_docs),
                "scores": relevant_docs_with_scores,
                "timestamp": datetime.now().isoformat(),
                "language": language
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing query with scores: {e}")
            return {
                "response": "An error occurred while processing your request. Please try again.",
                "sources": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def refresh_data(self) -> bool:
        """Refresh data from database"""
        try:
            if self.database_service:
                success = self.database_service.refresh_documents()
                if success:
                    # Reload documents into vector store
                    documents = self.database_service.get_documents()
                    if documents:
                        return self.vector_store.add_documents(documents)
                return success
            return False
        except Exception as e:
            logger.error(f"❌ Error refreshing data: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status and statistics"""
        try:
            status = {
                "initialized": self._initialized,
                "timestamp": datetime.now().isoformat()
            }
            
            if self._initialized:
                # Database status
                if self.database_service:
                    status["database"] = {
                        "document_count": self.database_service.get_document_count(),
                        "has_database_config": Config.get_database_config() is not None
                    }
                
                # Vector store status
                if self.vector_store:
                    status["vector_store"] = self.vector_store.get_collection_info()
                
                # LLM status
                if self.llm_service:
                    status["llm"] = self.llm_service.get_model_info()
                
                # Embedding service status
                if self.embedding_service:
                    status["embedding"] = {
                        "cache_size": self.embedding_service.get_cache_size(),
                        "connection_test": self.embedding_service.test_connection()
                    }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting status: {e}")
            return {
                "initialized": self._initialized,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def switch_llm(self, use_openai: bool = True) -> bool:
        """Switch between OpenAI and Gemini LLM"""
        if self.llm_service:
            return self.llm_service.switch_model(use_openai)
        return False
    
    def clear_cache(self) -> None:
        """Clear embedding cache"""
        if self.embedding_service:
            self.embedding_service.clear_cache()
    
    def reset_vector_store(self) -> bool:
        """Reset vector store (clear all documents)"""
        if self.vector_store:
            return self.vector_store.reset_collection()
        return False 