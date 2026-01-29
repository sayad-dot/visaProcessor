"""
Update required documents descriptions with detailed AI generation requirements
"""
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.database import engine
from app.models import RequiredDocument, DocumentType
from sqlalchemy.orm import Session
from loguru import logger


def update_document_descriptions():
    """Update descriptions for AI-generated documents"""
    
    with Session(engine) as session:
        try:
            # Updated descriptions for AI-generated documents
            updates = {
                'ASSET_VALUATION': 'Asset valuation certificate - AI researches and generates based on all provided information and questionnaire responses',
                'NID_ENGLISH': 'National ID English translation - Generated from Bangla NID maintaining official Bangladesh NID format',
                'VISITING_CARD': 'Professional visiting card - Beautiful, professional design based on applicant information and questionnaire',
                'COVER_LETTER': 'Visa application cover letter - MOST IMPORTANT - Comprehensive cover letter based on ALL information and Phase 3 questionnaire responses',
                'TRAVEL_ITINERARY': 'Detailed travel itinerary - Generated from hotel bookings and air ticket information',
                'TRAVEL_HISTORY': 'Travel history summary - Extracted and formatted from passport visa stamps',
                'HOME_TIE_STATEMENT': 'Home tie statement letter - Demonstrates strong connections to home country',
                'FINANCIAL_STATEMENT': 'Financial statement summary - Comprehensive financial overview based on bank statements',
            }
            
            # Update each document
            for doc_type_str, new_description in updates.items():
                doc_type_enum = DocumentType[doc_type_str]
                doc = session.query(RequiredDocument).filter(
                    RequiredDocument.document_type == doc_type_enum,
                    RequiredDocument.country == "Iceland",
                    RequiredDocument.visa_type == "Tourist"
                ).first()
                
                if doc:
                    doc.description = new_description
                    logger.info(f"Updated description for {doc_type_str}")
                else:
                    logger.warning(f"Document not found: {doc_type_str}")
            
            session.commit()
            logger.info("Successfully updated all document descriptions")
            
        except Exception as e:
            logger.error(f"Error updating descriptions: {str(e)}")
            session.rollback()
            raise


if __name__ == "__main__":
    logger.info("Updating document descriptions...")
    update_document_descriptions()
    logger.info("Update completed successfully!")
