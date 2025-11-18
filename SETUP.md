# Setup Instructions for Mutual Fund FAQ Chatbot

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
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

## Step 4: Set Up Environment Variables

1. Create a `.env` file in the project root directory:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API keys:

   ```env
   # Gemini API Configuration
   # Get your API key from: https://aistudio.google.com/app/apikey
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   
   # Pinecone Configuration
   # Get your API key from: https://www.pinecone.io/
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX_NAME=ragchatbot
   ```

### Getting API Keys

#### Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the generated API key and paste it in `.env` file

#### Pinecone API Key
1. Visit [Pinecone](https://www.pinecone.io/)
2. Sign up for a free account
3. Create a new index (or use existing)
4. Copy your API key from the dashboard
5. Note your index name (default: `ragchatbot`)

## Step 5: Verify Setup

### Run Tests
```bash
pytest tests/ -v
```

All tests should pass (91 tests total).

### Test LLM Service
```bash
python -c "from backend.llm_service import get_llm_service; service = get_llm_service(); print('LLM Service initialized successfully')"
```

### Test Retrieval System
```bash
python -c "from backend.retrieval import get_retrieval_system; retrieval = get_retrieval_system(); print('Retrieval System initialized successfully')"
```

## Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Make sure `.env` file exists in the project root
   - Verify the API key is correctly set in `.env` file
   - Check that `python-dotenv` is installed

2. **"PINECONE_API_KEY not found"**
   - Verify Pinecone API key is set in `.env` file
   - Check that the index name matches your Pinecone index

3. **"Module not found" errors**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again

4. **Streamlit not found**
   - Install Streamlit: `pip install streamlit`
   - Or reinstall all dependencies: `pip install -r requirements.txt`

5. **Port already in use**
   - Streamlit uses port 8501 by default
   - Use a different port: `streamlit run app.py --server.port 8502`

## Project Structure

```
Groww_FAQ-Chatbot/
├── app.py                 # Main Streamlit application
├── backend/               # Backend modules
│   ├── llm_service.py    # LLM integration
│   ├── retrieval.py      # Pinecone retrieval
│   ├── query_processor.py # Query processing
│   ├── validators.py     # Response validation
│   └── formatter.py      # Response formatting
├── frontend/              # Frontend components
│   ├── components/        # UI components
│   └── styles.css        # Styling
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (create this)
```

## Next Steps

- See `INSTRUCTIONS_GEMINI_SETUP.md` for detailed Gemini API setup
- Check `tasks/tasks-mutual-fund-chatbot.md` for project progress
- Review test files in `tests/` directory for usage examples

