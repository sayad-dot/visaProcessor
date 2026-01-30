"""
Analysis API endpoints - Document analysis and questionnaire generation
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import (
    VisaApplication, Document, ExtractedData, AnalysisSession, 
    QuestionnaireResponse, AnalysisStatus, ApplicationStatus as DBApplicationStatus
)
from app.schemas import (
    AnalysisStartResponse, AnalysisStatusResponse, AnalysisResultsResponse,
    QuestionnaireGenerateResponse, SaveQuestionnaireRequest, 
    QuestionnaireProgressResponse, QuestionResponse
)
from app.services.ai_analysis_service import get_analysis_service
from app.services.questionnaire_generator import get_questionnaire_service

router = APIRouter()


async def run_analysis_task(
    application_id: int,
    session_id: int,
    db: Session
):
    """Background task to analyze all documents"""
    try:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            logger.error(f"Analysis session {session_id} not found")
            return
        
        # Update status to analyzing
        session.status = AnalysisStatus.ANALYZING
        session.started_at = datetime.now()
        db.commit()
        
        # Get all uploaded documents for this application
        documents = db.query(Document).filter(
            Document.application_id == application_id,
            Document.is_uploaded == True
        ).all()
        
        session.total_documents = len(documents)
        db.commit()
        
        logger.info(f"Starting analysis for {len(documents)} documents")
        
        analysis_service = get_analysis_service()
        extracted_data_dict = {}
        
        for idx, doc in enumerate(documents, 1):
            try:
                # Update current document
                session.current_document = doc.document_type.value
                session.documents_analyzed = idx
                db.commit()
                
                logger.info(f"Analyzing document {idx}/{len(documents)}: {doc.document_type.value}")
                
                # Get extracted text from document
                extracted_text = doc.extracted_text or ""
                
                if not extracted_text:
                    logger.warning(f"No extracted text for {doc.document_type.value}, skipping")
                    continue
                
                # Analyze document
                result = await analysis_service.analyze_document(
                    document_type=doc.document_type,
                    extracted_text=extracted_text
                )
                
                # Save extracted data
                extracted_data = ExtractedData(
                    application_id=application_id,
                    document_id=doc.id,
                    document_type=doc.document_type,
                    data=result,
                    confidence_score=result.get("confidence", 0)
                )
                db.add(extracted_data)
                db.commit()
                
                # Store in dict for later use
                extracted_data_dict[doc.document_type.value] = result
                
                logger.info(f"✓ Analyzed {doc.document_type.value} - Confidence: {result.get('confidence', 0)}%")
                
            except Exception as e:
                logger.error(f"Error analyzing {doc.document_type.value}: {str(e)}")
                continue
        
        # Calculate completeness score
        total_fields = 0
        complete_fields = 0
        
        for doc_type, data in extracted_data_dict.items():
            if "error" not in data:
                for key, value in data.items():
                    if key not in ["confidence", "error"]:
                        total_fields += 1
                        if value and value not in [None, "", [], {}]:
                            complete_fields += 1
        
        completeness_score = int((complete_fields / total_fields * 100)) if total_fields > 0 else 0
        
        # Update session
        session.status = AnalysisStatus.COMPLETED
        session.completeness_score = completeness_score
        session.completed_at = datetime.now()
        db.commit()
        
        # Update application status
        application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
        if application:
            application.status = DBApplicationStatus.ANALYZING
            db.commit()
        
        logger.info(f"✅ Analysis completed - Completeness: {completeness_score}%")
        
    except Exception as e:
        logger.error(f"Analysis task failed: {str(e)}")
        session.status = AnalysisStatus.FAILED
        session.error_message = str(e)
        db.commit()


@router.post("/start/{application_id}", response_model=AnalysisStartResponse)
async def start_analysis(
    application_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start document analysis for an application
    Runs in background and returns immediately
    """
    # Check if application exists
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check if documents are uploaded
    documents = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    
    if not documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents uploaded yet"
        )
    
    # Check if analysis already running
    existing_session = db.query(AnalysisSession).filter(
        AnalysisSession.application_id == application_id,
        AnalysisSession.status.in_([AnalysisStatus.STARTED, AnalysisStatus.ANALYZING])
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis already in progress"
        )
    
    # Create new analysis session
    session = AnalysisSession(
        application_id=application_id,
        status=AnalysisStatus.STARTED,
        total_documents=len(documents)
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    logger.info(f"Created analysis session {session.id} for application {application_id}")
    
    # Start background analysis task
    background_tasks.add_task(run_analysis_task, application_id, session.id, db)
    
    return AnalysisStartResponse(
        session_id=session.id,
        status=session.status.value,
        total_documents=len(documents),
        message="Document analysis started. This may take a few minutes."
    )


@router.get("/status/{application_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get current status of document analysis"""
    
    # First check if application exists
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get most recent session
    session = db.query(AnalysisSession).filter(
        AnalysisSession.application_id == application_id
    ).order_by(AnalysisSession.created_at.desc()).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis session found for this application"
        )
    
    progress_percentage = 0
    if session.total_documents > 0:
        progress_percentage = int((session.documents_analyzed / session.total_documents) * 100)
    
    return AnalysisStatusResponse(
        session_id=session.id,
        status=session.status.value,
        documents_analyzed=session.documents_analyzed or 0,
        total_documents=session.total_documents or 0,
        current_document=session.current_document,
        progress_percentage=progress_percentage,
        completeness_score=session.completeness_score or 0
    )


@router.get("/results/{application_id}", response_model=AnalysisResultsResponse)
async def get_analysis_results(
    application_id: int,
    db: Session = Depends(get_db)
):
    """Get complete analysis results"""
    
    # Get most recent completed session
    session = db.query(AnalysisSession).filter(
        AnalysisSession.application_id == application_id,
        AnalysisSession.status == AnalysisStatus.COMPLETED
    ).order_by(AnalysisSession.created_at.desc()).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completed analysis found"
        )
    
    # Get all extracted data
    extracted_data_list = db.query(ExtractedData).filter(
        ExtractedData.application_id == application_id
    ).all()
    
    extracted_data_dict = {}
    for ed in extracted_data_list:
        extracted_data_dict[ed.document_type.value] = ed.data
    
    return AnalysisResultsResponse(
        session_id=session.id,
        status=session.status.value,
        completeness_score=session.completeness_score or 0,
        extracted_data=extracted_data_dict,
        missing_fields=session.missing_fields or [],
        completed_at=session.completed_at
    )
