"""
Embedding Service for RAG Chatbot
Handles text embeddings using Gemini API with caching
"""

import logging
import hashlib
from typing import List, Optional, Dict
from google.generativeai import configure, embed_content
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Simple embedding service using Gemini with caching"""
    
    def __init__(self):
        self._cache: Dict[str, List[float]] = {}
        self._configure_gemini()
    
    def _configure_gemini(self) -> None:
        """Configure Gemini API"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for embedding service")
        
        try:
            configure(api_key=Config.GEMINI_API_KEY)
            logger.info("✅ Gemini API configured successfully")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini API: {e}")
            raise
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text with caching"""
        if not text.strip():
            return None
        
        # Simple cache using MD5 hash
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            result = embed_content(
                model=Config.EMBEDDING_MODEL, 
                content=text
            )
            embedding = result['embedding']
            self._cache[cache_key] = embedding
            return embedding
        except Exception as e:
            logger.error(f"❌ Embedding error for text '{text[:50]}...': {e}")
            return None
    
    def get_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def clear_cache(self) -> None:
        """Clear the embedding cache"""
        self._cache.clear()
        logger.info("🗑️ Embedding cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self._cache)
    
    def test_connection(self) -> bool:
        """Test if embedding service is working"""
        try:
            test_embedding = self.get_embedding("test")
            return test_embedding is not None
        except Exception as e:
            logger.error(f"❌ Embedding service test failed: {e}")
            return False 