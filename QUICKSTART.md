# SupportPilot — Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys
```powershell
# Copy the example environment file
Copy-Item .env.example .env

# Edit .env and add your API keys
notepad .env
```

**Required API Keys** (at least one):
- **Groq** (recommended, free): https://console.groq.com/keys
- **Gemini** (fallback): https://aistudio.google.com/app/apikey  
- **OpenRouter** (fallback): https://openrouter.ai/keys

### Step 3: Initialize Database
```powershell
python seed.py
```

This creates the database and admin account:
- **Email**: admin@supportpilot.com
- **Password**: admin123

### Step 4: Build Knowledge Base
```powershell
python ingest_knowledge_base.py
```

This processes the 5 troubleshooting guides from `docs/` and builds the FAISS vector index.

### Step 5: Start Backend
```powershell
# Terminal 1
uvicorn backend.main:app --reload
```

Backend runs at: **http://localhost:8000**

### Step 6: Start Frontend
```powershell
# Terminal 2 (new terminal, activate venv first)
.\venv\Scripts\Activate.ps1
python frontend/app.py
```

Frontend runs at: **http://localhost:5000**

---

## ✅ Verify Installation

### 1. Check Backend Health
Open browser: http://localhost:8000/health

Should return:
```json
{
  "status": "healthy",
  "service": "SupportPilot API",
  "version": "1.0.0"
}
```

### 2. Check API Documentation
Open browser: http://localhost:8000/docs

You should see the interactive Swagger UI with all API endpoints.

### 3. Test Frontend
Open browser: http://localhost:5000

You should see the login page.

---

## 🎮 First Login

### Login as Admin
1. Go to http://localhost:5000
2. Enter:
   - **Email**: admin@supportpilot.com
   - **Password**: admin123
3. You'll see the Admin Dashboard

**What you can do:**
- ✅ View all tickets
- ✅ Approve pending engineers
- ✅ Assign tickets to engineers
- ✅ Access analytics and reports

---

## 👤 Test the Complete Workflow

### 1. Register as a User
1. Click "Register here" on login page
2. Fill in:
   - Name: Test User
   - Email: testuser@company.com
   - Password: password123
   - Account Type: **User**
3. Click "Create Account"
4. Login with your new credentials

### 2. Try AI Support (as User)
1. On the dashboard, enter a problem:
   - **Title**: "Cannot connect to VPN"
   - **Description**: "Getting error 691 when connecting to VPN from home"
2. Click "Get AI Solution"
3. AI will retrieve relevant KB articles and provide troubleshooting steps
4. Click "Didn't Work" to create a ticket

### 3. Register as Engineer
1. Logout
2. Register new account:
   - Name: Test Engineer
   - Email: testengineer@company.com
   - Password: password123
   - Account Type: **Engineer**
3. You'll see: "Engineer registration submitted. Your account is pending admin approval."

### 4. Approve Engineer (as Admin)
1. Logout and login as admin
2. Go to "Pending Engineers" section
3. Click "Approve" for the test engineer

### 5. Work on Ticket (as Engineer)
1. Logout and login as the engineer
2. View the engineer dashboard with KPIs
3. Click "Open Tickets" or "View All My Tickets"
4. Click "View" on the VPN ticket
5. Review:
   - Problem description
   - AI solution (what user saw)
   - AI technical analysis
6. Add remarks: "Investigating VPN credentials"
7. Add resolution notes: "Reset VPN password and verified MFA token"
8. Click "Mark as Resolved"

### 6. Close Ticket
1. After resolving, click "Close Ticket"
2. Ticket status changes to "closed"

### 7. View Analytics (as Admin)
1. Logout and login as admin
2. Click "Analytics" in sidebar
3. View:
   - Status counts
   - Category breakdown
   - Priority distribution
   - Resolution trends
   - Engineer performance

---

## 🧪 Run Tests

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

---

## 🐛 Common Issues

### "Module not found" errors
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Backend fails to start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed (replace PID)
taskkill /PID <PID> /F

# Or use a different port
uvicorn backend.main:app --reload --port 8001
```

### Frontend fails to start
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Edit frontend/app.py to use different port if needed
```

### FAISS errors
```powershell
# Reinstall faiss-cpu
pip uninstall faiss-cpu
pip install faiss-cpu==1.8.0
```

### AI not responding
- Verify at least one API key is set in `.env`
- Check backend logs for errors
- Try testing with Groq first (most reliable)

### Knowledge base empty
```powershell
# Rebuild the index
python ingest_knowledge_base.py

# Check files exist
Get-ChildItem docs\
```

---

## 📂 Project Structure Overview

```
d:\Projects\AI Ticket Management\
├── backend/              # FastAPI backend
│   ├── core/            # Config, database, logging
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── routers/         # API endpoints
│   ├── llm/             # LLM providers & prompts
│   ├── rag/             # RAG pipeline
│   └── main.py          # FastAPI app
├── frontend/            # Flask frontend
│   ├── routes/          # Flask routes
│   ├── templates/       # Jinja2 templates
│   ├── static/          # CSS, JS
│   └── app.py           # Flask app
├── docs/                # Knowledge base
├── tests/               # pytest tests
├── seed.py              # Database seeding
├── ingest_knowledge_base.py  # KB ingestion
└── README.md            # Full documentation
```

---

## 🎯 Next Steps

1. **Customize Knowledge Base**: Add your own `.md` or `.pdf` files to `docs/`
2. **Add Users**: Register multiple users and engineers
3. **Create Tickets**: Test different problem types
4. **Monitor Analytics**: Track resolution metrics
5. **Extend Features**: Add more LLM providers, custom prompts, or additional workflows

---

## 📞 Need Help?

- **API Docs**: http://localhost:8000/docs
- **Full README**: See `README.md` for complete documentation
- **Test Suite**: Run `pytest tests/ -v` to verify everything works

---

**Ready to use SupportPilot! 🚀**
