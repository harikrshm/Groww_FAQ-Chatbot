# Investigation Plan: Factual Answer Generation Issues

## Problem Statement

Not all factual queries are generating answers. Need to deep dive into why.

## Investigation Approach

### Phase 1: Data Collection

1. **Create Test Suite:**
   - Test all factual query types
   - Test queries for each scheme
   - Document which queries work and which fail

2. **Add Detailed Logging:**
   - Log at each step of the pipeline
   - Log retrieved chunks
   - Log context preparation
   - Log LLM requests/responses
   - Log validation results

### Phase 2: Root Cause Analysis

#### 2.1 Check Context Retrieval

**Questions to Answer:**
- Are chunks being retrieved from Pinecone?
- Do retrieved chunks contain the answer?
- Is the scheme name filtering too restrictive?
- Are chunks being ranked correctly?

**Test:**
```python
# Test retrieval for failing queries
query = "What is the expense ratio of SBI Large Cap Fund?"
chunks = retrieval_system.retrieve(query, top_k=3, scheme_name="SBI Large Cap Fund")
# Check if chunks contain expense ratio information
```

#### 2.2 Check Context Preparation

**Questions to Answer:**
- Is context being truncated too aggressively?
- Are source URLs being extracted correctly?
- Is the context length appropriate?

**Test:**
```python
# Check context preparation
context_dict = retrieval_system.prepare_context(chunks, max_chunks=3, max_context_tokens=800)
# Verify context contains answer
# Verify source URLs are extracted
```

#### 2.3 Check LLM Generation

**Questions to Answer:**
- Are LLM API calls successful?
- Are responses being generated?
- Are responses being filtered out by validation?
- Is token limit causing issues?

**Test:**
```python
# Test LLM generation directly
response = llm_service.generate_response(system_prompt, user_prompt)
# Check if response is generated
# Check if response contains answer
```

#### 2.4 Check Validation

**Questions to Answer:**
- Is validation too strict?
- Are valid responses being rejected?
- Is response fixing working correctly?

**Test:**
```python
# Test validation
validated_response, validation_result = validate_and_fix_response(response, source_url)
# Check validation results
# Check if fixes are applied correctly
```

### Phase 3: Specific Issues to Check

#### Issue 1: Source URL Extraction

**Problem:** `prepare_context()` shows 0 source URLs even when chunks have URLs

**Check:**
- `backend/retrieval.py` - `prepare_context()` method
- Verify source URL extraction logic
- Check if source URLs are in chunk metadata

**Fix:**
- Debug source URL extraction
- Ensure source URLs are properly extracted from chunks
- Verify source URLs are included in context_dict

#### Issue 2: Context Truncation

**Problem:** Context may be truncated too aggressively, removing important information

**Check:**
- Current max_context_tokens: 800
- Verify if this is sufficient
- Check if truncation is removing answer information

**Fix:**
- Test with different token limits
- Adjust truncation logic if needed
- Ensure truncation doesn't cut off mid-sentence

#### Issue 3: Scheme Name Filtering

**Problem:** Scheme name filtering may be too restrictive

**Check:**
- Verify scheme name matching logic
- Check if scheme names are being extracted correctly
- Test with and without scheme filtering

**Fix:**
- Relax scheme name matching if too strict
- Improve scheme name extraction
- Add fallback if scheme not found

#### Issue 4: Validation False Positives

**Problem:** Valid responses may be rejected by validation

**Check:**
- Review validation rules
- Check if validation is too strict
- Verify response fixing logic

**Fix:**
- Adjust validation rules if needed
- Improve response fixing
- Add better error handling

### Phase 4: Testing Plan

1. **Create Comprehensive Test Script:**
   - Test all factual query types
   - Test for each scheme
   - Log results at each step

2. **Test Specific Queries:**
   - "What is the expense ratio of SBI Large Cap Fund?"
   - "What is the exit load for SBI Equity Hybrid Fund?"
   - "What is the minimum SIP for SBI Small Cap Fund?" (working)
   - Add more test queries

3. **Compare Working vs Non-Working:**
   - Identify patterns
   - Find common issues
   - Document differences

### Phase 5: Fixes

1. Fix source URL extraction
2. Fix context retrieval/preparation
3. Fix validation if needed
4. Add better error handling
5. Improve logging

### Phase 6: Verification

1. Re-test all queries
2. Verify source URLs work
3. Verify all factual queries generate answers
4. Test with new sample queries

---

## Files to Review

1. `backend/retrieval.py` - Context retrieval and preparation
2. `backend/llm_service.py` - LLM generation
3. `backend/validators.py` - Response validation
4. `app.py` - Query processing pipeline
5. `frontend/components/chat_ui.py` - Source URL display

---

## Debugging Tools

1. **Add Logging:**
   ```python
   logger.debug(f"Retrieved chunks: {len(chunks)}")
   logger.debug(f"Context length: {len(context)}")
   logger.debug(f"Source URLs: {source_urls}")
   ```

2. **Create Test Script:**
   - Test individual components
   - Test full pipeline
   - Compare working vs non-working queries

3. **Add Debug Endpoints:**
   - Show retrieved chunks
   - Show context
   - Show LLM response
   - Show validation results

---

## Expected Outcomes

1. Source URLs work correctly
2. All factual queries generate answers
3. Better understanding of why some queries fail
4. Improved error handling and logging
5. More reliable answer generation


