# Setup Instructions for Groww Mutual Fund FAQ Chatbot

## Prerequisites

- **Python 3.9-3.12** (recommended - avoid 3.14 due to dependency issues)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Groq API key** (free tier available)
- **Pinecone API key** (free tier available)

## Step 1: Clone the Repository

```bash
git clone https://github.com/harikrshm/Groww_FAQ-Chatbot.git
cd Groww_FAQ-Chatbot
```

## Step 2: Create Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This will install:
- Streamlit (web framework)
- Groq SDK (for Llama LLM)
- Pinecone (vector database)
- sentence-transformers (embeddings)
- And other required packages

## Step 4: Set Up Environment Variables

1. **Create a `.env` file** in the project root directory:

   ```env
   # Groq API Configuration (for Llama 3.1 LLM)
   # Get your API key from: https://console.groq.com
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   
   # Pinecone Configuration (Vector Database)
   # Get your API key from: https://www.pinecone.io/
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=ragchatbot
   
   # Embedding Model (optional - defaults to sentence-transformers/all-MiniLM-L6-v2)
   EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
   ```

### Getting API Keys

#### Groq API Key (Free Tier)

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Click "Create API Key"
5. Copy the generated API key and paste it in `.env` file

**Free Tier Benefits:**
- Access to Llama 3.1 8B Instant model
- Fast inference speed
- Generous rate limits for testing

#### Pinecone API Key (Free Tier)

1. Visit [https://www.pinecone.io/](https://www.pinecone.io/)
2. Sign up for a free account
3. Create a new project
4. Create a new index:
   - **Index Name:** `ragchatbot` (or your preferred name)
   - **Dimensions:** 384
   - **Metric:** Cosine
   - **Cloud Provider:** AWS (recommended)
   - **Region:** us-east-1
5. Copy your API key from the dashboard
6. Update `.env` with your index name

**Free Tier Benefits:**
- 1 index with up to 100K vectors
- Sufficient for this chatbot project

## Step 5: Verify Setup

### Check Python Version
```bash
python --version
# Should show Python 3.9.x - 3.12.x
```

### Run Tests
```bash
pytest tests/ -v
```

All tests should pass.

### Test LLM Service (Groq/Llama)
```bash
python -c "from backend.llm_service import get_llm_service; service = get_llm_service(); print('✅ LLM Service initialized successfully')"
```

### Test Retrieval System (Pinecone)
```bash
python -c "from backend.retrieval import get_retrieval_system; retrieval = get_retrieval_system(); print('✅ Retrieval System initialized successfully')"
```

## Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found in environment variables"**
   - Make sure `.env` file exists in the project root
   - Verify the API key is correctly set in `.env` file
   - Check that `python-dotenv` is installed: `pip install python-dotenv`
   - Restart the application after editing `.env`

2. **"PINECONE_API_KEY not found in environment variables"**
   - Verify Pinecone API key is set in `.env` file
   - Check that the index name matches your Pinecone index
   - Ensure the index has 384 dimensions (for sentence-transformers embeddings)

3. **"Module not found" errors**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check Python version (3.9-3.12 recommended)

4. **"Cannot copy out of meta tensor" (PyTorch error)**
   - This is a Python 3.14 compatibility issue
   - Use Python 3.9-3.12 instead
   - Or update requirements.txt with newer torch versions

5. **Streamlit not found**
   - Install Streamlit: `pip install streamlit`
   - Or reinstall all dependencies: `pip install -r requirements.txt`

6. **Port already in use**
   - Streamlit uses port 8501 by default
   - Use a different port: `streamlit run app.py --server.port 8502`

7. **Rate limit errors from Groq**
   - Free tier has rate limits
   - Wait a few seconds between requests
   - Consider upgrading to paid tier for production

8. **Pinecone connection timeout**
   - Check your internet connection
   - Verify API key is correct
   - Ensure index exists and is active

## Project Structure

```
Groww_FAQ-Chatbot/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration constants
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
│
├── backend/                    # Backend logic
│   ├── llm_service.py         # Groq/Llama LLM integration
│   ├── retrieval.py           # Pinecone vector database
│   ├── query_processor.py     # Query classification
│   ├── validators.py          # Response validation
│   └── formatter.py           # Response formatting
│
├── frontend/                   # Frontend components
│   ├── components/
│   │   ├── chat_ui.py         # Chat interface
│   │   ├── welcome.py         # Schemes & samples
│   │   └── footer.py          # Disclaimer
│   └── styles.css             # Custom CSS
│
├── scripts/                    # Utility scripts
│   ├── scrape_sbi_schemes.py  # Web scraper
│   ├── process_documents.py   # Document processing
│   └── upload_to_pinecone.py  # Vector upload
│
├── tests/                      # Test suite
│   ├── test_query_processor.py
│   ├── test_retrieval.py
│   └── test_llm_service.py
│
└── data/                       # Data storage
    ├── raw/                    # Scraped JSON data
    └── processed/              # Processed chunks
```

## Next Steps

1. **Test the chatbot**:
   - Ask: "What is the NAV of SBI Large Cap Fund?"
   - Ask: "What is the exit load for SBI Multicap Fund?"
   - Ask: "What is the minimum SIP for SBI Small Cap Fund?"

2. **Explore the code**:
   - Review `backend/llm_service.py` for LLM integration
   - Check `backend/query_processor.py` for query classification
   - Look at `tests/` for usage examples

3. **Deploy** (optional):
   - See `DEPLOYMENT.md` for Streamlit Cloud deployment instructions

## Performance Tips

1. **Groq (Llama 3.1 8B Instant)**:
   - Very fast inference (~500 tokens/sec)
   - Low latency for real-time chat
   - Cost-effective for high volume

2. **Pinecone**:
   - Fast vector search (<100ms)
   - Automatic scaling
   - Reliable uptime

3. **Caching**:
   - Session state used to avoid re-initialization
   - Embedding model loaded once per session

## Security Best Practices

- ✅ **Never commit `.env` file** to Git (already in `.gitignore`)
- ✅ **Use environment variables** for sensitive data
- ✅ **Rotate API keys** periodically
- ✅ **Use Streamlit secrets** for cloud deployment
- ✅ **Don't share API keys** publicly

## Support

For issues or questions:
1. Check this SETUP.md file
2. Review troubleshooting section
3. Open a GitHub issue with error details
4. Include Python version and OS information

---

**Ready to chat? Run `streamlit run app.py` and start asking questions!** 🚀
