"""
Database initialization script
Run this to create all database tables
"""
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.database import init_db, engine
from app.models import Base, RequiredDocument, DocumentType, ApplicationType
from sqlalchemy.orm import Session
from loguru import logger


def seed_required_documents():
    """Seed the database with required documents for Iceland tourist visa
    - Different requirements for BUSINESS vs JOB applicants
    """
    
    with Session(engine) as session:
        try:
            # Check if data already exists
            existing = session.query(RequiredDocument).first()
            if existing:
                logger.info("Required documents already seeded. Clearing old data...")
                session.query(RequiredDocument).delete()
                session.commit()
            
            # ===== BUSINESS OWNER / SELF-EMPLOYED =====
            business_documents = [
                # Mandatory - to upload
                ('passport_copy', 'Passport copy - PDF', False, True),
                ('nid_bangla', 'NID Bangla version - PDF', False, True),
                ('visa_history', 'Visa history copies - PDF', False, True),
                ('nid_english', 'NID English translated copy - PDF', False, True),
                ('trade_license', 'Trade license English translated - PDF', False, True),
                ('tin_certificate', 'TIN certificate - PDF', False, True),
                ('visiting_card', 'Visiting card - PDF', False, True),
                ('cover_letter', 'Cover letter - PDF', True, True),
                ('travel_itinerary', 'Travel itinerary - PDF', True, True),
                ('travel_history', 'Travel History - PDF', True, True),
                ('air_ticket', 'Air ticket Booking - PDF', False, True),
                ('hotel_booking', 'Hotel Booking - PDF', False, True),
                ('bank_statement', 'Bank statement - PDF', False, True),
            ]
            
            # ===== JOB HOLDER / EMPLOYEE =====
            job_documents = [
                # Mandatory - to upload
                ('passport_copy', 'Passport copy - PDF', False, True),
                ('nid_bangla', 'NID Bangla version - PDF', False, True),
                ('visa_history', 'Visa history copies - PDF', False, True),
                ('nid_english', 'NID English translated copy - PDF', False, True),
                ('job_noc', 'JOB NOC (No Objection Certificate) - PDF', False, True),
                ('tin_certificate', 'TIN certificate - PDF', False, True),
                ('visiting_card', 'Visiting card - PDF', False, True),
                ('job_id_card', 'JOB ID card - PDF', False, True),
                ('payslip', 'Payslip of last 6 months salary - PDF', False, True),
                ('cover_letter', 'Cover letter - PDF', True, True),
                ('travel_itinerary', 'Travel itinerary - PDF', True, True),
                ('travel_history', 'Travel History - PDF', True, True),
                ('air_ticket', 'Air ticket Booking - PDF', False, True),
                ('hotel_booking', 'Hotel Booking - PDF', False, True),
                ('bank_statement', 'Bank statement - PDF', False, True),
            ]
            
            # Add business documents
            for doc_type, description, can_generate, is_mandatory in business_documents:
                doc = RequiredDocument(
                    country="Iceland",
                    visa_type="Tourist",
                    application_type=ApplicationType.BUSINESS,
                    document_type=DocumentType[doc_type.upper()],
                    is_mandatory=is_mandatory,
                    description=description,
                    can_be_generated=can_generate
                )
                session.add(doc)
            
            # Add job documents
            for doc_type, description, can_generate, is_mandatory in job_documents:
                doc = RequiredDocument(
                    country="Iceland",
                    visa_type="Tourist",
                    application_type=ApplicationType.JOB,
                    document_type=DocumentType[doc_type.upper()],
                    is_mandatory=is_mandatory,
                    description=description,
                    can_be_generated=can_generate
                )
                session.add(doc)
            
            session.commit()
            logger.info(f"Successfully seeded {len(business_documents)} business documents and {len(job_documents)} job documents")
            
        except Exception as e:
            logger.error(f"Error seeding database: {str(e)}")
            session.rollback()
            raise


if __name__ == "__main__":
    logger.info("Initializing database...")
    
    # Create all tables
    init_db()
    
    # Seed required documents
    seed_required_documents()
    
    logger.info("Database initialization completed successfully!")
