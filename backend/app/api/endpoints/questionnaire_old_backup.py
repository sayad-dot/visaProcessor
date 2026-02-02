"""
Questionnaire API endpoints - Generate and manage questionnaire responses
SIMPLE SYSTEM: Fixed 4-section structure that's easy to understand
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import (
    VisaApplication, ExtractedData, QuestionnaireResponse,
    QuestionCategory, QuestionDataType, Document
)
from app.schemas import (
    QuestionnaireGenerateResponse, SaveQuestionnaireRequest,
    QuestionnaireProgressResponse, QuestionResponse
)
from app.services.simple_questionnaire_generator import SimpleQuestionnaireGenerator

router = APIRouter()


@router.get("/generate/{application_id}", response_model=Dict)
async def generate_questionnaire(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    ✨ SIMPLE QUESTIONNAIRE GENERATION ✨
    
    Fixed 4-section structure:
    1. Personal Information (5 required fields)
    2. Travel Information (3 collapsible boxes - skip if documents uploaded)
    3. Financial/Assets Information
    4. Other Information (all optional)
    
    Simplified - no AI complexity, just straightforward questions!
    """
    # Check if application exists
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get uploaded document types
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    uploaded_doc_types = [doc.document_type for doc in uploaded_docs]
    
    logger.info(f"📤 Generating simple questionnaire for application {application_id}")
    logger.info(f"📊 Uploaded: {len(uploaded_doc_types)} documents")
    
    # ===== USE SIMPLE GENERATOR =====
    generator = SimpleQuestionnaireGenerator()
    questions_by_category = generator.generate_questions(
        uploaded_document_types=uploaded_doc_types
    )
    
    logger.info(f"✅ Generated questionnaire with {len(questions_by_category)} sections")
    
    # Convert to response format
    result = {
        "questions_by_category": questions_by_category,
        "total_questions": sum(len(questions) for questions in questions_by_category.values()),
        "sections": {
            "personal": "Personal Information (Required)",
            "travel_itinerary": "Travel Itinerary (Skip if uploaded)",
            "hotel_booking": "Hotel Booking (Skip if uploaded)",
            "air_ticket": "Air Ticket (Skip if uploaded)",
            "assets": "Financial & Assets Information",
            "financial": "Employment & Income Information",
            "home_ties": "Home Ties Information",
            "other": "Other Information (Optional)"
        },
        "note": "Personal information is required. Travel sections can be skipped if documents uploaded. Financial questions help generate Asset Valuation."
    }
    
    return result
                    "number": QuestionDataType.NUMBER,
                    "boolean": QuestionDataType.BOOLEAN,
                    "select": QuestionDataType.SELECT,
                    "multiselect": QuestionDataType.MULTISELECT,
                    "email": QuestionDataType.TEXT  # Email is just text type
                }
                data_type_enum = data_type_map.get(question_req.data_type, QuestionDataType.TEXT)
                
                # ===== CRITICAL: ALL QUESTIONS ARE OPTIONAL =====
                qr = QuestionnaireResponse(
                    application_id=application_id,
                    category=category_enum,
                    question_key=question_req.field_key,
                    question_text=question_req.question,
    
    # Convert to response format
    result = {
        "questions_by_category": questions_by_category,
        "total_questions": sum(len(questions) for questions in questions_by_category.values()),
        "sections": {
            "personal": "Personal Information (Required)",
            "travel_itinerary": "Travel Itinerary (Skip if uploaded)",
            "hotel_booking": "Hotel Booking (Skip if uploaded)",
            "air_ticket": "Air Ticket (Skip if uploaded)",
            "assets": "Financial & Assets Information",
            "financial": "Employment & Income Information",
            "home_ties": "Home Ties Information",
            "other": "Other Information (Optional)"
        },
        "note": "Personal information is required. Travel sections can be skipped if documents uploaded. Financial questions help generate Asset Valuation."
    }
    
    return result


@router.post("/response/{application_id}")
async def save_responses(
    application_id: int,
    request: SaveQuestionnaireRequest,
    db: Session = Depends(get_db)
):
    """
    Save user's questionnaire responses
    """
    # Check if application exists
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    saved_count = 0
    errors = []
    
    for response in request.responses:
        try:
            # Find the question
            question = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.application_id == application_id,
                QuestionnaireResponse.question_key == response.question_key
            ).first()
            
            if not question:
                errors.append(f"Question not found: {response.question_key}")
                continue
            
            # Update answer
            question.answer = response.answer
            question.answered_at = datetime.now()
            saved_count += 1
            
        except Exception as e:
            logger.error(f"Error saving response for {response.question_key}: {str(e)}")
            errors.append(f"{response.question_key}: {str(e)}")
    
    db.commit()
    
    logger.info(f"Saved {saved_count} responses for application {application_id}")
    
    return {
        "message": f"Saved {saved_count} responses",
        "saved_count": saved_count,
        "errors": errors if errors else None
    }


@router.get("/responses/{application_id}")
async def get_responses(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all questionnaire responses grouped by category
    """
    responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    
    if not responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questionnaire found"
        )
    
    # Group by category
    grouped = {}
    for resp in responses:
        category = resp.category.value
        if category not in grouped:
            grouped[category] = []
        
        grouped[category].append({
            "key": resp.question_key,
            "question": resp.question_text,
            "answer": resp.answer,
            "data_type": resp.data_type.value,
            "is_required": resp.is_required,
            "answered_at": resp.answered_at
        })
    
    return grouped


@router.get("/progress/{application_id}", response_model=QuestionnaireProgressResponse)
async def get_progress(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get questionnaire completion progress
    """
    all_questions = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    
    if not all_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questionnaire found"
        )
    
    total = len(all_questions)
    answered = sum(1 for q in all_questions if q.answer)
    
    # Get category status
    categories = {}
    for q in all_questions:
        cat = q.category.value
        if cat not in categories:
            categories[cat] = {"total": 0, "answered": 0}
        categories[cat]["total"] += 1
        if q.answer:
            categories[cat]["answered"] += 1
    
    completed_categories = [cat for cat, data in categories.items() if data["answered"] == data["total"]]
    pending_categories = [cat for cat, data in categories.items() if data["answered"] < data["total"]]
    
    completion_percentage = int((answered / total) * 100) if total > 0 else 0
    
    return QuestionnaireProgressResponse(
        total_questions=total,
        answered_questions=answered,
        completion_percentage=completion_percentage,
        categories_completed=completed_categories,
        categories_pending=pending_categories
    )


@router.get("/analysis-summary/{application_id}")
async def get_analysis_summary(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Get analysis summary showing uploaded vs missing documents
    Used by questionnaire wizard to show context
    """
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get uploaded documents
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    
    uploaded_types = [doc.document_type.value for doc in uploaded_docs]
    
    # All document types
    from app.models import DocumentType
    all_types = [dt.value for dt in DocumentType]
    
    missing_types = [t for t in all_types if t not in uploaded_types]
    
    return {
        "total_documents": 16,
        "uploaded_count": len(uploaded_types),
        "missing_count": len(missing_types),
        "uploaded_types": uploaded_types,
        "missing_types": missing_types
    }
