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
    
    # Get application type to determine which documents to generate
    app_type = getattr(app, 'application_type', 'business')
    
    # Calculate how many documents need to be generated (DYNAMIC based on type)
    # Base documents for both types (11 common docs)
    all_generatable_types = [
        "cover_letter", "nid_english", "visiting_card", "financial_statement",
        "travel_itinerary", "travel_history", "home_tie_statement", "asset_valuation",
        "tin_certificate", "tax_certificate", "hotel_booking", "air_ticket"
    ]
    
    # Add type-specific documents
    if app_type == 'business':
        all_generatable_types.append("trade_license")
    elif app_type == 'job':
        all_generatable_types.extend(["job_noc", "job_id_card"])
    
    # Check which ones are already uploaded
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    uploaded_types = [doc.document_type.value for doc in uploaded_docs]
    
    # Calculate documents that need generation (not uploaded)
    docs_to_generate = [doc for doc in all_generatable_types if doc not in uploaded_types]
    total_to_generate = len(docs_to_generate)
    
    # Initialize session tracking
    generation_sessions[application_id] = {
        "status": "started",
        "progress": 0,
        "current_document": None,
        "documents_completed": 0,
        "total_documents": total_to_generate,
        "docs_to_generate": docs_to_generate,
        "started_at": datetime.now().isoformat()
    }
    
    # Start generation in background
    background_tasks.add_task(generate_documents_task, application_id, db)
    
    return {
        "message": "PDF generation started",
        "application_id": application_id,
        "total_documents": total_to_generate,
        "status": "started"
    }


def generate_documents_task(application_id: int, db: Session):
    """Background task to generate all documents"""
    try:
        generator = PDFGeneratorService(db, application_id)
        application = generator.application
        
        # Get application type (fallback to 'business' for existing apps)
        app_type = getattr(application, 'application_type', 'business')
        
        # Update session
        generation_sessions[application_id]["status"] = "generating"
        generation_sessions[application_id]["progress"] = 5
        
        # Get dynamic list of documents to generate from session
        docs_to_generate = generation_sessions[application_id].get("docs_to_generate", [])
        
        # All possible documents with their display names and weights
        all_documents = {
            "cover_letter": ("Cover Letter", 8),
            "nid_english": ("NID Translation", 7),
            "visiting_card": ("Visiting Card", 6),
            "financial_statement": ("Financial Statement", 8),
            "travel_itinerary": ("Travel Itinerary", 9),
            "travel_history": ("Travel History", 6),
            "home_tie_statement": ("Home Tie Statement", 7),
            "asset_valuation": ("Asset Valuation", 10),
            "tin_certificate": ("TIN Certificate", 7),
            "tax_certificate": ("Tax Certificate", 7),
            "trade_license": ("Trade License", 7),  # Business only
            "job_noc": ("Job NOC", 7),  # Job only
            "job_id_card": ("Job ID Card", 6),  # Job only
            "hotel_booking": ("Hotel Booking", 9),
            "air_ticket": ("Air Ticket", 9),
        }
        
        # Filter to only generate documents that aren't uploaded
        documents = [(doc_type, all_documents[doc_type][0], all_documents[doc_type][1]) 
                     for doc_type in docs_to_generate if doc_type in all_documents]
        
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
                elif doc_type == "tin_certificate":
                    generator.generate_tin_certificate()
                elif doc_type == "tax_certificate":
                    generator.generate_tax_certificate()
                elif doc_type == "trade_license":
                    generator.generate_trade_license()
                elif doc_type == "job_noc":
                    generator.generate_job_noc()
                elif doc_type == "job_id_card":
                    generator.generate_job_id_card()
                elif doc_type == "hotel_booking":
                    generator.generate_hotel_booking()
                elif doc_type == "air_ticket":
                    generator.generate_air_ticket()
                
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
    
    # Calculate dynamic total based on uploaded documents
    all_generatable_types = [
        "cover_letter", "nid_english", "visiting_card", "financial_statement",
        "travel_itinerary", "travel_history", "home_tie_statement", "asset_valuation",
        "tin_certificate", "tax_certificate", "trade_license", "hotel_booking", "air_ticket"
    ]
    uploaded_docs = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    uploaded_types = [doc.document_type.value for doc in uploaded_docs]
    docs_to_generate = [doc for doc in all_generatable_types if doc not in uploaded_types]
    total_documents = len(docs_to_generate)
    
    if not docs:
        return {
            "status": "not_started",
            "progress": 0,
            "documents_completed": 0,
            "total_documents": total_documents
        }
    
    completed = sum(1 for d in docs if d.status == GenerationStatus.COMPLETED)
    generating = any(d.status == GenerationStatus.GENERATING for d in docs)
    
    return {
        "status": "generating" if generating else ("completed" if completed == total_documents else "partial"),
        "progress": int((completed / total_documents) * 100) if total_documents > 0 else 100,
        "documents_completed": completed,
        "total_documents": total_documents,
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
        # Add uploaded documents (all files in root folder)
        for doc in uploaded_docs:
            if os.path.exists(doc.file_path):
                # Use only the filename, no folder prefix
                arcname = doc.document_name
                zipf.write(doc.file_path, arcname)
        
        # Add generated documents (all files in root folder)
        for doc in generated_docs:
            if os.path.exists(doc.file_path):
                # Use only the filename, no folder prefix
                arcname = doc.file_name
                zipf.write(doc.file_path, arcname)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"Visa_Application_{application_id}_All_Documents.zip"
    )
