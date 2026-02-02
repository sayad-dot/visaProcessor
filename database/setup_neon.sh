#!/bin/bash
# Neon Database Setup Helper Script

echo "🚀 Neon Database Initialization"
echo "================================"
echo ""

# Database connection details
DB_URL="postgresql://neondb_owner:npg_gTl49fAVCaYI@ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

echo "📊 Database: neondb"
echo "🔗 Host: ep-aged-dawn-ah5in31p-pooler.c-3.us-east-1.aws.neon.tech"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ psql is not installed. Please install PostgreSQL client:"
    echo "   Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "   Mac: brew install postgresql"
    exit 1
fi

echo "✅ psql is installed"
echo ""

# Test connection
echo "🔌 Testing connection to Neon database..."
if psql "$DB_URL" -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Connection successful!"
else
    echo "❌ Connection failed. Please check your credentials."
    exit 1
fi

echo ""
echo "📋 Initializing database schema..."
echo ""

# Run the initialization script
psql "$DB_URL" -f "$(dirname "$0")/neon_init.sql"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database initialized successfully!"
    echo ""
    echo "📊 Verifying tables..."
    psql "$DB_URL" -c "\dt"
    echo ""
    echo "📝 Required documents count:"
    psql "$DB_URL" -c "SELECT COUNT(*) FROM required_documents;"
    echo ""
    echo "🎉 Setup complete! Your database is ready."
    echo ""
    echo "Next steps:"
    echo "1. Update GEMINI_API_KEY in .env file"
    echo "2. Start backend: cd backend && uvicorn app.main:app --reload"
    echo "3. Start frontend: cd frontend && npm run dev"
else
    echo ""
    echo "❌ Database initialization failed"
    exit 1
fi
