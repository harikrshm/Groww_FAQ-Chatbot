# Deployment Guide

This guide covers deployment of the Mutual Fund FAQ Chatbot on Streamlit Cloud.

## Prerequisites

- GitHub repository with code pushed
- Streamlit Cloud account (free tier available)
- Valid API keys (Groq and Pinecone)

## Environment Variables

The following environment variables must be set in Streamlit Cloud:

### Required Variables

1. **GROQ_API_KEY**
   - Description: Groq API key for LLM generation (Llama 3.1 8B Instant)
   - How to get: Visit [Groq Console](https://console.groq.com/keys)
   - Example: `gsk_...`

2. **PINECONE_API_KEY**
   - Description: Pinecone API key for vector database access
   - How to get: Visit [Pinecone Dashboard](https://app.pinecone.io/)
   - Example: `abc123...`

3. **PINECONE_INDEX_NAME**
   - Description: Name of your Pinecone index
   - Default: `ragchatbot`
   - Example: `ragchatbot`

## Streamlit Cloud Deployment Steps

### Step 1: Prepare Repository

1. Ensure all code is pushed to GitHub
2. Verify `app.py` is in the root directory
3. Verify `requirements.txt` exists and is up to date
4. Ensure `.env` is in `.gitignore` (never commit API keys!)

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Set branch: `main` or `feature/mutual-fund-chatbot`

### Step 3: Configure Environment Variables

1. In the app settings, go to "Secrets"
2. Add each environment variable:
   ```
   GROQ_API_KEY=your_actual_key_here
   PINECONE_API_KEY=your_actual_key_here
   PINECONE_INDEX_NAME=ragchatbot
   ```
3. Save the secrets

### Step 4: Deploy

1. Click "Deploy" or "Redeploy"
2. Wait for deployment to complete
3. Your app will be available at: `https://your-app-name.streamlit.app`

## Streamlit Configuration

The `.streamlit/config.toml` file (if needed) can contain:

```toml
[theme]
primaryColor = "#0F4C75"
backgroundColor = "#F8F9FA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1F2937"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

## Post-Deployment Verification

### 1. Test Basic Functionality
- [ ] App loads without errors
- [ ] Welcome screen displays correctly
- [ ] Logos load correctly
- [ ] Example questions are clickable

### 2. Test Query Processing
- [ ] Factual queries return responses
- [ ] Advice queries are blocked
- [ ] Non-MF queries are handled
- [ ] Source URLs are clickable

### 3. Test Error Handling
- [ ] Invalid queries handled gracefully
- [ ] API failures show fallback messages
- [ ] No crashes on edge cases

### 4. Check Logs
- [ ] No critical errors in Streamlit logs
- [ ] API calls are successful
- [ ] Response times are acceptable

## Troubleshooting

### App Won't Deploy

**Issue**: Deployment fails
- Check that `app.py` exists in root
- Verify `requirements.txt` is correct
- Check Streamlit Cloud logs for errors

**Issue**: Module not found errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

### API Errors

**Issue**: "GROQ_API_KEY not found"
- Verify environment variable is set in Streamlit Cloud secrets
- Check variable name spelling (case-sensitive)
- Redeploy after adding secrets

**Issue**: "PINECONE_API_KEY not found"
- Verify environment variable is set
- Check Pinecone index name matches
- Verify index exists in Pinecone dashboard

### Performance Issues

**Issue**: Slow response times
- Check Pinecone index performance
- Verify Groq API quota not exceeded (6000 TPM free tier)
- Check network latency
- Verify token optimization is working

**Issue**: Timeout errors
- Increase timeout settings if needed
- Optimize query processing
- Check API rate limits

## Security Best Practices

1. **Never commit API keys**
   - Keep `.env` in `.gitignore`
   - Use Streamlit Cloud secrets for production

2. **Rotate keys regularly**
   - Update API keys periodically
   - Revoke old keys when rotating

3. **Monitor usage**
   - Check API usage regularly
   - Set up alerts for quota limits

4. **Limit access**
   - Use least privilege principle
   - Restrict API key permissions where possible

## Cost Considerations

### Groq API
- Free tier: 6000 tokens per minute (TPM)
- Model: Llama 3.1 8B Instant (optimized for speed)
- Monitor usage in Groq Console
- Token optimization implemented (~965 tokens per request)

### Pinecone
- Free tier: 1 index, limited queries
- Paid tier: More indexes and queries
- Monitor usage in Pinecone dashboard

### Streamlit Cloud
- Free tier: Public apps only
- Team tier: Private apps available

## Maintenance

### Regular Updates
- Update dependencies monthly
- Check for security updates
- Monitor API changes

### Monitoring
- Set up error alerts
- Monitor response times
- Track API usage

### Backup
- Keep code in version control
- Document configuration changes
- Backup environment variable values (securely)

## Support Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Groq API Docs](https://console.groq.com/docs)
- [Pinecone Docs](https://docs.pinecone.io/)
- [Project Issues](https://github.com/your-repo/issues)

