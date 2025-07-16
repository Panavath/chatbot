"""
Simple RAG Service for Chatbot
Integrates database, embeddings, vector store, and response generation
"""
import logging
import os
import shutil
from typing import List, Dict, Any, Optional
import psycopg2
import pandas as pd
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """Simple RAG service that handles everything"""
    
    def __init__(self):
        self.db_connection = None
        self.openai_client = None
        self.chroma_client = None
        self.collection = None
        self.documents = []
        self._initialize()
    
    def _initialize(self):
        """Initialize all components"""
        try:
            Config.validate()
            self._setup_apis()
            self._setup_database()
            self._setup_vector_store()
            self._load_documents()
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def _setup_apis(self):
        """Setup API clients"""
        # Setup Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Setup OpenAI if available
        if Config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found - using basic responses")
    
    def _setup_database(self):
        """Setup database connection"""
        if Config.has_database_config():
            try:
                self.db_connection = psycopg2.connect(
                    host=Config.DB_HOST,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    port=Config.DB_PORT
                )
                logger.info("Database connected successfully")
            except Exception as e:
                logger.warning(f"Database connection failed: {e}")
                self.db_connection = None
        else:
            logger.info("Database not configured - using sample data")
    
    def _setup_vector_store(self):
        """Setup ChromaDB vector store"""
        try:
            # Create directory
            os.makedirs(Config.CHROMADB_DIR, exist_ok=True)
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=Config.CHROMADB_DIR,
                settings=Settings(allow_reset=True)
            )
            
            # Create collection
            try:
                self.chroma_client.delete_collection(Config.COLLECTION_NAME)
            except:
                pass
            
            self.collection = self.chroma_client.create_collection(
                name=Config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Vector store setup failed: {e}")
            # Try to reset ChromaDB
            if "collections.topic" in str(e) or "no such column" in str(e):
                logger.info("Resetting ChromaDB due to schema issue...")
                if os.path.exists(Config.CHROMADB_DIR):
                    shutil.rmtree(Config.CHROMADB_DIR)
                os.makedirs(Config.CHROMADB_DIR, exist_ok=True)
                self._setup_vector_store()  # Retry
            else:
                raise
    
    def _load_documents(self):
        """Load documents from database or use sample data"""
        self.documents = self._get_documents_from_db()
        if self.documents:
            self._index_documents()
        else:
            logger.warning("No documents loaded")
    
    def _get_documents_from_db(self) -> List[str]:
        """Get documents from database or return sample data"""
        if self.db_connection:
            try:
                df = pd.read_sql_query("SELECT * FROM sub_org ORDER BY id", self.db_connection)
                documents = []
                for _, row in df.iterrows():
                    doc_parts = []
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            doc_parts.append(f"{col}: {row[col]}")
                    if doc_parts:
                        documents.append(", ".join(doc_parts))
                logger.info(f"Loaded {len(documents)} documents from database")
                return documents
            except Exception as e:
                logger.error(f"Error loading from database: {e}")
        
        # Return sample data
        logger.info("Using sample documents")
        return [
            "Ministry of Interior: Responsible for internal affairs, immigration, and civil registration",
            "Ministry of Education: Manages education system, schools, and educational policies in Cambodia",
            "Ministry of Health: Oversees healthcare system, hospitals, and public health initiatives",
            "Ministry of Agriculture: Manages agricultural development, farming, and food security",
            "Ministry of Economy and Finance: Handles economic policies, budget, and financial management",
            "Ministry of Public Works and Transport: Manages infrastructure, roads, and transportation systems",
            "Ministry of Justice: Oversees legal system, courts, and law enforcement",
            "Ministry of Foreign Affairs: Manages international relations and diplomatic affairs",
            "Ministry of Defense: Responsible for national defense and military affairs",
            "Ministry of Environment: Protects environment and manages natural resources"
        ]
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using Gemini"""
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def _index_documents(self):
        """Index documents in vector store"""
        try:
            logger.info(f"Indexing {len(self.documents)} documents...")
            
            # Generate embeddings
            valid_docs = []
            valid_embeddings = []
            valid_ids = []
            
            for i, doc in enumerate(self.documents):
                embedding = self._get_embedding(doc)
                if embedding:
                    valid_docs.append(doc)
                    valid_embeddings.append(embedding)
                    valid_ids.append(str(i))
            
            if valid_docs:
                self.collection.add(
                    documents=valid_docs,
                    embeddings=valid_embeddings,
                    ids=valid_ids
                )
                logger.info(f"Successfully indexed {len(valid_docs)} documents")
            else:
                logger.error("No documents could be indexed")
                
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
    
    def _search_documents(self, query: str, n_results: int = None) -> List[str]:
        """Search for relevant documents"""
        if n_results is None:
            n_results = Config.MAX_RESULTS
            
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return []
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                return results['documents'][0]
            return []
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def _generate_response(self, query: str, context_docs: List[str]) -> str:
        """Generate response using OpenAI or fallback"""
        if not context_docs:
            return "I'm sorry, I couldn't find relevant information about your question. Please try asking about government organizations or their functions."
        
        context_text = "\n".join(context_docs)
        
        # Try OpenAI first
        if self.openai_client:
            try:
                prompt = f"""You are a helpful AI chatbot assistant for the Ministry of Public Works and Transport of Cambodia.
                Answer the question using only the provided context. Be accurate and helpful.

                Context:
                {context_text}

                Question: {query}

                Answer:"""

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=Config.MAX_TOKENS,
                    temperature=Config.TEMPERATURE
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI request failed: {e}")
        
        # Fallback response
        response = "Based on the available information:\n\n"
        for i, doc in enumerate(context_docs[:3], 1):
            response += f"{i}. {doc}\n\n"
        response += "Please let me know if you need more specific information."
        return response
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a query and return response"""
        try:
            # Search for relevant documents
            relevant_docs = self._search_documents(question)
            
            # Generate response
            response = self._generate_response(question, relevant_docs)
            
            return {
                "response": response,
                "sources": len(relevant_docs),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"An error occurred: {str(e)}",
                "sources": 0,
                "success": False
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "database_connected": self.db_connection is not None,
            "openai_available": self.openai_client is not None,
            "documents_loaded": len(self.documents),
            "vector_store_ready": self.collection is not None
        } 