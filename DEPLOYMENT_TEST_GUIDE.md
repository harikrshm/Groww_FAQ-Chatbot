# Deployment Test Guide - Task 8.7

This guide covers testing the complete pipeline: scraping documents, processing them, uploading to Pinecone, and testing queries.

## Prerequisites

1. **Environment Setup**:
   - Python virtual environment activated
   - All dependencies installed (`pip install -r requirements.txt`)
   - `.env` file configured with:
     - `PINECONE_API_KEY`
     - `PINECONE_INDEX_NAME` (default: `ragchatbot`)
     - `GROQ_API_KEY`

2. **Required Scripts**:
   - `scripts/scrape_urls.py` - Web scraping
   - `scripts/process_documents.py` - Document processing
   - `scripts/upload_to_pinecone.py` - Pinecone upload

3. **Directory Structure**:
   ```
   data/
   ├── raw/
   │   └── scraped_data.json (will be created)
   └── processed/
       └── chunks.json (will be created)
   ```

## Step 1: Prepare Sample URLs

Create a list of SBI Mutual Fund scheme URLs to scrape. Example:

```python
# Example URLs (replace with actual SBI MF scheme pages)
SAMPLE_URLS = [
    "https://www.sbimf.com/en-us/products/schemes/sbi-large-cap-fund",
    "https://www.sbimf.com/en-us/products/schemes/sbi-small-cap-fund",
    "https://www.sbimf.com/en-us/products/schemes/sbi-multicap-fund",
    "https://www.sbimf.com/en-us/products/schemes/sbi-equity-hybrid-fund",
]
```

**Note**: Use actual SBI Mutual Fund scheme pages. You can find these on the official SBI MF website.

## Step 2: Scrape Documents

### Option A: Using scrape_urls.py

```bash
# Create a Python script to run scraping
python -c "
from scripts.scrape_urls import scrape_url
import json

urls = [
    'https://www.sbimf.com/en-us/products/schemes/sbi-large-cap-fund',
    # Add more URLs
]

results = []
for url in urls:
    print(f'Scraping: {url}')
    result = scrape_url(url)
    if result:
        results.append(result)
    time.sleep(2)  # Rate limiting

# Save to data/raw/scraped_data.json
import os
os.makedirs('data/raw', exist_ok=True)
with open('data/raw/scraped_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f'Saved {len(results)} documents')
"
```

### Option B: Using scrape_sbi_schemes.py (if available)

```bash
python scripts/scrape_sbi_schemes.py
```

**Expected Output**:
- `data/raw/scraped_data.json` created with scraped documents
- Each document should have: `url`, `title`, `content`, `scheme_name`, `document_type`

**Verification**:
```bash
# Check scraped data
python -c "
import json
with open('data/raw/scraped_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Total documents: {len(data)}')
for doc in data[:3]:
    print(f\"- {doc.get('title', 'No title')}: {len(doc.get('content', ''))} chars\")
"
```

## Step 3: Process Documents

Process scraped documents into chunks:

```bash
python scripts/process_documents.py
```

**Expected Output**:
- `data/processed/chunks.json` created with processed chunks
- Each chunk should have: `text`, `source_url`, `scheme_name`, `document_type`, `chunk_index`

**Verification**:
```bash
# Check processed chunks
python -c "
import json
with open('data/processed/chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)
print(f'Total chunks: {len(chunks)}')
print(f'Sample chunk: {chunks[0].get(\"text\", \"\")[:200]}...')
"
```

**Expected Statistics**:
- Multiple chunks per document (depending on document length)
- Chunks should be ~500-1000 tokens each
- Metadata preserved (source_url, scheme_name, etc.)

## Step 4: Upload to Pinecone

Upload processed chunks to Pinecone:

```bash
python scripts/upload_to_pinecone.py
```

**Expected Output**:
```
Loading chunks from data/processed/chunks.json...
Loaded X chunks
Initializing Pinecone...
Creating/connecting to index: ragchatbot
Loading embedding model...
Generating embeddings...
Uploading to Pinecone...
Uploaded batch 1/10...
...
UPLOAD SUMMARY
Total chunks: X
Successfully uploaded: X
Failed: 0
Index: ragchatbot
```

**Verification**:
1. Check Pinecone Dashboard:
   - Go to [Pinecone Dashboard](https://app.pinecone.io/)
   - Verify index exists and has vectors
   - Check vector count matches uploaded chunks

2. Test retrieval:
```bash
python -c "
from backend.retrieval import get_retrieval_system

retrieval = get_retrieval_system()
chunks = retrieval.retrieve(
    query='What is the expense ratio of SBI Large Cap Fund?',
    top_k=3,
    include_metadata=True
)
print(f'Retrieved {len(chunks)} chunks')
for i, chunk in enumerate(chunks, 1):
    print(f'{i}. {chunk.get(\"scheme_name\", \"Unknown\")}: {chunk.get(\"text\", \"\")[:100]}...')
"
```

## Step 5: Test Queries

Test the complete RAG pipeline with various queries:

### Test Script

Create `test_deployment_pipeline.py`:

```python
"""
Test complete RAG pipeline after deployment
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from app import process_query

# Test queries
test_queries = [
    # Factual queries
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the exit load for SBI Multicap Fund?",
    "What is the riskometer rating for SBI Equity Hybrid Fund?",
    
    # Advice queries (should be blocked)
    "Should I invest in SBI Large Cap Fund?",
    "What is the best mutual fund?",
    
    # Non-MF queries (should be handled)
    "What is the stock price of Reliance?",
]

print("="*80)
print("DEPLOYMENT PIPELINE TEST")
print("="*80)

llm_service = get_llm_service()
retrieval_system = get_retrieval_system()

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}/{len(test_queries)}: {query}")
    print(f"{'-'*80}")
    
    try:
        response = process_query(query, llm_service, retrieval_system)
        print(f"✅ Response: {response.get('answer', 'No answer')[:200]}...")
        print(f"Source: {response.get('source_url', 'No source')}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
```

Run the test:

```bash
python test_deployment_pipeline.py
```

## Step 6: Verify Results

### Checklist

- [ ] **Scraping**: Documents scraped successfully
  - [ ] `data/raw/scraped_data.json` exists
  - [ ] Documents have required fields (url, title, content, scheme_name)
  - [ ] Content is clean (no HTML tags, proper formatting)

- [ ] **Processing**: Documents processed into chunks
  - [ ] `data/processed/chunks.json` exists
  - [ ] Chunks have appropriate size (~500-1000 tokens)
  - [ ] Metadata preserved (source_url, scheme_name, document_type)

- [ ] **Upload**: Chunks uploaded to Pinecone
  - [ ] Upload completed without errors
  - [ ] Vector count in Pinecone matches chunk count
  - [ ] Index is accessible

- [ ] **Retrieval**: Retrieval system working
  - [ ] Can retrieve relevant chunks for queries
  - [ ] Source URLs are preserved
  - [ ] Chunks are relevant to queries

- [ ] **LLM**: Response generation working
  - [ ] Factual queries return responses
  - [ ] Responses include source citations
  - [ ] Advice queries are blocked
  - [ ] Non-MF queries are handled

- [ ] **End-to-End**: Complete pipeline working
  - [ ] User query → Retrieval → LLM → Response
  - [ ] Responses are accurate and relevant
  - [ ] Source URLs are clickable
  - [ ] Error handling works

## Troubleshooting

### Issue: Scraping fails

**Symptoms**: No documents scraped, errors in logs

**Solutions**:
- Check internet connection
- Verify URLs are accessible
- Check robots.txt compliance
- Increase rate limiting delays
- Verify Selenium/ChromeDriver setup (if using Selenium)

### Issue: Processing fails

**Symptoms**: No chunks created, errors in logs

**Solutions**:
- Verify `data/raw/scraped_data.json` exists
- Check JSON format is valid
- Verify documents have `content` field
- Check chunk size settings in `config.py`

### Issue: Upload fails

**Symptoms**: Upload errors, vectors not in Pinecone

**Solutions**:
- Verify `PINECONE_API_KEY` is correct
- Check `PINECONE_INDEX_NAME` matches existing index
- Verify index dimension matches embedding dimension (384)
- Check Pinecone quota/limits
- Verify embedding model loads correctly

### Issue: Retrieval returns no results

**Symptoms**: Empty chunks list, no relevant results

**Solutions**:
- Verify vectors are in Pinecone (check dashboard)
- Check query embedding generation
- Verify index name is correct
- Test with simpler queries
- Check if scheme_name filtering is too restrictive

### Issue: LLM responses are poor

**Symptoms**: Irrelevant responses, missing information

**Solutions**:
- Verify context chunks are relevant
- Check system prompt is correct
- Verify LLM API key is valid
- Check token limits (context truncation)
- Test with different queries

## Next Steps

After completing this test:

1. **Task 8.11**: Deploy to Streamlit Cloud
2. **Task 8.13**: Test deployed application
3. **Documentation**: Update README with deployment steps

## Notes

- This is a **one-time setup** for initial data population
- Re-run scraping/processing only when:
  - New schemes are added
  - Documents are updated
  - Data needs refreshing
- Pinecone upload can be incremental (new chunks added to existing index)
- Monitor API usage (Groq, Pinecone) during testing

