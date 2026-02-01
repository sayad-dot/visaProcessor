"""
CRITICAL UPDATE for documents.py - Fix text extraction

This updates the /process endpoint to properly extract text from ALL file types
"""

# ADD THIS NEW FUNCTION to documents.py (around line 375, replace the existing process_documents function)

@router.post("/process/{application_id}")
async def process_documents(
    application_id: int,
    db: Session = Depends(get_db)
):
    """
    ENHANCED: Process all uploaded documents - extract text from PDFs AND images
    
    This is the CRITICAL fix that was missing - it now:
    1. Handles both PDF and image files
    2. Automatically uses OCR when needed
    3. Extracts text immediately after upload
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
        extraction_results = []
        
        for document in documents:
            try:
                logger.info(f"🔄 Processing document: {document.document_name} ({document.document_type.value})")
                
                # Get file extension
                file_extension = document.file_path.lower().split('.')[-1]
                
                # Extract text based on file type
                extracted_text = ""
                
                if file_extension in ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                    # Use the enhanced extraction method
                    extracted_text = pdf_service.extract_text_from_file(document.file_path)
                    
                    logger.info(f"📝 Extracted {len(extracted_text)} characters from {document.document_name}")
                else:
                    logger.warning(f"⚠️ Unsupported file type: {file_extension}")
                    extracted_text = ""
                
                # Update document record
                document.extracted_text = extracted_text
                document.is_processed = True
                document.processed_at = datetime.utcnow()
                
                extraction_results.append({
                    "document_id": document.id,
                    "document_type": document.document_type.value,
                    "file_name": document.document_name,
                    "text_length": len(extracted_text),
                    "status": "success" if len(extracted_text) > 0 else "no_text_found"
                })
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing document {document.id}: {str(e)}")
                
                extraction_results.append({
                    "document_id": document.id,
                    "document_type": document.document_type.value,
                    "file_name": document.document_name,
                    "status": "error",
                    "error": str(e)
                })
                continue
        
        db.commit()
        
        logger.info(f"✅ Processed {processed_count} documents for application {application.application_number}")
        
        return {
            "message": f"Successfully processed {processed_count} documents",
            "processed_count": processed_count,
            "total_documents": len(documents),
            "extraction_results": extraction_results
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing documents: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process documents: {str(e)}"
        )