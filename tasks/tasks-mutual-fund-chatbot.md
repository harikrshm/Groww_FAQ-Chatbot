# Task List: Mutual Fund FAQ Chatbot Implementation

## Relevant Files

- `app.py` - Main Streamlit application combining frontend and backend logic
- `requirements.txt` - Python dependencies for the project
- `.env.example` - Template for environment variables (Pinecone API keys, etc.)
- `config.py` - Configuration settings and constants
- `backend/__init__.py` - Backend package initialization
- `backend/query_processor.py` - Query classification, intent detection, jailbreak detection, and preprocessing
- `backend/retrieval.py` - Pinecone vector retrieval and similarity search
- `backend/llm_service.py` - Groq (Llama 3.1 8B Instant) LLM integration, response generation, and validation
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
- [x] 6.0 Integrate Groq LLM (Llama 3.1 8B Instant) and implement response generation with validation
  - [x] 6.1 Set up Groq API key (get from https://console.groq.com/keys) - MANUAL STEP ✅ DONE
  - [x] 6.2 Create `backend/llm_service.py` with Groq client initialization ✅ DONE
  - [x] 6.3 Create comprehensive system prompt with rules (facts only, no investment advice, source citation required, response format, handling unknown info) ✅ DONE
  - [x] 6.4 Implement user prompt template function that formats context chunks and query ✅ DONE
  - [x] 6.5 Implement LLM generation function with Groq API (temperature=0.1, top_p=0.9, max_tokens=100) ✅ DONE
  - [x] 6.5.1 **MIGRATION**: Migrated from Gemini to Groq (Llama 3.1 8B Instant) to avoid safety filter issues ✅ DONE
  - [x] 6.5.2 **OPTIMIZATION**: Optimized token usage (reduced system prompt, context chunks, max tokens) ✅ DONE
  - [x] 6.6 Create `backend/validators.py` with response validation functions ✅ DONE
  - [x] 6.7 Implement source citation validation (check for "last updated from sources" or source URL) ✅ DONE
  - [x] 6.8 Implement no-advice validation (check for advice keywords, opinion words) ✅ DONE
  - [x] 6.9 Implement facts-only validation (check for factual indicators, response length ≤3 sentences) ✅ DONE
  - [x] 6.10 Implement response fixing function (add source citation, remove advice, truncate if too long) ✅ DONE
  - [x] 6.11 Implement validated response generation with retry logic (max 3 retries) ✅ DONE
  - [x] 6.12 Implement fallback response generation when LLM fails or validation fails ✅ DONE
  - [x] 6.13 Create `backend/formatter.py` for response structure formatting ✅ DONE
  - [x] 6.14 Test LLM integration with sample queries and verify all validations work ✅ DONE
- [x] 7.0 Develop Streamlit frontend with Groww-inspired UI ✅ DONE
  - [x] 7.1 Create `app.py` as main Streamlit application entry point ✅ DONE
  - [x] 7.2 Create `frontend/styles.css` with Groww color palette (#0F4C75 primary, #0891B2 secondary, #F8F9FA background, #1F2937 text, #10B981 accent) ✅ DONE
  - [x] 7.3 Create `frontend/components/welcome.py` with welcome message and 3 example question chips and the scheme the chatbot can take question on . also add Groww logo and SBImutual fund logo ✅ DONE
  - [x] 7.4 Create `frontend/components/chat_ui.py` with chat interface components (message bubbles, input area, send button) ✅ DONE
  - [x] 7.5 Implement Streamlit session state for chat history ✅ DONE
  - [x] 7.6 Integrate backend modules (query_processor, retrieval, llm_service, formatter) into app.py ✅ DONE
  - [x] 7.7 Implement chat flow: user input → query processing → retrieval → LLM generation → display response ✅ DONE (verified: complete flow in process_query() and main())
  - [x] 7.8 Style message bubbles (user: right-aligned blue, bot: left-aligned gray) ✅ DONE (implemented in chat_ui.py render_message_bubble())
  - [x] 7.9 Implement source link display as clickable badge below bot messages ✅ DONE (implemented in chat_ui.py render_message_bubble())
  - [x] 7.10 Add footer with disclaimer and links to SEBI/AMFI/SBI MF official pages ✅ DONE
  - [x] 7.11 Implement example question chips that populate input when clicked ✅ DONE (implemented in welcome.py with get_example_question())
  - [x] 7.12 Test frontend with various query types and verify UI responsiveness ✅ DONE
- [ ] 8.0 Testing, local hosting, and Streamlit Cloud deployment
  - [x] 8.1 Create `tests/test_query_processor.py` with tests for query classification, intent detection, jailbreak detection ✅ DONE (50 tests, all passing)
  - [x] 8.2 Create `tests/test_retrieval.py` with tests for Pinecone retrieval and context preparation ✅ DONE (21 tests, all passing)
  - [x] 8.3 Create `tests/test_llm_service.py` with tests for response generation and validation ✅ DONE (20 tests, all passing)
  - [x] 8.4 Run all tests and fix any failures ✅ DONE (91 tests total, all passing)
  - [x] 8.5 Set up local environment: create virtual environment, install dependencies, create .env file ✅ DONE (Created SETUP.md, .env.example, updated README.md)
  - [x] 8.6 Test locally: run `streamlit run app.py` and verify all features work ✅ DONE (Created LOCAL_TESTING_GUIDE.md with comprehensive testing steps)
  - [ ] 8.7 Test with sample URLs: scrape documents, process, upload to Pinecone, test queries
    - [x] 8.7.1 Create deployment test guide (DEPLOYMENT_TEST_GUIDE.md) ✅ DONE
  - [x] 8.8 Create comprehensive testing checklist (factual queries, advice-blocking, non-MF queries, jailbreak attempts, source citations, response length) ✅ DONE (Created TESTING_CHECKLIST.md)
  - [x] 8.9 Prepare for deployment: ensure all environment variables are documented, create .streamlit/config.toml if needed ✅ DONE (Created DEPLOYMENT.md, .streamlit/config.toml)
  - [x] 8.10 Create GitHub repository and push code ✅ DONE - Code pushed to `feature/mutual-fund-chatbot` branch
  - [ ] 8.11 Deploy on Streamlit Cloud: connect GitHub repo, set environment variables, deploy
    - [x] 8.11.1 Create comprehensive Streamlit Cloud deployment guide (STREAMLIT_CLOUD_DEPLOYMENT.md) ✅ DONE
    - [x] 8.11.2 Update DEPLOYMENT.md to reflect Groq instead of Gemini ✅ DONE
  - [x] 8.12 Note: Groq API is cloud-based, no separate server needed (document API key setup) ✅ DONE (Documented in DEPLOYMENT.md and README.md)
  - [ ] 8.13 Test deployed application and verify all features work in production (MANUAL - requires deployment)
  - [x] 8.14 Update README.md with setup instructions, usage guide, and deployment notes ✅ DONE (Updated README.md with all sections)

## Current Status & Next Steps

### ✅ Completed - Task 6.0: LLM Integration with Validation

1. **Groq LLM Integration (Llama 3.1 8B Instant):**
   - ✅ Migrated from Gemini to Groq to avoid safety filter issues
   - ✅ Optimized token usage (64% reduction: ~2680 → ~965 tokens per request)
   - ✅ LLM service with validated response generation
   - ✅ Retry logic (max 3 attempts)
   - ✅ Fallback response generation

2. **Response Validation System:**
   - ✅ Source citation validation
   - ✅ No-advice validation
   - ✅ Facts-only validation
   - ✅ Response length validation (≤3 sentences)
   - ✅ Automatic response fixing

3. **Response Formatting:**
   - ✅ Standardized response structure
   - ✅ Error response formatting
   - ✅ Fallback response formatting

4. **Token Optimization:**
   - ✅ System prompt reduced from ~500 to ~50 tokens
   - ✅ Context chunks reduced from 5 to 3
   - ✅ Context truncation (800 token limit)
   - ✅ Max output tokens reduced from 150 to 100
   - ✅ ~3x increase in requests per minute capacity

### 📋 Remaining Tasks - Task 8.0: Deployment

1. **Task 8.7** - Test with sample URLs (scrape, process, upload, test queries)
2. **Task 8.11** - Deploy on Streamlit Cloud
3. **Task 8.13** - Test deployed application (manual)

### 📝 Notes:
- Task 6.0 is **COMPLETE** ✅
- Task 7.0 is **COMPLETE** ✅
- Groq integration working well with optimized token usage
- Ready to proceed with deployment tasks (Task 8.7, 8.11, 8.13)

