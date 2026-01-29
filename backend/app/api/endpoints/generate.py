"""
API endpoints for PDF document generation
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List
import os
import zipfile
from datetime import datetime

from app.database import get_db
from app.models import GeneratedDocument, GenerationStatus, Document, VisaApplication
from app.services.pdf_generator_service import PDFGeneratorService
from fastapi.responses import FileResponse, StreamingResponse

router = APIRouter()


# Global storage for generation status
generation_sessions = {}


@router.post("/{application_id}/start")
async def start_generation(
    application_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start PDF generation process in background"""
    
    # Verify application exists
    app = db.query(VisaApplication).filter(VisaApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if generation already in progress
    existing = db.query(GeneratedDocument).filter(
        GeneratedDocument.application_id == application_id,
        GeneratedDocument.status == GenerationStatus.GENERATING
    ).first()
    
    if existing:
        return {"message": "Generation already in progress", "status": "generating"}
    
    # Initialize session tracking
    generation_sessions[application_id] = {
        "status": "started",
        "progress": 0,
        "current_document": None,
        "documents_completed": 0,
        "total_documents": 8,
        "started_at": datetime.now().isoformat()
    }
    
    # Start generation in background
    background_tasks.add_task(generate_documents_task, application_id, db)
    
    return {
        "message": "PDF generation started",
        "application_id": application_id,
        "total_documents": 8,
        "status": "started"
    }


def generate_documents_task(application_id: int, db: Session):
    """Background task to generate all documents"""
    try:
        generator = PDFGeneratorService(db, application_id)
        
        # Update session
        generation_sessions[application_id]["status"] = "generating"
        generation_sessions[application_id]["progress"] = 5
        
        # Document generation order and progress weights
        documents = [
            ("cover_letter", "Cover Letter", 15),
            ("nid_english", "NID Translation", 12),
            ("visiting_card", "Visiting Card", 10),
            ("financial_statement", "Financial Statement", 15),
            ("travel_itinerary", "Travel Itinerary", 13),
            ("travel_history", "Travel History", 10),
            ("home_tie_statement", "Home Tie Statement", 12),
            ("asset_valuation", "Asset Valuation", 13),
        ]
        
        completed = 0
        total_progress = 5
        
        for doc_type, doc_name, weight in documents:
            try:
                # Update current document
                generation_sessions[application_id]["current_document"] = doc_name
                
                # Generate document
                if doc_type == "cover_letter":
                    generator.generate_cover_letter()
                elif doc_type == "nid_english":
                    generator.generate_nid_translation()
                elif doc_type == "visiting_card":
                    generator.generate_visiting_card()
                elif doc_type == "financial_statement":
                    generator.generate_financial_statement()
                elif doc_type == "travel_itinerary":
                    generator.generate_travel_itinerary()
                elif doc_type == "travel_history":
                    generator.generate_travel_history()
                elif doc_type == "home_tie_statement":
                    generator.generate_home_tie_statement()
                elif doc_type == "asset_valuation":
                    generator.generate_asset_valuation()
                
                completed += 1
                total_progress += weight
                
                # Update session
                generation_sessions[application_id]["documents_completed"] = completed
                generation_sessions[application_id]["progress"] = min(total_progress, 95)
                
            except Exception as e:
                print(f"Error generating {doc_name}: {e}")
                generation_sessions[application_id]["errors"] = generation_sessions[application_id].get("errors", [])
                generation_sessions[application_id]["errors"].append(f"{doc_name}: {str(e)}")
        
        # Complete
        generation_sessions[application_id]["status"] = "completed"
        generation_sessions[application_id]["progress"] = 100
        generation_sessions[application_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Generation error: {e}")
        generation_sessions[application_id]["status"] = "failed"
        generation_sessions[application_id]["error"] = str(e)


@router.get("/{application_id}/status")
async def get_generation_status(application_id: int, db: Session = Depends(get_db)):
    """Get current generation status"""
    
    # Check session tracking first
    if application_id in generation_sessions:
        session = generation_sessions[application_id]
        
        # Get completed documents from DB
        completed_docs = db.query(GeneratedDocument).filter(
            GeneratedDocument.application_id == application_id,
            GeneratedDocument.status == GenerationStatus.COMPLETED
        ).all()
        
        return {
            "status": session["status"],
            "progress": session["progress"],
            "current_document": session.get("current_document"),
            "documents_completed": session.get("documents_completed", 0),
            "total_documents": session["total_documents"],
            "completed_documents": [
                {
                    "type": doc.document_type,
                    "name": doc.file_name,
                    "size": doc.file_size
                }
                for doc in completed_docs
            ],
            "errors": session.get("errors", [])
        }
    
    # Fallback to DB check
    docs = db.query(GeneratedDocument).filter(
        GeneratedDocument.application_id == application_id
    ).all()
    
    if not docs:
        return {
            "status": "not_started",
            "progress": 0,
            "documents_completed": 0,
            "total_documents": 8
        }
    
    completed = sum(1 for d in docs if d.status == GenerationStatus.COMPLETED)
    generating = any(d.status == GenerationStatus.GENERATING for d in docs)
    
    return {
        "status": "generating" if generating else ("completed" if completed == 8 else "partial"),
        "progress": int((completed / 8) * 100),
        "documents_completed": completed,
        "total_documents": 8,
        "completed_documents": [
            {
                "type": doc.document_type,
                "name": doc.file_name,
                "size": doc.file_size
            }
            for doc in docs if doc.status == GenerationStatus.COMPLETED
        ]
    }


@router.get("/{application_id}/documents")
async def get_generated_documents(application_id: int, db: Session = Depends(get_db)):
    """Get list of all generated documents"""
    
    docs = db.query(GeneratedDocument).filter(
        GeneratedDocument.application_id == application_id,
        GeneratedDocument.status == GenerationStatus.COMPLETED
    ).all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "type": doc.document_type,
                "name": doc.file_name,
                "size": doc.file_size,
                "created_at": doc.created_at.isoformat()
            }
            for doc in docs
        ]
    }


@router.get("/{application_id}/download/{document_id}")
async def download_document(
    application_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Download a single generated document"""
    
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.id == document_id,
        GeneratedDocument.application_id == application_id,
        GeneratedDocument.status == GenerationStatus.COMPLETED
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        doc.file_path,
        media_type="application/pdf",
        filename=doc.file_name
    )


@router.get("/{application_id}/download-all")
async def download_all_documents(application_id: int, db: Session = Depends(get_db)):
    """Download all documents (uploaded + generated) as ZIP"""
    
    # Get uploaded documents
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_uploaded == True
    ).all()
    
    # Get generated documents
    generated_docs = db.query(GeneratedDocument).filter(
        GeneratedDocument.application_id == application_id,
        GeneratedDocument.status == GenerationStatus.COMPLETED
    ).all()
    
    # Create ZIP file
    zip_path = f"uploads/app_{application_id}/all_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add uploaded documents
        for doc in uploaded_docs:
            if os.path.exists(doc.file_path):
                arcname = f"01_Uploaded/{doc.document_name}"
                zipf.write(doc.file_path, arcname)
        
        # Add generated documents
        for doc in generated_docs:
            if os.path.exists(doc.file_path):
                arcname = f"02_Generated/{doc.file_name}"
                zipf.write(doc.file_path, arcname)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"Visa_Application_{application_id}_All_Documents.zip"
    )
