"""
Documents API endpoints - Upload and manage documents
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import VisaApplication, Document, DocumentType, ApplicationStatus as DBApplicationStatus
from app.schemas import DocumentUploadResponse, DocumentResponse
from app.config import settings
from app.services.pdf_service import PDFService
from app.services.storage_service import StorageService

router = APIRouter()
pdf_service = PDFService()
storage_service = StorageService()


@router.post("/upload/{application_id}", response_model=DocumentUploadResponse)
async def upload_document(
    application_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for a visa application
    Enhanced with StorageService integration
    """
    # Validate application exists
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Log received data for debugging
    logger.info(f"Upload request - document_type: '{document_type}', file: '{file.filename}'")
    
    # Validate document type
    try:
        doc_type_enum = DocumentType[document_type.upper()]
        logger.info(f"Document type validated: {doc_type_enum}")
    except KeyError:
        logger.error(f"Invalid document type received: '{document_type}' (type: {type(document_type)})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type: {document_type}. Must be one of: {[e.name for e in DocumentType]}"
        )
    
    # Read file content
    file_content = await file.read()
    logger.info(f"File read successfully: {len(file_content)} bytes")
    
    # Validate file size using StorageService
    is_size_valid = storage_service.validate_file_size(len(file_content))
    if not is_size_valid:
        logger.error(f"File size validation failed: {len(file_content)} bytes exceeds {settings.MAX_FILE_SIZE} bytes")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Validate file extension
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    is_extension_valid = storage_service.validate_file_extension(file.filename)
    if not is_extension_valid:
        logger.error(f"File extension validation failed: '{file_extension}' not in allowed extensions")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{file_extension}' not allowed. Allowed types: {', '.join(settings.allowed_extensions_list)}"
        )
    
    try:
        # Save file using StorageService (returns tuple of file_path and unique_filename)
        file_path, unique_filename = storage_service.save_file(
            file_content=file_content,
            original_filename=file.filename,
            application_number=application.application_number,
            document_type=document_type
        )
        
        # ===== CRITICAL FIX: Extract text immediately during upload =====
        extracted_text = ""
        validation_result = None
        
        try:
            logger.info(f"📄 Starting text extraction for {file.filename}...")
            
            # Extract text based on file type
            if file_extension in ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                extracted_text = pdf_service.extract_text_from_file(file_path)
                logger.info(f"✅ Extracted {len(extracted_text)} characters from {file.filename}")
                
                # Validate PDF if it's a PDF file
                if file_extension == 'pdf':
                    validation_result = pdf_service.validate_pdf(file_path)
                    if not validation_result.get('valid', False):
                        # Clean up invalid file
                        storage_service.delete_file(file_path)
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid PDF file: {validation_result.get('error', 'Unknown error')}"
                        )
                
                # Warn if no text extracted
                if len(extracted_text.strip()) < 10:
                    logger.warning(f"⚠️ Very little text extracted from {file.filename} ({len(extracted_text)} chars)")
                    logger.warning("This may be a blank page or the file may need manual OCR")
            else:
                logger.warning(f"⚠️ Unsupported file type for text extraction: {file_extension}")
                
        except Exception as e:
            logger.error(f"❌ Error extracting text during upload: {str(e)}")
            # Don't fail the upload, but log the error
            extracted_text = ""
        
        # Create document record with extracted text
        db_document = Document(
            application_id=application_id,
            document_type=doc_type_enum,
            document_name=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            mime_type=file.content_type or "application/octet-stream",
            is_uploaded=True,
            is_processed=True,  # ← FIXED: Mark as processed
            processed_at=datetime.now(),  # ← FIXED: Set processing timestamp
            extracted_text=extracted_text  # ← FIXED: Store extracted text
        )
        
        db.add(db_document)
        
        # Update application status
        if application.status == DBApplicationStatus.DRAFT:
            application.status = DBApplicationStatus.DOCUMENTS_UPLOADED
        
        db.commit()
        db.refresh(db_document)
        
        logger.info(f"Document uploaded: {file.filename} for application {application.application_number}")
        
        response_data = {
            "document_id": db_document.id,
            "document_type": document_type,
            "file_name": file.filename,
            "file_size": len(file_content),
            "message": "Document uploaded successfully",
            "text_extracted": len(extracted_text) > 0,  # ← NEW: Indicate if text was extracted
            "text_length": len(extracted_text),  # ← NEW: Length of extracted text
            "extraction_quality": (
                "excellent" if len(extracted_text) > 500 else
                "good" if len(extracted_text) > 100 else
                "fair" if len(extracted_text) > 10 else
                "poor"
            )  # ← NEW: Quality indicator
        }
        
        # Add PDF metadata if available
        if validation_result:
            response_data["metadata"] = {
                "num_pages": validation_result.get('num_pages', 0),
                "has_text": validation_result.get('has_text', False),
                "text_length": validation_result.get('text_length', 0)
            }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        db.rollback()
        
        # Clean up file if it was saved
        try:
            if 'file_path' in locals():
                storage_service.delete_file(file_path)
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post("/upload-batch/{application_id}")
async def upload_documents_batch(
    application_id: int,
    files: List[UploadFile] = File(...),
    document_types: str = Form(...),  # Comma-separated list
    db: Session = Depends(get_db)
):
    """
    Upload multiple documents at once for a visa application
    document_types should be comma-separated list matching the order of files
    Example: "passport,photo,bank_statement"
    """
    # Validate application exists
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Parse document types
    doc_types_list = [dt.strip() for dt in document_types.split(',')]
    
    if len(files) != len(doc_types_list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of files ({len(files)}) must match number of document types ({len(doc_types_list)})"
        )
    
    results = []
    uploaded_files = []
    errors = []
    
    for idx, (file, document_type) in enumerate(zip(files, doc_types_list)):
        try:
            # Validate document type
            try:
                doc_type_enum = DocumentType[document_type.upper()]
            except KeyError:
                errors.append({
                    "file": file.filename,
                    "error": f"Invalid document type: {document_type}"
                })
                continue
            
            # Read file content
            file_content = await file.read()
            
            # Validate file
            validation_error = storage_service.validate_file_size(len(file_content))
            if validation_error:
                errors.append({
                    "file": file.filename,
                    "error": validation_error
                })
                continue
            
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            validation_error = storage_service.validate_file_extension(file_extension)
            if validation_error:
                errors.append({
                    "file": file.filename,
                    "error": validation_error
                })
                continue
            
            # Save file
            file_path = storage_service.save_file(
                file_content=file_content,
                original_filename=file.filename,
                application_number=application.application_number,
                document_type=document_type
            )
            
            # Validate PDF
            if file_extension == 'pdf':
                validation_result = pdf_service.validate_pdf(file_path)
                if not validation_result.get('valid', False):
                    storage_service.delete_file(file_path)
                    errors.append({
                        "file": file.filename,
                        "error": f"Invalid PDF: {validation_result.get('error', 'Unknown error')}"
                    })
                    continue
            
            # Create document record
            db_document = Document(
                application_id=application_id,
                document_type=doc_type_enum,
                document_name=file.filename,
                file_path=file_path,
                file_size=len(file_content),
                mime_type=file.content_type or "application/octet-stream",
                is_uploaded=True,
                is_processed=False
            )
            
            db.add(db_document)
            uploaded_files.append(file_path)
            
            results.append({
                "file_name": file.filename,
                "document_type": document_type,
                "status": "success",
                "file_size": len(file_content)
            })
            
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            errors.append({
                "file": file.filename,
                "error": str(e)
            })
    
    try:
        # Update application status if any files were uploaded
        if results:
            if application.status == DBApplicationStatus.DRAFT:
                application.status = DBApplicationStatus.DOCUMENTS_UPLOADED
        
        db.commit()
        
        logger.info(f"Batch upload completed: {len(results)} successful, {len(errors)} failed")
        
        return {
            "message": f"Uploaded {len(results)} of {len(files)} documents",
            "successful_uploads": len(results),
            "failed_uploads": len(errors),
            "results": results,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        logger.error(f"Error committing batch upload: {str(e)}")
        db.rollback()
        
        # Clean up uploaded files
        for file_path in uploaded_files:
            try:
                storage_service.delete_file(file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete batch upload: {str(e)}"
        )


@router.get("/application/{application_id}", response_model=List[DocumentResponse])
async def list_application_documents(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    List all documents for an application
    """
    # Validate application exists
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    documents = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    
    return documents


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document using StorageService
    """
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from filesystem using StorageService
    try:
        storage_service.delete_file(document.file_path)
    except Exception as e:
        logger.warning(f"Error deleting file {document.file_path}: {str(e)}")
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    logger.info(f"Deleted document: {document.document_name}")
    
    return None


@router.post("/process/{application_id}")
async def process_documents(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    Process all uploaded documents for an application
    This will extract text and data from PDFs
    """
    # Validate application exists
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Get all unprocessed documents
    documents = db.query(Document).filter(
        Document.application_id == application_id,
        Document.is_processed == False,
        Document.is_uploaded == True
    ).all()
    
    if not documents:
        return {
            "message": "No documents to process",
            "processed_count": 0
        }
    
    try:
        # Update application status
        application.status = DBApplicationStatus.ANALYZING
        db.commit()
        
        processed_count = 0
        
        for document in documents:
            try:
                # Extract text from PDF
                extracted_text = pdf_service.extract_text_from_pdf(document.file_path)
                
                # Update document record
                document.extracted_text = extracted_text
                document.is_processed = True
                document.processed_at = datetime.utcnow()
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing document {document.id}: {str(e)}")
                continue
        
        db.commit()
        
        logger.info(f"Processed {processed_count} documents for application {application.application_number}")
        
        return {
            "message": f"Successfully processed {processed_count} documents",
            "processed_count": processed_count,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process documents: {str(e)}"
        )


@router.get("/storage/stats")
async def get_storage_stats():
    """
    Get storage statistics (total files, total size, etc.)
    """
    try:
        stats = storage_service.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage stats: {str(e)}"
        )


@router.get("/validate/{document_id}")
async def validate_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Validate a document (especially useful for PDFs)
    """
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        file_extension = document.file_path.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            validation_result = pdf_service.validate_pdf(document.file_path)
            return {
                "document_id": document_id,
                "file_name": document.document_name,
                "validation": validation_result
            }
        else:
            # For non-PDF files, just check if file exists
            file_exists = os.path.exists(document.file_path)
            return {
                "document_id": document_id,
                "file_name": document.document_name,
                "validation": {
                    "valid": file_exists,
                    "file_exists": file_exists,
                    "file_size_mb": round(os.path.getsize(document.file_path) / (1024 * 1024), 2) if file_exists else 0
                }
            }
    
    except Exception as e:
        logger.error(f"Error validating document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate document: {str(e)}"
        )
