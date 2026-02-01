"""
Questionnaire API endpoints - Generate and manage questionnaire responses
INTELLIGENT SYSTEM: Generates dynamic questions based on uploaded documents and missing information
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
from app.services.intelligent_questionnaire_analyzer import get_intelligent_analyzer

router = APIRouter()


@router.get("/generate/{application_id}", response_model=Dict)
async def generate_questionnaire(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    ✨ INTELLIGENT QUESTIONNAIRE GENERATION ✨
    
    Analyzes uploaded documents and generates dynamic questions based on:
    1. Which documents are uploaded vs missing
    2. What information is already extracted
    3. What information is needed to generate missing documents
    4. Low-confidence extractions that need verification
    
    Returns ONLY questions for missing information - no fixed questions!
    ALL questions are OPTIONAL - user can skip any they don't want to answer.
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
    
    logger.info(f"📤 Generating intelligent questionnaire for application {application_id}")
    logger.info(f"📊 Uploaded: {len(uploaded_doc_types)} documents, Missing: {16 - len(uploaded_doc_types)} documents")
    
    # ===== USE INTELLIGENT ANALYZER =====
    analyzer = get_intelligent_analyzer()
    questions_list, analysis_summary = analyzer.analyze_and_generate_questions(
        uploaded_documents=uploaded_doc_types,
        extracted_data=extracted_data_dict,
        target_country=application.country,
        visa_type=application.visa_type
    )
    
    # Group questions by category for better UX
    questions_by_category = analyzer.group_questions_by_category(questions_list)
    
    # Save questions to database for tracking
    for category_name, questions in questions_by_category.items():
        for question_req in questions:
            # Check if question already exists
            existing = db.query(QuestionnaireResponse).filter(
                QuestionnaireResponse.application_id == application_id,
                QuestionnaireResponse.question_key == question_req.field_key
            ).first()
            
            if not existing:
                # Determine category enum
                category_enum = QuestionCategory.PERSONAL  # Default
                if 'business' in category_name or 'employment' in category_name:
                    category_enum = QuestionCategory.BUSINESS
                elif 'travel' in category_name:
                    category_enum = QuestionCategory.TRAVEL_PURPOSE
                elif 'financial' in category_name:
                    category_enum = QuestionCategory.FINANCIAL
                elif 'assets' in category_name:
                    category_enum = QuestionCategory.ASSETS
                elif 'home_ties' in category_name:
                    category_enum = QuestionCategory.HOME_TIES
                
                # Determine data type enum
                data_type_map = {
                    "text": QuestionDataType.TEXT,
                    "textarea": QuestionDataType.TEXTAREA,
                    "date": QuestionDataType.DATE,
                    "number": QuestionDataType.NUMBER,
                    "boolean": QuestionDataType.BOOLEAN,
                    "select": QuestionDataType.SELECT,
                    "email": QuestionDataType.EMAIL
                }
                data_type_enum = data_type_map.get(question_req.data_type, QuestionDataType.TEXT)
                
                # ===== CRITICAL: ALL QUESTIONS ARE OPTIONAL =====
                qr = QuestionnaireResponse(
                    application_id=application_id,
                    category=category_enum,
                    question_key=question_req.field_key,
                    question_text=question_req.question,
                    data_type=data_type_enum,
                    is_required=False,  # ← ALL QUESTIONS OPTIONAL
                    options=question_req.options if question_req.options else None
                )
                db.add(qr)
    
    db.commit()
    
    # Convert to response format
    response_by_category = {}
    for category_name, questions in questions_by_category.items():
        response_by_category[category_name] = [
            {
                "key": q.field_key,
                "text": q.question,
                "data_type": q.data_type,
                "priority": q.priority,
                "is_required": False,  # ← ALL OPTIONAL
                "options": q.options if q.options else [],
                "placeholder": q.placeholder,
                "help_text": q.help_text
            }
            for q in questions
        ]
    
    total_questions = sum(len(q) for q in response_by_category.values())
    
    logger.info(f"✅ Generated {total_questions} intelligent questions across {len(response_by_category)} categories")
    
    # Add metadata to response
    result = response_by_category.copy()
    result["total_questions"] = total_questions
    result["analysis_summary"] = analysis_summary
    result["note"] = "All questions are OPTIONAL. Answer only what you want to provide."
    
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
