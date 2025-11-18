# Phase 2.5: Safety Filter Analysis & Solution Strategy

## Current Problem
Factual queries (like "What is the expense ratio?") are being blocked by Gemini's safety filters, even with `BLOCK_NONE` settings. The current fallback strategy of using chunk data is not working well.

## Key Insights from Gemini Safety Settings Documentation

### 1. Safety Filter Categories
- **Harassment**: Negative/harmful comments targeting identity
- **Hate Speech**: Rude, disrespectful, or profane content
- **Sexually Explicit**: References to sexual acts
- **Dangerous**: Promotes harmful acts
- **Civic Integrity**: Election-related queries

### 2. Block Thresholds (from most to least restrictive)
- `BLOCK_LOW_AND_ABOVE`: Blocks low, medium, or high probability
- `BLOCK_MEDIUM_AND_ABOVE`: Blocks medium or high probability (DEFAULT)
- `BLOCK_ONLY_HIGH`: Blocks only high probability
- `BLOCK_NONE`: Always show regardless of probability
- `OFF`: Turn off the safety filter

### 3. Important Findings
- **Default threshold**: `BLOCK_MEDIUM_AND_ABOVE` for most categories
- **Newer stable GA models** (like `gemini-2.0-flash`): Default is `BLOCK_NONE` for all categories except Civic Integrity
- **Blocking is probability-based, not severity-based**: Low probability content can still be blocked if threshold is too restrictive
- **Account-level settings**: There may be account-level safety settings that override request-level settings

### 4. Model-Specific Behavior
- `gemini-2.0-flash` and `gemini-2.0-flash-lite`: Default `BLOCK_NONE` for all categories (except Civic Integrity)
- Other models: Default `BLOCK_MEDIUM_AND_ABOVE`
- Current model: `gemini-2.5-flash` (may not be a valid model name - should verify)

## Current Implementation Analysis

### Current Safety Settings
```python
# In llm_service.py, line 170-187
safety_settings_override = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_NONE,
    },
    # ... all set to BLOCK_NONE
]
```

### Issues Identified
1. **Model name**: Using `gemini-2.5-flash` which may not exist. Should use `gemini-2.0-flash` or `gemini-1.5-flash`
2. **Account-level overrides**: Even with `BLOCK_NONE`, account-level settings may still block
3. **Fallback strategy**: Using chunk data as fallback is not ideal - should remove per user request
4. **Prompt engineering**: Current alternative prompt strategy may not be effective enough

## Proposed Solutions

### Solution 1: Use Correct Model Name
- Change from `gemini-2.5-flash` to `gemini-2.0-flash` (newer, defaults to BLOCK_NONE)
- Or use `gemini-1.5-flash` (stable, well-tested)

### Solution 2: Enhanced Safety Settings Strategy
- Use `BLOCK_ONLY_HIGH` instead of `BLOCK_NONE` (more balanced)
- This blocks only high-probability unsafe content while allowing factual financial terms
- If still blocked, try `BLOCK_NONE` as fallback

### Solution 3: Improved Prompt Engineering
- Frame queries as "information requests" rather than direct questions
- Use educational/instructional framing
- Emphasize "factual data" and "official sources" in prompts

### Solution 4: Remove Chunk Data Fallback
- Remove the fallback that uses raw chunk data
- Instead, provide a helpful error message directing users to official sources
- This is cleaner and more transparent

### Solution 5: Query Preprocessing
- Preprocess queries to use more neutral language before sending to LLM
- Replace potentially triggering terms with safer alternatives
- Example: "expense ratio" → "cost structure information"

## Recommended Implementation Strategy

1. **Change model to `gemini-2.0-flash`** (has better default safety settings)
2. **Use `BLOCK_ONLY_HIGH` as primary threshold** (more balanced than BLOCK_NONE)
3. **Remove chunk data fallback** from app.py
4. **Enhance prompt engineering** with better framing
5. **Add query preprocessing** to use neutral language
6. **Implement progressive fallback**: Try BLOCK_ONLY_HIGH first, then BLOCK_NONE if needed

