"""
Simple Configuration for RAG Chatbot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Simple configuration class"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # RAG Settings
    MAX_RESULTS = 15
    MAX_TOKENS = 800
    TEMPERATURE = 0.3
    
    # ChromaDB Settings
    CHROMADB_DIR = "./data/chromadb"
    COLLECTION_NAME = "documents"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        return True
    
    @classmethod
    def has_database_config(cls):
        """Check if database is configured"""
        return all([cls.DB_HOST, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD]) 