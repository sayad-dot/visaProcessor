"""
Move asset_valuation from upload documents to AI-generated documents
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


def fix_asset_valuation():
    """Change asset_valuation to AI-generated document"""
    
    with Session(engine) as session:
        try:
            # Find asset_valuation document
            doc = session.query(RequiredDocument).filter(
                RequiredDocument.document_type == DocumentType.ASSET_VALUATION,
                RequiredDocument.country == "Iceland",
                RequiredDocument.visa_type == "Tourist"
            ).first()
            
            if doc:
                logger.info(f"Found asset_valuation: can_be_generated={doc.can_be_generated}")
                
                # Change to AI-generated
                doc.can_be_generated = True
                doc.is_mandatory = False  # Not required to upload (AI creates it)
                doc.description = 'Asset valuation certificate - AI researches and generates based on all provided information and questionnaire responses'
                
                session.commit()
                logger.info("✓ asset_valuation is now AI-generated (NOT required to upload)")
            else:
                logger.error("asset_valuation document not found!")
            
        except Exception as e:
            logger.error(f"Error updating asset_valuation: {str(e)}")
            session.rollback()
            raise


if __name__ == "__main__":
    logger.info("Fixing asset_valuation...")
    fix_asset_valuation()
    logger.info("Fix completed!")
