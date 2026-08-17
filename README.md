# SupportPilot

**AI-Powered Enterprise IT Support & Ticket Management System**

SupportPilot is a full-stack enterprise IT support platform that uses AI and RAG (Retrieval-Augmented Generation) to help employees resolve technical problems instantly. When AI can't solve the issue, tickets are created and routed to engineers through an intelligent workflow system.

---

## 🎯 Features

### 🤖 AI-Powered Support
- **RAG-based Knowledge Base**: FAISS vector search retrieves relevant troubleshooting guides
- **Multi-Provider LLM**: Automatic fallback between Groq → Gemini → OpenRouter
- **Intelligent Classification**: Auto-categorizes tickets by category, severity, and priority
- **Context-Aware Responses**: AI answers using internal KB before falling back to general knowledge

### 🎫 Ticket Management
- **Complete Lifecycle**: Pending → Escalated → Resolved → Closed
- **Engineer Assignment**: Admin assigns tickets to available engineers
- **Resolution Tracking**: Immutable audit trail for every status change
- **Search & Filter**: Find tickets by status, priority, category, severity, and search terms

### 👥 Role-Based Access Control
- **Users**: Submit problems, interact with AI, view own tickets
- **Engineers**: Manage assigned tickets, add remarks, resolve issues (requires admin approval)
- **Admins**: Approve engineers, assign tickets, view analytics and reports

### 📊 Analytics & Reporting
- **Status Metrics**: Real-time KPI dashboard
- **Category Analysis**: Ticket distribution by category
- **Priority Analysis**: P1-P4 breakdown
- **Resolution Trends**: 30-day resolution timeline
- **Engineer Performance**: Resolution rates and workload tracking

### 🎨 Professional UI
- Modern enterprise SaaS design with Bootstrap 5
- Responsive layout with sidebar navigation
- Real-time loading states and flash notifications
- Chart.js visualizations for analytics

---

## 🏗️ Architecture

```
Browser (User)
     ↓
Flask Frontend (Jinja2, HTML, CSS, JS)
     ↓ HTTP/REST
FastAPI Backend (Python)
     ↓
┌────────────┬─────────────┐
│            │             │
SQLAlchemy   AI/RAG Layer  Services
    ↓            ↓
SQLite      FAISS Index    (ticket, auth, analytics)
            SentenceTransformers
            LLM Providers (Groq/Gemini/OpenRouter)
```

**Frontend**: Flask serves templates and communicates with FastAPI backend via centralized API client.

**Backend**: FastAPI handles all business logic, database operations, and AI orchestration.

**AI Layer**: RAG pipeline embeds queries, searches FAISS, constructs context, and calls LLM providers with retry/fallback.

---

## 📋 Tech Stack

### Backend
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM with SQLite (PostgreSQL-ready)
- **Pydantic**: Request/response validation
- **Uvicorn**: ASGI server

### Frontend
- **Flask**: Web framework
- **Jinja2**: Template engine
- **Bootstrap 5**: UI framework
- **Chart.js**: Analytics charts

### AI/RAG
- **Sentence Transformers**: Text embeddings (`all-MiniLM-L6-v2`)
- **FAISS**: Vector similarity search (IndexFlatL2)
- **Groq**: Primary LLM provider (llama3-8b-8192)
- **Google Gemini**: Secondary fallback (gemini-1.5-flash)
- **OpenRouter**: Tertiary fallback (mistral-7b-instruct)

### Security
- **Werkzeug**: Password hashing (bcrypt)
- **Flask Sessions**: Cookie-based authentication

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.10+
- pip or uv package manager

### 2. Clone Repository
```bash
cd "d:\Projects\AI Ticket Management"
```

### 3. Create Virtual Environment
```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
Copy-Item .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
SECRET_KEY=your-random-secret-key
FLASK_SECRET_KEY=your-flask-secret-key
```

**Get API Keys:**
- **Groq** (recommended): https://console.groq.com/keys
- **Gemini**: https://aistudio.google.com/app/apikey
- **OpenRouter**: https://openrouter.ai/keys

**Note**: See `LLM_SETUP.md` for detailed provider setup instructions and troubleshooting.

### 6. Initialize Database
```bash
python seed.py
```

This creates:
- Database tables
- Admin account: `admin@supportpilot.com` / `admin123`
- Sample user: `user@supportpilot.com` / `user123`
- Sample engineer: `engineer@supportpilot.com` / `engineer123`
- Sample tickets

### 7. Ingest Knowledge Base
```bash
python ingest_knowledge_base.py
```

This processes all `.md` and `.pdf` files from `docs/` directory, generates embeddings, and builds the FAISS index.

**Knowledge Base Contents:**
- Network troubleshooting (VPN, connectivity, slow performance)
- Password and account management (reset, lockout, MFA)
- Hardware troubleshooting (PC, monitor, peripherals, printers)
- Software troubleshooting (crashes, Office, Teams, performance)
- Security guidelines (phishing, malware, data protection)

### 8. Start Backend Server
```bash
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000

API docs available at: http://localhost:8000/docs

### 9. Start Frontend Server
Open a **new terminal** and activate the virtual environment:
```bash
.\venv\Scripts\Activate.ps1  # Windows
python frontend/app.py
```

Frontend runs at: http://localhost:5000

---

## 🎮 Usage

### 1. Login as Admin
- Go to http://localhost:5000
- Login with: `admin@supportpilot.com` / `admin123`

**Admin Can:**
- Approve pending engineers
- View all tickets
- Assign tickets to engineers
- Access analytics and reports

### 2. Login as User
- Register a new user account or use: `user@supportpilot.com` / `user123`

**User Workflow:**
1. **Describe Problem**: Enter title and description
2. **Get AI Solution**: Click "Get AI Solution" — AI retrieves KB articles and provides troubleshooting steps
3. **Problem Solved?**
   - Click "Works" → Done, no ticket created
   - Click "Didn't Work" → Ticket automatically created
4. **View Tickets**: See status of all submitted tickets

### 3. Register as Engineer
- Register with role "Engineer"
- Account status will be "Pending"
- Admin must approve before you can access engineer dashboard

### 4. Login as Engineer
- After admin approval, login with engineer credentials
- View: `engineer@supportpilot.com` / `engineer123`

**Engineer Workflow:**
1. **Dashboard**: See KPI metrics, priority breakdown, recent activity
2. **View Tickets**: Browse assigned tickets with filters (status, priority, category)
3. **Ticket Detail**:
   - View problem description
   - Review AI solution (what user saw)
   - Review AI technical analysis (engineer-facing)
   - Add investigation remarks
   - Add resolution notes
   - Mark as Resolved
4. **Close Ticket**: After resolution is verified

---

## 🧪 Testing

Run pytest tests:
```bash
pytest tests/ -v
```

**Test Coverage:**
- Authentication (register, login, RBAC)
- Engineer approval workflow
- Ticket lifecycle (create, assign, resolve, close)
- Engineer access control (can only view assigned tickets)
- Analytics authorization (admin-only)
- RAG vector store operations
- Ticket classification fallback

---

## 📁 Project Structure

```
d:\Projects\AI Ticket Management\
├── backend/
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   └── logging_config.py  # Centralized logging
│   ├── models/
│   │   ├── user.py             # User/Engineer/Admin model
│   │   ├── ticket.py           # Ticket model with status/category/priority
│   │   └── ticket_history.py  # Immutable audit trail
│   ├── schemas/
│   │   ├── user.py             # Pydantic request/response schemas
│   │   ├── ticket.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── auth_service.py     # Authentication & user management
│   │   ├── ticket_service.py   # Ticket lifecycle operations
│   │   ├── ai_service.py       # AI/RAG integration
│   │   └── analytics_service.py
│   ├── routers/
│   │   ├── auth.py             # POST /auth/register, /auth/login
│   │   ├── user.py             # POST /user/ai, /user/create-ticket
│   │   ├── admin.py            # Admin endpoints
│   │   ├── engineer.py         # Engineer endpoints
│   │   └── analytics.py        # GET /analytics/, /reports/
│   ├── llm/
│   │   ├── base_provider.py    # LLM provider interface
│   │   ├── groq_provider.py
│   │   ├── gemini_provider.py
│   │   ├── openrouter_provider.py
│   │   ├── provider_manager.py # Retry & fallback logic
│   │   └── prompts.py          # ASK_AI, CLASSIFICATION, RESOLUTION
│   ├── rag/
│   │   ├── knowledge_loader.py  # Load .md/.pdf from docs/
│   │   ├── embedding_generator.py # SentenceTransformers wrapper
│   │   ├── vector_store.py     # FAISS IndexFlatL2 wrapper
│   │   └── rag_pipeline.py     # RAG orchestration
│   └── main.py                 # FastAPI application entry point
├── frontend/
│   ├── routes/
│   │   ├── auth.py             # Login, register, logout
│   │   ├── user.py             # User dashboard & AJAX endpoints
│   │   ├── admin.py            # Admin dashboard
│   │   ├── engineer.py         # Engineer dashboard & tickets
│   │   └── analytics.py        # Analytics & reports
│   ├── services/
│   │   └── api_client.py       # Centralized HTTP client for backend
│   ├── templates/
│   │   ├── base.html           # Base layout with navbar/sidebar
│   │   ├── components/         # Reusable components
│   │   ├── auth/               # Login & register
│   │   ├── user/               # User dashboard (unified AI + tickets)
│   │   ├── admin/              # Admin dashboard
│   │   ├── engineer/           # Engineer dashboard & ticket detail
│   │   ├── analytics/          # Analytics dashboard
│   │   └── reports/            # Reports dashboard
│   ├── static/
│   │   ├── css/
│   │   │   ├── theme.css       # CSS variables & base styles
│   │   │   ├── layout.css      # Navbar, sidebar, page structure
│   │   │   ├── components.css  # Cards, badges, tables, buttons
│   │   │   └── pages.css       # Page-specific styles
│   │   └── js/
│   │       ├── app.js          # Core JS (flash, loader, markdown)
│   │       ├── user.js         # User dashboard AI interaction
│   │       ├── engineer.js     # Engineer confirmation dialogs
│   │       └── charts.js       # Chart.js wrappers
│   ├── config.py
│   └── app.py                  # Flask application entry point
├── docs/                       # Knowledge base (ingested by RAG)
│   ├── network_troubleshooting.md
│   ├── password_and_account.md
│   ├── hardware_troubleshooting.md
│   ├── software_troubleshooting.md
│   └── security_guidelines.md
├── tests/
│   ├── conftest.py             # pytest fixtures
│   ├── test_auth.py
│   ├── test_ticket_lifecycle.py
│   └── test_rag.py
├── seed.py                     # Database seeding script
├── ingest_knowledge_base.py   # Knowledge base ingestion script
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔐 Security Considerations

- **Password Storage**: Werkzeug bcrypt hashing (never plaintext)
- **Session Management**: Flask secure cookies with HTTPONLY flag
- **Authorization**: Backend enforces role-based access on every endpoint
- **CORS**: Restricted to localhost:5000 (frontend origin)
- **API Keys**: Never committed to repository (use .env)
- **SQL Injection**: Protected via SQLAlchemy ORM
- **CSRF**: Flash AJAX calls could benefit from CSRF tokens (production enhancement)

---

## 🎯 Complete Workflow Example

### User Journey: VPN Connection Issue

1. **User Action**: Alice opens SupportPilot and describes:
   - Title: "Cannot connect to VPN from home"
   - Description: "Getting Authentication Failed error code 691"

2. **AI Processing**:
   - Query embedded using `all-MiniLM-L6-v2`
   - FAISS searches KB and retrieves `network_troubleshooting.md`
   - Context injected into prompt
   - Groq LLM generates structured response with:
     - Answer (using KB article)
     - Recommended Action (step-by-step fix)
     - Confidence level
     - Related KB articles

3. **User Tries Solution**: Follows AI's troubleshooting steps

4. **Solution Doesn't Work**: Clicks "Didn't Work → Create Ticket"

5. **Ticket Created**:
   - Status: `pending`
   - AI classification runs in background:
     - Category: `VPN`
     - Severity: `High`
     - Priority: `P2`
     - AI Analysis: "Authentication failure suggests credential mismatch..."
     - AI Recommendation: "Verify credentials, check MFA token..."

6. **Admin Review**:
   - Admin sees ticket in dashboard
   - Assigns to engineer Bob

7. **Status Change**: `pending` → `escalated`

8. **Engineer Bob**:
   - Views ticket detail
   - Reads problem, AI solution, AI analysis
   - Investigates: checks VPN logs, verifies account
   - Adds remarks: "User's MFA token was expired"
   - Adds resolution: "Reset MFA token, user reconnected successfully"
   - Marks as `resolved`

9. **Status Change**: `escalated` → `resolved`

10. **Ticket Closed**: Bob closes ticket

11. **Status Change**: `resolved` → `closed`

12. **Analytics Updated**: Resolution metrics, engineer performance updated

---

## 🔧 Troubleshooting

### Backend won't start
- Check port 8000 is available
- Verify all dependencies installed: `pip list`
- Check `.env` file exists (copy from `.env.example`)

### Frontend won't start
- Check port 5000 is available
- Ensure backend is running first
- Verify Flask dependencies installed

### AI not responding
- Check API keys in `.env` are valid
- Verify FAISS index exists: `backend/rag/faiss_index.index`
- Run `python ingest_knowledge_base.py` to regenerate index
- Check backend logs for LLM provider errors

### Knowledge Base not returning results
- Ensure `docs/` directory contains `.md` or `.pdf` files
- Run ingestion script: `python ingest_knowledge_base.py`
- Check FAISS index created successfully

### Cannot login as engineer
- Engineer accounts require admin approval
- Login as admin and approve engineer from dashboard

---

## 🚀 Production Deployment Considerations

1. **Database**: Switch from SQLite to PostgreSQL (change `DATABASE_URL` in `.env`)
2. **Secrets**: Use environment-specific secrets, rotate regularly
3. **HTTPS**: Deploy behind reverse proxy (nginx/Apache) with SSL
4. **CORS**: Update allowed origins to production domain
5. **Rate Limiting**: Add rate limiting to API endpoints
6. **Monitoring**: Add logging aggregation (ELK, Datadog)
7. **Scaling**: Use Gunicorn/uWSGI with multiple workers
8. **Vector Store**: Consider hosted FAISS or move to Pinecone/Weaviate for scale
9. **LLM Costs**: Monitor token usage, implement caching layer
10. **Backup**: Automated database backups

---

## 📊 API Documentation

FastAPI provides auto-generated interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Key endpoints:
- `POST /auth/register` - Register user/engineer
- `POST /auth/login` - Authenticate user
- `POST /user/ai` - Ask AI for solution
- `POST /user/create-ticket` - Create support ticket
- `GET /admin/engineers/pending` - Get pending engineers (admin)
- `POST /admin/assign` - Assign ticket to engineer (admin)
- `GET /engineer/tickets` - Get assigned tickets (engineer)
- `POST /engineer/tickets/{id}/resolve` - Resolve ticket (engineer)
- `GET /analytics/` - Get analytics data (admin)

---

## 🤝 Contributing

This is a demonstration project built for showcasing full-stack AI integration.

---

## 📝 License

This project is provided as-is for educational and demonstration purposes.

---

## 👨‍💻 Author

Built as a complete full-stack AI-powered support system demonstration.

**Technologies**: Python • FastAPI • Flask • SQLAlchemy • FAISS • Sentence Transformers • Groq • Gemini • Bootstrap • Chart.js

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Full-stack web development (Flask + FastAPI)
- ✅ REST API design and implementation
- ✅ SQL database modeling with relationships
- ✅ Authentication and role-based authorization
- ✅ RAG (Retrieval-Augmented Generation) architecture
- ✅ Vector embeddings and similarity search (FAISS)
- ✅ LLM integration with fallback providers
- ✅ Professional UI/UX design
- ✅ Testing with pytest
- ✅ Clean architecture and separation of concerns
- ✅ Production-ready error handling and logging

---

**Ready to deploy an AI-powered support system? Follow the setup instructions and start resolving tickets with AI! 🚀**
