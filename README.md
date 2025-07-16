# Simple RAG Chatbot

A minimal Retrieval-Augmented Generation (RAG) chatbot built with Streamlit that connects to your database to provide information about Cambodian government organizations.

## Features

- 🤖 **RAG-powered responses** using Google Gemini embeddings and OpenAI
- 💾 **Database integration** connects to your PostgreSQL database
- 🔍 **Vector search** using ChromaDB for semantic document retrieval
- 🌐 **Clean Streamlit interface** with chat functionality
- 📚 **Fallback responses** when OpenAI is unavailable
- 📊 **Status monitoring** to check system health

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for better responses)
OPENAI_API_KEY=your_openai_api_key_here

# Optional (database connection - uses sample data if not provided)
DB_HOST=localhost
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### 3. Run the Chatbot

```bash
streamlit run app.py
```

The chatbot will be available at http://localhost:8501

## How It Works

1. **Database Connection**: Connects to your PostgreSQL database and loads documents from the `sub_org` table
2. **Document Indexing**: Uses Google Gemini to generate embeddings and stores them in ChromaDB
3. **Query Processing**: When you ask a question, it:
   - Generates an embedding for your question
   - Searches for similar documents using vector similarity
   - Uses OpenAI (or fallback logic) to generate a response based on relevant documents

## File Structure

```
chatbot/
├── app.py              # Main Streamlit application
├── rag_service.py      # RAG service (database, embeddings, vector store)
├── config.py           # Configuration and settings
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (you create this)
├── data/              # ChromaDB vector database storage
└── logs/              # Application logs
```

## Configuration

### API Keys

- **GEMINI_API_KEY** (Required): Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OPENAI_API_KEY** (Optional): Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### Database

If you don't provide database credentials, the chatbot will use sample data about Cambodian government ministries.

To connect to your database, ensure:
- PostgreSQL is running
- Database contains a `sub_org` table
- User has read permissions

### Settings

Edit `config.py` to customize:
- `MAX_RESULTS`: Number of documents to retrieve (default: 10)
- `MAX_TOKENS`: Maximum response length (default: 800)
- `TEMPERATURE`: Response creativity 0.0-1.0 (default: 0.3)

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY is required"**
- Create a `.env` file with your Gemini API key

**"ChromaDB schema error"**
- Delete the `data/chromadb` folder and restart the app

**"Database connection failed"**
- Check your database credentials in `.env`
- The app will use sample data if database is unavailable

**"No documents loaded"**
- Ensure your database has a `sub_org` table with data
- Check database permissions

### Getting Help

1. Check the sidebar status indicators in the web interface
2. Look at console output for detailed error messages
3. Ensure all environment variables are set correctly

## Requirements

- Python 3.8+
- PostgreSQL (optional)
- Google Gemini API key
- OpenAI API key (optional but recommended)

---

**Ready to use!** Just run `streamlit run app.py` and start chatting with your RAG-powered assistant. 