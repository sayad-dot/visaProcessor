"""
Applications API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from loguru import logger
import uuid

from app.database import get_db
from app.models import VisaApplication, RequiredDocument, ApplicationStatus as DBApplicationStatus
from app.schemas import (
    ApplicationCreate, 
    ApplicationResponse, 
    ApplicationDetailResponse,
    RequiredDocumentResponse
)

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new visa application
    """
    try:
        # Generate unique application number
        app_number = f"VISA-{uuid.uuid4().hex[:8].upper()}"
        
        # Create new application
        db_application = VisaApplication(
            application_number=app_number,
            applicant_name=application.applicant_name,
            applicant_email=application.applicant_email,
            applicant_phone=application.applicant_phone,
            country=application.country.value,
            visa_type=application.visa_type.value,
            status=DBApplicationStatus.DRAFT
        )
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        logger.info(f"Created new application: {app_number}")
        
        return db_application
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all visa applications
    """
    applications = db.query(VisaApplication)\
        .order_by(VisaApplication.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return applications


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific visa application by ID
    """
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a visa application
    """
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    db.delete(application)
    db.commit()
    
    logger.info(f"Deleted application: {application.application_number}")
    
    return None


@router.get("/{application_id}/required-documents", response_model=List[RequiredDocumentResponse])
async def get_required_documents(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of required documents for an application
    """
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get required documents for this country and visa type
    required_docs = db.query(RequiredDocument).filter(
        RequiredDocument.country == application.country,
        RequiredDocument.visa_type == application.visa_type
    ).all()
    
    return required_docs
