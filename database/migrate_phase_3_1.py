"""
Phase 3.1 Database Migration - Add Analysis and Questionnaire Tables
Run this to create new tables for document analysis and questionnaire
"""
import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from app.database import engine, Base
from app.models import ExtractedData, QuestionnaireResponse, AnalysisSession
from loguru import logger


def run_migration():
    """Create new tables for Phase 3.1"""
    
    try:
        logger.info("Starting Phase 3.1 migration...")
        
        # Create only the new tables
        logger.info("Creating extracted_data table...")
        ExtractedData.__table__.create(engine, checkfirst=True)
        
        logger.info("Creating questionnaire_responses table...")
        QuestionnaireResponse.__table__.create(engine, checkfirst=True)
        
        logger.info("Creating analysis_sessions table...")
        AnalysisSession.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ Phase 3.1 migration completed successfully!")
        logger.info("   - extracted_data table created")
        logger.info("   - questionnaire_responses table created")
        logger.info("   - analysis_sessions table created")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Phase 3.1 Database Migration")
    logger.info("=" * 60)
    run_migration()
