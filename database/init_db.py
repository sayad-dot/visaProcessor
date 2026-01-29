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
from app.models import Base, RequiredDocument, DocumentType
from sqlalchemy.orm import Session
from loguru import logger


def seed_required_documents():
    """Seed the database with required documents for Iceland tourist visa"""
    
    with Session(engine) as session:
        try:
            # Check if data already exists
            existing = session.query(RequiredDocument).first()
            if existing:
                logger.info("Required documents already seeded")
                return
            
            # Documents user must upload (9 documents - Required)
            user_documents = [
                ('passport_copy', 'Valid passport copy', False),
                ('nid_bangla', 'National ID card (Bangla)', False),
                ('visa_history', 'Previous visa history from passport', False),
                ('tin_certificate', 'Tax Identification Number certificate', False),
                ('income_tax_3years', 'Income tax returns for last 3 years', False),
                ('hotel_booking', 'Hotel booking confirmation', False),
                ('air_ticket', 'Air ticket booking', False),
                ('bank_solvency', 'Bank solvency certificate', False),
            ]
            
            # Documents AI will generate (8 documents - NOT Required to upload)
            generated_documents = [
                ('asset_valuation', 'Asset valuation certificate - AI researches and generates based on all provided information and questionnaire responses', True),
                ('nid_english', 'National ID English translation - Generated from Bangla NID maintaining official Bangladesh NID format', True),
                ('visiting_card', 'Professional visiting card - Beautiful, professional design based on applicant information and questionnaire', True),
                ('cover_letter', 'Visa application cover letter - MOST IMPORTANT - Comprehensive cover letter based on ALL information and Phase 3 questionnaire responses', True),
                ('travel_itinerary', 'Detailed travel itinerary - Generated from hotel bookings and air ticket information', True),
                ('travel_history', 'Travel history summary - Extracted and formatted from passport visa stamps', True),
                ('home_tie_statement', 'Home tie statement letter - Demonstrates strong connections to home country', True),
                ('financial_statement', 'Financial statement summary - Comprehensive financial overview based on bank statements', True),
            ]
            
            # Add user documents
            for doc_type, description, can_generate in user_documents:
                doc = RequiredDocument(
                    country="Iceland",
                    visa_type="Tourist",
                    document_type=DocumentType[doc_type.upper()],
                    is_mandatory=True,
                    description=description,
                    can_be_generated=can_generate
                )
                session.add(doc)
            
            # Add generated documents
            for doc_type, description, can_generate in generated_documents:
                doc = RequiredDocument(
                    country="Iceland",
                    visa_type="Tourist",
                    document_type=DocumentType[doc_type.upper()],
                    is_mandatory=True,
                    description=description,
                    can_be_generated=can_generate
                )
                session.add(doc)
            
            session.commit()
            logger.info("Successfully seeded required documents")
            
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
