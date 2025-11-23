# Groww Mutual Fund FAQ Chatbot

A smart FAQ assistant that provides factual information about SBI Mutual Fund schemes—including NAV, expense ratios, exit loads, minimum SIP amounts, lock-in periods (ELSS), riskometer ratings, benchmarks, and more—using only official public sources.

## 🌟 Features

- **Factual Information Only**: Provides accurate, fact-based answers about mutual fund schemes
- **RAG-based Architecture**: Uses Retrieval Augmented Generation with Pinecone vector database
- **Llama 3.1 8B Instant**: Powered by Meta's Llama model via Groq for fast, efficient response generation
- **Intelligent Query Classification**: Automatically detects and blocks investment advice requests
- **Source Citations**: All responses include clickable source URLs for verification
- **Modern UI**: Clean, Groww-inspired Streamlit interface with chat bubbles
- **Real-time Data**: Answers based on scraped data from official SBI Mutual Fund website

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/harikrshm/Groww_FAQ-Chatbot.git
   cd Groww_FAQ-Chatbot
   ```

2. **Set up virtual environment** (Python 3.9-3.12 recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Groq API (for Llama LLM)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.1-8b-instant
   
   # Pinecone (Vector Database)
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=ragchatbot
   
   # Embedding Model (optional - defaults to sentence-transformers/all-MiniLM-L6-v2)
   EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will be available at `http://localhost:8501`

## 📚 Detailed Documentation

- **[SETUP.md](SETUP.md)** - Comprehensive setup instructions, API key configuration
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide for Streamlit Cloud

## 🧪 Testing

The project includes a comprehensive test suite covering all backend modules:

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_query_processor.py -v
pytest tests/test_retrieval.py -v
pytest tests/test_llm_service.py -v
```

**Test Coverage:**
- Query preprocessing and classification
- Retrieval system and vector search
- LLM response generation and validation
- Response formatting and error handling

## 🌐 Live Demo

**Deployed on Streamlit Cloud:** [https://growwfaq-chatbot.streamlit.app/]

Try asking:
- "What is the NAV of SBI Large Cap Fund?"
- "What is the exit load for SBI Multicap Fund?"
- "What is the minimum SIP for SBI Small Cap Fund?"

## 🏗️ Project Structure

```
Groww_FAQ-Chatbot/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration constants
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
│
├── backend/                    # Backend logic
│   ├── llm_service.py         # Groq/Llama LLM integration
│   ├── retrieval.py           # Pinecone vector database queries
│   ├── query_processor.py     # Query classification & preprocessing
│   ├── validators.py          # Response validation rules
│   └── formatter.py           # Response formatting
│
├── frontend/                   # Frontend components
│   ├── components/
│   │   ├── chat_ui.py         # Chat interface with message bubbles
│   │   ├── welcome.py         # Schemes list & sample queries
│   │   └── footer.py          # Disclaimer footer
│   └── styles.css             # Custom styling
│
├── scripts/                    # Utility scripts
│   ├── scrape_sbi_schemes.py  # Web scraper for SBI MF data
│   ├── process_documents.py   # Document chunking pipeline
│   └── upload_to_pinecone.py  # Vector database upload
│
├── tests/                      # Test suite
│   ├── test_query_processor.py
│   ├── test_retrieval.py
│   └── test_llm_service.py
│
└── data/                       # Data storage
    ├── raw/                    # Scraped data (JSON)
    └── processed/              # Processed chunks
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Llama 3.1 8B Instant (via Groq) | Response generation |
| **Vector DB** | Pinecone | Semantic search & retrieval |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Text vectorization |
| **Frontend** | Streamlit | Web interface |
| **Web Scraping** | BeautifulSoup4, Selenium | Data extraction |
| **Testing** | pytest | Automated testing |

## 🔑 API Keys Required

1. **Groq API Key** (Free tier available)
   - Get it here: [https://console.groq.com](https://console.groq.com)
   - Used for: Llama 3.1 8B Instant model access
   - Free tier: Generous rate limits for testing

2. **Pinecone API Key** (Free tier available)
   - Get it here: [https://www.pinecone.io/](https://www.pinecone.io/)
   - Used for: Vector database storage and semantic search
   - Free tier: 1 index, 100K vectors

## 💡 How It Works

1. **User Query** → Query classification (factual, advice, non-MF, jailbreak)
2. **Query Expansion** → Add synonyms for better retrieval
3. **Vector Search** → Retrieve top-k relevant chunks from Pinecone
4. **Context Preparation** → Format retrieved chunks as context
5. **LLM Generation** → Llama 3.1 generates response using context
6. **Validation** → Check for advice, opinions, source citations
7. **Response** → Display formatted answer with source URL

## 🚨 Important Notes

- **Not Financial Advice**: This chatbot provides factual information only, not investment recommendations
- **Official Sources**: All data scraped from official SBI Mutual Fund and AMFI websites
- **Rate Limits**: Groq free tier has rate limits; consider paid plan for production
- **Python Version**: Tested on Python 3.9-3.12 (avoid 3.14 due to dependency issues)

## 📦 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard (TOML format):
   ```toml
   GROQ_API_KEY = "your_key"
   PINECONE_API_KEY = "your_key"
   PINECONE_INDEX_NAME = "ragchatbot"
   ```
5. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- SBI Mutual Fund terms of service when scraping
- Groq and Pinecone terms of service
- Financial advisory regulations in your jurisdiction

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ by Hari using Cursor, Llama 3.1, Pinecone, and Streamlit**
