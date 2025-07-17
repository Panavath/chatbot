"""
Database Service for RAG Chatbot
Handles loading documents from database or sample data
"""

import logging
import psycopg2
import pandas as pd
from typing import List, Optional
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    """Handles document loading from database or sample data"""
    
    def __init__(self):
        self.documents: List[str] = []
        self._load_documents()
    
    def _load_documents(self) -> None:
        """Load documents from database or use sample data"""
        try:
            if self._try_database():
                logger.info(f"✅ Loaded {len(self.documents)} documents from database")
            else:
                self._load_sample_data()
                logger.info(f"📋 Using {len(self.documents)} sample documents")
        except Exception as e:
            logger.error(f"❌ Error loading documents: {e}")
            self._load_sample_data()
    
    def _try_database(self) -> bool:
        """Try to load from database"""
        db_config = Config.get_database_config()
        if not db_config:
            logger.info("ℹ️ No database configuration found, using sample data")
            return False
        
        try:
            conn = psycopg2.connect(**db_config)
            df = pd.read_sql_query("SELECT * FROM sub_org ORDER BY id", conn)
            conn.close()
            
            # Convert to document strings
            self.documents = []
            for _, row in df.iterrows():
                doc_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and str(row[col]).strip():
                        doc_parts.append(f"{col}: {row[col]}")
                if doc_parts:
                    self.documents.append(", ".join(doc_parts))
            
            return len(self.documents) > 0
            
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
            return False
    
    def _load_sample_data(self) -> None:
        """Load sample government organization data"""
        self.documents = [
            "Sample Data hehe"
        ]
    
    def get_documents(self) -> List[str]:
        """Get loaded documents"""
        return self.documents
    
    def get_document_count(self) -> int:
        """Get number of loaded documents"""
        return len(self.documents)
    
    def refresh_documents(self) -> bool:
        """Refresh documents from database"""
        logger.info("🔄 Refreshing documents from database...")
        return self._try_database() 