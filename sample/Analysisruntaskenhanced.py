"""
CRITICAL UPDATE for analysis.py - Ensure text extraction before analysis

This updates the run_analysis_task to:
1. Check if text extraction is done first
2. Trigger extraction if needed
3. Better error handling
"""

# REPLACE the existing run_analysis_task function in analysis.py with this enhanced version:

async def run_analysis_task(
    application_id: int,
    session_id: int,
    db: Session
):
    """Enhanced background task to analyze all documents"""
    try:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            logger.error(f"❌ Analysis session {session_id} not found")
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
        
        logger.info(f"🔍 Starting analysis for {len(documents)} documents")
        
        # ===== CRITICAL FIX: Ensure text extraction first =====
        from app.services.pdf_service import PDFService
        pdf_service = PDFService()
        
        extraction_needed = False
        for doc in documents:
            # Check if text extraction is needed
            if not doc.extracted_text or len(doc.extracted_text.strip()) < 10:
                extraction_needed = True
                logger.info(f"⚠️ Text not extracted for {doc.document_type.value}, extracting now...")
                
                try:
                    # Extract text based on file type
                    file_extension = doc.file_path.lower().split('.')[-1]
                    
                    if file_extension in ['pdf', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                        extracted_text = pdf_service.extract_text_from_file(doc.file_path)
                        
                        # Update document
                        doc.extracted_text = extracted_text
                        doc.is_processed = True
                        doc.processed_at = datetime.now()
                        
                        logger.info(f"✅ Extracted {len(extracted_text)} characters from {doc.document_type.value}")
                    else:
                        logger.warning(f"⚠️ Unsupported file type for {doc.document_type.value}: {file_extension}")
                        doc.extracted_text = ""
                        doc.is_processed = True
                        
                except Exception as e:
                    logger.error(f"❌ Error extracting text from {doc.document_type.value}: {str(e)}")
                    doc.extracted_text = ""
                    doc.is_processed = True
        
        # Commit all extractions
        if extraction_needed:
            db.commit()
            logger.info("✅ Text extraction completed for all documents")
        
        # ===== Now proceed with AI analysis =====
        analysis_service = get_analysis_service()
        extracted_data_dict = {}
        
        for idx, doc in enumerate(documents, 1):
            try:
                # Update current document
                session.current_document = doc.document_type.value
                session.documents_analyzed = idx
                db.commit()
                
                logger.info(f"🤖 Analyzing document {idx}/{len(documents)}: {doc.document_type.value}")
                
                # Get extracted text
                extracted_text = doc.extracted_text or ""
                
                # Check if we have enough text to analyze
                if len(extracted_text.strip()) < 10:
                    logger.warning(f"⚠️ Insufficient text for {doc.document_type.value} ({len(extracted_text)} chars), skipping AI analysis")
                    
                    # Still save a record with error
                    extracted_data = ExtractedData(
                        application_id=application_id,
                        document_id=doc.id,
                        document_type=doc.document_type,
                        data={
                            "error": "Insufficient text extracted from document",
                            "text_length": len(extracted_text),
                            "confidence": 0
                        },
                        confidence_score=0
                    )
                    db.add(extracted_data)
                    db.commit()
                    continue
                
                # Analyze document with AI
                result = await analysis_service.analyze_document(
                    document_type=doc.document_type,
                    extracted_text=extracted_text
                )
                
                # Ensure confidence score exists
                confidence = result.get("confidence", 0)
                
                # Save extracted data
                extracted_data = ExtractedData(
                    application_id=application_id,
                    document_id=doc.id,
                    document_type=doc.document_type,
                    data=result,
                    confidence_score=confidence
                )
                db.add(extracted_data)
                db.commit()
                
                # Store in dict for later use
                extracted_data_dict[doc.document_type.value] = result
                
                logger.info(f"✅ Analyzed {doc.document_type.value} - Confidence: {confidence}%")
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {doc.document_type.value}: {str(e)}")
                
                # Save error record
                extracted_data = ExtractedData(
                    application_id=application_id,
                    document_id=doc.id,
                    document_type=doc.document_type,
                    data={
                        "error": str(e),
                        "confidence": 0
                    },
                    confidence_score=0
                )
                db.add(extracted_data)
                db.commit()
                continue
        
        # Calculate completeness score
        total_fields = 0
        complete_fields = 0
        
        for doc_type, data in extracted_data_dict.items():
            if "error" not in data or data.get("confidence", 0) > 0:
                for key, value in data.items():
                    if key not in ["confidence", "error", "raw_text_sample", "raw_response"]:
                        total_fields += 1
                        # Check if field has meaningful value
                        if value and value not in [None, "", [], {}, "null", "None"]:
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
        logger.info(f"📊 Fields: {complete_fields}/{total_fields} complete")
        
    except Exception as e:
        logger.error(f"❌ Analysis task failed: {str(e)}")
        
        # Update session with error
        try:
            session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
            if session:
                session.status = AnalysisStatus.FAILED
                session.error_message = str(e)
                db.commit()
        except:
            pass