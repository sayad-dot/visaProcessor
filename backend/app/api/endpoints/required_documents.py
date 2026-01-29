"""
Required Documents API endpoints - Get list of required documents
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from app.database import get_db
from app.models import RequiredDocument
from app.schemas import RequiredDocumentResponse

router = APIRouter()


@router.get("/{country}/{visa_type}")
async def get_required_documents(
    country: str,
    visa_type: str,
    db: Session = Depends(get_db)
):
    """
    Get list of required documents for a specific country and visa type
    """
    try:
        # Capitalize for consistency with database storage
        country_formatted = country.capitalize()
        visa_type_formatted = visa_type.capitalize()
        
        # Query required documents
        required_docs = db.query(RequiredDocument).filter(
            RequiredDocument.country == country_formatted,
            RequiredDocument.visa_type == visa_type_formatted
        ).all()
        
        if not required_docs:
            logger.warning(f"No required documents found for {country_formatted}/{visa_type_formatted}")
            return []
        
        logger.info(f"Found {len(required_docs)} required documents for {country_formatted}/{visa_type_formatted}")
        
        # Convert to dict for response
        result = []
        for doc in required_docs:
            result.append({
                "id": doc.id,
                "country": doc.country,
                "visa_type": doc.visa_type,
                "document_type": doc.document_type.value if hasattr(doc.document_type, 'value') else str(doc.document_type),
                "description": doc.description,
                "is_mandatory": doc.is_mandatory,
                "can_be_generated": doc.can_be_generated
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching required documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch required documents: {str(e)}"
        )


@router.get("/", response_model=List[RequiredDocumentResponse])
async def list_all_required_documents(
    db: Session = Depends(get_db)
):
    """
    Get all required documents across all countries and visa types
    """
    try:
        required_docs = db.query(RequiredDocument).all()
        logger.info(f"Found {len(required_docs)} total required documents")
        return required_docs
    except Exception as e:
        logger.error(f"Error fetching all required documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch required documents: {str(e)}"
        )
