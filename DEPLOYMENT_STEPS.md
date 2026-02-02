# 🚀 Complete Deployment Steps - Your Visa Processing System

## ✅ Database Setup - COMPLETED! 
Your Neon PostgreSQL database is ready with all tables and data.

---

## 📋 Step-by-Step Deployment Guide

### Step 1: Get Gemini API Key (5 minutes)

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (starts with `AIza...`)
4. Update `backend/.env`:
   ```bash
   GEMINI_API_KEY=AIzaSy...your-actual-key-here
   ```

---

### Step 2: Test Locally (5 minutes)

#### Backend Test:
```bash
cd backend
source ../venv/bin/activate  # or 'venv\Scripts\activate' on Windows
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs
- You should see FastAPI Swagger UI
- Test the `/api/health` endpoint

#### Frontend Test:
```bash
cd frontend
npm install  # if not already done
npm run dev
```

Open: http://localhost:5173
- You should see the application interface
- Try uploading a test document

---

### Step 3: Prepare for Deployment (10 minutes)

#### Create `.gitignore` (if not exists):
```bash
# Add to root .gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
.env.local
uploads/
generated/
logs/
*.log
node_modules/
dist/
.DS_Store
```

#### Update deployment configuration files:

**Create `backend/Procfile`** (for Railway):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Create `backend/railway.json`**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

### Step 4: Create GitHub Repository (5 minutes)

```bash
# Initialize git (if not done)
cd /media/sayad/Ubuntu-Data/visa
git init
git add .
git commit -m "Initial commit - visa processing system"

# Create repo on GitHub:
# Go to: https://github.com/new
# Repository name: visa-processing
# Visibility: Private (recommended)
# Don't initialize with README (you already have files)

# Push to GitHub:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/visa-processing.git
git push -u origin main
```

---

### Step 5: Deploy Backend to Railway (10 minutes)

1. **Sign up**: https://railway.app
   - Use GitHub login
   - Add payment method (you get $5 free credit monthly)

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `visa-processing` repo

3. **Configure Service**:
   - Service name: `visa-backend`
   - Click "Settings" → "Root Directory"
   - Set to: `backend`

4. **Add Environment Variables** (Settings → Variables):
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   GEMINI_API_KEY=your_actual_gemini_api_key
   SECRET_KEY=your_secret_key_here
   DEBUG=False
   CORS_ORIGINS=https://your-app.vercel.app
   FRONTEND_URL=https://your-app.vercel.app
   MAX_FILE_SIZE=10485760
   LOG_LEVEL=INFO
   ```

5. **Deploy**:
   - Railway auto-deploys
   - Wait 2-3 minutes
   - Copy the generated URL: `https://visa-backend-production-xyz.up.railway.app`

6. **Verify**:
   - Visit: `https://your-backend-url.railway.app/docs`
   - Test health endpoint: `https://your-backend-url.railway.app/api/health`

---

### Step 6: Deploy Frontend to Vercel (10 minutes)

1. **Sign up**: https://vercel.com
   - Use GitHub login (100% free for hobby projects)

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import `visa-processing` repo from GitHub

3. **Configure Build**:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://visa-backend-production-xyz.up.railway.app
   ```
   (Use your actual Railway backend URL)

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Copy URL: `https://visa-processing.vercel.app`

---

### Step 7: Update CORS Configuration (5 minutes)

Go back to **Railway** → Your backend service → Variables:

Update these variables with your actual Vercel URL:
```
CORS_ORIGINS=https://visa-processing.vercel.app
FRONTEND_URL=https://visa-processing.vercel.app
```

Railway will automatically redeploy with new settings.

---

### Step 8: Update Frontend API Configuration (2 minutes)

In your local code, update `frontend/src/services/api.js`:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

Commit and push:
```bash
git add .
git commit -m "Update API configuration for production"
git push
```

Vercel will auto-deploy the changes in ~2 minutes.

---

## 🧪 Testing Your Deployment

### Test Backend:
```bash
# Health check
curl https://your-backend.railway.app/api/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-02-03T...",
  "database": "connected"
}
```

### Test Frontend:
1. Visit: https://your-app.vercel.app
2. Click "Create New Application"
3. Fill in applicant details
4. Upload a test PDF document
5. Click "Analyze Documents"
6. Generate documents (visiting card, asset valuation)
7. Download generated PDFs

---

## 🔧 Troubleshooting

### Backend Issues:

**"Database connection failed"**
- Check DATABASE_URL in Railway has `?sslmode=require` at the end
- Verify Neon database is not paused (it auto-resumes on connection)

**"CORS error"**
- Verify CORS_ORIGINS in Railway matches your Vercel URL exactly
- Check for trailing slashes (should NOT have them)

**"Service unhealthy"**
- Check Railway logs: Service → "Logs" tab
- Common issue: Missing environment variables

### Frontend Issues:

**"Cannot reach API"**
- Verify VITE_API_URL in Vercel points to Railway backend
- Check Railway backend is running (visit /docs endpoint)

**Build fails**
- Check Vercel build logs
- Ensure `package.json` has all dependencies
- Verify Node version compatibility

### Get Logs:

**Railway logs:**
```bash
# Or view in dashboard
railway logs --service visa-backend
```

**Vercel logs:**
- Dashboard → Your Project → "Logs" tab
- Real-time function logs

---

## 💰 Cost Estimate

| Service | Cost | What You Get |
|---------|------|--------------|
| **Vercel** | **$0** | Unlimited deployments, 100GB bandwidth |
| **Railway** | **$5/month** | 500 hours execution, $5 credit included |
| **Neon** | **$0** | 0.5GB storage (enough for 5000+ apps) |
| **Gemini AI** | **$0-5/month** | Free tier: 1500 requests/day |
| **TOTAL** | **$5-10/month** | Production-ready system |

---

## 🎯 Post-Deployment Checklist

- [ ] Backend deployed and health check passing ✅
- [ ] Frontend deployed and accessible ✅
- [ ] CORS configured correctly ✅
- [ ] Environment variables set ✅
- [ ] Database connected ✅
- [ ] Gemini API working ✅
- [ ] Test full workflow: upload → analyze → generate ✅
- [ ] Download generated PDFs working ✅
- [ ] Set up monitoring alerts (optional)
- [ ] Share URL with first users 🎉

---

## 🚀 Automatic Deployments

From now on, every time you push to GitHub:
```bash
git add .
git commit -m "Your changes"
git push
```

- **Railway** auto-deploys backend (2-3 min)
- **Vercel** auto-deploys frontend (2-3 min)

You can watch deployments in each dashboard!

---

## 📊 Monitoring

### Railway Dashboard:
- CPU/Memory usage
- Request count
- Response times
- Error rates

### Vercel Analytics:
- Page views
- Load times
- Visitor count
- Geographic distribution

### Neon Monitoring:
- Database size
- Query performance
- Connection count
- Storage usage

---

## 🎉 You're Done!

Your visa processing system is now:
- ✅ Live and accessible globally
- ✅ Auto-deploying on every git push
- ✅ Backed by production database
- ✅ Cost-optimized ($5-10/month)
- ✅ Scalable to 1000+ applications

**Share your Vercel URL and start processing visa applications!** 🚀

---

## 🆘 Need Help?

Common commands:
```bash
# Check Railway status
railway status

# View Railway logs
railway logs

# Redeploy Vercel
vercel --prod

# Check database
psql "postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

Issues? Check:
1. Railway logs for backend errors
2. Vercel logs for frontend errors
3. Browser console for client errors
4. Network tab for API call failures
