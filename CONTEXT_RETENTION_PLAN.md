# Context Retention Implementation Plan

## Overview

Add conversation context retention so the chatbot can use previous messages in the session to answer follow-up questions.

## Current State

- Chat history is stored in `st.session_state.chat_history`
- Each query is processed independently
- No conversation context is used when generating responses

## Implementation Strategy

### Phase 1: Update LLM Service

**File:** `backend/llm_service.py`

**Changes:**
1. Modify `generate_response()` to accept conversation history
2. Format chat history for Groq API (messages format)
3. Include conversation history in API call
4. Manage token limits for conversation history

**New Method Signature:**
```python
def generate_response(
    self,
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[List[Dict]] = None,  # New parameter
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_output_tokens: Optional[int] = None
) -> Optional[str]:
```

**Conversation History Format:**
```python
conversation_history = [
    {"role": "user", "content": "What is the expense ratio of SBI Large Cap Fund?"},
    {"role": "assistant", "content": "The expense ratio is 1.48%..."},
    {"role": "user", "content": "What about the minimum SIP?"}
]
```

**Groq API Format:**
```python
messages = [
    {"role": "system", "content": system_prompt},
    *conversation_history,  # Include previous messages
    {"role": "user", "content": user_prompt}  # Current query
]
```

### Phase 2: Context Window Management

**Strategy:**
- Include last N messages (suggest: 3-5 messages)
- Calculate token usage for conversation history
- Truncate if exceeds token budget
- Reserve tokens for current query and response

**Configuration:**
```python
# In config.py
CONTEXT_RETENTION_CONFIG = {
    "max_history_messages": 5,  # Last 5 messages
    "max_history_tokens": 500,  # Max tokens for history
    "include_full_conversation": True,  # Include both user and bot messages
}
```

**Token Management:**
- Current query: ~900 tokens
- Response: ~100 tokens
- Available for history: ~500 tokens (from 6000 TPM budget)
- Keep most recent messages that fit

### Phase 3: Update Query Processing

**File:** `app.py`

**Changes:**
1. Extract conversation history from session state
2. Format history for LLM service
3. Pass history to `generate_validated_response()`
4. Update `generate_validated_response()` to pass history to `generate_response()`

**History Extraction:**
```python
def get_conversation_history(max_messages: int = 5) -> List[Dict]:
    """Extract conversation history from session state"""
    if 'chat_history' not in st.session_state:
        return []
    
    history = st.session_state.chat_history[-max_messages:]
    formatted_history = []
    for msg in history:
        role = "user" if msg['role'] == 'user' else "assistant"
        formatted_history.append({
            "role": role,
            "content": msg['content']
        })
    return formatted_history
```

### Phase 4: Context Relevance

**Optional Enhancement:**
- Filter conversation history to include only relevant messages
- Use semantic similarity to select relevant context
- Include only messages related to current query

**Simple Approach (Initial):**
- Include last N messages (chronological)
- Let LLM determine relevance

**Advanced Approach (Future):**
- Use embeddings to find relevant previous messages
- Include only semantically similar messages
- More efficient token usage

## Implementation Steps

### Step 1: Update Config

Add context retention configuration to `config.py`:
```python
CONTEXT_RETENTION_CONFIG = {
    "max_history_messages": 5,
    "max_history_tokens": 500,
    "enabled": True,
}
```

### Step 2: Update LLM Service

1. Add `conversation_history` parameter to `generate_response()`
2. Format messages for Groq API
3. Include history in API call
4. Add token management for history

### Step 3: Update App.py

1. Create `get_conversation_history()` function
2. Extract history in `process_query()`
3. Pass history to LLM service
4. Update `generate_validated_response()` to accept and pass history

### Step 4: Testing

1. Test with follow-up questions
2. Verify context is used correctly
3. Test token limits
4. Verify performance

## Example Flow

**User Session:**
1. User: "What is the expense ratio of SBI Large Cap Fund?"
   - Bot: "The expense ratio is 1.48% for regular plans..."
   - History: [user_msg1, bot_msg1]

2. User: "What about the minimum SIP?"
   - Context: Previous message about SBI Large Cap Fund
   - Bot understands: "What is the minimum SIP for SBI Large Cap Fund?"
   - Bot: "The minimum SIP is ₹500..."
   - History: [user_msg1, bot_msg1, user_msg2, bot_msg2]

3. User: "And the exit load?"
   - Context: Still about SBI Large Cap Fund
   - Bot: "The exit load is..."
   - History: [user_msg1, bot_msg1, user_msg2, bot_msg2, user_msg3, bot_msg3]

## Token Budget Management

**Total Budget:** ~6000 tokens per minute (Groq free tier)

**Per Request Allocation:**
- System prompt: ~76 tokens
- Current user prompt: ~900 tokens
- Conversation history: ~500 tokens (max)
- Response: ~100 tokens
- **Total:** ~1576 tokens per request

**History Token Calculation:**
- Estimate: ~4 characters per token
- Last 5 messages: ~2000 characters = ~500 tokens
- Adjust based on actual usage

## Edge Cases

1. **First message in session:**
   - No history, process normally

2. **History exceeds token limit:**
   - Truncate to fit within budget
   - Keep most recent messages

3. **Topic change:**
   - Include recent history anyway
   - LLM can determine if context is relevant

4. **Very long conversation:**
   - Limit to last N messages
   - Consider summarization for older messages (future)

## Testing Plan

1. **Test Basic Context:**
   - Ask question about a fund
   - Ask follow-up without mentioning fund name
   - Verify bot uses context

2. **Test Token Limits:**
   - Long conversation
   - Verify history is truncated correctly
   - Verify no token limit errors

3. **Test Topic Changes:**
   - Ask about one fund
   - Ask about different fund
   - Verify context doesn't confuse

4. **Test Performance:**
   - Verify response times
   - Check token usage
   - Monitor API limits

## Files to Modify

1. `config.py` - Add context retention config
2. `backend/llm_service.py` - Add conversation history support
3. `app.py` - Extract and pass conversation history
4. `frontend/components/chat_ui.py` - (No changes needed, history already stored)

## Benefits

1. **Better UX:** Users can ask follow-up questions naturally
2. **More Natural:** Conversation flows better
3. **Efficient:** Users don't need to repeat information
4. **Smarter:** Bot understands context from previous messages

## Future Enhancements

1. **Context Summarization:** Summarize old messages to save tokens
2. **Semantic Context Selection:** Use embeddings to select relevant history
3. **Multi-turn Reasoning:** Support complex multi-step queries
4. **Context Persistence:** Save context across sessions (optional)


