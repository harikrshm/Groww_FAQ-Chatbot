# Streamlit Cloud Deployment Guide - Task 8.11

Complete step-by-step guide for deploying the Mutual Fund FAQ Chatbot on Streamlit Cloud.

## Prerequisites Checklist

Before starting deployment, ensure:

- [ ] Code is pushed to GitHub repository
- [ ] `app.py` is in the root directory
- [ ] `requirements.txt` is up to date
- [ ] `.env` is in `.gitignore` (never commit API keys!)
- [ ] Groq API key obtained from [Groq Console](https://console.groq.com/keys)
- [ ] Pinecone API key obtained from [Pinecone Dashboard](https://app.pinecone.io/)
- [ ] Pinecone index created and populated with data
- [ ] All tests pass locally

## Step 1: Prepare Repository

### 1.1 Verify Repository Structure

Ensure your repository has this structure:

```
Groww_FAQ-Chatbot/
├── app.py                    # Main Streamlit app (REQUIRED)
├── requirements.txt          # Dependencies (REQUIRED)
├── config.py
├── .streamlit/
│   └── config.toml          # Optional: Streamlit config
├── backend/
│   ├── __init__.py
│   ├── llm_service.py
│   ├── retrieval.py
│   ├── query_processor.py
│   ├── formatter.py
│   └── validators.py
├── frontend/
│   ├── components/
│   │   ├── chat_ui.py
│   │   ├── welcome.py
│   │   └── footer.py
│   └── styles.css
└── README.md
```

### 1.2 Verify requirements.txt

Ensure `requirements.txt` includes all dependencies:

```txt
streamlit>=1.28.0
groq>=0.4.0
pinecone-client>=5.0.0
sentence-transformers>=2.2.0
python-dotenv>=1.0.0
# ... other dependencies
```

### 1.3 Verify .gitignore

Ensure `.env` is in `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
```

### 1.4 Commit and Push

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main  # or your branch name
```

## Step 2: Create Streamlit Cloud Account

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "Sign up" or "Get started"
3. Sign in with your GitHub account
4. Authorize Streamlit Cloud to access your repositories

## Step 3: Deploy Application

### 3.1 Create New App

1. In Streamlit Cloud dashboard, click **"New app"**
2. Fill in the deployment form:

   **Repository**: Select your repository
   - `your-username/Groww_FAQ-Chatbot`

   **Branch**: Select branch
   - `main` or `feature/mutual-fund-chatbot`

   **Main file path**: 
   - `app.py`

   **App URL** (optional):
   - `groww-mutual-fund-chatbot` (will create: `groww-mutual-fund-chatbot.streamlit.app`)

3. Click **"Deploy"**

### 3.2 Initial Deployment

- Streamlit Cloud will:
  - Clone your repository
  - Install dependencies from `requirements.txt`
  - Start the app
  - Show deployment logs

**Note**: The first deployment will likely fail because environment variables are not set yet. This is expected.

## Step 4: Configure Environment Variables

### 4.1 Access App Settings

1. In Streamlit Cloud dashboard, find your app
2. Click the **"⋮"** (three dots) menu
3. Select **"Settings"**

### 4.2 Add Secrets

1. Scroll to **"Secrets"** section
2. Click **"Open secrets editor"**
3. Add the following secrets:

```toml
[secrets]
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
PINECONE_API_KEY = "your_actual_pinecone_api_key_here"
PINECONE_INDEX_NAME = "ragchatbot"
```

**Important Notes**:
- Use `[secrets]` section (not `[env]`)
- No quotes needed around values in TOML
- Replace placeholder values with actual keys
- Save the secrets

### 4.3 Verify Secrets

After saving, verify:
- Secrets are saved (no error messages)
- Key names match exactly (case-sensitive)
- No extra spaces or quotes

## Step 5: Redeploy Application

### 5.1 Trigger Redeploy

1. In app settings, click **"Redeploy"** or **"Save and redeploy"**
2. Wait for deployment to complete
3. Check deployment logs for errors

### 5.2 Monitor Deployment

Watch the deployment logs for:
- ✅ Dependencies installing successfully
- ✅ No import errors
- ✅ App starting without errors
- ⚠️ Any warnings (usually safe to ignore)

## Step 6: Verify Deployment

### 6.1 Access Your App

Your app will be available at:
```
https://your-app-name.streamlit.app
```

### 6.2 Basic Functionality Test

Test the following:

- [ ] **App loads**: No error pages
- [ ] **Welcome screen**: Displays correctly
- [ ] **Example questions**: Visible and clickable
- [ ] **Chat interface**: Input field and send button visible
- [ ] **Styling**: Colors and layout match design

### 6.3 Query Processing Test

Test with sample queries:

- [ ] **Factual query**: "What is the expense ratio of SBI Large Cap Fund?"
  - Should return a response
  - Should include source URL
  - Should be factual (no advice)

- [ ] **Advice query**: "Should I invest in SBI Large Cap Fund?"
  - Should be blocked
  - Should show appropriate message

- [ ] **Non-MF query**: "What is the stock price of Reliance?"
  - Should be handled gracefully
  - Should redirect to appropriate resources

### 6.4 Error Handling Test

- [ ] **Invalid query**: Empty or malformed queries
  - Should handle gracefully
  - Should not crash

- [ ] **API errors**: (if possible to simulate)
  - Should show fallback messages
  - Should not expose sensitive information

## Step 7: Post-Deployment Checklist

### 7.1 Functionality

- [ ] All example questions work
- [ ] Chat history persists during session
- [ ] Source URLs are clickable
- [ ] Footer links work
- [ ] Responsive design works on mobile

### 7.2 Performance

- [ ] Response times are acceptable (<5 seconds)
- [ ] No timeout errors
- [ ] App loads quickly
- [ ] No memory leaks (check over time)

### 7.3 Security

- [ ] API keys are not exposed in frontend
- [ ] No sensitive data in logs
- [ ] Error messages don't reveal internals
- [ ] HTTPS is enabled (automatic on Streamlit Cloud)

### 7.4 Monitoring

- [ ] Check Streamlit Cloud logs regularly
- [ ] Monitor API usage (Groq, Pinecone)
- [ ] Set up alerts for errors (if available)
- [ ] Track response times

## Troubleshooting

### Issue: App Won't Deploy

**Symptoms**: Deployment fails, error in logs

**Solutions**:
1. Check `app.py` exists in root directory
2. Verify `requirements.txt` is correct
3. Check Python version compatibility
4. Review deployment logs for specific errors
5. Ensure all imports are available in `requirements.txt`

### Issue: Module Not Found

**Symptoms**: `ModuleNotFoundError` in logs

**Solutions**:
1. Verify all dependencies in `requirements.txt`
2. Check import paths (relative vs absolute)
3. Ensure `backend/__init__.py` exists
4. Verify package structure

### Issue: API Key Errors

**Symptoms**: "GROQ_API_KEY not found" or "PINECONE_API_KEY not found"

**Solutions**:
1. Verify secrets are set in Streamlit Cloud
2. Check key names match exactly (case-sensitive)
3. Ensure secrets are in `[secrets]` section
4. Redeploy after adding secrets
5. Check `.env` is not being used (Streamlit Cloud uses secrets)

### Issue: Slow Response Times

**Symptoms**: Queries take >10 seconds

**Solutions**:
1. Check Pinecone index performance
2. Verify Groq API quota not exceeded
3. Check network latency
4. Review token optimization settings
5. Consider upgrading API tiers

### Issue: App Crashes

**Symptoms**: App stops responding, shows error page

**Solutions**:
1. Check Streamlit Cloud logs
2. Review recent code changes
3. Test locally to reproduce
4. Check API rate limits
5. Verify all environment variables are set

### Issue: Styling Issues

**Symptoms**: CSS not loading, colors wrong

**Solutions**:
1. Verify `frontend/styles.css` is in repository
2. Check CSS file path in `app.py`
3. Clear browser cache
4. Verify CSS is loaded in `app.py`:
   ```python
   with open('frontend/styles.css') as f:
       st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
   ```

## Advanced Configuration

### Custom Domain (Optional)

Streamlit Cloud free tier doesn't support custom domains. For custom domain:
- Upgrade to Streamlit Cloud Team tier
- Or use alternative hosting (AWS, GCP, etc.)

### Environment-Specific Configs

If you need different configs for dev/prod:

1. Use environment variables in `config.py`:
   ```python
   import os
   ENV = os.getenv("ENVIRONMENT", "production")
   ```

2. Set in Streamlit Cloud secrets:
   ```toml
   [secrets]
   ENVIRONMENT = "production"
   ```

### Monitoring and Logging

1. **Streamlit Cloud Logs**:
   - Access via dashboard
   - View real-time logs
   - Download log files

2. **External Monitoring** (Optional):
   - Set up Sentry for error tracking
   - Use Datadog/New Relic for performance
   - Configure uptime monitoring

## Maintenance

### Regular Updates

- [ ] Update dependencies monthly
- [ ] Check for security updates
- [ ] Monitor API changes (Groq, Pinecone)
- [ ] Review and update documentation

### Backup

- [ ] Code is in version control (GitHub)
- [ ] Document configuration changes
- [ ] Backup environment variable values (securely)
- [ ] Keep deployment notes

### Scaling

If you need to scale:

1. **API Limits**:
   - Monitor Groq TPM usage
   - Upgrade to paid tier if needed
   - Implement request queuing

2. **Pinecone**:
   - Monitor query limits
   - Upgrade index tier if needed
   - Optimize query patterns

3. **Streamlit Cloud**:
   - Free tier: Public apps only
   - Team tier: Private apps, more resources
   - Consider self-hosting for more control

## Next Steps

After successful deployment:

1. **Task 8.13**: Test deployed application thoroughly
2. **Documentation**: Update README with live app URL
3. **Monitoring**: Set up regular checks
4. **User Testing**: Gather feedback
5. **Iteration**: Improve based on usage

## Support

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Groq API Docs](https://console.groq.com/docs)
- [Pinecone Docs](https://docs.pinecone.io/)

## Deployment Checklist Summary

- [ ] Repository prepared and pushed
- [ ] Streamlit Cloud account created
- [ ] App deployed (initial)
- [ ] Environment variables configured
- [ ] App redeployed with secrets
- [ ] Basic functionality verified
- [ ] Query processing tested
- [ ] Error handling verified
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Monitoring set up
- [ ] Documentation updated

---

**Congratulations!** Your Mutual Fund FAQ Chatbot is now live on Streamlit Cloud! 🎉

