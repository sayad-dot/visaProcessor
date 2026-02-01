"""
Intelligent Questionnaire Analyzer - Determines what questions to ask based on:
1. Which documents are uploaded
2. Which documents are missing
3. What information is already extracted
4. What information is still needed for document generation
"""
from typing import Dict, List, Set, Tuple
from loguru import logger

from app.models import DocumentType
from app.services.document_requirements import DocumentRequirementsMapping, FieldRequirement


class IntelligentQuestionnaireAnalyzer:
    """
    Analyzes uploaded documents and extracted data to determine
    what additional information is needed
    """
    
    def __init__(self):
        self.requirements_map = DocumentRequirementsMapping()
    
    def analyze_and_generate_questions(
        self,
        uploaded_documents: List[DocumentType],
        extracted_data: Dict[str, Dict],
        target_country: str = "Iceland",
        visa_type: str = "Tourist"
    ) -> Tuple[List[FieldRequirement], Dict[str, any]]:
        """
        Main analysis method - determines what questions to ask
        
        Args:
            uploaded_documents: List of document types that user uploaded
            extracted_data: Dict of extracted data from uploaded documents
                            Format: {document_type: {field: value}}
            target_country: Target country for visa
            visa_type: Type of visa
        
        Returns:
            Tuple of (questions_to_ask, analysis_summary)
        """
        logger.info(f"🔍 Starting intelligent questionnaire analysis")
        logger.info(f"📤 Uploaded documents: {len(uploaded_documents)}")
        logger.info(f"📥 Missing documents: {16 - len(uploaded_documents)}")
        
        # Step 1: Identify missing documents
        missing_documents = self._identify_missing_documents(uploaded_documents)
        logger.info(f"📋 Missing document types: {[d.value for d in missing_documents]}")
        
        # Step 2: Identify what information we already have
        available_fields = self._extract_available_fields(extracted_data)
        logger.info(f"✅ Already have {len(available_fields)} fields from uploaded documents")
        
        # Step 3: Determine what information is needed for missing documents
        required_fields = self._determine_required_fields(missing_documents)
        logger.info(f"📝 Need {len(required_fields)} total fields for missing documents")
        
        # Step 4: Find gaps - what we need but don't have
        missing_fields = self._identify_missing_fields(
            required_fields=required_fields,
            available_fields=available_fields,
            extracted_data=extracted_data
        )
        logger.info(f"❓ Missing {len(missing_fields)} critical fields - will generate questions")
        
        # Step 5: Generate questions for missing fields
        questions = self._generate_questions_for_missing_fields(missing_fields)
        
        # Step 6: Add verification questions for low-confidence extractions
        verification_questions = self._generate_verification_questions(
            extracted_data=extracted_data,
            uploaded_documents=uploaded_documents
        )
        questions.extend(verification_questions)
        
        # Step 7: Sort questions by priority
        questions = self._sort_questions_by_priority(questions)
        
        # Create analysis summary
        analysis_summary = {
            "total_documents": 16,
            "uploaded_count": len(uploaded_documents),
            "missing_count": len(missing_documents),
            "uploaded_types": [d.value for d in uploaded_documents],
            "missing_types": [d.value for d in missing_documents],
            "fields_available": len(available_fields),
            "fields_needed": len(required_fields),
            "fields_missing": len(missing_fields),
            "questions_generated": len(questions),
            "critical_questions": len([q for q in questions if q.priority == "critical"]),
            "important_questions": len([q for q in questions if q.priority == "important"]),
            "optional_questions": len([q for q in questions if q.priority == "optional"])
        }
        
        logger.info(f"✅ Generated {len(questions)} intelligent questions")
        logger.info(f"   - Critical: {analysis_summary['critical_questions']}")
        logger.info(f"   - Important: {analysis_summary['important_questions']}")
        logger.info(f"   - Optional: {analysis_summary['optional_questions']}")
        
        return questions, analysis_summary
    
    def _identify_missing_documents(
        self,
        uploaded_documents: List[DocumentType]
    ) -> List[DocumentType]:
        """Identify which documents are missing"""
        all_documents = set(DocumentType)
        uploaded_set = set(uploaded_documents)
        missing = all_documents - uploaded_set
        return list(missing)
    
    def _extract_available_fields(
        self,
        extracted_data: Dict[str, Dict]
    ) -> Dict[str, any]:
        """
        Extract all available fields from extracted data
        Returns dict of {field_key: value}
        """
        available = {}
        
        for doc_type, data in extracted_data.items():
            if not isinstance(data, dict):
                continue
            
            # Map document type to field prefix
            # e.g., passport_copy -> passport.*
            prefix = self._get_field_prefix(doc_type)
            
            # Extract all non-empty fields
            for key, value in data.items():
                # Skip metadata fields
                if key in ['confidence', 'error', 'raw_text_sample', 'raw_response']:
                    continue
                
                # Check if field has meaningful value
                if value and value not in [None, "", [], {}, "null", "None", "N/A"]:
                    field_key = f"{prefix}.{key}"
                    available[field_key] = value
        
        return available
    
    def _get_field_prefix(self, document_type_value: str) -> str:
        """Get field prefix for a document type"""
        mapping = {
            "passport_copy": "passport",
            "nid_bangla": "nid",
            "bank_solvency": "bank",
            "visa_history": "visa_history",
            "tin_certificate": "tin",
            "income_tax_3years": "tax",
            "hotel_booking": "hotel",
            "air_ticket": "flight",
            "asset_valuation": "assets"
        }
        return mapping.get(document_type_value, document_type_value.replace("_", "."))
    
    def _determine_required_fields(
        self,
        missing_documents: List[DocumentType]
    ) -> List[FieldRequirement]:
        """
        Determine what fields are required to generate missing documents
        """
        required_fields = []
        seen_keys = set()  # Avoid duplicate questions
        
        for doc_type in missing_documents:
            requirements = self.requirements_map.get_requirements(doc_type)
            
            for req in requirements:
                # Avoid duplicate questions for same field
                if req.field_key not in seen_keys:
                    required_fields.append(req)
                    seen_keys.add(req.field_key)
        
        return required_fields
    
    def _identify_missing_fields(
        self,
        required_fields: List[FieldRequirement],
        available_fields: Dict[str, any],
        extracted_data: Dict[str, Dict]
    ) -> List[FieldRequirement]:
        """
        Identify which required fields are missing or have low confidence
        """
        missing = []
        
        for req in required_fields:
            # Check if we already have this field
            if req.field_key in available_fields:
                # We have the field, check confidence
                confidence = self._get_field_confidence(req.field_key, extracted_data)
                
                # If confidence is low, ask for verification
                if confidence < 70:
                    # Mark as verification question
                    req_copy = FieldRequirement(
                        field_key=req.field_key,
                        field_name=f"{req.field_name} (Verification)",
                        question=f"We extracted '{available_fields[req.field_key]}' for {req.field_name}. Is this correct?",
                        data_type=req.data_type,
                        priority="important",
                        help_text=f"Extracted value: {available_fields[req.field_key]}. Please verify or correct.",
                        placeholder=req.placeholder
                    )
                    missing.append(req_copy)
                # else: We have it with high confidence, no need to ask
            else:
                # We don't have this field at all
                missing.append(req)
        
        return missing
    
    def _get_field_confidence(
        self,
        field_key: str,
        extracted_data: Dict[str, Dict]
    ) -> int:
        """Get confidence score for a specific field"""
        # Extract document type from field key (e.g., "passport.full_name" -> "passport")
        prefix = field_key.split('.')[0]
        
        # Find corresponding document
        for doc_type, data in extracted_data.items():
            if prefix in doc_type.lower():
                return data.get('confidence', 0)
        
        return 0
    
    def _generate_questions_for_missing_fields(
        self,
        missing_fields: List[FieldRequirement]
    ) -> List[FieldRequirement]:
        """
        Generate actual questions for missing fields
        Already in FieldRequirement format, just return
        """
        return missing_fields
    
    def _generate_verification_questions(
        self,
        extracted_data: Dict[str, Dict],
        uploaded_documents: List[DocumentType]
    ) -> List[FieldRequirement]:
        """
        Generate questions to verify critical fields from uploaded documents
        that had low confidence extraction
        """
        verification_questions = []
        
        for doc_type in uploaded_documents:
            doc_type_value = doc_type.value
            
            if doc_type_value not in extracted_data:
                continue
            
            data = extracted_data[doc_type_value]
            confidence = data.get('confidence', 0)
            
            # If overall confidence is low, ask for critical field verification
            if confidence < 75:
                # Get critical fields for this document type
                requirements = self.requirements_map.get_requirements(doc_type)
                critical_reqs = [r for r in requirements if r.priority == "critical"]
                
                prefix = self._get_field_prefix(doc_type_value)
                
                for req in critical_reqs:
                    # Check if field was extracted
                    field_name = req.field_key.split('.')[-1]  # Get last part
                    extracted_value = data.get(field_name)
                    
                    if extracted_value:
                        # Create verification question
                        verify_req = FieldRequirement(
                            field_key=f"{req.field_key}_verify",
                            field_name=f"{req.field_name} (Please Verify)",
                            question=f"We extracted '{extracted_value}' from your {doc_type.value}. Is this correct? If not, please provide the correct value.",
                            data_type=req.data_type,
                            priority="important",
                            help_text=f"Low confidence extraction ({confidence}%). Please verify.",
                            placeholder=str(extracted_value)
                        )
                        verification_questions.append(verify_req)
        
        return verification_questions
    
    def _sort_questions_by_priority(
        self,
        questions: List[FieldRequirement]
    ) -> List[FieldRequirement]:
        """
        Sort questions by priority: critical -> important -> optional
        """
        priority_order = {"critical": 1, "important": 2, "optional": 3}
        
        return sorted(
            questions,
            key=lambda q: priority_order.get(q.priority, 99)
        )
    
    def group_questions_by_category(
        self,
        questions: List[FieldRequirement]
    ) -> Dict[str, List[FieldRequirement]]:
        """
        Group questions by logical categories for better UX
        """
        categories = {
            "personal_identity": [],
            "travel_details": [],
            "business_employment": [],
            "financial": [],
            "assets_property": [],
            "home_ties": [],
            "verification": []
        }
        
        for q in questions:
            # Determine category based on field key
            if any(x in q.field_key for x in ['passport', 'nid', 'name', 'birth', 'identity']):
                categories['personal_identity'].append(q)
            elif any(x in q.field_key for x in ['travel', 'trip', 'visit', 'hotel', 'flight', 'itinerary']):
                categories['travel_details'].append(q)
            elif any(x in q.field_key for x in ['business', 'company', 'employment', 'designation', 'job']):
                categories['business_employment'].append(q)
            elif any(x in q.field_key for x in ['financial', 'income', 'bank', 'savings', 'tax']):
                categories['financial'].append(q)
            elif any(x in q.field_key for x in ['assets', 'property', 'vehicle', 'investment']):
                categories['assets_property'].append(q)
            elif any(x in q.field_key for x in ['home_ties', 'family', 'reasons_to_return']):
                categories['home_ties'].append(q)
            elif 'verify' in q.field_key:
                categories['verification'].append(q)
            else:
                # Default to personal
                categories['personal_identity'].append(q)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}


# Singleton instance
_intelligent_analyzer = None

def get_intelligent_analyzer() -> IntelligentQuestionnaireAnalyzer:
    """Get or create intelligent analyzer instance"""
    global _intelligent_analyzer
    if _intelligent_analyzer is None:
        _intelligent_analyzer = IntelligentQuestionnaireAnalyzer()
    return _intelligent_analyzer
