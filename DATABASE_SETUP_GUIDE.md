# COMPLETE DATABASE SETUP VERIFICATION CHECKLIST

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. DATABASE SETUP (5-10 minutes)

**Copy and run the SQL script:**
- File: `database/COMPLETE_NEON_SETUP.sql`
- Location: Neon.tech → SQL Editor
- Action: Copy entire file, paste, click "Run"

**Expected success output:**
```
DATABASE SETUP COMPLETE!

Tables Created:
- analysis_sessions (11 columns)
- ai_interactions (7 columns)
- documents (12 columns)
- extracted_data (7 columns)
- generated_documents (10 columns)
- questionnaire_responses (10 columns)
- required_documents (7 columns)
- visa_applications (11 columns)

Enum Types Created:
- analysis_status: ['pending', 'started', 'analyzing', 'completed', 'failed']
- application_status: ['DRAFT', 'DOCUMENTS_UPLOADED', 'ANALYZING', 'GENERATING', 'COMPLETED', 'FAILED']
- document_type: [21 document types - lowercase]
- generation_status: ['pending', 'generating', 'completed', 'failed']
- question_category: [7 categories - lowercase]
- question_data_type: [7 types - lowercase]

Required Documents for Iceland Tourist Visa:
total_documents: 16
mandatory_docs: 7
ai_generated_docs: 9
```

**If you see errors:**
- Make sure you're connected to the correct database
- Check if you have write permissions
- Try running in smaller sections if needed

---

### 2. BACKEND DEPLOYMENT (Auto-triggered, 7-10 minutes)

**Status:** Render auto-deploys when you pushed code

**Check deployment:**
1. Go to: https://dashboard.render.com
2. Find service: `visa-backend` or `visaprocessor`
3. Click on it → Check "Logs" tab

**Wait for this line:**
```
==> Your service is live 🎉
==> Available at your primary URL https://visaprocessor.onrender.com
```

**Verify backend is working:**
```bash
curl https://visaprocessor.onrender.com
```

**Expected response:**
```json
{"message":"Visa Document Processing System API","version":"1.0.0","status":"operational"}
```

---

### 3. FRONTEND VERIFICATION (No action needed)

**URL:** https://visa-processor.vercel.app

**Frontend is already deployed and configured with:**
- `VITE_API_URL` = `https://visaprocessor.onrender.com/api`
- CORS properly configured

---

## ✅ POST-DEPLOYMENT TESTING

### Test 1: Create Application

1. Go to: https://visa-processor.vercel.app
2. Click "Create New Application"
3. Fill in:
   - Name: `Test User`
   - Email: `test@example.com`
   - Phone: `1234567890`
4. Click "Create"

**Expected:**
- ✅ Success message
- ✅ Application number like `VISA-XXXXX`
- ✅ Redirects to application details page

**If error:**
- Check browser console (F12 → Console tab)
- Check Render logs for backend errors
- Verify database connection

---

### Test 2: View Applications List

1. Go to homepage
2. Should see the test application in the list

**Expected:**
- ✅ Application shows with DRAFT status
- ✅ Application number visible
- ✅ Created timestamp shows

---

### Test 3: Application Details

1. Click on the test application
2. Should see details page

**Expected:**
- ✅ Application info displayed
- ✅ Document upload section visible
- ✅ No errors in console

---

## 🔍 TROUBLESHOOTING

### Problem: "Column does not exist" error
**Solution:** Database schema mismatch
```sql
-- Run this to check columns:
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'visa_applications';
```

### Problem: "Invalid enum value" error
**Solution:** Enum case mismatch
```sql
-- Check enum values:
SELECT enumlabel 
FROM pg_enum 
JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
WHERE pg_type.typname = 'application_status';
```

### Problem: Backend not responding
**Solution:** Check Render status
1. Render dashboard → visa-backend → Logs
2. Look for "Your service is live" message
3. If stuck, click "Manual Deploy" → "Deploy latest commit"

### Problem: CORS error
**Solution:** Check CORS_ORIGINS in Render
1. Render → visa-backend → Environment
2. Verify: `CORS_ORIGINS=https://visa-processor.vercel.app,http://localhost:5173`
3. If changed, redeploy

---

## 📊 DATABASE SCHEMA SUMMARY

### visa_applications
- **Purpose:** Main application records
- **Key columns:** application_number, status, applicant_name/email/phone
- **Status values:** DRAFT, DOCUMENTS_UPLOADED, ANALYZING, GENERATING, COMPLETED, FAILED

### documents
- **Purpose:** Uploaded and generated documents
- **Key columns:** document_type, file_path, is_uploaded
- **Document types:** 21 types (passport_copy, nid_bangla, cover_letter, etc.)

### ai_interactions
- **Purpose:** Track AI processing
- **Key columns:** interaction_type, prompt, response, model_used

### required_documents
- **Purpose:** Define what documents are needed
- **Pre-populated:** 16 documents for Iceland Tourist visa

### generated_documents
- **Purpose:** Track AI-generated documents
- **Key columns:** document_type, file_path, status, generation_progress

### questionnaire_responses
- **Purpose:** Store user answers to questions
- **Key columns:** question_key, answer, category

### analysis_sessions
- **Purpose:** Track document analysis progress
- **Key columns:** status, completeness_score, missing_fields

### extracted_data
- **Purpose:** Store extracted information from documents
- **Key columns:** data (JSONB), confidence_score

---

## 🎯 SUCCESS CRITERIA

All systems working when:
1. ✅ Database shows 8 tables created
2. ✅ Backend returns JSON at https://visaprocessor.onrender.com
3. ✅ Frontend loads at https://visa-processor.vercel.app
4. ✅ Can create new application successfully
5. ✅ Application appears in list with DRAFT status
6. ✅ No errors in browser console
7. ✅ No errors in Render backend logs

---

## 📝 CURRENT CONFIGURATION

**Database:** Neon PostgreSQL
- Host: ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech
- Database: neondb
- Connection via: DATABASE_URL environment variable

**Backend:** Render.com
- URL: https://visaprocessor.onrender.com
- Runtime: Python 3.11.9
- Free tier (may sleep after inactivity)

**Frontend:** Vercel
- URL: https://visa-processor.vercel.app
- Framework: React + Vite
- API URL: https://visaprocessor.onrender.com/api

---

## ⏭️ NEXT STEPS AFTER SUCCESS

1. Test document upload functionality
2. Test document analysis with Gemini AI
3. Test document generation
4. Add more test applications
5. Monitor Render logs for any issues
6. Consider upgrading to paid tier if needed (for always-on backend)
