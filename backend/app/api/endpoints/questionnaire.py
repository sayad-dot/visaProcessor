"""
Questionnaire API endpoints - SIMPLIFIED VERSION + SMART VERSION
Fixed 4-section structure: Personal, Travel, Financial, Other
New smart endpoints for enhanced questionnaire with conditional logic
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import VisaApplication, QuestionnaireResponse, Document, QuestionCategory, QuestionDataType, DocumentType
from app.schemas import SaveQuestionnaireRequest, QuestionnaireProgressResponse
from app.services.simple_questionnaire_generator import SimpleQuestionnaireGenerator
from app.services.smart_questionnaire_service import (
    get_questionnaire_structure, 
    get_all_questions,
    validate_answer,
    calculate_progress
)
from app.services.auto_fill_service import auto_fill_questionnaire

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


# ============================================
# SMART QUESTIONNAIRE ENDPOINTS (NEW)
# ============================================

@router.get("/smart-generate/{application_id}")
async def smart_generate_questionnaire(application_id: int, db: Session = Depends(get_db)):
    """
    Generate smart questionnaire with conditional logic
    Returns structured questionnaire with sections, required/suggested/optional levels
    """
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    logger.info(f"📤 Generating SMART questionnaire for application {application_id}")
    
    structure = get_questionnaire_structure()
    
    return {
        "application_id": application_id,
        "questionnaire": structure,
        "sections": list(structure.keys()),
        "total_questions": sum(len(section.get("questions", [])) for section in structure.values()),
        "metadata": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "features": [
                "conditional_logic",
                "visual_hierarchy",
                "dynamic_arrays",
                "auto_validation"
            ]
        }
    }


@router.post("/smart-save/{application_id}")
async def smart_save_responses(
    application_id: int, 
    answers: Dict[str, Any], 
    auto_fill: bool = False,  # New parameter
    db: Session = Depends(get_db)
):
    """
    Save smart questionnaire responses with validation
    Accepts answers as {question_key: answer_value}
    
    Args:
        application_id: Application ID
        answers: Dictionary of answers
        auto_fill: If True, auto-fills missing fields with realistic data (default: False)
    """
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    logger.info(f"💾 Saving SMART questionnaire responses for application {application_id}")
    
    # AUTO-FILL missing data if requested
    auto_fill_summary = None
    if auto_fill:
        logger.info(f"🤖 Auto-filling missing fields for application {application_id}")
        filled_answers, auto_fill_summary = auto_fill_questionnaire(answers)
        answers = filled_answers
        logger.info(f"✨ Auto-filled {auto_fill_summary['auto_filled_count']} fields")
    
    # Get all questions to validate
    all_questions = get_all_questions()
    questions_map = {q["key"]: q for q in all_questions}
    
    saved_count = 0
    errors = []
    
    for question_key, answer in answers.items():
        # Find question definition
        question_def = questions_map.get(question_key)
        if not question_def:
            logger.warning(f"Unknown question key: {question_key}")
            continue
        
        # Validate answer
        is_valid, error_msg = validate_answer(question_def, answer)
        if not is_valid:
            errors.append({"question": question_key, "error": error_msg})
            continue
        
        # Save or update response
        existing = db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.application_id == application_id,
            QuestionnaireResponse.question_key == question_key
        ).first()
        
        # Convert answer to string (handle lists/dicts)
        if isinstance(answer, (list, dict)):
            import json
            answer_str = json.dumps(answer)
        else:
            answer_str = str(answer)
        
        if existing:
            existing.answer = answer_str
            existing.answered_at = datetime.now()
        else:
            new_response = QuestionnaireResponse(
                application_id=application_id,
                question_key=question_key,
                question_text=question_def.get("label", ""),
                answer=answer_str,
                category=QuestionCategory.PERSONAL,  # Will be updated based on section
                data_type=QuestionDataType.TEXT,
                is_required=question_def.get("required", False),
                answered_at=datetime.now()
            )
            db.add(new_response)
        
        saved_count += 1
    
    db.commit()
    
    # Calculate progress
    all_responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    answers_dict = {r.question_key: r.answer for r in all_responses}
    progress = calculate_progress(answers_dict)
    
    response_data = {
        "message": f"Saved {saved_count} responses",
        "saved_count": saved_count,
        "errors": errors,
        "progress": progress
    }
    
    # Add auto-fill summary if used
    if auto_fill and auto_fill_summary:
        response_data["auto_fill"] = auto_fill_summary
    
    return response_data


@router.get("/smart-load/{application_id}")
async def smart_load_responses(application_id: int, db: Session = Depends(get_db)):
    """
    Load saved smart questionnaire responses
    Returns {question_key: answer} mapping
    """
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    
    # Convert to simple key-value mapping
    answers = {}
    for resp in responses:
        answers[resp.question_key] = resp.answer
    
    # Calculate progress
    progress = calculate_progress(answers)
    
    return {
        "application_id": application_id,
        "answers": answers,
        "progress": progress,
        "total_saved": len(answers)
    }


@router.get("/smart-progress/{application_id}")
async def smart_get_progress(application_id: int, db: Session = Depends(get_db)):
    """
    Get detailed progress of smart questionnaire
    Includes section-wise progress
    """
    responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    
    answers = {r.question_key: r.answer for r in responses}
    progress = calculate_progress(answers)
    
    return progress


@router.post("/smart-auto-fill/{application_id}")
async def smart_auto_fill(application_id: int, db: Session = Depends(get_db)):
    """
    Auto-fill ALL missing fields with realistic data
    Returns the complete filled questionnaire without saving
    """
    application = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    logger.info(f"🤖 Auto-filling questionnaire for application {application_id}")
    
    # Load existing responses
    responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.application_id == application_id
    ).all()
    
    existing_answers = {}
    for resp in responses:
        # Try to parse JSON arrays/objects
        try:
            import json
            existing_answers[resp.question_key] = json.loads(resp.answer)
        except:
            existing_answers[resp.question_key] = resp.answer
    
    # Auto-fill missing fields
    filled_answers, summary = auto_fill_questionnaire(existing_answers)
    
    logger.info(f"✨ Auto-filled {summary['auto_filled_count']} missing fields")
    
    return {
        "application_id": application_id,
        "filled_answers": filled_answers,
        "summary": summary,
        "message": f"Auto-filled {summary['auto_filled_count']} fields. Use /smart-save with auto_fill=true to save."
    }

