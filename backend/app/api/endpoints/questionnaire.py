"""
Questionnaire API endpoints - Generate and manage questionnaire responses
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
from app.services.questionnaire_generator import get_questionnaire_service

router = APIRouter()


@router.get("/generate/{application_id}", response_model=Dict)
async def generate_questionnaire(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate intelligent questionnaire based on analysis results
    """
    # Check if application exists
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get extracted data
    extracted_data_list = db.query(ExtractedData).filter(
        ExtractedData.application_id == application_id
    ).all()
    
    if not extracted_data_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis data found. Please run document analysis first."
        )
    
    # Convert to dict
    extracted_data_dict = {}
    for ed in extracted_data_list:
        extracted_data_dict[ed.document_type.value] = ed.data
    
    # Get uploaded document types
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    uploaded_doc_types = [doc.document_type for doc in uploaded_docs]
    
    # Generate questionnaire
    questionnaire_service = get_questionnaire_service()
    questions_by_category = questionnaire_service.generate_questions(
        extracted_data=extracted_data_dict,
        uploaded_document_types=uploaded_doc_types
    )
    
    # Save questions to database for tracking
    for category, questions in questions_by_category.items():
        for question in questions:
            # Check if question already exists
            existing = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.application_id == application_id,
                QuestionnaireResponse.question_key == question["key"]
            ).first()
            
            if not existing:
                qr = QuestionnaireResponse(
                    application_id=application_id,
                    category=QuestionCategory[category.upper()],
                    question_key=question["key"],
                    question_text=question["text"],
                    data_type=QuestionDataType[question["data_type"].upper()],
                    is_required=question["is_required"],
                    options=question.get("options")
                )
                db.add(qr)
    
    db.commit()
    
    # Calculate total questions
    total_questions = sum(len(q) for q in questions_by_category.values())
    
    logger.info(f"Generated {total_questions} questions for application {application_id}")
    
    # Add total_questions to response
    result = questions_by_category.copy()
    result["total_questions"] = total_questions
    
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
