# Deployment Checklist

## Pre-Deployment Steps

### 1. Commit and Push Code

```bash
# Add all necessary files
git add app.py
git add requirements.txt
git add config.py
git add backend/
git add frontend/
git add .streamlit/
git add .gitignore
git add *.md

# Commit
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to GitHub
git push origin feature/mutual-fund-chatbot
```

### 2. Verify Required Files

- [x] `app.py` - Main Streamlit application
- [x] `requirements.txt` - All dependencies
- [x] `.streamlit/config.toml` - Streamlit configuration
- [x] `.gitignore` - Excludes .env files
- [x] `backend/` - All backend modules
- [x] `frontend/` - All frontend components

### 3. Environment Variables Needed

You'll need to set these in Streamlit Cloud Secrets:

1. **GROQ_API_KEY** - Your Groq API key
2. **PINECONE_API_KEY** - Your Pinecone API key  
3. **PINECONE_INDEX_NAME** - Your Pinecone index name (default: `ragchatbot`)

## Deployment Steps

### Step 1: Go to Streamlit Cloud
Visit: https://streamlit.io/cloud

### Step 2: Sign In
Sign in with your GitHub account

### Step 3: Deploy App
1. Click "New app"
2. Select your repository: `your-username/Groww_FAQ-Chatbot`
3. Select branch: `feature/mutual-fund-chatbot` (or `main`)
4. Main file: `app.py`
5. Click "Deploy"

### Step 4: Add Secrets
1. Click "⋮" → "Settings"
2. Go to "Secrets"
3. Add:
```toml
[secrets]
GROQ_API_KEY = "your_groq_key"
PINECONE_API_KEY = "your_pinecone_key"
PINECONE_INDEX_NAME = "ragchatbot"
```

### Step 5: Redeploy
Click "Redeploy" after adding secrets

## Post-Deployment Verification

- [ ] App loads without errors
- [ ] Chat interface displays correctly
- [ ] Can submit queries
- [ ] Responses are generated
- [ ] Source URLs work
- [ ] No errors in logs

## Your App URL
After deployment: `https://your-app-name.streamlit.app`

