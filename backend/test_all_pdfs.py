"""
Test PDF generation with actual data from database - ALL 13 DOCUMENTS
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
print("TESTING PDF GENERATION - ALL 13 DOCUMENTS")
print("=" * 80)

# Test with application 9 (has data in database)
application_id = 9

print(f"\n📄 Generating ALL 13 documents for application {application_id}...\n")

# Create PDF generator
generator = PDFGeneratorService(
    db=db,
    application_id=application_id
)

print(f"📁 Output directory: {generator.output_dir}\n")

# Generate all 13 documents
documents_to_generate = [
    ("Cover Letter", generator.generate_cover_letter),
    ("NID Translation", generator.generate_nid_translation),
    ("Visiting Card", generator.generate_visiting_card),
    ("Financial Statement", generator.generate_financial_statement),
    ("Travel Itinerary", generator.generate_travel_itinerary),
    ("Travel History", generator.generate_travel_history),
    ("Home Tie Statement", generator.generate_home_tie_statement),
    ("Asset Valuation", generator.generate_asset_valuation),
    ("TIN Certificate", generator.generate_tin_certificate),
    ("Tax Certificate", generator.generate_tax_certificate),
    ("Trade License", generator.generate_trade_license),
    ("Hotel Booking", generator.generate_hotel_booking),
    ("Air Ticket", generator.generate_air_ticket),
]

success_count = 0
error_count = 0
errors = []

for i, (doc_name, generator_func) in enumerate(documents_to_generate, 1):
    print(f"[{i}/13] Generating {doc_name}...", end=" ")
    try:
        file_path = generator_func()
        print(f"✅ Success: {os.path.basename(file_path)}")
        success_count += 1
    except Exception as e:
        print(f"❌ Error: {str(e)[:60]}")
        error_count += 1
        errors.append((doc_name, str(e)))

print("\n" + "=" * 80)
print("GENERATION SUMMARY")
print("=" * 80)
print(f"✅ Successful: {success_count}/13")
print(f"❌ Failed: {error_count}/13")

if errors:
    print("\nErrors encountered:")
    for doc_name, error in errors:
        print(f"  • {doc_name}: {error[:100]}")

print("\n" + "=" * 80)
print(f"📂 All generated files are in: {generator.output_dir}")
print("=" * 80)

# Close database
db.close()
