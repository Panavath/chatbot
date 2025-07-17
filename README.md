# MPWT Assistant - RAG Chatbot

An intelligent Retrieval-Augmented Generation (RAG) chatbot for the Ministry of Public Works and Transport (MPWT) of Cambodia. This system provides accurate information about government departments, services, and organizational structure using advanced AI technology.

## 🚀 Features

- 🏛️ **MPWT-Specific Knowledge** - Specialized for Ministry of Public Works and Transport data
- 🤖 **Advanced RAG Pipeline** - Uses Gemini embeddings and GPT-4o-mini for high-quality responses
- 🔍 **Vector Similarity Search** - Powered by ChromaDB for semantic document retrieval
- 💬 **Clean Chat Interface** - Minimalistic Gradio UI for seamless interaction
- 📊 **Database Integration** - Connects to PostgreSQL database or uses sample data
- 🌐 **Multi-Language Support** - English and Khmer language responses
- 📄 **Document Processing** - Handles structured organizational data

## 🏗️ Architecture

The application follows a modular architecture:

```
📁 Project Structure
├── main.py              # Main entry point
├── ui.py                # Gradio web interface
├── rag_service.py       # Core RAG service orchestrator
├── llm.py              # LLM service (OpenAI & Gemini)
├── embedding.py         # Embedding service (Gemini)
├── vectorstore.py       # ChromaDB vector store
├── database.py          # Database service
├── config.py            # Configuration and settings
├── chatbot_prompt.py    # MPWT-specific prompt templates
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (you create this)
├── data/                # ChromaDB data storage
└── README.md            # This file
```

### Key Components

1. **DatabaseService** - Handles data loading from PostgreSQL or sample data
2. **EmbeddingService** - Manages Gemini embeddings with caching
3. **VectorStore** - ChromaDB-based document storage and retrieval
4. **LLMService** - OpenAI and Gemini integration for response generation
5. **RAGService** - Orchestrates all components
6. **GradioUI** - Clean, minimalistic web interface

## 🛠️ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (Optional)
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### 3. Run the Application

```bash
python main.py
```

The application will be available at http://localhost:7860

## 📋 Data Sources

The system can work with two data sources:

### 🗄️ PostgreSQL Database
- **Table**: `sub_org` with organizational data
- **Fields**: id, en_name, kh_name, description, category, etc.
- **Setup**: Configure database connection in `.env` file

### 📋 Sample Data
- **Fallback**: Pre-loaded sample government organization data
- **Content**: 15 sample ministries and departments
- **Usage**: Automatically used if no database connection

## 🔄 How It Works

### Query Processing Flow

1. **Query Input** - User enters a question in the chat interface
2. **Embedding Generation** - Query is converted to vector using Gemini
3. **Vector Search** - System searches ChromaDB for similar documents
4. **Context Retrieval** - Relevant documents are retrieved based on similarity
5. **Response Generation** - LLM generates answer using retrieved context
6. **Conversational Handling** - Greetings and casual queries are handled appropriately

### RAG Pipeline

```python
# 1. Query Processing
query_embedding = embedding_service.get_embedding(query)

# 2. Vector Search
relevant_docs = vector_store.search(query_embedding)

# 3. Response Generation
response = llm_service.generate_response(query, relevant_docs)

# 4. Return Result
return {"response": response, "sources": len(relevant_docs)}
```

## 🔧 Configuration

### API Keys Required

- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Used for embeddings (`models/embedding-001`)
  - Used for chat completions (`gemini-1.5-flash`)

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Used for chat completions (`gpt-4o-mini`)
  - Fallback LLM option

### Advanced Configuration

Edit `config.py` to customize:

```python
# Model Settings
EMBEDDING_MODEL = "models/embedding-001"  # Gemini
CHAT_MODEL = "gpt-4o-mini"               # OpenAI
LLM_TEMPERATURE = 0.7

# Document Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Settings
MAX_RETRIEVAL_DOCS = 5
SIMILARITY_THRESHOLD = 0.1

# ChromaDB Settings
CHROMADB_DIR = './data/chromadb'
COLLECTION_NAME = 'sub_orgs_collection'
```

## 📖 Usage Guide

### 1. Start the Application

1. Run `python main.py`
2. Wait for initialization messages
3. Open browser to http://localhost:7860

### 2. Start Chatting

1. Type your question in the input box
2. Press Enter or click Send
3. View the AI-generated response
4. See source count if relevant documents were found

### Example Queries

**General Questions:**
- "What departments are there?"
- "Tell me about the General Department of Techniques"
- "What does the Ministry of Public Works and Transport do?"

**Specific Information:**
- "What is the role of the General Department of Administration and Finance?"
- "List all general departments"
- "What are the responsibilities of the Planning and Policy department?"

**Conversational:**
- "Hello" or "Hi" - Gets a friendly introduction
- "What can you help me with?" - Shows available capabilities

## 🔍 Troubleshooting

### Common Issues

**"Service not initialized"**
- Check that API keys are set in `.env` file
- Verify internet connection
- Check console for initialization errors

**"No relevant information found"**
- The system will politely redirect to MPWT topics
- Try asking about specific departments or services
- Check if database has the information you're looking for

**"Failed to connect to database"**
- Verify database credentials in `.env`
- System will automatically use sample data as fallback
- Check PostgreSQL service is running

**Enter key not working**
- Make sure you're using the latest version
- Try clicking the Send button as alternative
- Check browser console for JavaScript errors

### Getting Help

1. Check the console output for detailed error messages
2. Verify all environment variables are set correctly
3. Make sure all required dependencies are installed
4. Restart the application if needed

## 🧪 Development

### Project Structure

```
rag_service.py
├── DatabaseService     # Data loading and management
├── EmbeddingService    # Gemini embeddings
├── VectorStore         # ChromaDB operations
├── LLMService          # OpenAI/Gemini integration
└── RAGService          # Main orchestrator

ui.py
├── GradioUI            # Web interface class
├── create_interface()  # UI layout
├── chat_response()     # Chat handling
└── launch()           # Application startup
```

### Adding New Features

1. **New Data Sources**: Update `DatabaseService` to connect to additional databases
2. **Custom Prompts**: Modify `chatbot_prompt.py` for different use cases
3. **UI Enhancements**: Extend `ui.py` with additional Gradio components
4. **LLM Integration**: Add new models in `llm.py`

### Customizing Responses

Edit the prompt templates in `chatbot_prompt.py`:

```python
SYSTEM_TEMPLATE = """
You are MPWT Assistant, an advanced AI system for the Ministry of Public Works and Transport of Cambodia.

[Your custom instructions here]
"""
```

## 📚 Dependencies

### Core Frameworks
- **Gradio**: Web interface
- **LangChain**: RAG pipeline and document processing
- **ChromaDB**: Vector database

### AI/ML Services  
- **Google Gemini**: Embeddings and chat completions
- **OpenAI**: Chat completions (fallback)
- **PostgreSQL**: Database storage (optional)

### Document Processing
- **psycopg2**: PostgreSQL database adapter
- **pandas**: Data manipulation

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

---

**Ready to use!** Just run `python main.py` and start chatting with your MPWT Assistant. 🚀 