# 🚀 DEPLOY NOW - 3 Simple Steps!

**Repository**: https://github.com/sayad-dot/visaProcessor ✅  
**Database**: Already setup on Neon ✅  
**Secret Key**: `e0c7cacf5cd65450caabb0ca9f75c7180b9cd68a1cca7ba05d0a99e3838de362`

---

## 🎯 STEP 1: Get Gemini API Key (2 mins)

1. Open: https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. **Copy it** - you'll paste it in Step 2!

---

## 🎯 STEP 2: Deploy Backend on Render.com (5 mins)

### Sign Up:
- Go to: https://render.com
- Click "Sign in with GitHub" → Authorize

### Create Service:
1. Click "New +" → "Web Service"
2. Select "visaProcessor" → "Connect"

### Fill These:
```
Name: visa-backend
Region: Oregon
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### Add Environment Variables:
Click "Add Environment Variable" for each:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require` |
| `GEMINI_API_KEY` | **[YOUR KEY FROM STEP 1]** |
| `SECRET_KEY` | `e0c7cacf5cd65450caabb0ca9f75c7180b9cd68a1cca7ba05d0a99e3838de362` |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | `http://localhost:5173` |
| `MAX_FILE_SIZE` | `10485760` |
| `UPLOAD_FOLDER` | `/tmp/uploads` |
| `GENERATED_FOLDER` | `/tmp/generated` |
| `LOG_LEVEL` | `INFO` |

### Deploy:
- Click "Create Web Service"
- Wait 7-10 minutes
- **SAVE YOUR URL**: `https://visa-backend-XXXXX.onrender.com`

---

## 🎯 STEP 3: Deploy Frontend on Vercel (3 mins)

### Sign Up:
- Go to: https://vercel.com
- Click "Continue with GitHub" → Authorize

### Import:
1. Click "Add New..." → "Project"
2. Find "visaProcessor" → "Import"

### Configure:
```
Framework: Vite (auto-detected)
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

### Environment Variable:
Add one variable:

| Name | Value |
|------|-------|
| `VITE_API_URL` | **[YOUR RENDER URL FROM STEP 2]** |

### Deploy:
- Click "Deploy"
- Wait 2-3 minutes
- **SAVE YOUR URL**: `https://visaprocessor.vercel.app`

---

## 🎯 STEP 4: Update CORS (1 min)

Go back to Render.com:
1. Open "visa-backend" service
2. Go to "Environment" tab
3. Edit `CORS_ORIGINS`
4. Change to: **[YOUR VERCEL URL FROM STEP 3]**
5. Click "Save" (auto-redeploys in 2 mins)

---

## ✅ DONE! Test Your App

Open your Vercel URL and start processing visas! 🎉

---

## ⚠️ Troubleshooting

**Backend fails to build?**
- Check Render logs tab
- Verify GEMINI_API_KEY is set correctly

**Frontend can't connect?**
- Verify VITE_API_URL = exact Render URL (no trailing slash)
- Verify CORS_ORIGINS = exact Vercel URL (no trailing slash)

**Still stuck?** Tell me which step and I'll help! 🚀
