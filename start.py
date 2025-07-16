#!/usr/bin/env python3
"""
Simple startup script for RAG Chatbot
"""
import os
import sys
import subprocess

def check_requirements():
    """Check if requirements are installed"""
    try:
        import streamlit
        import openai
        import google.generativeai
        import chromadb
        import psycopg2
        import pandas
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
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("\n📝 Please create a .env file with:")
        print("GEMINI_API_KEY=your_gemini_api_key")
        print("OPENAI_API_KEY=your_openai_api_key  # optional")
        print("\n🔗 Get Gemini API key: https://makersuite.google.com/app/apikey")
        print("🔗 Get OpenAI API key: https://platform.openai.com/api-keys")
        return False

def main():
    """Main startup function"""
    print("🤖 RAG Chatbot Startup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment
    if not check_env_file():
        return
    
    print("\n🚀 Starting RAG Chatbot...")
    print("🌐 Opening at: http://localhost:8501")
    print("⭐ Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Chatbot stopped")
    except Exception as e:
        print(f"\n❌ Error starting chatbot: {e}")

if __name__ == "__main__":
    main() 