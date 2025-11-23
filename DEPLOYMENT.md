# Deployment Guide - Streamlit Cloud

This guide covers deployment of the Groww Mutual Fund FAQ Chatbot on Streamlit Cloud.

## 📋 Prerequisites

- ✅ GitHub repository with code pushed
- ✅ Streamlit Cloud account ([free tier available](https://streamlit.io/cloud))
- ✅ Valid Groq API key ([get here](https://console.groq.com))
- ✅ Valid Pinecone API key ([get here](https://www.pinecone.io/))

## 🔑 Environment Variables

The following environment variables must be configured in Streamlit Cloud Secrets:

### Required Variables

| Variable | Description | Where to Get | Example |
|----------|-------------|--------------|---------|
| `GROQ_API_KEY` | Groq API key for Llama 3.1 8B Instant | [Groq Console](https://console.groq.com/keys) | `gsk_...` |
| `PINECONE_API_KEY` | Pinecone API key for vector database | [Pinecone Dashboard](https://app.pinecone.io/) | `pcsk_...` |
| `PINECONE_INDEX_NAME` | Name of your Pinecone index | Your Pinecone project | `ragchatbot` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_MODEL` | Llama model to use | `llama-3.1-8b-instant` |
| `EMBEDDING_MODEL_NAME` | Sentence transformer model | `sentence-transformers/all-MiniLM-L6-v2` |

## 🚀 Streamlit Cloud Deployment Steps

### Step 1: Prepare Repository

1. **Ensure all code is pushed to GitHub main branch**
   ```bash
   git status
   git add .
   git commit -m "Final deployment preparation"
   git push origin main
   ```

2. **Verify required files exist**:
   - ✅ `app.py` (entry point)
   - ✅ `requirements.txt` (dependencies)
   - ✅ `config.py` (configuration)
   - ✅ `.streamlit/config.toml` (optional theme config)

3. **Double-check `.gitignore`**:
   - ✅ `.env` is ignored (never commit API keys!)
   - ✅ `__pycache__/` is ignored
   - ✅ `*.pyc` is ignored

### Step 2: Deploy on Streamlit Cloud

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **"Sign in"** with your GitHub account
3. Click **"New app"** button
4. Configure deployment:
   - **Repository:** Select `Groww_FAQ-Chatbot`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Choose a custom name (e.g., `groww-mf-chatbot`)

### Step 3: Configure Secrets (TOML Format)

Streamlit Cloud uses TOML format for secrets. Click **"Advanced settings"** → **"Secrets"** and add:

```toml
# Groq API Configuration (for Llama LLM)
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
GROQ_MODEL = "llama-3.1-8b-instant"

# Pinecone Configuration (Vector Database)
PINECONE_API_KEY = "pcsk_your_actual_pinecone_api_key_here"
PINECONE_INDEX_NAME = "ragchatbot"

# Embedding Model (optional)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
```

**Important Notes:**
- Use actual values (remove placeholders)
- TOML format: `KEY = "value"` (not `KEY=value`)
- Changes take ~1 minute to propagate

### Step 4: Deploy & Verify

1. Click **"Deploy!"** button
2. Wait for deployment (usually 2-5 minutes)
3. Check deployment logs for errors
4. Your app will be live at: `https://your-app-name.streamlit.app`

## ✅ Post-Deployment Verification

### 1. Basic Functionality Tests

- [ ] App loads without errors
- [ ] Title and header display correctly
- [ ] Left column shows "Available Schemes" (5 schemes)
- [ ] Left column shows "Sample Query" (3 example buttons)
- [ ] Right column shows welcome message
- [ ] Input box appears below chat area

### 2. Query Processing Tests

Try these test queries:

| Query | Expected Result |
|-------|----------------|
| "What is the NAV of SBI Large Cap Fund?" | Returns NAV value with source URL |
| "What is the exit load for SBI Multicap Fund?" | Returns exit load details |
| "What is the minimum SIP for SBI Small Cap Fund?" | Returns minimum SIP amount |
| "Should I invest in SBI funds?" | Blocks with advice warning |
| "What is bitcoin?" | Blocks with non-MF warning |

### 3. UI/UX Tests

- [ ] User messages appear right-aligned (green)
- [ ] Bot messages appear left-aligned (white with green border)
- [ ] Source URLs are clickable purple badges
- [ ] Input box has green styling
- [ ] Loading indicator shows "Thinking..."
- [ ] Chat scrolls automatically

### 4. Error Handling Tests

- [ ] Empty query handled gracefully
- [ ] Invalid scheme name returns fallback
- [ ] API failures show error message (not crash)

## 🐛 Troubleshooting

### Deployment Fails

**Issue:** "Could not find a version that satisfies the requirement torch==2.0.1"
- **Fix:** Update `requirements.txt` with compatible versions for Python 3.11+:
  ```txt
  sentence-transformers>=3.0.0
  torch>=2.5.0
  ```

**Issue:** "ModuleNotFoundError: No module named 'backend'"
- **Fix:** Ensure directory structure is correct
- **Fix:** Add `__init__.py` to backend/ folder

**Issue:** "No such file or directory: 'frontend/styles.css'"
- **Fix:** Verify file paths are correct
- **Fix:** Check capitalization (case-sensitive on Linux servers)

### API Key Errors

**Issue:** "GROQ_API_KEY not found in environment variables"
- **Fix:** Check secrets are added in Streamlit Cloud dashboard
- **Fix:** Verify TOML format is correct: `KEY = "value"`
- **Fix:** Click "Reboot app" after adding secrets

**Issue:** "401 Unauthorized" from Groq API
- **Fix:** Regenerate API key in Groq Console
- **Fix:** Update secret in Streamlit Cloud
- **Fix:** Ensure key hasn't expired

**Issue:** "PINECONE_API_KEY not found"
- **Fix:** Verify API key is added to secrets
- **Fix:** Check index name matches your Pinecone project
- **Fix:** Ensure index is active (not paused)

### Performance Issues

**Issue:** Slow response times (>10 seconds)
- **Cause:** Cold start (first query after idle)
- **Fix:** Normal behavior - subsequent queries will be faster
- **Optimization:** Already implemented (token limits, top-k=3)

**Issue:** "Cannot copy out of meta tensor" error
- **Cause:** PyTorch compatibility issue
- **Fix:** Already fixed with `device='cpu'` in `retrieval.py`
- **Fix:** Ensure `requirements.txt` has correct versions

**Issue:** Rate limit errors from Groq
- **Symptom:** "Rate limit exceeded" message
- **Cause:** Free tier: 6,000 tokens/minute
- **Fix:** Wait 60 seconds
- **Fix:** Consider Groq paid tier for production

## 🔒 Security Best Practices

1. **API Keys**
   - ❌ Never commit `.env` to Git
   - ✅ Use Streamlit Cloud secrets only
   - ✅ Rotate keys every 3-6 months
   - ✅ Revoke old keys immediately

2. **Access Control**
   - ✅ Keep repo private if handling sensitive data
   - ✅ Limit collaborator access
   - ✅ Use read-only API keys where possible

3. **Monitoring**
   - ✅ Check Streamlit logs regularly
   - ✅ Monitor Groq API usage
   - ✅ Track Pinecone query volume
   - ✅ Set up alerts for quota limits

## 💰 Cost Considerations

### Groq API (Llama 3.1 8B Instant)
- **Free Tier:** 6,000 tokens/minute, 14,400 requests/day
- **Our Usage:** ~965 tokens per query (optimized)
- **Capacity:** ~370 queries/hour on free tier
- **Paid Tier:** Available for higher volume

### Pinecone (Vector Database)
- **Free Tier:** 1 index, 100K vectors, limited queries
- **Our Usage:** <10K vectors (SBI MF data)
- **Queries:** Fast (<100ms response time)
- **Paid Tier:** Starts at $70/month for more indexes

### Streamlit Cloud
- **Free Tier:** Public apps only, community resources
- **Limitations:** App sleeps after inactivity
- **Paid Tier:** $20/month per private app

### Total Cost (Free Tier)
- ✅ **$0/month** for testing and low-volume production!

## 🔧 Maintenance

### Regular Updates

**Monthly:**
- Update dependencies: `pip list --outdated`
- Check for security patches
- Review API changelog

**Quarterly:**
- Rotate API keys
- Review usage patterns
- Optimize token usage

**Annually:**
- Audit permissions
- Review architecture
- Consider scaling options

### Monitoring Checklist

- [ ] Check Streamlit app health
- [ ] Monitor Groq API usage
- [ ] Monitor Pinecone query volume
- [ ] Review error logs
- [ ] Test example queries
- [ ] Verify source URLs still valid

## 📚 Support Resources

- **Streamlit:** [docs.streamlit.io](https://docs.streamlit.io/)
- **Groq:** [console.groq.com/docs](https://console.groq.com/docs)
- **Pinecone:** [docs.pinecone.io](https://docs.pinecone.io/)
- **GitHub Issues:** [Your Repository Issues]

## 🎉 Success!

Your chatbot is now live! Share the URL and start answering mutual fund questions!

**Live URL:** `https://your-app-name.streamlit.app`

Test it with: "What is the NAV of SBI Large Cap Fund?"
