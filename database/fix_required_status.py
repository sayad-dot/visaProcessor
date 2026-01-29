"""
Fix required status: Only upload documents (can_be_generated=False) are mandatory
AI-generated documents (can_be_generated=True) are NOT mandatory for users
"""
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.database import engine
from app.models import RequiredDocument
from sqlalchemy.orm import Session
from loguru import logger


def fix_required_status():
    """Update is_mandatory based on can_be_generated"""
    
    with Session(engine) as session:
        try:
            # Get all required documents for Iceland/Tourist
            docs = session.query(RequiredDocument).filter(
                RequiredDocument.country == "Iceland",
                RequiredDocument.visa_type == "Tourist"
            ).all()
            
            logger.info(f"Found {len(docs)} documents to update")
            
            for doc in docs:
                # Only documents that CANNOT be generated are mandatory (user must upload)
                # Documents that CAN be generated are NOT mandatory (AI creates them)
                if doc.can_be_generated:
                    # AI will generate - NOT required to upload
                    doc.is_mandatory = False
                    logger.info(f"✓ {doc.document_type.value}: NOT required (AI generated)")
                else:
                    # User must upload - REQUIRED
                    doc.is_mandatory = True
                    logger.info(f"✓ {doc.document_type.value}: REQUIRED (user must upload)")
            
            session.commit()
            logger.info("Successfully updated all document required status")
            
            # Summary
            upload_required = session.query(RequiredDocument).filter(
                RequiredDocument.country == "Iceland",
                RequiredDocument.visa_type == "Tourist",
                RequiredDocument.is_mandatory == True
            ).count()
            
            ai_generated = session.query(RequiredDocument).filter(
                RequiredDocument.country == "Iceland",
                RequiredDocument.visa_type == "Tourist",
                RequiredDocument.can_be_generated == True
            ).count()
            
            logger.info(f"\n📊 Summary:")
            logger.info(f"   - Upload Required: {upload_required} documents")
            logger.info(f"   - AI Generated: {ai_generated} documents")
            logger.info(f"   - Total: {upload_required + ai_generated} documents")
            
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            session.rollback()
            raise


if __name__ == "__main__":
    logger.info("Fixing required status for documents...")
    fix_required_status()
    logger.info("Fix completed successfully!")
