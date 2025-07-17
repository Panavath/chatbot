"""
Gradio UI for RAG Chatbot
Provides a modern web interface for the RAG system
"""

import gradio as gr
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime
from rag_service import RAGService
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GradioUI:
    """Gradio UI for RAG Chatbot"""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.chat_history: List[Tuple[str, str]] = []
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize the RAG service"""
        try:
            success = self.rag_service.initialize()
            if success:
                logger.info("✅ RAG Service initialized successfully for Gradio UI")
            else:
                logger.error("❌ Failed to initialize RAG Service for Gradio UI")
        except Exception as e:
            logger.error(f"❌ Error initializing RAG Service: {e}")
    
    def chat_response(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """Handle chat response"""
        if not message.strip():
            return "", history
        
        try:
            # Process query (default to English)
            result = self.rag_service.query(message, "en")
            
            # Extract response
            response = result.get("response", "Sorry, I couldn't process your request.")
            sources = result.get("sources", 0)
            
            # Add source count to response if available
            if sources > 0:
                response += f"\n\n📚 *Found {sources} relevant sources*"
            
            # Update history
            history.append([message, response])
            
            return "", history
            
        except Exception as e:
            logger.error(f"❌ Error in chat response: {e}")
            error_msg = "Sorry, an error occurred while processing your request. Please try again."
            history.append([message, error_msg])
            return "", history
    
    def get_status_info(self) -> str:
        """Get status information for display"""
        try:
            status = self.rag_service.get_status()
            
            if not status.get("initialized", False):
                return "❌ **Service Status**: Not initialized"
            
            # Build status string
            status_lines = ["✅ **Service Status**: Initialized"]
            
            # Database info
            if "database" in status:
                db_info = status["database"]
                doc_count = db_info.get("document_count", 0)
                has_db = db_info.get("has_database_config", False)
                db_source = "Database" if has_db else "Sample Data"
                status_lines.append(f"📊 **Documents**: {doc_count} ({db_source})")
            
            # Vector store info
            if "vector_store" in status:
                vs_info = status["vector_store"]
                if "document_count" in vs_info:
                    status_lines.append(f"🗄️ **Vector Store**: {vs_info['document_count']} documents")
            
            # LLM info
            if "llm" in status:
                llm_info = status["llm"]
                primary = llm_info.get("primary_model", "Unknown")
                status_lines.append(f"🤖 **Primary LLM**: {primary}")
            
            # Embedding info
            if "embedding" in status:
                emb_info = status["embedding"]
                cache_size = emb_info.get("cache_size", 0)
                status_lines.append(f"🧠 **Embedding Cache**: {cache_size} items")
            
            # Timestamp
            timestamp = status.get("timestamp", "")
            if timestamp:
                status_lines.append(f"🕒 **Last Updated**: {timestamp}")
            
            return "\n".join(status_lines)
            
        except Exception as e:
            logger.error(f"❌ Error getting status: {e}")
            return f"❌ **Error**: {str(e)}"
    
    def refresh_data(self) -> str:
        """Refresh data from database"""
        try:
            success = self.rag_service.refresh_data()
            if success:
                return "✅ Data refreshed successfully!"
            else:
                return "❌ Failed to refresh data"
        except Exception as e:
            logger.error(f"❌ Error refreshing data: {e}")
            return f"❌ Error: {str(e)}"
    
    def clear_chat(self) -> Tuple[str, List[List[str]]]:
        """Clear chat history"""
        self.chat_history = []
        return "", []
    
    def switch_llm(self, use_openai: bool) -> str:
        """Switch between OpenAI and Gemini"""
        try:
            success = self.rag_service.switch_llm(use_openai)
            if success:
                model = "OpenAI" if use_openai else "Gemini"
                return f"✅ Switched to {model}"
            else:
                return "❌ Failed to switch LLM"
        except Exception as e:
            logger.error(f"❌ Error switching LLM: {e}")
            return f"❌ Error: {str(e)}"
    
    def clear_cache(self) -> str:
        """Clear embedding cache"""
        try:
            self.rag_service.clear_cache()
            return "✅ Cache cleared successfully!"
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return f"❌ Error: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        # Custom CSS for minimalistic styling
        css = """
        .gradio-container {
            max-width: 800px !important;
            margin: auto !important;
        }
        .chat-message {
            padding: 12px;
            border-radius: 8px;
            margin: 8px 0;
        }
        .user-message {
            background-color: #f0f8ff;
            border-left: 3px solid #007acc;
        }
        .bot-message {
            background-color: #f8f9fa;
            border-left: 3px solid #28a745;
        }
        """
        
        with gr.Blocks(
            title="RAG Chatbot - Government Organizations",
            theme=gr.themes.Soft(),
            css=css
        ) as interface:
            
            # Header
            gr.Markdown("""
            # 🏛️ MPWT Assistant
            
            Ask questions about the Ministry of Public Works and Transport departments and services.
            
            ---
            """)
            
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat",
                height=500,
                show_label=False,
                container=True,
                bubble_full_width=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Ask about MPWT departments...",
                    lines=1,
                    scale=4,
                    show_label=False,
                    container=False
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            with gr.Row():
                clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            # Event handlers
            submit_btn.click(
                self.chat_response,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            # Handle Enter key press
            msg.submit(
                self.chat_response,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot]
            )
            
            clear_btn.click(
                self.clear_chat,
                outputs=[msg, chatbot]
            )
        
        return interface
    
    def launch(self, **kwargs) -> None:
        """Launch the Gradio interface"""
        interface = self.create_interface()
        interface.launch(
            share=False,
            **kwargs
        )

def main():
    """Main function to run the Gradio UI"""
    ui = GradioUI()
    ui.launch()

if __name__ == "__main__":
    main() 