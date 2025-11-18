# Groww FAQ Chatbot

A small FAQ assistant that answers facts about mutual fund schemes—e.g., expense ratio, exit load, minimum SIP, lock-in (ELSS), riskometer, benchmark, and how to download statements—using only official public pages.

## Features

- **Factual Information Only**: Provides factual answers about mutual fund schemes
- **RAG-based**: Uses Retrieval Augmented Generation with Pinecone vector database
- **Gemini LLM**: Powered by Google Gemini for response generation
- **Query Classification**: Automatically detects and blocks investment advice requests
- **Source Citations**: All responses include source URLs
- **Modern UI**: Groww-inspired Streamlit interface

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Groww_FAQ-Chatbot
   ```

2. **Set up virtual environment**
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
   - Create `.env` file in project root
   - Add your API keys (see `SETUP.md` for details)
   ```env
   GEMINI_API_KEY=your_key_here
   PINECONE_API_KEY=your_key_here
   PINECONE_INDEX_NAME=ragchatbot
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Detailed Setup

See [SETUP.md](SETUP.md) for comprehensive setup instructions.

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

See [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) for comprehensive manual testing checklist.

## Deployment

### Streamlit Cloud Deployment

1. Push code to GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set environment variables in Streamlit Cloud secrets:
   - `GEMINI_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME`
5. Deploy!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Environment Variables

Required environment variables:
- `GEMINI_API_KEY` - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)
- `PINECONE_API_KEY` - Get from [Pinecone](https://www.pinecone.io/)
- `PINECONE_INDEX_NAME` - Your Pinecone index name (default: `ragchatbot`)

Optional:
- `GEMINI_MODEL` - Model to use (default: `gemini-2.5-flash`)

**Note**: Gemini API is cloud-based, no separate server needed. Just set the API key!

## Project Structure

- `app.py` - Main Streamlit application
- `backend/` - Backend modules (LLM, retrieval, query processing)
- `frontend/` - Frontend components and styling
- `tests/` - Comprehensive test suite (91 tests)
- `scripts/` - Utility scripts for data processing

## Requirements

- Python 3.8+
- Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- Pinecone API key ([Get it here](https://www.pinecone.io/))

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]
