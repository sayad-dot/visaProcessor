# 🚀 PRODUCTION DEPLOYMENT GUIDE

## Overview
This guide covers deploying all recent changes to production:
- **Frontend**: Vercel (auto-deploys from GitHub)
- **Backend**: Render (auto-deploys from GitHub)
- **Database**: Neon PostgreSQL

## ⚠️ CRITICAL: Deployment Order
**You MUST follow this exact order to avoid errors:**

1. ✅ Commit & Push to GitHub
2. ✅ Run Database Migration on Neon
3. ✅ Deploy Backend & Frontend (auto)

---

## Step 1: Commit & Push Changes to GitHub

### 1.1 Check Status
```bash
cd /media/sayad/Ubuntu-Data/visa
git status
```

### 1.2 Add All Changes
```bash
# Add all modified files
git add backend/app/api/endpoints/applications.py
git add backend/app/models.py
git add backend/app/schemas.py
git add frontend/src/components/DocumentCard.jsx
git add frontend/src/components/ProgressTracker.jsx
git add frontend/src/pages/NewApplicationPage.jsx
git add frontend/src/pages/ApplicationDetailsPage.jsx

# Add new database script
git add database/seed_documents.py
git add database/production_migration.sql
```

### 1.3 Commit Changes
```bash
git commit -m "feat: Add business vs job document differentiation

- Added application_type field to RequiredDocument model
- Business applicants: 14 documents (2 required, 12 optional)
- Job applicants: 15 documents (2 required, 13 optional)
- Updated frontend UI with new 2-column layout
- Fixed required document badges (both passport and NID Bangla show as required)
- Added dynamic document counts in ProgressTracker
- Added new document types: payslip, bank_statement, job_noc, job_id_card"
```

### 1.4 Push to GitHub
```bash
git push origin main
```

**✅ Wait for this to complete before proceeding!**

---

## Step 2: Run Database Migration on Neon

### 2.1 Access Neon Console
1. Go to https://console.neon.tech
2. Select your project: **neondb**
3. Click **SQL Editor**

### 2.2 Run Migration Script
1. Copy the entire contents of `/media/sayad/Ubuntu-Data/visa/database/production_migration.sql`
2. Paste it into the Neon SQL Editor
3. Click **Run** or press `Ctrl+Enter`

### 2.3 Verify Migration Success
You should see this output at the end:
```
application_type | total_documents | required_documents | optional_documents
----------------+----------------+-------------------+-------------------
business        | 14             | 2                 | 12
job             | 15             | 2                 | 13
```

**✅ If you see this, migration is successful!**

### 2.4 What This Migration Does:
- ✅ Adds new document types (payslip, bank_statement, job_noc, job_id_card)
- ✅ Adds `application_type` column to `required_documents` table
- ✅ Updates unique constraint to include `application_type`
- ✅ Clears old data and seeds correct documents for both business and job types

---

## Step 3: Deploy Backend (Render)

### 3.1 Auto-Deploy from GitHub
Render will automatically detect your GitHub push and start deploying.

### 3.2 Monitor Deployment
1. Go to https://dashboard.render.com
2. Find your backend service (visa-backend or similar)
3. Click on it to see deployment logs
4. Wait for **"Build successful"** and **"Deploy live"** messages

### 3.3 Check Backend Health
After deployment completes:
```bash
curl https://your-backend-url.onrender.com/health
```

Or visit: https://your-backend-url.onrender.com/docs

**✅ If you see API docs, backend is live!**

---

## Step 4: Deploy Frontend (Vercel)

### 4.1 Auto-Deploy from GitHub
Vercel will automatically detect your GitHub push and start deploying.

### 4.2 Monitor Deployment
1. Go to https://vercel.com/dashboard
2. Find your frontend project (visa-frontend or similar)
3. Click on it to see deployment status
4. Wait for **"Deployment Complete"** (usually 1-2 minutes)

### 4.3 Check Frontend Health
Visit your production URL:
```
https://your-app.vercel.app
```

**✅ If you see your app, frontend is live!**

---

## Step 5: Test Production System

### 5.1 Create Test Application
1. Go to your production URL
2. Click **New Application**
3. Fill in details:
   - Name: Test User
   - Email: test@example.com
   - Phone: +880123456789
   - Country: Iceland
   - Visa Type: Tourist
   - Applicant Type: **Business Owner**

4. Click **CREATE APPLICATION**

### 5.2 Verify Business Documents
You should see:
- ✅ **Required Documents: 0/2** (Passport Copy ❌, NID Bangla ❌)
- ✅ **Optional Documents: 0/12** (all blue badges)
- ✅ **AI Will Generate: 12/12 ⭐**
- ✅ Total 14 documents

### 5.3 Test Job Application
1. Go back and create another application
2. Change **Applicant Type** to: **Job Holder**
3. You should see:
   - ✅ **Required Documents: 0/2** (Passport Copy ❌, NID Bangla ❌)
   - ✅ **Optional Documents: 0/13** (all blue badges)
   - ✅ **AI Will Generate: 13/13 ⭐**
   - ✅ Total 15 documents (includes JOB NOC, JOB ID card, Payslip)

---

## 🎯 Success Checklist

- [ ] All files committed and pushed to GitHub
- [ ] Neon database migration completed successfully
- [ ] Render backend deployment succeeded
- [ ] Vercel frontend deployment succeeded
- [ ] Business applicants show 14 documents (2 required, 12 optional)
- [ ] Job applicants show 15 documents (2 required, 13 optional)
- [ ] Both Passport and NID Bangla show as required (red badges)
- [ ] New application page shows beautiful 2-column layout

---

## 🚨 Troubleshooting

### Issue: Backend deployment fails
**Solution**: Check Render logs for errors. Common issues:
- Missing environment variables
- Database connection issues

### Issue: Frontend shows old design
**Solution**: 
- Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear browser cache
- Check Vercel deployment logs

### Issue: Documents not showing correctly
**Solution**: 
1. Verify database migration ran successfully
2. Check backend logs on Render
3. Verify API endpoint: `https://your-backend-url.onrender.com/docs`

### Issue: "Application not found" error
**Solution**: 
- Make sure backend is connected to Neon database
- Check DATABASE_URL environment variable in Render

---

## 📝 Rollback Plan (If Needed)

If something goes wrong:

### Rollback Database:
```sql
-- Connect to Neon SQL Editor
DELETE FROM required_documents;
-- Then re-run old seed data if you have it backed up
```

### Rollback Code:
```bash
# Revert to previous commit
git revert HEAD
git push origin main
```

Wait for Render and Vercel to auto-deploy the reverted version.

---

## ✅ Post-Deployment

After successful deployment:
1. Test all features thoroughly
2. Monitor error logs for 24 hours
3. Inform users about new features
4. Document any issues in GitHub Issues

---

## 🎉 You're Done!

Your production system is now updated with:
- ✅ Different document requirements for Business vs Job applicants
- ✅ Beautiful new application form design
- ✅ Correct required document badges
- ✅ Dynamic document counts

**Deployment Date**: {{ DATE }}
**Deployed By**: {{ YOUR_NAME }}
