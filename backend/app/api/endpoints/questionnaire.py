"""
Questionnaire API endpoints - SIMPLIFIED VERSION
Fixed 4-section structure: Personal, Travel, Financial, Other
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import VisaApplication, QuestionnaireResponse, Document, QuestionCategory, QuestionDataType, DocumentType
from app.schemas import SaveQuestionnaireRequest, QuestionnaireProgressResponse
from app.services.simple_questionnaire_generator import SimpleQuestionnaireGenerator

router = APIRouter()

@router.get("/generate/{application_id}")
async def generate_questionnaire(application_id: int, db: Session = Depends(get_db)):
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    uploaded_doc_types = [doc.document_type for doc in uploaded_docs]
    
    logger.info(f"📤 Generating simple questionnaire for application {application_id}")
    
    generator = SimpleQuestionnaireGenerator()
    questions_by_category = generator.generate_questions(uploaded_document_types=uploaded_doc_types)
    
    return {
        "questions_by_category": questions_by_category,
        "total_questions": sum(len(q) for q in questions_by_category.values()),
        "sections": {
            "personal": "Personal Information (Required)",
            "travel_itinerary": "Travel Itinerary (Skip if uploaded)",
            "hotel_booking": "Hotel Booking (Skip if uploaded)",
            "air_ticket": "Air Ticket (Skip if uploaded)",
            "assets": "Financial & Assets",
            "financial": "Employment & Income",
            "home_ties": "Home Ties",
            "other": "Other (Optional)"
        }
    }

@router.post("/response/{application_id}")
async def save_responses(application_id: int, request: SaveQuestionnaireRequest, db: Session = Depends(get_db)):
    saved_count = 0
    for resp in request.responses:
        q = db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.application_id == application_id,
            QuestionnaireResponse.question_key == resp.question_key
        ).first()
        
        if q:
            q.answer = resp.answer
            q.answered_at = datetime.now()
        else:
            q = QuestionnaireResponse(
                application_id=application_id,
                question_key=resp.question_key,
                question_text=resp.question_key.replace('_', ' ').title(),
                answer=resp.answer,
                category=QuestionCategory.PERSONAL,
                data_type=QuestionDataType.TEXT,
                is_required=False,
                answered_at=datetime.now()
            )
            db.add(q)
        saved_count += 1
    
    db.commit()
    return {"message": f"Saved {saved_count} responses", "saved_count": saved_count}

@router.post("/complete/{application_id}")
async def mark_complete(application_id: int, db: Session = Depends(get_db)):
    app = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if app:
        app.questionnaire_complete = True
        db.commit()
    return {"message": "Questionnaire complete"}

@router.get("/status/{application_id}")
async def get_status(application_id: int, db: Session = Depends(get_db)):
    app = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    return {"questionnaire_complete": getattr(app, 'questionnaire_complete', False) if app else False}

@router.get("/responses/{application_id}")
async def get_responses(application_id: int, db: Session = Depends(get_db)):
    """Get questionnaire responses - returns empty dict if no responses yet"""
    responses = db.query(QuestionnaireResponse).filter(QuestionnaireResponse.application_id == application_id).all()
    
    # Return empty dict if no responses (not an error - just means questionnaire not filled yet)
    if not responses:
        return {}
    
    grouped = {}
    for r in responses:
        cat = r.category.value
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append({"key": r.question_key, "question": r.question_text, "answer": r.answer})
    return grouped

@router.get("/progress/{application_id}")
async def get_progress(application_id: int, db: Session = Depends(get_db)):
    questions = db.query(QuestionnaireResponse).filter(QuestionnaireResponse.application_id == application_id).all()
    total = len(questions)
    answered = sum(1 for q in questions if q.answer)
    return {
        "total_questions": total,
        "answered_questions": answered,
        "completion_percentage": int((answered/total)*100) if total > 0 else 0
    }
