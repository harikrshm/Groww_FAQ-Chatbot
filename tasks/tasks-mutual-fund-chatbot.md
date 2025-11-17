# Task List: Mutual Fund FAQ Chatbot Implementation

## Relevant Files

- `app.py` - Main Streamlit application combining frontend and backend logic
- `requirements.txt` - Python dependencies for the project
- `.env.example` - Template for environment variables (Pinecone API keys, etc.)
- `config.py` - Configuration settings and constants
- `backend/__init__.py` - Backend package initialization
- `backend/query_processor.py` - Query classification, intent detection, jailbreak detection, and preprocessing
- `backend/retrieval.py` - Pinecone vector retrieval and similarity search
- `backend/llm_service.py` - Gemini LLM integration, response generation, and validation
- `backend/formatter.py` - Response formatting and structure
- `backend/validators.py` - Response validation (no advice, facts only, source citations)
- `scripts/scrape_urls.py` - BeautifulSoup web scraper for official URLs
- `scripts/process_documents.py` - Document chunking, preprocessing, and metadata extraction
- `scripts/upload_to_pinecone.py` - Embedding generation and Pinecone upload
- `data/raw/` - Directory for raw scraped HTML data
- `data/processed/` - Directory for processed document chunks
- `data/metadata.json` - Metadata about scraped documents
- `frontend/components/chat_ui.py` - Chat interface components (message bubbles, input area)
- `frontend/components/welcome.py` - Welcome section with example questions
- `frontend/styles.css` - Custom CSS for Groww-inspired styling
- `tests/test_query_processor.py` - Unit tests for query processing and classification
- `tests/test_retrieval.py` - Unit tests for retrieval system
- `tests/test_llm_service.py` - Unit tests for LLM service and validation

### Notes

- All Python files use `.py` extension
- Tests use pytest framework (`pip install pytest`)
- Run tests with `pytest tests/` or `python -m pytest tests/`
- Environment variables loaded via `python-dotenv` package
- Ensure `.env` file is created from `.env.example` before running

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [x] 0.0 Create feature branch
  - [x] 0.1 Create and checkout a new branch for this feature (e.g., `git checkout -b feature/mutual-fund-chatbot`)
- [x] 1.0 Set up project structure and dependencies
  - [x] 1.1 Create project directory structure (backend/, scripts/, data/, frontend/, tests/, tasks/)
  - [x] 1.2 Create `requirements.txt` with all dependencies (streamlit, beautifulsoup4, requests, sentence-transformers, pinecone-client, google-generativeai, python-dotenv, lxml, pytest)
  - [x] 1.3 Create `.env.example` file with template environment variables (PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME)
  - [x] 1.4 Create `config.py` with configuration constants (factual intents, advice keywords, jailbreak patterns, etc.)
  - [x] 1.5 Create `backend/__init__.py` to make backend a package
  - [x] 1.6 Create empty `data/raw/` and `data/processed/` directories
  - [x] 1.7 Initialize git repository if not already initialized
  
- [x] 2.0 Implement document collection system (Selenium + BeautifulSoup scraper for JavaScript-rendered pages)
  - [x] 2.1 Create `scripts/scrape_urls.py` with BeautifulSoup setup and URL validation functions
  - [x] 2.2 Implement robots.txt checking using urllib.robotparser
  - [x] 2.3 Implement rate limiting (1-2 second delays between requests) and user-agent header
  - [x] 2.4 Implement HTML content extraction (remove nav, footer, ads, preserve tables and lists)
  - [x] 2.5 Implement metadata extraction (page title, last modified date, breadcrumbs)
  - [x] 2.6 Implement error handling for 404/403/500/timeout/malformed HTML
  - [x] 2.7 Implement data structure to store scraped content with URL, title, content, scheme_name, document_type, scraped_date
  - [x] 2.8 Implement logging system for failed URLs
  - [x] 2.9 Create main scraping function that accepts list of URLs and saves to `data/raw/scraped_data.json`
  - [x] 2.10 Test scraper with sample URLs (Updated to use Selenium for JavaScript-rendered pages)

- [x] 3.0 Set up vector store (Pinecone) and embedding pipeline
  - [x] 3.1 Create Pinecone account and index (dimension: 384 for MiniLM, metric: cosine, type: serverless)
  - [x] 3.2 Create `scripts/process_documents.py` for document preprocessing
  - [x] 3.3 Implement text cleaning (remove HTML tags, normalize whitespace)
  - [x] 3.4 Implement document chunking (500-1000 tokens per chunk, 100-200 token overlap)
  - [x] 3.5 Implement metadata preservation (source_url, scheme_name, document_type, chunk_index)
  - [x] 3.6 Create `scripts/upload_to_pinecone.py` for embedding generation and upload
  - [x] 3.7 Implement embedding generation using sentence-transformers/all-MiniLM-L6-v2
  - [x] 3.8 Implement batch processing for embeddings (batch size: 32-64)
  - [x] 3.9 Implement Pinecone upsert with metadata (id, values, metadata fields)
  - [x] 3.10 Test embedding generation and Pinecone upload with sample documents
- [x] 4.0 Implement query processing and classification system
  - [x] 4.1 Create `backend/query_processor.py` with query preprocessing functions (normalize, trim, extract scheme name)
  - [x] 4.2 Implement factual intent detection with expanded keyword patterns (expense_ratio, exit_load, minimum_sip, lock_in, riskometer, benchmark, statement, nav, aum, fund_manager, investment_objective, scheme_details)
  - [x] 4.3 Implement non-MF query detection (stocks, FD, crypto, insurance, etc.) with fallback response
  - [x] 4.4 Implement jailbreak detection with patterns (instruction override, role-playing, system prompt injection, encoding tricks, unicode tricks)
  - [x] 4.5 Implement advice-seeking detection with expanded blocklist patterns (should i, recommend, best/worst, buy/sell, predictions, personalization, portfolio advice)
  - [x] 4.6 Implement query classification flow (non-MF → jailbreak → advice → factual → default)
  - [x] 4.7 Implement query expansion with synonyms for better retrieval
  - [x] 4.8 Create response templates for non-MF queries, jailbreak attempts, and advice queries
  - [x] 4.9 Test query classification with various query types
- [x] 5.0 Build retrieval system with Pinecone
  - [x] 5.1 Create `backend/retrieval.py` with Pinecone client initialization
  - [x] 5.2 Implement query embedding generation using same model (all-MiniLM-L6-v2)
  - [x] 5.3 Implement semantic search with Pinecone query (top_k=5, include_metadata=True)
  - [x] 5.4 Implement optional metadata filtering by scheme_name if detected in query
  - [x] 5.5 Implement optional re-ranking by semantic similarity, keyword match, document type priority
  - [x] 5.6 Implement context preparation (combine top-k chunks with source URLs)
  - [x] 5.7 Test retrieval with sample queries and verify source URLs are preserved
- [ ] 6.0 Integrate Gemini LLM and implement response generation with validation
  - [x] 6.1 Set up Gemini API key (get from https://aistudio.google.com/app/apikey) - MANUAL STEP ✅ DONE
  - [x] 6.2 Create `backend/llm_service.py` with Gemini client initialization ✅ DONE
  - [x] 6.3 Create comprehensive system prompt with rules (facts only, no investment advice, source citation required, response format, handling unknown info) ✅ DONE
  - [x] 6.4 Implement user prompt template function that formats context chunks and query ✅ DONE
  - [x] 6.5 Implement LLM generation function with Gemini API (temperature=0.1, top_p=0.9, max_output_tokens=150) ✅ DONE
  - [ ] 6.5.1 **BLOCKER**: Fix Gemini safety filter blocking all responses - check Google Cloud Console API settings, verify API key permissions, or try alternative model
  - [ ] 6.6 Create `backend/validators.py` with response validation functions
  - [ ] 6.7 Implement source citation validation (check for "last updated from sources" or source URL)
  - [ ] 6.8 Implement no-advice validation (check for advice keywords, opinion words)
  - [ ] 6.9 Implement facts-only validation (check for factual indicators, response length ≤3 sentences)
  - [ ] 6.10 Implement response fixing function (add source citation, remove advice, truncate if too long)
  - [ ] 6.11 Implement validated response generation with retry logic (max 3 retries)
  - [ ] 6.12 Implement fallback response generation when LLM fails or validation fails
  - [ ] 6.13 Create `backend/formatter.py` for response structure formatting
  - [ ] 6.14 Test LLM integration with sample queries and verify all validations work
- [ ] 7.0 Develop Streamlit frontend with Groww-inspired UI
  - [ ] 7.1 Create `app.py` as main Streamlit application entry point
  - [ ] 7.2 Create `frontend/styles.css` with Groww color palette (#0F4C75 primary, #0891B2 secondary, #F8F9FA background, #1F2937 text, #10B981 accent)
  - [ ] 7.3 Create `frontend/components/welcome.py` with welcome message and 3 example question chips
  - [ ] 7.4 Create `frontend/components/chat_ui.py` with chat interface components (message bubbles, input area, send button)
  - [ ] 7.5 Implement Streamlit session state for chat history
  - [ ] 7.6 Integrate backend modules (query_processor, retrieval, llm_service, formatter) into app.py
  - [ ] 7.7 Implement chat flow: user input → query processing → retrieval → LLM generation → display response
  - [ ] 7.8 Style message bubbles (user: right-aligned blue, bot: left-aligned gray)
  - [ ] 7.9 Implement source link display as clickable badge below bot messages
  - [ ] 7.10 Add footer with disclaimer and links to SEBI/AMFI/SBI MF official pages
  - [ ] 7.11 Implement example question chips that populate input when clicked
  - [ ] 7.12 Test frontend with various query types and verify UI responsiveness
- [ ] 8.0 Testing, local hosting, and Streamlit Cloud deployment
  - [ ] 8.1 Create `tests/test_query_processor.py` with tests for query classification, intent detection, jailbreak detection
  - [ ] 8.2 Create `tests/test_retrieval.py` with tests for Pinecone retrieval and context preparation
  - [ ] 8.3 Create `tests/test_llm_service.py` with tests for response generation and validation
  - [ ] 8.4 Run all tests and fix any failures
  - [ ] 8.5 Set up local environment: create virtual environment, install dependencies, create .env file
  - [ ] 8.6 Test locally: run `streamlit run app.py` and verify all features work
  - [ ] 8.7 Test with sample URLs: scrape documents, process, upload to Pinecone, test queries
  - [ ] 8.8 Create comprehensive testing checklist (factual queries, advice-blocking, non-MF queries, jailbreak attempts, source citations, response length)
  - [ ] 8.9 Prepare for deployment: ensure all environment variables are documented, create .streamlit/config.toml if needed
  - [x] 8.10 Create GitHub repository and push code ✅ DONE - Code pushed to `feature/mutual-fund-chatbot` branch
  - [ ] 8.11 Deploy on Streamlit Cloud: connect GitHub repo, set environment variables, deploy
  - [ ] 8.12 Note: Gemini API is cloud-based, no separate server needed (document API key setup)
  - [ ] 8.13 Test deployed application and verify all features work in production
  - [ ] 8.14 Update README.md with setup instructions, usage guide, and deployment notes

## Current Status & Tomorrow's Priorities

### ✅ Completed Today:
1. **Migration from Ollama to Google Gemini 2.5 Flash**
   - Updated `backend/llm_service.py` to use Gemini API
   - Configured safety settings (BLOCK_NONE for all categories)
   - Updated `config.py` with Gemini parameters
   - Updated `requirements.txt` (replaced `ollama` with `google-generativeai`)
   - Updated `.env.example` with `GEMINI_API_KEY`
   - Created `INSTRUCTIONS_GEMINI_SETUP.md`
   - Deleted Ollama-related files (`INSTRUCTIONS_OLLAMA_SETUP.md`, `setup_ollama_model.py`)
   - Updated task descriptions in `tasks/tasks-mutual-fund-chatbot.md`

2. **Testing Results:**
   - ✅ API key validation: Working
   - ✅ Model initialization: Working (model: `models/gemini-2.5-flash`)
   - ✅ Query processing: Working
   - ✅ Retrieval system: Working (retrieving chunks correctly)
   - ✅ Context preparation: Working
   - ❌ **LLM response generation: BLOCKED** - All responses blocked by Gemini safety filters (finish_reason: 2 = SAFETY)

3. **Git Commit & Push:**
   - ✅ All changes committed with message: "Migrate from Ollama to Google Gemini 2.5 Flash..."
   - ✅ Pushed to `feature/mutual-fund-chatbot` branch on GitHub

### 🚨 BLOCKER - Gemini Safety Filter Issue:
**Problem:** All prompts (including simple ones like "Hello", "What is 2+2?") are being blocked by Gemini's safety filters, even with `BLOCK_NONE` safety settings configured in code.

**Possible Causes:**
1. Account-level safety restrictions in Google Cloud Console
2. API key restrictions
3. Account verification/permission issues
4. Model-specific safety requirements

**Next Steps (Priority 1):**
1. Check Google Cloud Console → APIs & Services → Gemini API → Safety Settings
2. Verify API key doesn't have restrictive safety policies
3. Try creating a new API key from Google AI Studio
4. Test with alternative model (`gemini-1.5-pro` or `gemini-2.0-flash-exp`)
5. Check if account needs verification/approval for Generative AI APIs

### 📋 Tomorrow's Task List (In Order):

1. **Fix Gemini Safety Filter Issue (CRITICAL - Blocking Task 6.0)**
   - [ ] Research and resolve Gemini safety filter blocking responses
   - [ ] Verify API key permissions in Google Cloud Console
   - [ ] Test with alternative models if needed
   - [ ] Once resolved, retest `backend/llm_service.py` and `test_llm_response.py`

2. **Continue Task 6.0 - Response Validation & Formatting**
   - [ ] 6.6 Create `backend/validators.py` with response validation functions
   - [ ] 6.7 Implement source citation validation
   - [ ] 6.8 Implement no-advice validation
   - [ ] 6.9 Implement facts-only validation
   - [ ] 6.10 Implement response fixing function
   - [ ] 6.11 Implement validated response generation with retry logic
   - [ ] 6.12 Implement fallback response generation
   - [ ] 6.13 Create `backend/formatter.py` for response structure formatting
   - [ ] 6.14 Test LLM integration with sample queries and verify all validations work

3. **Task 7.0 - Build Streamlit Frontend** (Can proceed in parallel if Task 6.0 is partially done)
   - [ ] 7.1 Create `app.py` as main Streamlit application entry point
   - [ ] 7.2 Create `frontend/styles.css` with Groww color palette
   - [ ] Continue with remaining frontend tasks...

### 📝 Notes:
- All code changes have been committed and pushed to GitHub
- Branch: `feature/mutual-fund-chatbot`
- Repository: `harikrshm/Groww_FAQ-Chatbot`
- The Gemini API integration is complete, but responses are blocked by safety filters - this needs to be resolved before proceeding with validators and frontend development

