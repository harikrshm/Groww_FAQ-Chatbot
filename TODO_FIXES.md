# TODO: Fixes and Improvements

## Issues Identified - To Fix Tomorrow

### 1. Source Citations Do Not Work ❌

**Problem:**
- Source URLs are not being displayed or are not clickable
- Source citations may not be properly extracted from chunks
- Source URL extraction in `prepare_context()` may be failing

**Files to Check:**
- `backend/retrieval.py` - `prepare_context()` method (source URL extraction)
- `frontend/components/chat_ui.py` - Source link rendering
- `app.py` - How source URLs are passed to frontend

**Investigation Steps:**
1. Check if `prepare_context()` is correctly extracting source URLs from chunks
2. Verify source URLs are being passed through the response pipeline
3. Test source link rendering in chat UI component
4. Check if source URLs are being stored in chat history correctly

**Expected Behavior:**
- Source URLs should be extracted from retrieved chunks
- Source URLs should be displayed as clickable badges below bot messages
- Source URLs should open in new tab when clicked

---

### 2. All Factual Answers Are Not Generated ❌

**Problem:**
- Some factual queries are not generating answers
- May be related to:
  - Context retrieval issues
  - LLM generation failures
  - Validation failures
  - Token limits or truncation

**Files to Check:**
- `backend/retrieval.py` - Context retrieval and chunk preparation
- `backend/llm_service.py` - Response generation
- `backend/validators.py` - Response validation
- `app.py` - Query processing pipeline

**Investigation Steps:**
1. **Check Context Retrieval:**
   - Verify chunks are being retrieved from Pinecone
   - Check if chunks contain relevant information
   - Test with different queries to see which ones fail

2. **Check LLM Generation:**
   - Verify Groq API calls are successful
   - Check for rate limiting issues
   - Review token usage and limits
   - Check if responses are being generated but then filtered out

3. **Check Validation:**
   - Review validation logic - may be too strict
   - Check if valid responses are being rejected
   - Verify response fixing logic

4. **Check Context Truncation:**
   - Verify context is not being truncated too aggressively
   - Check if 800 token limit is removing important information
   - Test with different context sizes

5. **Deep Dive Analysis:**
   - Add detailed logging at each step
   - Test with specific queries that are failing
   - Compare working vs non-working queries
   - Check if scheme name filtering is too restrictive

**Test Queries to Investigate:**
- "What is the expense ratio of SBI Large Cap Fund?" (failed in test)
- "What is the exit load for SBI Equity Hybrid Fund?" (failed in test)
- Other factual queries that may be failing

**Expected Behavior:**
- All factual queries should generate answers
- Answers should be accurate and from context
- Fallback responses should only be used when context is truly unavailable

---

### 3. Test and Add More Sample Queries ✅

**Problem:**
- Currently only 1 example query
- Need to test more queries to ensure they work
- Need to add more sample queries that have verified answers

**Tasks:**
1. **Test Existing Queries:**
   - Test all factual query types (expense ratio, exit load, minimum SIP, riskometer, benchmark, etc.)
   - Verify each query type works correctly
   - Document which queries work and which don't

2. **Find Working Queries:**
   - Test queries for each scheme
   - Identify queries that successfully retrieve and generate answers
   - Create a list of verified working queries

3. **Add More Sample Queries:**
   - Add 2-3 more example queries to welcome page
   - Ensure all example queries have pre-computed answers
   - Choose queries that cover different factual intents
   - Ensure queries work reliably

4. **Update Frontend:**
   - Update `frontend/components/welcome.py` to include more example questions
   - Add pre-computed answers for each new example query
   - Update UI to accommodate multiple example questions

**Suggested Additional Sample Queries (to test first):**
- "What is the riskometer rating for SBI Large Cap Fund?"
- "What is the benchmark for SBI Small Cap Fund?"
- "What is the minimum investment for SBI Equity Hybrid Fund?"
- "What is the lock-in period for SBI Equity Hybrid Fund?"

**Files to Update:**
- `frontend/components/welcome.py` - Add more example questions and answers
- `app.py` - Update example question handling if needed

---

### 4. Add Context Retention for User Sessions 🔄

**Problem:**
- Currently, each query is processed independently
- No conversation context is retained between queries
- User has to repeat information in follow-up questions

**Requirements:**
- Store conversation history for each user session
- Use previous conversation context when answering subsequent questions
- Include relevant chat history in LLM prompts
- Maintain context window limits (token management)

**Implementation Plan:**

1. **Update Chat History Storage:**
   - Already stored in `st.session_state.chat_history`
   - Need to format it for LLM context
   - Include user queries and bot responses

2. **Update LLM Service:**
   - Modify `generate_response()` to accept conversation history
   - Format chat history for LLM (system/user/assistant messages)
   - Include recent conversation context in prompts
   - Manage token limits (include only recent messages if needed)

3. **Update Query Processing:**
   - Pass chat history to LLM service
   - Include relevant context from previous messages
   - Filter/select relevant conversation history (last N messages)

4. **Context Window Management:**
   - Limit conversation history to fit within token budget
   - Keep most recent messages
   - Include summary of older messages if needed
   - Balance between context and current query tokens

**Files to Update:**
- `backend/llm_service.py` - Add conversation history support
- `app.py` - Pass chat history to LLM service
- `config.py` - Add context retention configuration (max history messages, token limits)

**Expected Behavior:**
- User asks: "What is the expense ratio of SBI Large Cap Fund?"
- Bot responds with answer
- User asks follow-up: "What about the minimum SIP?"
- Bot understands "minimum SIP" refers to SBI Large Cap Fund from context
- Bot provides answer using conversation context

**Considerations:**
- Token limits (Groq: 6000 TPM, need to reserve for current query)
- How many previous messages to include (suggest: last 3-5 messages)
- Whether to include only user queries or full conversation
- Context relevance filtering (only include relevant previous messages)

---

### 5. Fix Interface Dimming During Query Processing 🔄

**Problem:**
- Interface dims/freezes when query is being processed
- User cannot interact with the interface during processing
- Poor user experience - appears unresponsive

**Possible Causes:**
- Streamlit blocking behavior during processing
- No loading indicator or feedback
- Long processing times without user feedback
- Session state blocking UI updates

**Investigation Steps:**
1. Check if `st.rerun()` is being called unnecessarily
2. Verify loading indicators are displayed correctly
3. Check if processing is blocking the main thread
4. Review Streamlit session state management
5. Check if there are any blocking operations in the processing pipeline

**Files to Check:**
- `app.py` - Main processing loop and rerun logic
- `frontend/components/chat_ui.py` - Loading indicator rendering
- `frontend/components/welcome.py` - UI state during processing

**Potential Solutions:**
1. **Improve Loading Indicators:**
   - Ensure loading spinner is visible during processing
   - Add progress indicators if possible
   - Show "Processing..." message clearly

2. **Optimize Processing:**
   - Reduce processing time where possible
   - Use async operations if applicable
   - Optimize API calls

3. **Better State Management:**
   - Use `st.spinner()` context manager
   - Ensure UI remains responsive
   - Avoid unnecessary reruns

4. **User Feedback:**
   - Show clear processing status
   - Disable input during processing (but show why)
   - Provide visual feedback that system is working

**Expected Behavior:**
- Interface should remain visible and responsive
- Clear loading indicator during processing
- User should see progress/status updates
- No dimming or freezing

---

### 6. Add More Scraping URLs and Check for Specific Information 📊

**Problem:**
- Limited data in Pinecone index
- Some queries fail because information is not available
- Need more comprehensive data coverage
- Need to verify specific information is scraped correctly

**Requirements:**
1. **Add More URLs:**
   - Identify additional SBI Mutual Fund scheme pages
   - Add scheme detail pages for all available schemes
   - Include FAQ pages, fact sheets, and other relevant documents
   - Verify URLs are accessible and contain useful information

2. **Verify Information Coverage:**
   - Check if all factual information types are covered:
     - Expense ratios
     - Exit loads
     - Minimum SIP amounts
     - Lock-in periods
     - Riskometer ratings
     - Benchmarks
     - NAV information
     - AUM data
     - Fund manager information
   - Identify gaps in information coverage

3. **Quality Check:**
   - Verify scraped data contains required information
   - Check data accuracy
   - Ensure metadata is correctly extracted
   - Verify scheme names match correctly

**Tasks:**
1. **URL Collection:**
   - List all SBI Mutual Fund schemes
   - Find scheme detail pages for each
   - Identify additional relevant pages (FAQs, fact sheets, etc.)
   - Verify URLs are accessible

2. **Scraping:**
   - Run scraper for new URLs
   - Verify scraping is successful
   - Check data quality

3. **Processing:**
   - Process new scraped data
   - Verify chunks are created correctly
   - Check metadata extraction

4. **Upload to Pinecone:**
   - Upload new chunks to Pinecone
   - Verify upload is successful
   - Test retrieval with new data

5. **Verification:**
   - Test queries that previously failed
   - Verify information is now available
   - Check answer quality

**Files to Update:**
- `scripts/scrape_urls.py` - Add new URLs
- `scripts/scrape_sbi_schemes.py` - Update scheme URLs if needed
- `data/raw/scraped_data.json` - New scraped data
- `data/processed/chunks.json` - New processed chunks

**URLs to Add:**
- SBI Large Cap Fund detail page
- SBI Small Cap Fund detail page (verify current data)
- SBI Equity Hybrid Fund detail page
- SBI Multicap Fund detail page
- Additional scheme pages as needed
- FAQ pages
- Fact sheet pages

**Information to Verify:**
- Expense ratios for all schemes
- Exit loads for all schemes
- Minimum SIP amounts
- Lock-in periods
- Riskometer ratings
- Benchmarks
- Other factual information

**Expected Outcome:**
- More comprehensive data coverage
- All factual queries can be answered
- Better answer quality
- Reduced fallback responses

---

## Priority Order

1. **High Priority:** Fix source citations (affects user experience)
2. **High Priority:** Fix factual answer generation (core functionality)
3. **High Priority:** Add context retention for user sessions (improves UX significantly)
4. **High Priority:** Fix interface dimming during query processing (affects user experience)
5. **High Priority:** Add more scraping URLs and verify information coverage (core functionality)
6. **Medium Priority:** Add more sample queries (improves UX)

---

## Testing Checklist

After fixes, test:

- [ ] Source URLs are displayed correctly
- [ ] Source URLs are clickable and open in new tab
- [ ] All factual query types generate answers
- [ ] Example queries work correctly
- [ ] Pre-computed answers display correctly
- [ ] Chat history preserves source URLs
- [ ] Context retention works - follow-up questions use previous context
- [ ] Context retention respects token limits
- [ ] Interface does not dim/freeze during processing
- [ ] Loading indicators are visible and clear
- [ ] More URLs scraped and data uploaded to Pinecone
- [ ] All factual information types are covered in database
- [ ] Previously failing queries now work
- [ ] No errors in console/logs

---

## Notes

- Keep detailed logs during investigation
- Document any findings
- Test incrementally after each fix
- Verify fixes don't break existing functionality

