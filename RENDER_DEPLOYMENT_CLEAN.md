# 🔥 RENDER DEPLOYMENT - COMPLETE GUIDE

## 🎯 THE PROBLEM WE FIXED

**Issue**: Render was using `uvicorn app.main:app` instead of `uvicorn main:app`

**Why**: When you created the service manually, Render saved wrong settings in the UI that override config files.

**Solution**: Delete the old service and deploy from Blueprint.

---

## 📋 STEP-BY-STEP DEPLOYMENT

### Step 1: Get Your Gemini API Key (if you don't have it)

1. Go to: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy it (starts with `AIzaSy...`)

---

### Step 2: Push the Blueprint File

```bash
cd /media/sayad/Ubuntu-Data/visa
git add render-blueprint.yaml
git commit -m "Add Render blueprint for clean deployment"
git push origin main
```

---

### Step 3: Delete Old Service (In Render Dashboard)

1. Go to: https://dashboard.render.com
2. Click on **visa-backend** service
3. Click **Settings** tab (bottom left)
4. Scroll all the way down
5. Click **Delete Web Service** (red button)
6. Type the service name to confirm
7. Click **Delete**

---

### Step 4: Deploy from Blueprint

#### Option A: Via Render Dashboard (RECOMMENDED - Easy)

1. Go to: https://dashboard.render.com
2. Click **New +** → **Blueprint**
3. Connect your repository: `sayad-dot/visaProcessor`
4. Render will find `render-blueprint.yaml` automatically ✅
5. Review the configuration:
   - Service: visa-backend
   - Runtime: Python
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT` ✅
6. **IMPORTANT**: Update the `GEMINI_API_KEY` environment variable
   - Click on the environment variable
   - Paste your actual API key
7. Click **Apply**

Render will now deploy correctly! ⏱️ Takes 5-8 minutes.

#### Option B: Via render.yaml (Alternative)

If you want to use the original render.yaml:

1. Make sure `GEMINI_API_KEY` is in your environment variables on Render
2. In Render Dashboard → New + → Blueprint
3. Select `render.yaml` instead of `render-blueprint.yaml`
4. Render will use those settings

---

### Step 5: Watch the Deployment

You should see:

```
✅ Cloning repository...
✅ Installing Python 3.11.9...
✅ Installing dependencies...
✅ Successfully installed fastapi, uvicorn, pydantic...
✅ Starting service...
✅ Running 'uvicorn main:app --host 0.0.0.0 --port $PORT'
✅ INFO: Started server process
✅ INFO: Application startup complete
✅ Your service is live 🎉
```

---

### Step 6: Get Your Backend URL

Once deployed:
- Your backend URL: `https://visa-backend.onrender.com` (or similar)
- Test health: `https://visa-backend.onrender.com/health`
- Should return: `{"status": "healthy", "version": "1.0.0"}`

---

### Step 7: Update Frontend (Vercel)

1. Go to: https://vercel.com/dashboard
2. Click your frontend project
3. Go to **Settings** → **Environment Variables**
4. Update `VITE_API_URL`:
   ```
   VITE_API_URL = https://your-backend.onrender.com/api
   ```
5. Go to **Deployments** tab
6. Click `•••` on latest → **Redeploy**

---

### Step 8: Update Backend CORS

1. Go back to Render dashboard
2. Click visa-backend service
3. Go to **Environment** tab
4. Edit `CORS_ORIGINS`:
   ```
   https://your-frontend.vercel.app
   ```
5. Click Save (service auto-redeploys)

---

## ✅ SUCCESS CHECKLIST

- [ ] Old Render service deleted
- [ ] New service deployed from blueprint
- [ ] Service shows "Live" status
- [ ] `/health` endpoint returns success
- [ ] Frontend `VITE_API_URL` updated
- [ ] Backend `CORS_ORIGINS` updated
- [ ] Both frontend and backend redeployed
- [ ] Test: Create an application in frontend

---

## 🎯 WHAT THIS FIXES

### Before (Broken):
```
Render: uvicorn app.main:app ❌
Looking for: /backend/app/main.py (doesn't exist)
Result: ERROR: Could not import module "app.main"
```

### After (Fixed):
```
Render: uvicorn main:app ✅
Looking for: /backend/main.py (exists!)
Result: INFO: Application startup complete ✅
```

---

## 🔍 WHY BLUEPRINT WORKS

1. **Explicit Configuration**: Blueprint file has exact commands
2. **No UI Override**: Blueprint settings take priority
3. **Version Controlled**: Settings are in your repo
4. **Reproducible**: Anyone can deploy with same settings

---

## 📊 DEPLOYMENT TIMELINE

```
Delete old service:        1 minute
Push blueprint:            30 seconds
Deploy from blueprint:     5-8 minutes
Update frontend:           2 minutes
Update backend CORS:       2 minutes
─────────────────────────────────────
Total:                     ~12 minutes
```

---

## 🐛 TROUBLESHOOTING

### "Blueprint not found"
- Make sure you pushed `render-blueprint.yaml` to GitHub
- Refresh the repository connection in Render

### "Build failed"
- Check that all dependencies install successfully
- Python 3.11.9 should be used automatically

### "Service starts but crashes"
- Check Environment variables are set correctly
- Especially `GEMINI_API_KEY` - must be your actual key

### "Can't connect from frontend"
- Check `CORS_ORIGINS` includes your Vercel URL
- Check `VITE_API_URL` points to Render backend URL

---

## 🎉 ONCE DEPLOYED

Your complete stack:
- ✅ **Frontend**: Vercel (React + Vite)
- ✅ **Backend**: Render (FastAPI + Python)
- ✅ **Database**: Neon (PostgreSQL)
- ✅ **AI**: Google Gemini

**Total Cost**: $0/month 💰

Test your app:
1. Go to your frontend URL
2. Create a new visa application
3. Upload documents
4. Watch the AI analyze them
5. Generate visa documents

**Everything should work perfectly!** 🚀

---

## 💡 PRO TIP

Save your backend and frontend URLs:

```bash
# Backend (Render)
BACKEND_URL=https://visa-backend-xxxx.onrender.com

# Frontend (Vercel)
FRONTEND_URL=https://visa-processor-xxxx.vercel.app
```

You'll need these for CORS and API configuration.

---

## 🆘 STILL HAVING ISSUES?

If deployment still fails after following this guide:

1. Share the **full deployment logs** from Render
2. Share your **service URL**
3. Share the **error message**

I'll help you debug it step by step!
