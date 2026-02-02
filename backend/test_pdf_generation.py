"""
Test PDF generation with actual data from database
"""
import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_generator_service import PDFGeneratorService
from app.config import settings

# Load environment
load_dotenv()

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("=" * 80)
print("TESTING PDF GENERATION WITH APPLICATION ID 9")
print("=" * 80)

# Test with application 9 (has data in database)
application_id = 9
output_dir = "/media/sayad/Ubuntu-Data/visa/02_Generated"

print(f"\n📂 Output directory: {output_dir}")
print(f"📄 Generating PDFs for application {application_id}...\n")

# Create PDF generator
generator = PDFGeneratorService(
    db=db,
    application_id=application_id
)

print(f"📁 Using output directory: {generator.output_dir}")
print("GENERATING COVER LETTER")
print("=" * 80)

try:
    file_path = generator.generate_cover_letter()
    print(f"✅ Cover Letter generated: {file_path}")
except Exception as e:
    print(f"❌ Error generating Cover Letter: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("PDF GENERATION TEST COMPLETE")
print("=" * 80)

# Close database
db.close()
