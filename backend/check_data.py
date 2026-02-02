"""
Check database for extracted data and questionnaire responses
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in environment")
    sys.exit(1)

# Create database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("CHECKING EXTRACTED DATA")
print("=" * 80)

# Check extracted data
result = db.execute(text("""
    SELECT id, application_id, document_type, data
    FROM extracted_data
    ORDER BY id DESC
    LIMIT 5
"""))

rows = result.fetchall()
if rows:
    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Application ID: {row[1]}")
        print(f"Document Type: {row[2]}")
        print(f"Data: {row[3]}")
        print("-" * 40)
else:
    print("No extracted data found!")

print("\n" + "=" * 80)
print("CHECKING QUESTIONNAIRE RESPONSES")
print("=" * 80)

# Check questionnaire responses
result = db.execute(text("""
    SELECT id, application_id, question_key, answer
    FROM questionnaire_responses
    ORDER BY id DESC
    LIMIT 10
"""))

rows = result.fetchall()
if rows:
    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Application ID: {row[1]}")
        print(f"Question Key: {row[2]}")
        print(f"Answer: {row[3]}")
        print("-" * 40)
else:
    print("No questionnaire responses found!")

print("\n" + "=" * 80)
print("CHECKING APPLICATIONS")
print("=" * 80)

# Check applications
result = db.execute(text("""
    SELECT id, applicant_name, destination_country, visa_type, status
    FROM visa_applications
    ORDER BY id DESC
    LIMIT 5
"""))

rows = result.fetchall()
if rows:
    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Applicant Name: {row[1]}")
        print(f"Destination: {row[2]}")
        print(f"Visa Type: {row[3]}")
        print(f"Status: {row[4]}")
        print("-" * 40)
else:
    print("No applications found!")

db.close()
