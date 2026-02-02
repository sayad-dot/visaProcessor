# 🗄️ Neon Database Setup Guide

## Quick Setup (Recommended)

### Option 1: Automated Setup Script

```bash
cd /media/sayad/Ubuntu-Data/visa
./database/setup_neon.sh
```

This script will:
- ✅ Test connection to Neon
- ✅ Create all tables and types
- ✅ Insert required documents
- ✅ Verify the setup

---

## Manual Setup

### Step 1: Update .env File ✅ (Already Done!)

Your `.env` file has been updated with Neon credentials:

```env
DATABASE_URL=postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
DB_HOST=ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=npg_gTl49fAVCaYI
```

### Step 2: Connect to Neon Database

#### Option A: Using psql (Command Line)

```bash
psql 'postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'
```

#### Option B: Using Neon SQL Editor (Web Interface)

1. Go to https://console.neon.tech
2. Select your project
3. Click "SQL Editor" in the left sidebar
4. Copy and paste the SQL from `database/neon_init.sql`
5. Click "Run" button

### Step 3: Initialize Database Schema

#### If using psql:

```bash
cd /media/sayad/Ubuntu-Data/visa
psql 'postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require' -f database/neon_init.sql
```

#### If using Neon SQL Editor:

Copy the entire content of `/media/sayad/Ubuntu-Data/visa/database/neon_init.sql` and paste it into the SQL Editor, then run it.

### Step 4: Verify Setup

```bash
# Check tables
psql 'postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require' -c "\dt"

# Check required documents
psql 'postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require' -c "SELECT COUNT(*) FROM required_documents;"
```

Expected output:
- 6 tables created
- 18 required documents inserted

---

## What Gets Created

### Tables:
1. **visa_applications** - Main application records
2. **documents** - Uploaded user documents
3. **generated_documents** - System-generated documents
4. **ai_interactions** - AI/Gemini interactions log
5. **required_documents** - Document requirements by visa type
6. **questionnaire_responses** - User questionnaire answers

### Enum Types:
- `application_status` - draft, documents_uploaded, analyzing, generating, completed, failed
- `document_type` - All document types (passport, NID, bank solvency, etc.)
- `generation_status` - pending, in_progress, completed, failed

### Indexes:
- Optimized queries on application status, dates, document types

---

## Connection Details

| Field | Value |
|-------|-------|
| **Host** | ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech |
| **Port** | 5432 |
| **Database** | neondb |
| **User** | neondb_owner |
| **Password** | npg_gTl49fAVCaYI |
| **SSL Mode** | require |

---

## Test the Setup

After initialization, test with:

```bash
cd /media/sayad/Ubuntu-Data/visa/backend
python -c "from app.database import get_db; from app.models import VisaApplication; print('✅ Database connection working!')"
```

---

## Start the Application

### 1. Start Backend:
```bash
cd /media/sayad/Ubuntu-Data/visa/backend
uvicorn app.main:app --reload
```

### 2. Start Frontend:
```bash
cd /media/sayad/Ubuntu-Data/visa/frontend
npm run dev
```

### 3. Open Browser:
```
http://localhost:5173
```

---

## Troubleshooting

### Connection Failed?

1. **Check Neon Project Status**
   - Go to https://console.neon.tech
   - Ensure project is active (not suspended)

2. **Verify Credentials**
   - Make sure the connection string is correct
   - Password: `npg_gTl49fAVCaYI`

3. **SSL Issues**
   - Neon requires SSL connection
   - Make sure `sslmode=require` is in connection string

### psql Not Found?

Install PostgreSQL client:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-client

# Mac
brew install postgresql
```

### Permission Denied?

The database user `neondb_owner` has full permissions. If you get permission errors:
1. Check that you're using the correct database name: `neondb`
2. Verify the connection string includes `?sslmode=require`

---

## Next Steps

1. ✅ Database initialized
2. ⏭️ Add your Gemini API key to `.env`:
   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```
3. ⏭️ Start the backend server
4. ⏭️ Start the frontend
5. ⏭️ Create your first visa application!

---

## Quick Reference

### Connect to Neon:
```bash
psql 'postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'
```

### Run Migrations:
```bash
./database/setup_neon.sh
```

### Check Database:
```sql
-- List tables
\dt

-- Count applications
SELECT COUNT(*) FROM visa_applications;

-- Check required documents
SELECT * FROM required_documents WHERE country = 'Iceland';
```

---

**Need Help?** Check the Neon console: https://console.neon.tech
