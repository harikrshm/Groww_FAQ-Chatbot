# Quick Deployment Guide - Streamlit Cloud

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] GitHub account
- [ ] Code pushed to GitHub repository
- [ ] Groq API key from [Groq Console](https://console.groq.com/keys)
- [ ] Pinecone API key from [Pinecone Dashboard](https://app.pinecone.io/)
- [ ] Pinecone index created and populated with data

## Step 1: Verify Repository

Ensure your repository has:
- ✅ `app.py` in root directory
- ✅ `requirements.txt` with all dependencies
- ✅ `.gitignore` (to exclude .env files)
- ✅ All code committed and pushed to GitHub

## Step 2: Deploy to Streamlit Cloud

### 2.1 Create Streamlit Cloud Account

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Click **"Sign up"** or **"Get started"**
3. Sign in with your **GitHub account**
4. Authorize Streamlit Cloud to access your repositories

### 2.2 Deploy Your App

1. In Streamlit Cloud dashboard, click **"New app"**
2. Fill in the form:
   - **Repository**: Select `your-username/Groww_FAQ-Chatbot`
   - **Branch**: `main` or `feature/mutual-fund-chatbot`
   - **Main file path**: `app.py`
   - **App URL** (optional): `groww-mutual-fund-chatbot`
3. Click **"Deploy"**

**Note**: First deployment will fail because secrets aren't set yet. This is expected.

## Step 3: Configure Secrets

1. In your app dashboard, click **"⋮"** (three dots) → **"Settings"**
2. Scroll to **"Secrets"** section
3. Click **"Open secrets editor"**
4. Add these secrets:

```toml
[secrets]
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
PINECONE_INDEX_NAME = "ragchatbot"
```

5. Click **"Save"**

## Step 4: Redeploy

1. After saving secrets, click **"Redeploy"** or **"Save and redeploy"**
2. Wait for deployment to complete (2-5 minutes)
3. Check deployment logs for any errors

## Step 5: Verify Deployment

1. Access your app at: `https://your-app-name.streamlit.app`
2. Test with a sample query: "What is the expense ratio of SBI Large Cap Fund?"
3. Verify:
   - ✅ App loads without errors
   - ✅ Chat interface works
   - ✅ Queries return responses
   - ✅ Source URLs are clickable

## Troubleshooting

### App Won't Deploy

**Check**:
- `app.py` exists in root
- `requirements.txt` is correct
- All dependencies are listed
- Check deployment logs for specific errors

### "GROQ_API_KEY not found" Error

**Solution**:
- Verify secrets are saved in Streamlit Cloud
- Check key name is exactly `GROQ_API_KEY` (case-sensitive)
- Redeploy after adding secrets

### "PINECONE_API_KEY not found" Error

**Solution**:
- Verify Pinecone API key is correct
- Check `PINECONE_INDEX_NAME` matches your index
- Verify index exists in Pinecone dashboard

### Slow Response Times

**Check**:
- Groq API quota (6000 TPM free tier)
- Pinecone index performance
- Network latency

## Your App URL

After successful deployment, your app will be available at:
```
https://your-app-name.streamlit.app
```

## Next Steps

1. Test all features
2. Share the app URL
3. Monitor usage and performance
4. Update as needed

---

**Need Help?** Check `STREAMLIT_CLOUD_DEPLOYMENT.md` for detailed guide.

