#!/usr/bin/env python3
"""
Main entry point for RAG Chatbot with ChromaDB and Gradio
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from ui import GradioUI
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rag_chatbot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    logger.info("🔍 Checking environment...")
    
    # Check API keys
    if not Config.GEMINI_API_KEY and not Config.OPENAI_API_KEY:
        logger.error("❌ No API keys found. Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file")
        return False
    
    # Check if at least one API key is available
    if Config.GEMINI_API_KEY:
        logger.info("✅ Gemini API key found")
    if Config.OPENAI_API_KEY:
        logger.info("✅ OpenAI API key found")
    
    # Check database configuration (optional)
    db_config = Config.get_database_config()
    if db_config:
        logger.info("✅ Database configuration found")
    else:
        logger.info("ℹ️ No database configuration found - will use sample data")
    
    return True

def create_directories():
    """Create necessary directories"""
    try:
        # Create ChromaDB directory
        os.makedirs(Config.CHROMADB_DIR, exist_ok=True)
        logger.info(f"✅ Created directory: {Config.CHROMADB_DIR}")
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        logger.info("✅ Created logs directory")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creating directories: {e}")
        return False

def main():
    """Main function"""
    print("🏛️ RAG Chatbot - Government Organizations")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please check your configuration.")
        return
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create necessary directories.")
        return
    
    print("\n🚀 Starting RAG Chatbot...")
    print(f"🌐 Gradio UI will be available at: http://localhost:{Config.GRADIO_PORT}")
    print("⭐ Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Create and launch UI
        ui = GradioUI()
        ui.launch(
            server_name="0.0.0.0",
            show_error=True,
            quiet=False
        )
    except KeyboardInterrupt:
        print("\n👋 RAG Chatbot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting RAG Chatbot: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 