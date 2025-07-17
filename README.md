# Multi-Database RAG Agent with Routing

An intelligent Retrieval-Augmented Generation (RAG) agent that automatically routes queries to specialized databases and provides accurate responses with web search fallback.

## 🚀 Features

- 🎯 **Intelligent Query Routing** - Automatically determines the best database for each query
- 📚 **Multi-Database Support** - Products, Support, and Finance specialized databases
- 🤖 **Advanced RAG Pipeline** - Uses OpenAI embeddings and LLM for high-quality responses
- 🔍 **Vector Similarity Search** - Powered by Qdrant vector database for semantic retrieval
- 🌐 **Web Search Fallback** - DuckDuckGo integration when no relevant documents found
- 📄 **PDF Document Processing** - Upload and process multiple PDF documents
- 💬 **Interactive Chat Interface** - Clean Streamlit UI with real-time routing information
- 📊 **Status Monitoring** - Real-time system health and database status

## 🏗️ Architecture

The application follows a modular architecture:

```
📁 Project Structure
├── app.py              # Streamlit web interface
├── rag_service.py      # Core RAG service with all components
├── config.py           # Configuration and settings
├── start.py            # Startup script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (you create this)
└── README.md           # This file
```

### Key Components

1. **DocumentProcessor** - Handles PDF processing and text chunking
2. **QueryRouter** - Routes queries using vector similarity + LLM fallback
3. **ResponseGenerator** - Generates responses from retrieved documents
4. **WebSearchAgent** - Provides web search fallback using LangGraph
5. **RAGService** - Orchestrates all components

## 🛠️ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration (Required) 
QDRANT_URL=https://your-cluster.qdrant.tech
QDRANT_API_KEY=your_qdrant_api_key_here
```

### 3. Run the Application

Using the startup script:
```bash
python start.py
```

Or directly with Streamlit:
```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

## 📋 Database Collections

The system supports three specialized databases:

### 🛍️ Products Database
- **Purpose**: Product information, specifications, features
- **Use Cases**: Product manuals, specifications, feature details
- **Routing Triggers**: "product", "features", "specifications", "manual"

### 🆘 Support Database  
- **Purpose**: Customer support, FAQs, troubleshooting guides
- **Use Cases**: Help documentation, troubleshooting, customer service
- **Routing Triggers**: "help", "support", "troubleshooting", "guide", "FAQ"

### 💰 Finance Database
- **Purpose**: Financial data, reports, costs, revenue
- **Use Cases**: Financial reports, pricing, revenue data, investments
- **Routing Triggers**: "cost", "price", "revenue", "financial", "budget"

## 🔄 How It Works

### Query Processing Flow

1. **Query Input** - User enters a question
2. **Vector Routing** - System searches all databases for similarity scores
3. **Confidence Check** - If confidence > threshold, route to best database
4. **LLM Fallback** - If low confidence, use LLM-based routing
5. **Document Retrieval** - Retrieve relevant documents from chosen database
6. **Response Generation** - Generate answer using retrieved context
7. **Web Search Fallback** - If no relevant documents, use web search

### Routing Logic

```python
# Vector Similarity Routing (Primary)
best_score = max(similarity_scores_across_databases)
if best_score >= confidence_threshold:
    return best_database

# LLM Routing (Fallback)
routing_decision = llm_agent.analyze(query)
return routing_decision

# Web Search (Last Resort)
if no_suitable_database:
    return web_search_results
```

## 🔧 Configuration

### API Keys Required

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Used for embeddings (`text-embedding-3-small`)
  - Used for chat completions (`gpt-4o`)
  - Used for query routing agent

- **Qdrant API Key**: Get from [Qdrant Cloud](https://cloud.qdrant.io/)
  - Vector database for document storage
  - Semantic similarity search

### Advanced Configuration

Edit `config.py` to customize:

```python
# Model Settings
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o" 
LLM_TEMPERATURE = 0

# Document Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval Settings
MAX_RETRIEVAL_DOCS = 4
SIMILARITY_THRESHOLD = 0.5
```

## 📖 Usage Guide

### 1. Initialize the Service

1. Open the application
2. Enter your API keys in the sidebar
3. Click "🚀 Initialize Service"
4. Wait for successful initialization

### 2. Upload Documents

1. Go to the "Document Management" section
2. Select the appropriate database tab
3. Upload PDF files
4. Click "Process Documents"

### 3. Start Chatting

1. Type your question in the chat input
2. Watch the routing decision in real-time
3. View the response with source information
4. See which database was used

### Example Queries

**Products Database:**
- "What are the specifications of the new laptop?"
- "Tell me about the features of product X"
- "Where can I find the user manual?"

**Support Database:**
- "How do I troubleshoot connection issues?"
- "What should I do if the system crashes?"
- "Where can I find installation guides?"

**Finance Database:**
- "What was our revenue last quarter?"
- "Show me the cost breakdown for project Y"
- "What are the pricing details for service Z?"

## 🔍 Troubleshooting

### Common Issues

**"Service not initialized"**
- Check that all API keys are entered correctly
- Verify Qdrant URL format (should include https://)
- Check internet connection

**"Failed to connect to Qdrant"**
- Verify Qdrant URL and API key
- Check if your Qdrant cluster is running
- Ensure proper network access

**"No relevant documents found"**
- Upload more documents to the databases
- Try rephrasing your question
- System will automatically fall back to web search

**Routing not working properly**
- Check that documents are uploaded to correct databases
- Try more specific keywords in your queries
- Review routing triggers in database descriptions

### Getting Help

1. Check the sidebar status indicators
2. Look at console output for detailed error messages  
3. Verify all environment variables are set correctly
4. Make sure all required dependencies are installed

## 🧪 Development

### Project Structure

```
rag_service.py
├── DocumentProcessor     # PDF processing and chunking
├── QueryRouter          # Query routing logic
├── ResponseGenerator    # Response generation from docs
├── WebSearchAgent      # Web search fallback
└── RAGService          # Main orchestrator

app.py
├── init_session_state()      # Session management
├── display_sidebar()         # Configuration UI
├── display_document_upload() # Document management UI
└── display_chat_interface()  # Chat interface
```

### Adding New Databases

1. Update `config.py` with new database configuration
2. Add routing logic in `QueryRouter`
3. Update UI tabs in `display_document_upload()`

### Customizing Routing

Edit the routing agent instructions in `QueryRouter._create_routing_agent()`:

```python
instructions=[
    "Your custom routing rules here",
    "1. For topic X → return 'database_name'",
    "2. For topic Y → return 'other_database'",
    # ...
]
```

## 📚 Dependencies

### Core Frameworks
- **Streamlit**: Web interface
- **LangChain**: RAG pipeline and document processing
- **LangGraph**: Agent framework for web search

### AI/ML Services  
- **OpenAI**: Embeddings and chat completions
- **Qdrant**: Vector database
- **Agno**: Agent framework for routing

### Document Processing
- **PyPDF**: PDF text extraction
- **RecursiveCharacterTextSplitter**: Text chunking

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

---

**Ready to use!** Just run `python start.py` and start chatting with your intelligent RAG agent. 🚀 