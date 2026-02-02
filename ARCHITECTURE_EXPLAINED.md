# 🏗️ Architecture - How Everything Connects

## 📊 The Big Picture

```
┌─────────────┐
│   BROWSER   │  👤 User interacts here
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────────────────────────────────┐
│      FRONTEND (React + Vite)            │
│  📍 http://localhost:5173 (local)       │
│  📍 https://vercel.app (deployed)       │
│                                         │
│  Files: frontend/src/                   │
│  - App.jsx (main app)                   │
│  - services/api.js (connects to backend)│
└──────────────┬──────────────────────────┘
               │ axios.post/get/put
               │ URL: VITE_API_URL
               ▼
┌─────────────────────────────────────────┐
│      BACKEND (FastAPI/Python)           │
│  📍 http://localhost:8000 (local)       │
│  📍 https://render.com (deployed)       │
│                                         │
│  Files: backend/                        │
│  - main.py (app entry point)            │
│  - app/api/ (endpoints)                 │
│  - app/services/ (business logic)       │
└──────┬──────────────┬───────────────────┘
       │              │
       │              │ Gemini API calls
       │              ▼
       │         ┌──────────────┐
       │         │  Google AI   │
       │         │  (Gemini)    │
       │         │              │
       │         │ Document     │
       │         │ Analysis     │
       │         └──────────────┘
       │
       │ SQLAlchemy ORM
       │ DATABASE_URL
       ▼
┌─────────────────────────────────────────┐
│      DATABASE (PostgreSQL)              │
│  📍 Neon.tech (cloud)                   │
│                                         │
│  Tables:                                │
│  - applications (main data)             │
│  - document_types (requirements)        │
│  - document_uploads (uploaded files)    │
│  - generated_documents (AI outputs)     │
│  - questionnaire_responses (answers)    │
└─────────────────────────────────────────┘
```

---

## 🔗 Connection Details

### 1️⃣ Frontend → Backend Connection

**File**: [frontend/src/services/api.js](frontend/src/services/api.js)

```javascript
// This is the connection point!
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
```

**How it works:**
- Frontend reads `VITE_API_URL` from environment variable
- Local: `http://localhost:8000/api`
- Deployed: `https://visa-backend.onrender.com/api`
- All API calls go through this URL

**Example API call:**
```javascript
// In frontend/src/pages/ApplicationForm.jsx
const response = await api.post('/applications', formData)
// This actually calls: http://localhost:8000/api/applications
```

---

### 2️⃣ Backend → Database Connection

**File**: [backend/app/config.py](backend/app/config.py#L19)

```python
# This is the database connection string
DATABASE_URL: str  # Read from environment variable
```

**File**: [backend/app/database.py](backend/app/database.py#L12)

```python
# Create database engine
engine = create_engine(
    settings.DATABASE_URL,  # PostgreSQL connection string
    pool_pre_ping=True,
    echo=settings.DEBUG
)
```

**How it works:**
- Backend reads `DATABASE_URL` from environment variable
- Format: `postgresql://user:password@host:port/database`
- Your Neon URL: `postgresql://neondb_owner:npg_...@ep-aged-dawn...neon.tech/neondb`
- SQLAlchemy handles all database operations

**Example database operation:**
```python
# In backend/app/api/applications.py
def create_application(db: Session, data):
    app = Application(**data)
    db.add(app)  # SQLAlchemy adds to database
    db.commit()  # Saves to PostgreSQL
    return app
```

---

### 3️⃣ Backend → Gemini AI Connection

**File**: [backend/app/config.py](backend/app/config.py#L26-L27)

```python
GEMINI_API_KEY: str  # Your API key
GEMINI_MODEL: str = "models/gemini-2.5-flash"
```

**How it works:**
- Backend reads `GEMINI_API_KEY` from environment variable
- Uses Google's Gemini API for document analysis
- Makes HTTP requests to Google's servers

**Example AI operation:**
```python
# In backend/app/services/document_processor.py
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)
response = model.generate_content(prompt)
```

---

## 🔐 Environment Variables - The Connection Keys

### **Local Development** (.env file)

```bash
# Backend connects to database
DATABASE_URL=postgresql://neondb_owner:npg_...@ep-aged-dawn...neon.tech/neondb

# Backend calls Gemini AI
GEMINI_API_KEY=AIzaSy...

# Backend allows frontend requests
CORS_ORIGINS=http://localhost:5173

# Frontend connects to backend
VITE_API_URL=http://localhost:8000/api
```

### **Production Deployment**

**Render (Backend):**
```
DATABASE_URL → PostgreSQL connection
GEMINI_API_KEY → AI service
CORS_ORIGINS → https://your-app.vercel.app
```

**Vercel (Frontend):**
```
VITE_API_URL → https://visa-backend.onrender.com/api
```

---

## 🔄 Data Flow Example

### Creating a new application:

```
1. User fills form in browser
   ↓
2. Frontend (React) calls:
   api.post('/applications', formData)
   ↓
3. Request goes to: http://localhost:8000/api/applications
   ↓
4. Backend (FastAPI) receives request:
   - Validates data
   - Creates Application object
   ↓
5. Backend saves to database:
   - SQLAlchemy converts to SQL
   - Executes: INSERT INTO applications ...
   - PostgreSQL stores the data
   ↓
6. Database returns saved record with ID
   ↓
7. Backend sends response to frontend:
   { "id": 123, "status": "created", ... }
   ↓
8. Frontend shows success message to user
```

### Analyzing a document:

```
1. User uploads PDF
   ↓
2. Frontend sends file to: POST /api/documents
   ↓
3. Backend saves file locally:
   - uploads/app_123/document.pdf
   ↓
4. Backend calls Gemini API:
   - Sends document text
   - Asks AI to analyze
   ↓
5. Gemini returns analysis:
   { "extracted_data": {...}, "completeness": 85% }
   ↓
6. Backend saves analysis to database:
   - Updates document_uploads table
   ↓
7. Frontend receives result and displays it
```

---

## 🛠️ Configuration Files

### Backend Configuration
- [backend/main.py](backend/main.py) - App entry point, CORS setup
- [backend/app/config.py](backend/app/config.py) - All settings
- [backend/app/database.py](backend/app/database.py) - Database connection
- [backend/requirements.txt](backend/requirements.txt) - Python packages

### Frontend Configuration
- [frontend/vite.config.js](frontend/vite.config.js) - Vite settings
- [frontend/src/services/api.js](frontend/src/services/api.js) - Backend connection
- [frontend/package.json](frontend/package.json) - Dependencies

### Deployment Configuration
- [render.yaml](render.yaml) - Render.com settings
- [vercel.json](vercel.json) - Vercel settings
- [Procfile](Procfile) - Process commands

---

## ✅ Deployment Guide is FULLY GUIDED

Yes! Your [EASY_DEPLOY_FREE.md](EASY_DEPLOY_FREE.md) file contains:

✅ **Step-by-step instructions**
✅ **Exact commands to run**
✅ **All environment variables needed**
✅ **Screenshots/guidance for each platform**
✅ **Troubleshooting section**
✅ **Cost breakdown ($0!)**

### Quick Deployment Checklist:

1. [ ] Get Gemini API key (2 min)
2. [ ] Push to GitHub (3 min)
3. [ ] Deploy backend on Render (5 min)
4. [ ] Deploy frontend on Vercel (3 min)
5. [ ] Update CORS settings (1 min)
6. [ ] Test the app!

**Total time: ~15 minutes**
**Total cost: $0/month**

---

## 🚨 Common Issues & Fixes

### "Cannot connect to backend"
**Problem**: Frontend can't reach backend
**Fix**: Check `VITE_API_URL` in frontend/.env
```bash
VITE_API_URL=http://localhost:8000/api
```

### "Database connection failed"
**Problem**: Backend can't reach PostgreSQL
**Fix**: Check `DATABASE_URL` in backend/.env
```bash
DATABASE_URL=postgresql://...neon.tech/neondb
```

### "CORS error"
**Problem**: Backend blocks frontend requests
**Fix**: Check `CORS_ORIGINS` in backend/.env
```bash
CORS_ORIGINS=http://localhost:5173
```

### "Gemini API error"
**Problem**: AI analysis not working
**Fix**: Check `GEMINI_API_KEY` in backend/.env
```bash
GEMINI_API_KEY=AIzaSy...
```

---

## 🎯 Next Steps

1. **Local Development**:
   ```bash
   # Terminal 1: Start backend
   cd backend
   uvicorn main:app --reload
   
   # Terminal 2: Start frontend
   cd frontend
   npm run dev
   ```

2. **Deploy to Production**:
   - Follow [EASY_DEPLOY_FREE.md](EASY_DEPLOY_FREE.md)
   - Takes 15 minutes total
   - Completely FREE hosting

3. **Monitor Your App**:
   - Render: Check backend logs
   - Vercel: Check frontend deployment
   - Neon: Check database usage

---

## 📚 Want More Details?

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Detailed deployment docs
- [README.md](README.md) - Project overview
- [docs/DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md) - Development setup

Need help? Just ask! 🤝
