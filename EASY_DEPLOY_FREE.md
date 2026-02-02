# 🚀 Easy FREE Deployment Guide

## 💰 Total Cost: **$0/month** - Completely FREE!

### Stack:
- **Frontend**: Vercel (FREE forever)
- **Backend**: Render.com (FREE forever)
- **Database**: Neon PostgreSQL (FREE - already set up ✅)
- **Storage**: Local disk (FREE)
- **AI**: Gemini Flash Exp (FREE)

---

## ✅ What's Already Done:

1. ✅ Database created on Neon
2. ✅ All tables and data initialized
3. ✅ Backend code ready
4. ✅ Frontend code ready
5. ✅ Templates working

---

## 🎯 Step 1: Get Your Gemini API Key (2 minutes)

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key (looks like: `AIzaSy...`)
4. Save it for later

---

## 🎯 Step 2: Push Code to GitHub (3 minutes)

### If you DON'T have a GitHub account:
1. Create one: https://github.com/signup (takes 2 minutes)

### Push your code:

```bash
cd /media/sayad/Ubuntu-Data/visa

# Remove old git history if exists
rm -rf .git

# Initialize new repo
git init
git add .
git commit -m "Initial commit - visa processing system"

# Create repo on GitHub (do this in browser):
# 1. Go to https://github.com/new
# 2. Name: visa-processing
# 3. Click "Create repository" (keep it PUBLIC)

# Connect and push (replace YOUR_USERNAME with your GitHub username)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/visa-processing.git
git push -u origin main
```

**Stuck?** Just tell me your GitHub username and I'll give you exact commands!

---

## 🎯 Step 3: Deploy Backend on Render.com (5 minutes)

1. **Sign up**: https://render.com
   - Use "Sign in with GitHub" (easiest!)

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Select your `visa-processing` repository
   - Click "Connect"

3. **Configure**:
   - **Name**: `visa-backend`
   - **Region**: Oregon (US West)
   - **Branch**: main
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: FREE

4. **Add Environment Variables** (click "Add Environment Variable"):
   ```
   DATABASE_URL = postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   
   GEMINI_API_KEY = [YOUR KEY FROM STEP 1]
   
   SECRET_KEY = [Generate one with: openssl rand -hex 32]
   
   DEBUG = False
   
   CORS_ORIGINS = http://localhost:5173
   
   MAX_FILE_SIZE = 10485760
   
   UPLOAD_FOLDER = /tmp/uploads
   
   GENERATED_FOLDER = /tmp/generated
   
   LOG_LEVEL = INFO
   ```

5. **Deploy**:
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Copy your URL: `https://visa-backend.onrender.com`

---

## 🎯 Step 4: Deploy Frontend on Vercel (3 minutes)

1. **Sign up**: https://vercel.com
   - Use "Continue with GitHub" (easiest!)

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Select `visa-processing` repository
   - Click "Import"

3. **Configure**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

4. **Add Environment Variable**:
   ```
   VITE_API_URL = https://visa-backend.onrender.com
   ```
   (Use the URL from Step 3)

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Copy your URL: `https://visa-processing.vercel.app`

---

## 🎯 Step 5: Update CORS (1 minute)

Go back to Render.com:
1. Open your `visa-backend` service
2. Go to "Environment" tab
3. Edit `CORS_ORIGINS` variable:
   ```
   https://visa-processing.vercel.app
   ```
4. Click "Save Changes"
5. Service will auto-redeploy (2-3 minutes)

---

## 🎉 Done! Test Your App

1. Open your Vercel URL: `https://visa-processing.vercel.app`
2. Create a new visa application
3. Upload some documents
4. Watch the AI analyze them
5. Generate visiting card and asset valuation

---

## 🐛 Troubleshooting

### Backend won't start:
- Check Render logs: Dashboard → visa-backend → Logs
- Most common: Missing GEMINI_API_KEY

### Frontend can't reach backend:
- Check CORS_ORIGINS matches your Vercel URL exactly
- Check VITE_API_URL in Vercel environment variables

### Database errors:
- Your Neon connection is already working ✅
- If issues, verify DATABASE_URL in Render matches exactly

---

## 📝 Important Notes

### Render.com FREE tier:
- ✅ 750 hours/month (enough for 1 service 24/7)
- ✅ Sleeps after 15 min inactivity
- ✅ First request wakes it (30 seconds)
- ✅ No credit card required
- ✅ 512 MB RAM, 0.1 CPU

### Vercel FREE tier:
- ✅ Unlimited projects
- ✅ 100 GB bandwidth
- ✅ Always online
- ✅ Global CDN
- ✅ No credit card required

### Perfect for:
- Personal projects
- Testing
- Small business (5-50 apps/month)
- Portfolio demonstrations

---

## 🚀 Quick Commands Reference

### Generate SECRET_KEY:
```bash
openssl rand -hex 32
```

### Test backend locally:
```bash
cd backend
uvicorn app.main:app --reload
```

### Test frontend locally:
```bash
cd frontend
npm run dev
```

### Update deployment (after code changes):
```bash
git add .
git commit -m "Your changes"
git push
# Render + Vercel auto-deploy in 3-5 minutes
```

---

## 💡 Need Help?

Just ask! I can:
- Generate your exact git commands with your username
- Explain any step in detail
- Help debug deployment issues
- Show you how to add custom domain (FREE with Vercel)

**Let's get you deployed! 🚀**
