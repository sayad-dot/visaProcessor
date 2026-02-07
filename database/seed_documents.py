"""
Seed required documents directly using SQL
"""
import sys
import os

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.database import engine
from sqlalchemy import text
from loguru import logger

def seed_documents():
    """Seed documents using raw SQL"""
    
    # Format: (country, visa_type, app_type, doc_type, is_mandatory, can_be_generated, description)
    
    # Business: 13 documents (2 required, 11 optional)
    business_docs = [
        # REQUIRED (2 docs) - only these 2 should be marked required
        ('Iceland', 'Tourist', 'business', 'passport_copy', True, False, 'Passport copy - PDF'),
        ('Iceland', 'Tourist', 'business', 'nid_bangla', True, True, 'NID Bangla (will be translated to English)'),
        # OPTIONAL/SUGGESTED (11 docs) - rest are optional
        ('Iceland', 'Tourist', 'business', 'visa_history', False, False, 'Visa history copies - PDF'),
        ('Iceland', 'Tourist', 'business', 'nid_english', False, True, 'NID English translated copy - PDF'),
        ('Iceland', 'Tourist', 'business', 'trade_license', False, False, 'Trade license English translated - PDF'),
        ('Iceland', 'Tourist', 'business', 'tin_certificate', False, False, 'TIN certificate - PDF'),
        ('Iceland', 'Tourist', 'business', 'visiting_card', False, True, 'Visiting card - PDF'),
        ('Iceland', 'Tourist', 'business', 'cover_letter', False, True, 'Cover letter - PDF'),
        ('Iceland', 'Tourist', 'business', 'asset_valuation', False, True, 'Asset valuation document - PDF'),
        ('Iceland', 'Tourist', 'business', 'travel_itinerary', False, True, 'Travel itinerary - PDF'),
        ('Iceland', 'Tourist', 'business', 'travel_history', False, True, 'Travel History - PDF'),
        ('Iceland', 'Tourist', 'business', 'air_ticket', False, False, 'Air ticket Booking - PDF'),
        ('Iceland', 'Tourist', 'business', 'hotel_booking', False, False, 'Hotel Booking - PDF'),
    ]
    
    # Job: 14 documents (2 required, 12 optional)
    job_docs = [
        # REQUIRED (2 docs) - only these 2 should be marked required
        ('Iceland', 'Tourist', 'job', 'passport_copy', True, False, 'Passport copy - PDF'),
        ('Iceland', 'Tourist', 'job', 'nid_bangla', True, True, 'NID Bangla (will be translated to English)'),
        # OPTIONAL/SUGGESTED (12 docs) - rest are optional
        ('Iceland', 'Tourist', 'job', 'visa_history', False, False, 'Visa history copies - PDF'),
        ('Iceland', 'Tourist', 'job', 'nid_english', False, True, 'NID English translated copy - PDF'),
        ('Iceland', 'Tourist', 'job', 'job_noc', False, False, 'JOB NOC (No Objection Certificate) - PDF'),
        ('Iceland', 'Tourist', 'job', 'tin_certificate', False, False, 'TIN certificate - PDF'),
        ('Iceland', 'Tourist', 'job', 'visiting_card', False, True, 'Visiting card - PDF'),
        ('Iceland', 'Tourist', 'job', 'job_id_card', False, False, 'JOB ID card - PDF'),
        ('Iceland', 'Tourist', 'job', 'payslip', False, False, 'Payslip of last 6 months salary - PDF'),
        ('Iceland', 'Tourist', 'job', 'cover_letter', False, True, 'Cover letter - PDF'),
        ('Iceland', 'Tourist', 'job', 'travel_itinerary', False, True, 'Travel itinerary - PDF'),
        ('Iceland', 'Tourist', 'job', 'travel_history', False, True, 'Travel History - PDF'),
        ('Iceland', 'Tourist', 'job', 'air_ticket', False, False, 'Air ticket Booking - PDF'),
        ('Iceland', 'Tourist', 'job', 'hotel_booking', False, False, 'Hotel Booking - PDF'),
    ]
    
    with engine.connect() as conn:
        # Clear existing
        conn.execute(text("DELETE FROM required_documents"))
        logger.info("Cleared existing documents")
        
        # Insert business documents
        for doc in business_docs:
            conn.execute(text("""
                INSERT INTO required_documents 
                (country, visa_type, application_type, document_type, is_mandatory, can_be_generated, description)
                VALUES (:country, :visa_type, :app_type, CAST(:doc_type AS document_type), :is_mandatory, :can_gen, :description)
            """), {
                'country': doc[0],
                'visa_type': doc[1],
                'app_type': doc[2],
                'doc_type': doc[3],
                'is_mandatory': doc[4],
                'can_gen': doc[5],
                'description': doc[6]
            })
        
        # Insert job documents  
        for doc in job_docs:
            conn.execute(text("""
                INSERT INTO required_documents 
                (country, visa_type, application_type, document_type, is_mandatory, can_be_generated, description)
                VALUES (:country, :visa_type, :app_type, CAST(:doc_type AS document_type), :is_mandatory, :can_gen, :description)
            """), {
                'country': doc[0],
                'visa_type': doc[1],
                'app_type': doc[2],
                'doc_type': doc[3],
                'is_mandatory': doc[4],
                'can_gen': doc[5],
                'description': doc[6]
            })
        
        conn.commit()
        logger.info(f"✅ Seeded {len(business_docs)} business documents and {len(job_docs)} job documents")

if __name__ == "__main__":
    seed_documents()
