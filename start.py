#!/usr/bin/env python3
"""
Startup script for Multi-Database RAG Agent
"""
import os
import sys
import subprocess

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import langchain
        import langchain_openai
        import chromadb
        import agno
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("📦 Installing requirements...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install requirements")
            return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("⚠️  No .env file found")
        print("📝 Creating sample .env file...")
        
        sample_env = """# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Gemini Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here
"""
        
        with open('.env', 'w') as f:
            f.write(sample_env)
        
        print("✅ Created .env file")
        print("🔧 Please edit .env file with your API keys")
        print("   - OpenAI API Key: https://platform.openai.com/api-keys")
        print("   - Gemini API Key: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ .env file found")
    return True

def get_database_names():
    """Get database names from config"""
    try:
        from config import Config
        return [config.name for config in Config.COLLECTIONS.values()]
    except ImportError:
        return ["Products", "Support", "Finance"]  # Fallback

def main():
    """Main startup function"""
    print("📚 RAG Agent with Database Routing - Startup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment
    if not check_env_file():
        return
    
    # Get database names
    db_names = get_database_names()
    
    print("\n🚀 Starting RAG Agent...")
    print("🌐 Opening at: http://localhost:8501")
    print(f"📋 Available databases: {', '.join(db_names)}")
    print("⭐ Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 RAG Agent stopped")
    except Exception as e:
        print(f"\n❌ Error starting RAG Agent: {e}")

if __name__ == "__main__":
    main() 