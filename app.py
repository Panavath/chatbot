"""
Multi-Database RAG Agent with Routing
A Streamlit interface for the RAG agent with intelligent database routing
"""
import streamlit as st
import logging
from datetime import datetime
from typing import Dict, Any
from rag_service import RAGService
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="RAG Agent with Database Routing",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .database-tab {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1e3c72;
    }
    .routing-info {
        background: #e8f4f8;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Auto-initialize on app start
@st.cache_resource
def get_rag_service():
    try:
        service = RAGService()
        service.initialize()  # No args, uses config/.env
        return service
    except RuntimeError as e:
        error_msg = str(e)
        if "rate limits" in error_msg.lower() or "quota" in error_msg.lower():
            st.error("⚠️ **Service Unavailable**\n\nYour OpenAI account has exceeded its quota. Please check your billing details or try again later.")
        elif "event loop" in error_msg.lower() or "async" in error_msg.lower():
            st.error("⚠️ **Configuration Issue**\n\nGemini fallback is not compatible with the current environment. Please ensure you have a valid OpenAI API key with sufficient quota.")
        else:
            st.error(f"⚠️ **Initialization Error**\n\n{error_msg}")
        return None
    except Exception as e:
        st.error(f"⚠️ **Unexpected Error**\n\nAn unexpected error occurred: {str(e)}")
        return None

rag_service = get_rag_service()

# Check if service initialized successfully
if rag_service is None:
    st.stop()  # Stop the app if service failed to initialize

st.title("RAG Chatbot")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me anything about sub_orgs."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = rag_service.query(prompt)
            st.markdown(result["response"])
            st.session_state.messages.append({"role": "assistant", "content": result["response"]}) 