# 🚀 Deploy to Streamlit Cloud - Quick Start

## ✅ Pre-Deployment Checklist

- [x] `.gitignore` created (excludes .env files)
- [x] `.streamlit/config.toml` created
- [x] `requirements.txt` verified
- [x] `app.py` ready
- [x] Code committed to git

## 📋 Next Steps

### Step 1: Push to GitHub

```bash
git push origin feature/mutual-fund-chatbot
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**: https://streamlit.io/cloud
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Fill in**:
   - Repository: `your-username/Groww_FAQ-Chatbot`
   - Branch: `feature/mutual-fund-chatbot` (or `main`)
   - Main file: `app.py`
   - App URL: `groww-mutual-fund-chatbot` (optional)
5. **Click "Deploy"**

### Step 3: Add Secrets

After first deployment (it will fail - that's expected):

1. Click **"⋮"** (three dots) → **"Settings"**
2. Scroll to **"Secrets"**
3. Click **"Open secrets editor"**
4. Add these secrets:

```toml
[secrets]
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
PINECONE_INDEX_NAME = "ragchatbot"
```

5. **Save** the secrets

### Step 4: Redeploy

1. Click **"Redeploy"** or **"Save and redeploy"**
2. Wait 2-5 minutes for deployment
3. Your app will be live at: `https://groww-mutual-fund-chatbot.streamlit.app`

## 🧪 Test Your Deployment

Once deployed, test with:
- Query: "What is the expense ratio of SBI Large Cap Fund?"
- Verify: Response is generated, source URL is clickable

## 📚 Detailed Guides

- **Quick Guide**: `QUICK_DEPLOYMENT_GUIDE.md`
- **Detailed Guide**: `STREAMLIT_CLOUD_DEPLOYMENT.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`

## ⚠️ Important Notes

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use Streamlit Cloud Secrets** for API keys (not .env)
3. **Verify Pinecone index** is populated before deploying
4. **Monitor API usage** (Groq: 6000 TPM free tier)

## 🆘 Troubleshooting

If deployment fails:
- Check deployment logs in Streamlit Cloud
- Verify all secrets are set correctly
- Ensure `requirements.txt` has all dependencies
- Check that `app.py` is in root directory

---

**Ready to deploy?** Push your code and follow the steps above! 🚀

