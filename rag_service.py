"""
RAG Service for Multi-Database Agent with Routing
Handles document processing, vector storage, query routing, and response generation
"""
import logging
import os
import shutil
from typing import List, Dict, Any, Optional
import psycopg2
import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from openai import RateLimitError, APIError
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """RAG service for a single database (sub_orgs table) with fallback support"""
    def __init__(self):
        self.embeddings = None
        self.llm = None
        self.vectorstore = None
        self._initialized = False
        self._using_openai = True  # Track which service were using

    def initialize(self):
        Config.validate()
        
        # Try OpenAI first, fall back to Gemini if needed
        if Config.OPENAI_API_KEY:
            try:
                os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
                self.embeddings = OpenAIEmbeddings(model=Config.EMBEDDING_MODEL)
                self.llm = ChatOpenAI(temperature=Config.LLM_TEMPERATURE)
                self._using_openai = True
                logger.info("Using OpenAI for embeddings and LLM")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
                if Config.GEMINI_API_KEY:
                    self._fallback_to_gemini()
                else:
                    raise RuntimeError("OpenAI failed and no Gemini fallback available")
        elif Config.GEMINI_API_KEY:
            self._fallback_to_gemini()
        else:
            raise RuntimeError("No API keys available")
        
        # Set up ChromaDB
        os.makedirs(Config.CHROMADB_DIR, exist_ok=True)
        
        # Load and chunk documents from sub_orgs table
        docs = self._load_documents_from_db()
        texts = self._chunk_documents(docs)
        
        # Create Chroma vectorstore
        self.vectorstore = Chroma(
            collection_name=Config.COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=Config.CHROMADB_DIR
        )
        
        # Try to add documents, with fallback if rate limited
        if texts:
            try:
                self.vectorstore.add_documents(texts)
            except RateLimitError as e:
                logger.error(f"OpenAI rate limit exceeded during initialization: {e}")
                if not self._using_openai:
                    raise RuntimeError("Service unavailable due to rate limits")
                
                # Try to fall back to Gemini
                try:
                    logger.info("Attempting to fall back to Gemini due to OpenAI rate limit during initialization")
                    self._fallback_to_gemini()
                    # Recreate vectorstore with new embeddings
                    self.vectorstore = Chroma(
                        collection_name=Config.COLLECTION_NAME,
                        embedding_function=self.embeddings,
                        persist_directory=Config.CHROMADB_DIR
                    )
                    self.vectorstore.add_documents(texts)
                except Exception as fallback_error:
                    logger.error(f"Fallback to Gemini failed during initialization: {fallback_error}")
                    raise RuntimeError("Service unavailable due to rate limits")
            except APIError as e:
                logger.error(f"OpenAI API error during initialization: {e}")
                if not self._using_openai:
                    raise RuntimeError("Service temporarily unavailable")
                
                # Try to fall back to Gemini
                try:
                    logger.info("Attempting to fall back to Gemini due to OpenAI API error during initialization")
                    self._fallback_to_gemini()
                    # Recreate vectorstore with new embeddings
                    self.vectorstore = Chroma(
                        collection_name=Config.COLLECTION_NAME,
                        embedding_function=self.embeddings,
                        persist_directory=Config.CHROMADB_DIR
                    )
                    self.vectorstore.add_documents(texts)
                except Exception as fallback_error:
                    logger.error(f"Fallback to Gemini failed during initialization: {fallback_error}")
                    raise RuntimeError("Service temporarily unavailable")
        
        self._initialized = True
        service_name = "OpenAI" if self._using_openai else "Gemini"
        logger.info(f"RAGService initialized with {len(texts)} chunks using {service_name}")

    def _fallback_to_gemini(self):
        """Fallback to Gemini when OpenAI is unavailable"""
        try:
            os.environ["GOOGLE_API_KEY"] = Config.GEMINI_API_KEY
            # Force synchronous mode to avoid event loop issues
            os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
            
            # Try to initialize Gemini with error handling for event loop issues
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-1"
                )
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",       temperature=Config.LLM_TEMPERATURE,
                    convert_system_message_to_human=True
                )
                self._using_openai = False
                logger.info("Falling back to Gemini for embeddings and LLM")
            except RuntimeError as e:
                if "event loop" in str(e).lower() or "nocurrent event loop" in str(e):
                    logger.error("Gemini requires async event loop which is not available in Streamlit")
                    raise RuntimeError("Gemini is not compatible with current environment (async event loop required)")
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise RuntimeError("Both OpenAI and Gemini failed to initialize")

    def _load_documents_from_db(self) -> List[str]:
        try:
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                port=Config.DB_PORT
            )
            df = pd.read_sql_query("SELECT * FROM sub_org ORDER BY id", conn)
            docs = []
            for _, row in df.iterrows():
                doc_parts = []
                for col in df.columns:
                    if pd.notna(row[col]) and str(row[col]).strip():
                        doc_parts.append(f"{col}: {row[col]}")
                if doc_parts:
                    docs.append("; ".join(doc_parts))
            conn.close()
            return docs
        except Exception as e:
            logger.error(f"Error loading from database: {e}")
            return []

    def _chunk_documents(self, docs: List[str]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        return splitter.create_documents(docs)

    def query(self, question: str) -> Dict[str, Any]:
        if not self._initialized:
            return {"response": "Service not initialized.", "sources": 0}
        
        try:
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": Config.MAX_RETRIEVAL_DOCS}
            )
            relevant_docs = retriever.get_relevant_documents(question)
            
            if relevant_docs:
                # Create appropriate prompt based on the service being used
                if self._using_openai:
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "You are a helpful AI assistant that answers questions based on provided context. Be direct and concise. If the context doesn't contain enough information, say so."),
                        ("human", "Here is the context:\n{context}"),
                        ("human", "Question: {input}"),
                        ("assistant", "I'll help answer your question based on the context provided."),
                        ("human", "Please provide your answer:")
                    ])
                else:
                    # Gemini-specific prompt (no system message)
                    prompt = ChatPromptTemplate.from_messages([
                        ("human", "You are a helpful AI assistant that answers questions based on provided context. Be direct and concise. If the context doesn't contain enough information, say so.\n\nHere is the context:\n{context}\n\nQuestion: {input}\n\nPlease provide your answer:")
                    ])
                
                combine_docs_chain = create_stuff_documents_chain(self.llm, prompt)
                retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
                response = retrieval_chain.invoke({"input": question})
                return {"response": response['answer'], "sources": len(relevant_docs)}
            else:
                return {"response": "No relevant information found in the database.", "sources": 0}
                
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            if not self._using_openai:
                return {"response": "Service temporarily unavailable due to rate limits. Please try again later.", "sources": 0}
            
            # Try to fall back to Gemini
            try:
                logger.info("Attempting to fall back to Gemini due to OpenAI rate limit")
                self._fallback_to_gemini()
                # Retry the query with Gemini
                return self.query(question)
            except Exception as fallback_error:
                logger.error(f"Fallback to Gemini failed: {fallback_error}")
                return {"response": "Service temporarily unavailable due to rate limits. Please try again later.", "sources": 0}
                
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            if not self._using_openai:
                return {"response": "Service temporarily unavailable. Please try again later.", "sources": 0}
            
            # Try to fall back to Gemini
            try:
                logger.info("Attempting to fall back to Gemini due to OpenAI API error")
                self._fallback_to_gemini()
                # Retry the query with Gemini
                return self.query(question)
            except Exception as fallback_error:
                logger.error(f"Fallback to Gemini failed: {fallback_error}")
                return {"response": "Service temporarily unavailable. Please try again later.", "sources": 0}
                
        except Exception as e:
            logger.error(f"Unexpected error in query: {e}")
            return {"response": f"An error occurred while processing your request: {str(e)}", "sources": 0} 