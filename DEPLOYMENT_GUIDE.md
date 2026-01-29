# 🚀 Deployment Guide - Budget-Optimized Stack

## 💰 Total Cost: **$5-15/month** (Scales with usage)

### Stack Architecture:
- **Frontend**: Vercel (FREE)
- **Backend**: Railway ($5/month)
- **Database**: Neon PostgreSQL (FREE - 0.5GB)
- **Storage**: Cloudflare R2 (~$0.015/GB)
- **AI**: Gemini 2.0 Flash Exp (FREE) + Flash ($0.01/app)

---

## 📊 Cost Breakdown

| Service | Tier | Monthly Cost | What You Get |
|---------|------|--------------|--------------|
| **Vercel** | Hobby | **FREE** | Unlimited sites, 100GB bandwidth, global CDN |
| **Railway** | Hobby | **$5** | 500 hours/month, $5 credit (perfect for 1 backend) |
| **Neon DB** | Free | **FREE** | 0.5GB storage, 1 branch, auto-suspend |
| **Cloudflare R2** | Pay-as-you-go | **$0-10** | Free 10GB/month, then $0.015/GB |
| **Gemini AI** | Free + Paid | **$0-5** | Free tier: 1500 req/day, Paid: $0.01/app |
| **TOTAL** | | **$5-15** | Handles 100-500 apps/month easily |

### Cost at Scale:
- **0-100 apps/month**: $5 (just Railway)
- **100-300 apps**: $8-12 (Railway + minimal storage)
- **300-500 apps**: $12-15 (Railway + storage + minimal AI)
- **500+ apps**: Upgrade Railway to $20/month

---

## 🎯 Step 1: Database Setup (Neon PostgreSQL)

### Why Neon?
- ✅ FREE 0.5GB forever (enough for 5,000+ applications)
- ✅ Auto-suspend when idle (saves resources)
- ✅ PostgreSQL compatible (no code changes needed)
- ✅ Fast connection pooling
- ✅ Daily backups included

### Setup Steps:

1. **Sign up**: https://neon.tech
   - Use GitHub/Google login (instant)

2. **Create Project**:
   ```
   Project Name: visa-processing
   Region: US East (Ohio) - closest to Railway
   PostgreSQL Version: 16
   ```

3. **Get Connection String**:
   - Click "Connection Details"
   - Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/visa_db?sslmode=require
   ```

4. **Initialize Database**:
   - Go to "SQL Editor" in Neon dashboard
   - Run your schema (from `database/schema.sql`)
   - Or connect via psql:
   ```bash
   psql "postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/visa_db?sslmode=require"
   ```

---

## 🎯 Step 2: Storage Setup (Cloudflare R2)

### Why R2?
- ✅ 10GB FREE monthly
- ✅ 90% cheaper than AWS S3
- ✅ Zero egress fees
- ✅ S3-compatible API
- ✅ Global CDN included

### Setup Steps:

1. **Sign up**: https://cloudflare.com
   - Create account (free tier)

2. **Create R2 Bucket**:
   - Dashboard → R2 → "Create bucket"
   - Bucket name: `visa-documents`
   - Location: Automatic (multi-region)

3. **Get API Credentials**:
   - Go to R2 → Manage R2 API Tokens
   - Create API token:
     - Permissions: Read & Write
     - Bucket: visa-documents
   - Save:
     - Access Key ID
     - Secret Access Key
     - Endpoint URL (e.g., https://abc123.r2.cloudflarestorage.com)

4. **Update Backend Code** (optional - for cloud storage):
   ```python
   # backend/.env
   STORAGE_TYPE=r2  # or 'local' for Railway disk
   R2_ACCESS_KEY=your_access_key
   R2_SECRET_KEY=your_secret_key
   R2_ENDPOINT=https://abc123.r2.cloudflarestorage.com
   R2_BUCKET=visa-documents
   ```

---

## 🎯 Step 3: Backend Deployment (Railway)

### Why Railway?
- ✅ $5/month for 500 hours (perfect for single app)
- ✅ Auto-deploy from GitHub
- ✅ Built-in PostgreSQL option (but Neon is better)
- ✅ Environment variables management
- ✅ Automatic HTTPS
- ✅ Health checks + auto-restart

### Setup Steps:

1. **Sign up**: https://railway.app
   - Use GitHub login

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your visa processing repo

3. **Configure Service**:
   - Service name: `visa-backend`
   - Root directory: `/backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables**:
   ```
   DATABASE_URL=postgresql://user:password@neon-host.aws.neon.tech/visa_db?sslmode=require
   GEMINI_API_KEY=your_gemini_api_key
   FRONTEND_URL=https://your-app.vercel.app
   ALLOWED_ORIGINS=https://your-app.vercel.app
   SECRET_KEY=your_secret_key_here
   STORAGE_TYPE=local
   ```

5. **Deploy**:
   - Railway auto-deploys on git push
   - Copy the generated URL: `https://visa-backend-production-xyz.up.railway.app`

6. **Verify**:
   ```bash
   curl https://visa-backend-production-xyz.up.railway.app/api/health
   ```

---

## 🎯 Step 4: Frontend Deployment (Vercel)

### Why Vercel?
- ✅ Completely FREE for hobby projects
- ✅ Made for React/Vite apps
- ✅ Global CDN (300+ locations)
- ✅ Auto-preview deployments
- ✅ Instant rollbacks
- ✅ Automatic HTTPS

### Setup Steps:

1. **Sign up**: https://vercel.com
   - Use GitHub login

2. **Import Project**:
   - Click "Add New..." → "Project"
   - Import your GitHub repo
   - Vercel auto-detects Vite

3. **Configure Build**:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables**:
   ```
   VITE_API_URL=https://visa-backend-production-xyz.up.railway.app
   ```

5. **Update Backend URL in Code**:
   - Edit `frontend/src/config/api.js`:
   ```javascript
   export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```

6. **Deploy**:
   - Click "Deploy"
   - Vercel builds and deploys automatically
   - Copy URL: `https://visa-processing.vercel.app`

7. **Update Railway Backend**:
   - Go back to Railway
   - Update `FRONTEND_URL` and `ALLOWED_ORIGINS`:
   ```
   FRONTEND_URL=https://visa-processing.vercel.app
   ALLOWED_ORIGINS=https://visa-processing.vercel.app
   ```

---

## 🎯 Step 5: AI Configuration (Gemini)

### Free Tier Strategy:
- **Analysis**: Use `gemini-2.0-flash-exp` (FREE experimental model)
- **Critical Generation**: Use `gemini-2.0-flash` (paid but cheap)

### Update Backend:

Edit `backend/.env`:
```bash
# AI Model Configuration
GEMINI_MODEL_ANALYSIS=gemini-2.0-flash-exp  # FREE for analysis
GEMINI_MODEL_GENERATION=gemini-2.0-flash    # Cheap for generation
```

Edit `backend/app/services/ai_analysis_service.py` (line 20):
```python
model = genai.GenerativeModel(os.getenv('GEMINI_MODEL_ANALYSIS', 'gemini-2.0-flash-exp'))
```

Edit `backend/app/services/pdf_generator_service.py` (line 34):
```python
model = genai.GenerativeModel(os.getenv('GEMINI_MODEL_GENERATION', 'gemini-2.0-flash'))
```

### Cost Estimate:
- Analysis (8 docs): FREE with experimental model
- Generation (8 docs): ~$0.01 per application
- **100 apps/month**: ~$1 AI cost
- **500 apps/month**: ~$5 AI cost

---

## 🚀 Deployment Commands

### First-Time Setup:

```bash
# 1. Initialize git (already done)
cd /media/sayad/Ubuntu-Data/visa
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit - visa processing system"

# 4. Create GitHub repo (via web interface)
# Go to github.com → New repository → "visa-processing"

# 5. Push to GitHub
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/visa-processing.git
git push -u origin main

# 6. Deploy backend to Railway
# - Connect GitHub repo in Railway dashboard
# - Auto-deploys on push

# 7. Deploy frontend to Vercel
# - Connect GitHub repo in Vercel dashboard
# - Auto-deploys on push
```

### Continuous Deployment:

After initial setup, every code change auto-deploys:
```bash
git add .
git commit -m "Your change description"
git push
# Railway + Vercel auto-deploy in 2-3 minutes
```

---

## 🔒 Security Best Practices

### Environment Variables:
- ✅ **NEVER** commit `.env` files
- ✅ Use Railway/Vercel dashboards for secrets
- ✅ Rotate API keys monthly
- ✅ Use strong `SECRET_KEY` (generate with: `openssl rand -hex 32`)

### Database:
- ✅ Use Neon's built-in connection pooling
- ✅ Enable SSL mode (already in connection string)
- ✅ Regular backups (Neon auto-backups daily)

### API:
- ✅ Enable CORS only for your frontend domain
- ✅ Rate limiting (Railway has built-in protection)
- ✅ File upload size limits (already configured)

---

## 📊 Monitoring & Logs

### Railway:
- Go to your service → "Logs" tab
- Real-time logs for debugging
- Filter by error/warning/info

### Vercel:
- Project → "Logs" → "Functions"
- Build logs + runtime logs
- Analytics tab shows traffic

### Neon:
- Dashboard → "Monitoring"
- Shows queries, connections, storage usage

---

## 🐛 Troubleshooting

### Backend not starting:
```bash
# Check Railway logs
# Common issues:
# 1. Missing environment variables
# 2. Database connection timeout
# 3. Port binding (use $PORT not 8000)
```

### Frontend can't reach backend:
```bash
# Check CORS settings in Railway:
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Check API URL in Vercel:
VITE_API_URL=https://your-backend.railway.app
```

### Database connection issues:
```bash
# Test connection locally:
psql "postgresql://user:password@neon-host.aws.neon.tech/visa_db?sslmode=require"

# Common fixes:
# 1. Add ?sslmode=require to connection string
# 2. Check IP whitelist (Neon allows all by default)
# 3. Verify username/password
```

---

## 💡 Pro Tips

1. **Enable Railway Webhooks**: Get notified on deployment failures
2. **Use Vercel Preview Deployments**: Test changes before production
3. **Monitor Neon Storage**: Upgrade before hitting 0.5GB limit
4. **Set up Cloudflare CDN**: Cache generated PDFs for faster downloads
5. **Use Railway Sleep Mode**: Save costs during low-traffic hours

---

## 📈 Scaling Strategy

### Month 1-3 (0-100 apps): $5/month
- Railway $5
- Everything else FREE

### Month 4-6 (100-300 apps): $10-12/month
- Railway $5
- Storage $2-5
- AI $3-5

### Month 7+ (300-500 apps): $15-20/month
- Railway $5-10 (upgrade to Pro if needed)
- Storage $5-8
- AI $5-10

### 500+ apps/month: Upgrade Time! 🚀
- Railway Pro: $20/month (more resources)
- Neon Pro: $19/month (1GB + better performance)
- Consider caching layer (Cloudflare Workers)
- Total: $40-50/month for 1000+ apps

---

## ✅ Deployment Checklist

- [ ] Neon PostgreSQL database created
- [ ] Database schema imported
- [ ] Cloudflare R2 bucket created (optional)
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Railway service connected to GitHub
- [ ] Railway environment variables configured
- [ ] Backend deployed and health check passing
- [ ] Vercel project connected to GitHub
- [ ] Vercel environment variables configured
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] Test upload → analyze → generate → download flow
- [ ] Monitor logs for errors

---

## 🎉 You're Live!

Your visa processing system is now:
- ✅ Globally accessible
- ✅ Auto-scaling
- ✅ Auto-deploying
- ✅ Cost-optimized
- ✅ Production-ready

**Share your Vercel URL with users and start processing visa applications!** 🚀
