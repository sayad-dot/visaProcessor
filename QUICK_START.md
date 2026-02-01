# 🚀 Quick Start Guide

## Get Your Visa Processing System Running in 5 Minutes!

### Step 1: Setup Database (2 minutes)
```bash
# Install PostgreSQL
sudo apt update && sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE visa_processing_db;"
sudo -u postgres psql -c "CREATE USER visa_user WITH PASSWORD 'visa123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE visa_processing_db TO visa_user;"
```

### Step 2: Setup Backend (2 minutes)
```bash
cd /media/sayad/Ubuntu-Data/visa/backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
DATABASE_URL=postgresql://visa_user:visa123@localhost:5432/visa_processing_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=visa_processing_db
DB_USER=visa_user
DB_PASSWORD=visa123

GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

BACKEND_PORT=8000
FRONTEND_PORT=3000
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
EOL

# Initialize database
python database/init_db.py
```

### Step 3: Setup Frontend (1 minute)
```bash
cd /media/sayad/Ubuntu-Data/visa/frontend

# Install dependencies
npm install
```

### Step 4: Run the Application!

**Open Terminal 1 - Backend:**
```bash
cd /media/sayad/Ubuntu-Data/visa/backend
source venv/bin/activate
python main.py
```

**Open Terminal 2 - Frontend:**
```bash
cd /media/sayad/Ubuntu-Data/visa/frontend
npm run dev
```

### Step 5: Access Your Application! 🎊

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Test It Out!

1. Go to http://localhost:3000
2. Click **"New Application"**
3. Fill in your details:
   - Name: Your Name
   - Email: your@email.com
   - Phone: +880...
   - Country: Iceland (pre-selected)
   - Visa Type: Tourist (pre-selected)
4. Click **"Create Application"**
5. See your application in the list! ✅

## Important Notes

### Get Your Gemini API Key (FREE)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Paste it in `backend/.env` for `GEMINI_API_KEY`

### Folder Structure Created
```
visa/
├── backend/        ✅ Python FastAPI backend
├── frontend/       ✅ React + Material-UI frontend
├── database/       ✅ PostgreSQL scripts
└── docs/           ✅ Documentation
```

### What Works Right Now (Phase 1)
- ✅ Create visa applications
- ✅ View all applications
- ✅ Application details page
- ✅ Database fully configured
- ✅ API endpoints ready
- ✅ Beautiful UI with Material-UI

### Coming Next (Phase 2)
- Document upload interface
- File management
- Document preview
- Progress tracking

## Troubleshooting

### PostgreSQL not starting?
```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### Port 8000 already in use?
```bash
# Find and kill the process
sudo lsof -i :8000
kill -9 <PID>
```

### Module not found errors?
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Database connection error?
- Check PostgreSQL is running
- Verify database exists: `sudo -u postgres psql -l`
- Check credentials in `backend/.env`

## Need Help?

- Check `docs/DEVELOPMENT_GUIDE.md` for detailed setup
- Check `docs/PHASE_1_COMPLETE.md` for what's been built
- API documentation: http://localhost:8000/docs

---

## 🎯 Your Project is Ready!

Phase 1 Complete! You now have:
- ✅ Full-stack application running
- ✅ PostgreSQL database configured
- ✅ Beautiful React UI (no Tailwind!)
- ✅ FastAPI backend with AI integration
- ✅ Ready for Phase 2 (Document Upload)

**Let me know when you're ready to start Phase 2!** 🚀
