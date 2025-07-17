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
            "id: 1, en_name: Ministry of Education, kh_name: ក្រសួងអប់រំ, description: Responsible for education policy and management, category: Education",
            "id: 2, en_name: Ministry of Health, kh_name: ក្រសួងសុខាភិបាល, description: Oversees healthcare system and public health, category: Healthcare",
            "id: 3, en_name: Ministry of Interior, kh_name: ក្រសួងមហាផ្ទៃ, description: Manages internal affairs and local administration, category: Administration",
            "id: 4, en_name: Ministry of Agriculture, kh_name: ក្រសួងកសិកម្ម, description: Agricultural development and food security, category: Agriculture",
            "id: 5, en_name: Ministry of Commerce, kh_name: ក្រសួងពាណិជ្ជកម្ម, description: Trade promotion and commercial policy, category: Commerce",
            "id: 6, en_name: Ministry of Tourism, kh_name: ក្រសួងទេសចរណ៍, description: Tourism development and promotion, category: Tourism",
            "id: 7, en_name: Ministry of Information, kh_name: ក្រសួងព័ត៌មាន, description: Information and communication management, category: Information",
            "id: 8, en_name: Ministry of Justice, kh_name: ក្រសួងយុត្តិធម៌, description: Legal affairs and judicial system oversight, category: Justice",
            "id: 9, en_name: Ministry of Defense, kh_name: ក្រសួងការពារជាតិ, description: National defense and military affairs, category: Defense",
            "id: 10, en_name: Ministry of Economy, kh_name: ក្រសួងសេដ្ឋកិច្ច, description: Economic planning and financial policy, category: Economy",
            "id: 11, en_name: Ministry of Environment, kh_name: ក្រសួងបរិស្ថាន, description: Environmental protection and natural resource management, category: Environment",
            "id: 12, en_name: Ministry of Public Works, kh_name: ក្រសួងសាធារណកម្ម, description: Infrastructure development and public works, category: Infrastructure",
            "id: 13, en_name: Ministry of Labor, kh_name: ក្រសួងការងារ, description: Labor relations and employment policies, category: Labor",
            "id: 14, en_name: Ministry of Social Affairs, kh_name: ក្រសួងកិច្ចការសង្គម, description: Social welfare and community development, category: Social Affairs",
            "id: 15, en_name: Ministry of Culture, kh_name: ក្រសួងវប្បធម៌, description: Cultural preservation and arts promotion, category: Culture"
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