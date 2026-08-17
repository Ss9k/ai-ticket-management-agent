# LLM Provider Setup Guide

## 🔧 Current Models (Updated)

The following models are currently configured in SupportPilot:

1. **Groq** (Primary): `llama-3.1-8b-instant`
2. **Gemini** (Secondary): `gemini-1.5-flash`
3. **OpenRouter** (Tertiary): `meta-llama/llama-3.1-8b-instruct:free`

---

## 🚀 Quick Setup (Choose ONE)

You only need **one** API key to get started. Groq is recommended.

### Option 1: Groq (Recommended - Fast & Free)

1. Go to: https://console.groq.com/keys
2. Sign up / Log in
3. Click "Create API Key"
4. Copy the key
5. Add to `.env`:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

**Why Groq?**
- ✅ Fast response times
- ✅ Generous free tier
- ✅ Reliable service
- ✅ No credit card required

---

### Option 2: Google Gemini (Good Alternative)

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. Add to `.env`:
   ```env
   GEMINI_API_KEY=AIza...your_key_here
   ```

**Why Gemini?**
- ✅ Free tier available
- ✅ Good quality responses
- ✅ Google's infrastructure

---

### Option 3: OpenRouter (Backup)

1. Go to: https://openrouter.ai/keys
2. Sign up / Log in
3. Create API key
4. Add to `.env`:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-...your_key_here
   ```

**Note**: OpenRouter aggregates multiple providers. Free tier available.

---

## ⚙️ Configuration

1. **Copy environment template:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit `.env` file:**
   ```env
   # Add at least ONE of these:
   GROQ_API_KEY=your_groq_key_here
   GEMINI_API_KEY=your_gemini_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here
   
   # Other required settings:
   SECRET_KEY=your-random-secret-key
   FLASK_SECRET_KEY=your-flask-secret-key
   DATABASE_URL=sqlite:///./supportpilot.db
   ```

3. **Restart backend:**
   ```powershell
   # Stop the backend (Ctrl+C)
   # Start it again:
   uvicorn backend.main:app --reload
   ```

---

## 🔄 Provider Fallback Order

SupportPilot tries providers in this order:

1. **Groq** → 2 retry attempts
2. **Gemini** → 2 retry attempts (if Groq fails)
3. **OpenRouter** → 2 retry attempts (if Gemini fails)

If all providers fail, the user sees a helpful error message and can create a ticket.

---

## 🧪 Testing Your Setup

### 1. Test Backend Health
```powershell
# Should return: {"status": "healthy", ...}
curl http://localhost:8000/health
```

### 2. Test AI Endpoint (requires auth)
```powershell
# Login first, then test the AI
# Or use the frontend at http://localhost:5000
```

### 3. Check Backend Logs

When you click "Get AI Solution", you should see in the backend logs:

```
INFO | Trying GroqProvider (attempt 1/2)
INFO | GroqProvider success
```

If you see warnings, check:
- ✅ API key is correct in `.env`
- ✅ Backend was restarted after editing `.env`
- ✅ API key has sufficient quota/credits

---

## ❌ Common Issues

### "API key not configured"
**Solution**: Add at least one API key to `.env` and restart backend

### "Model decommissioned" / "Model not found"
**Solution**: This guide already has the updated models. Just restart the backend.

### "Rate limit exceeded"
**Solution**: 
- Wait a few minutes (free tier limits)
- Try a different provider
- Upgrade to paid tier if needed

### "404 Not Found"
**Solution**: Make sure you're using the latest code (already fixed in this guide)

---

## 📊 Model Comparison

| Provider | Model | Speed | Free Tier | Quality |
|----------|-------|-------|-----------|---------|
| Groq | llama-3.1-8b-instant | ⚡⚡⚡ Very Fast | ✅ Generous | ⭐⭐⭐⭐ |
| Gemini | gemini-1.5-flash | ⚡⚡ Fast | ✅ Available | ⭐⭐⭐⭐⭐ |
| OpenRouter | llama-3.1-8b (free) | ⚡ Good | ✅ Limited | ⭐⭐⭐ |

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** (already in `.gitignore`)
2. **Rotate API keys periodically**
3. **Use environment-specific keys** (dev vs prod)
4. **Monitor API usage** to avoid unexpected charges
5. **Set usage limits** in provider dashboards

---

## 🎯 Recommendation

**For Development**: Use Groq (fast, free, reliable)

**For Production**: 
- Configure all three providers for maximum reliability
- Consider paid tiers for guaranteed availability
- Monitor usage and costs
- Set up alerts for failures

---

## 📞 Need Help?

If AI still doesn't work after following this guide:

1. Check backend logs for specific errors
2. Verify your API key is valid on the provider's website
3. Test the API key directly with curl:

```bash
# Test Groq
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_KEY"

# Test Gemini
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_KEY"
```

4. Create an issue with the error logs

---

## 🔄 Changing Models

To use different models, edit these files:

- `backend/llm/groq_provider.py` - Line 14: `MODEL = "..."`
- `backend/llm/gemini_provider.py` - Line 14: `MODEL = "..."`
- `backend/llm/openrouter_provider.py` - Line 14: `MODEL = "..."`

Available models:
- **Groq**: https://console.groq.com/docs/models
- **Gemini**: https://ai.google.dev/models/gemini
- **OpenRouter**: https://openrouter.ai/models

---

**Updated**: August 10, 2026
**Compatible with**: SupportPilot v1.0

---

## ✅ Quick Checklist

- [ ] Got API key from at least one provider
- [ ] Added API key to `.env` file
- [ ] Restarted backend server
- [ ] Tested "Get AI Solution" button
- [ ] Saw successful response in logs

If all checked, you're ready to go! 🚀
