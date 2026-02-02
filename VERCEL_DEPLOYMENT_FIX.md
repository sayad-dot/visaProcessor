# 🔧 Vercel Deployment - Quick Fix Guide

## ❌ Common Issues & Solutions

### Issue 1: Build Configuration Mismatch
**Problem**: Output directory doesn't match
**Fixed**: Updated `vercel.json` to use `frontend/build` (matches `vite.config.js`)

### Issue 2: Missing Environment Variable
**Problem**: Frontend can't connect to backend
**Solution**: Add environment variable in Vercel

---

## ✅ Correct Vercel Setup

### Step 1: Project Settings

Go to your Vercel project → **Settings** → **General**

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build (auto-detected)
Output Directory: build (auto-detected)
Install Command: npm install (auto-detected)
```

### Step 2: Environment Variables

Go to **Settings** → **Environment Variables**

Add this variable:

```
Name: VITE_API_URL
Value: https://your-backend-name.onrender.com/api
Environment: Production, Preview, Development
```

**Important**: Replace `your-backend-name` with your actual Render backend URL!

### Step 3: Redeploy

After adding environment variables:
1. Go to **Deployments** tab
2. Click the three dots `...` on the latest deployment
3. Click **Redeploy**
4. Wait 2-3 minutes

---

## 🎯 Deploy Backend First (Render.com)

You MUST deploy the backend before frontend!

### Quick Render Setup:

1. **Sign up**: https://render.com (use GitHub login)

2. **New Web Service**:
   - Repository: `sayad-dot/visaProcessor`
   - Name: `visa-backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: **Free**

3. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
   
   GEMINI_API_KEY=your_gemini_api_key_here
   
   SECRET_KEY=generate_random_key_here
   
   DEBUG=False
   
   CORS_ORIGINS=https://your-project.vercel.app
   
   DB_USER=neondb_owner
   
   DB_PASSWORD=npg_gTl49fAVCaYI
   
   DB_HOST=ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech
   
   DB_PORT=5432
   
   DB_NAME=neondb
   
   UPLOAD_FOLDER=/tmp/uploads
   
   GENERATED_FOLDER=/tmp/generated
   
   LOG_LEVEL=INFO
   ```

4. **Deploy** and copy your URL: `https://visa-backend-xxxx.onrender.com`

---

## 🔄 Complete Deployment Order

### 1. Backend (Render) - 5 minutes
✅ Get backend URL: `https://visa-backend-xxxx.onrender.com`

### 2. Frontend (Vercel) - 3 minutes
✅ Add `VITE_API_URL` with backend URL
✅ Deploy

### 3. Update CORS (Render) - 1 minute
✅ Go back to Render backend
✅ Update `CORS_ORIGINS` with Vercel URL
✅ Save (auto-redeploys)

---

## 🐛 Troubleshooting Vercel

### "Build failed"
**Check**: 
- Root directory is set to `frontend`
- Build command is `npm run build`
- Output directory is `build`

### "Cannot connect to backend"
**Check**:
- `VITE_API_URL` environment variable is set
- Backend URL ends with `/api`
- Backend is deployed and running on Render

### "API calls return 404"
**Check**:
- Backend CORS includes your Vercel URL
- VITE_API_URL format: `https://backend.onrender.com/api`

### "Still not working after fixes"
**Do this**:
1. Go to Vercel Deployments tab
2. Click `...` → Redeploy
3. Make sure to redeploy with environment variables

---

## 📝 Current File Status

✅ Fixed Files:
- `vercel.json` - Corrected output directory
- `frontend/.env.example` - Environment variable template

✅ Configuration:
- Output: `frontend/build` (matches vite.config.js)
- Framework: Vite (auto-detected)
- Root: `frontend`

---

## 🚀 Quick Redeploy Steps

If deployment failed, follow these exact steps:

### 1. On Vercel Dashboard:
```
Settings → General:
  ✓ Root Directory: frontend
  
Settings → Environment Variables:
  ✓ VITE_API_URL = https://your-backend.onrender.com/api
  
Deployments:
  ✓ Click latest deployment → ... → Redeploy
```

### 2. Wait for Build:
- Should take 2-3 minutes
- Watch build logs for errors
- Look for: "Build Completed" ✅

### 3. Test Your App:
- Open your Vercel URL
- Check browser console for errors
- Try creating an application

---

## 💡 Pro Tips

### Check Backend is Running:
Visit: `https://your-backend.onrender.com/api/health`
Should return: `{"status": "healthy"}`

### Check Environment Variables:
In Vercel project → Settings → Environment Variables
Make sure `VITE_API_URL` is set for all environments

### View Build Logs:
Deployments → Click deployment → View Function Logs
This shows what went wrong during build

---

## 📞 Need Help?

### Backend not deployed?
Follow: [EASY_DEPLOY_FREE.md](EASY_DEPLOY_FREE.md#-step-3-deploy-backend-on-rendercom-5-minutes)

### Still stuck?
Share:
1. Vercel build logs (full output)
2. Your backend URL
3. Environment variables (hide sensitive data)

---

## ✅ Success Checklist

- [ ] Backend deployed on Render
- [ ] Backend URL obtained
- [ ] VITE_API_URL added in Vercel
- [ ] CORS updated in Render backend
- [ ] Vercel redeployed
- [ ] App tested and working

Once all checked, your app should be live! 🎉
