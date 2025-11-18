# Gemini API Setup Instructions

## Task 6.1: Set Up Gemini API Key

### Step 1: Get Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the generated API key

### Step 2: Add API Key to .env File
1. Open or create `.env` file in the project root
2. Add the following line:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. Optionally, you can also set the model name:
   ```
   GEMINI_MODEL=gemini-1.5-flash
   ```
   (Default is `gemini-1.5-flash`. Other options: `gemini-2.0-flash-exp`, `gemini-1.5-pro`)

### Step 3: Install Dependencies
Make sure you have installed the required package:
```bash
pip install google-generativeai
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup
Test the LLM service:
```bash
python backend\llm_service.py
```

Or test with full retrieval and generation:
```bash
python test_llm_response.py
```

### Notes
- Gemini API is cloud-based, no local server needed
- API key is required for all requests
- Free tier has rate limits (check Google AI Studio for current limits)
- Model `gemini-1.5-flash` is fast and cost-effective for this use case

### Troubleshooting
- **"GEMINI_API_KEY not found"**: Make sure `.env` file exists and contains the API key
- **"Invalid API key"**: Verify the key is correct and hasn't been revoked
- **"Quota exceeded"**: Check your API usage limits in Google AI Studio
- **"google-generativeai not installed"**: Run `pip install google-generativeai`

