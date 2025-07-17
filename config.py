import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration for RAG Chatbot with ChromaDB and Gradio"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database Configuration (Optional)
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # ChromaDB Configuration
    CHROMADB_DIR = './data/chromadb'
    COLLECTION_NAME = 'sub_orgs_collection'
    
    # Model Settings
    EMBEDDING_MODEL = 'models/embedding-001'  # Gemini embedding model
    CHAT_MODEL = 'gpt-4o-mini'  # OpenAI chat model (using mini to avoid quota issues)
    GEMINI_CHAT_MODEL = 'gemini-1.5-flash'  # Gemini chat model
    LLM_TEMPERATURE = 0.7
    
    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval Settings
    MAX_RETRIEVAL_DOCS = 15
    SIMILARITY_THRESHOLD = 0.1
    
    # Response Settings
    MAX_TOKENS = 800
    CACHE_TTL = 3600  # Cache duration in seconds
    
    # UI Settings
    GRADIO_THEME = "soft"
    GRADIO_PORT = 7860
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError("At least one API key (GEMINI or OPENAI) is required")
        return True
    
    @classmethod
    def get_database_config(cls) -> Optional[dict]:
        """Get database configuration if available"""
        if all([cls.DB_HOST, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD]):
            return {
                'host': cls.DB_HOST,
                'database': cls.DB_NAME,
                'user': cls.DB_USER,
                'password': cls.DB_PASSWORD,
                'port': cls.DB_PORT
            }
        return None 