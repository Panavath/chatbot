import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration for RAG Chatbot (single database, sub_orgs table)"""
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # ChromaDB
    CHROMADB_DIR = './data/chromadb'
    COLLECTION_NAME = 'sub_orgs_collection'

    # Model Settings
    EMBEDDING_MODEL = 'text-embedding-3-small'
    CHAT_MODEL = 'gpt-4o'
    LLM_TEMPERATURE = 0

    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Retrieval
    MAX_RETRIEVAL_DOCS = 4
    SIMILARITY_THRESHOLD = 0.5

    # Search
    SEARCH_NUM_RESULTS = 5
    RECURSION_LIMIT = 100

    # RAG
    MAX_RESULTS = 15
    MAX_TOKENS = 800
    TEMPERATURE = 0.3

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY and not cls.OPENAI_API_KEY:
            raise ValueError("At least one API key (GEMINI or OPENAI) is required in .env file")
        if not all([cls.DB_HOST, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD]):
            raise ValueError("Database credentials are required in .env file")
        return True 