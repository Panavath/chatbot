"""
Simple RAG Chatbot App
A minimal Streamlit interface for the RAG chatbot
"""
import streamlit as st
import logging
from datetime import datetime
from rag_service import RAGService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
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
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_service():
    """Initialize the RAG service with caching"""
    try:
        logger.info("Initializing RAG service...")
        service = RAGService()
        return service, None
    except Exception as e:
        error_msg = f"Failed to initialize RAG service: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def display_sidebar(rag_service):
    """Display system status in sidebar"""
    st.sidebar.markdown("## 📊 System Status")
    
    if rag_service:
        status = rag_service.get_status()
        
        # Database status
        if status["database_connected"]:
            st.sidebar.success("🟢 Database Connected")
        else:
            st.sidebar.warning("🟡 Using Sample Data")
        
        # OpenAI status
        if status["openai_available"]:
            st.sidebar.success("🟢 OpenAI Available")
        else:
            st.sidebar.warning("🟡 Basic Responses Only")
        
        # Vector store status
        if status["vector_store_ready"]:
            st.sidebar.success("🟢 Vector Store Ready")
        else:
            st.sidebar.error("🔴 Vector Store Error")
        
        # Document count
        st.sidebar.info(f"📄 Documents: {status['documents_loaded']}")
    else:
        st.sidebar.error("🔴 Service Not Available")

def main():
    """Main application function"""
    # Header
    st.markdown(
        '<div class="main-header"><h1>🤖 RAG Chatbot</h1><p>Ask me about Cambodian government organizations</p></div>',
        unsafe_allow_html=True
    )
    
    # Initialize RAG service
    rag_service, error = initialize_rag_service()
    
    if error:
        st.error(f"❌ {error}")
        st.info("Please check your configuration:")
        st.code("""
1. Create a .env file with:
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key (optional)

2. For database connection (optional):
   DB_HOST=localhost
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
        """)
        return
    
    # Display sidebar
    display_sidebar(rag_service)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm here to help you with information about Cambodian government organizations. What would you like to know?",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = rag_service.query(prompt)
                
                # Display response
                st.markdown(result["response"])
                
                # Show sources info
                if result["sources"] > 0:
                    st.caption(f"📚 Based on {result['sources']} relevant sources")
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "timestamp": datetime.now().isoformat()
                })
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm here to help you with information about Cambodian government organizations. What would you like to know?",
                "timestamp": datetime.now().isoformat()
            }
        ]
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        f"Simple RAG Chatbot | Powered by Google Gemini & OpenAI | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 