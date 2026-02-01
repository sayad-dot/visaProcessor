# Development Guide

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Git

### Installation

#### 1. Clone and Navigate
```bash
cd /media/sayad/Ubuntu-Data/visa
```

#### 2. Database Setup
```bash
# Install PostgreSQL (if not installed)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE visa_processing_db;
CREATE USER visa_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE visa_processing_db TO visa_user;
\q
```

#### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
.\venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env
```

Edit `.env` file with your configurations:
```bash
DATABASE_URL=postgresql://visa_user:your_secure_password@localhost:5432/visa_processing_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=visa_processing_db
DB_USER=visa_user
DB_PASSWORD=your_secure_password

GEMINI_API_KEY=your_gemini_api_key_here

BACKEND_PORT=8000
FRONTEND_PORT=3000
DEBUG=True
SECRET_KEY=change-this-to-a-random-secret-key
```

#### 4. Initialize Database
```bash
# Make sure you're in backend directory with venv activated
python database/init_db.py
```

#### 5. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create frontend .env (optional)
echo "VITE_API_URL=http://localhost:8000/api" > .env
```

### Running the Application

#### Development Mode

**Terminal 1 - Backend:**
```bash
cd /media/sayad/Ubuntu-Data/visa/backend
source venv/bin/activate
uvicorn main:app --port 8000
python main.py

```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs (Swagger UI)

**Terminal 2 - Frontend:**
```bash
cd /media/sayad/Ubuntu-Data/visa/frontend
npm run dev
```

Frontend: http://localhost:3000

#### Production Build

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
npm run preview
```

## Project Structure

```
visa/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── config.py    # Configuration
│   │   ├── database.py  # Database setup
│   │   ├── models.py    # SQLAlchemy models
│   │   └── schemas.py   # Pydantic schemas
│   ├── uploads/         # Uploaded files
│   ├── generated/       # Generated documents
│   ├── logs/            # Application logs
│   └── main.py          # Application entry point
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── services/    # API services
│   └── package.json
├── database/            # Database scripts
└── docs/                # Documentation
```

## API Endpoints

### Applications
- `POST /api/applications/` - Create new application
- `GET /api/applications/` - List all applications
- `GET /api/applications/{id}` - Get application details
- `DELETE /api/applications/{id}` - Delete application
- `GET /api/applications/{id}/required-documents` - Get required documents

### Documents
- `POST /api/documents/upload/{application_id}` - Upload document
- `GET /api/documents/application/{application_id}` - List documents
- `DELETE /api/documents/{document_id}` - Delete document
- `POST /api/documents/process/{application_id}` - Process documents

### Generate (Coming in future phases)
- `POST /api/generate/{application_id}/analyze` - Analyze documents
- `POST /api/generate/{application_id}/generate` - Generate documents
- `GET /api/generate/{application_id}/download-all` - Download all

## Database Schema

### Tables
- `visa_applications` - Main application records
- `documents` - Uploaded and generated documents
- `ai_interactions` - AI processing history
- `required_documents` - Master list of required documents

See `backend/app/models.py` for complete schema.

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
GEMINI_API_KEY=your_api_key
BACKEND_PORT=8000
DEBUG=True
SECRET_KEY=your_secret_key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000/api
```

## Testing

```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env` file
- Check database exists: `sudo -u postgres psql -l`

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>
```

### Module Import Errors
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

1. **Backend Development**
   - Use `DEBUG=True` in development
   - Check logs in `backend/logs/app.log`
   - API documentation at `/docs`

2. **Frontend Development**
   - React DevTools for debugging
   - Check browser console for errors
   - Material-UI documentation: https://mui.com/

3. **Database Changes**
   - Modify `models.py`
   - Create migration script
   - Test with sample data

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit for review

## Support

For issues or questions, check:
- Project documentation in `docs/`
- API documentation at http://localhost:8000/docs
- Backend logs in `backend/logs/`
