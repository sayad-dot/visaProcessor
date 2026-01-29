"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VisaType(str, Enum):
    """Supported visa types"""
    TOURIST = "Tourist"


class Country(str, Enum):
    """Supported countries"""
    ICELAND = "Iceland"


class ApplicationStatus(str, Enum):
    """Application status"""
    DRAFT = "draft"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentTypeEnum(str, Enum):
    """Document types"""
    # User provided
    PASSPORT_COPY = "passport_copy"
    NID_BANGLA = "nid_bangla"
    VISA_HISTORY = "visa_history"
    TIN_CERTIFICATE = "tin_certificate"
    INCOME_TAX_3YEARS = "income_tax_3years"
    ASSET_VALUATION = "asset_valuation"
    HOTEL_BOOKING = "hotel_booking"
    AIR_TICKET = "air_ticket"
    BANK_SOLVENCY = "bank_solvency"
    
    # System generated
    NID_ENGLISH = "nid_english"
    VISITING_CARD = "visiting_card"
    COVER_LETTER = "cover_letter"
    TRAVEL_ITINERARY = "travel_itinerary"
    TRAVEL_HISTORY = "travel_history"
    HOME_TIE_STATEMENT = "home_tie_statement"
    FINANCIAL_STATEMENT = "financial_statement"


# Request Schemas
class ApplicationCreate(BaseModel):
    """Schema for creating a new visa application"""
    applicant_name: Optional[str] = None
    applicant_email: Optional[EmailStr] = None
    applicant_phone: Optional[str] = None
    country: Country = Country.ICELAND
    visa_type: VisaType = VisaType.TOURIST


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: int
    document_type: DocumentTypeEnum
    file_name: str
    file_size: int
    message: str
    metadata: Optional[Dict[str, Any]] = None  # Added for PDF metadata


class MissingInfoQuestion(BaseModel):
    """Question about missing information"""
    field_name: str
    question: str
    data_type: str  # 'text', 'date', 'number', etc.


class MissingInfoResponse(BaseModel):
    """User's response to missing info questions"""
    field_name: str
    value: Any


# Response Schemas
class RequiredDocumentResponse(BaseModel):
    """Required document response schema"""
    id: int
    country: str
    visa_type: str
    document_type: str
    description: Optional[str]
    is_mandatory: bool
    can_be_generated: bool
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: int
    document_type: str
    document_name: str
    file_path: str
    file_size: Optional[int]
    is_uploaded: bool
    is_processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    """Visa application response schema"""
    id: int
    application_number: str
    applicant_name: Optional[str]
    applicant_email: Optional[str]
    applicant_phone: Optional[str]
    country: str
    visa_type: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    documents: List[DocumentResponse] = []
    
    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    """Detailed application response with extracted data"""
    extracted_data: Dict[str, Any] = {}
    missing_info: List[str] = []


class RequiredDocumentResponse(BaseModel):
    """Required document information"""
    document_type: str
    description: str
    is_mandatory: bool
    can_be_generated: bool
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Phase 3.1 Schemas - Analysis & Questionnaire

class AnalysisStartResponse(BaseModel):
    """Response when starting document analysis"""
    session_id: int
    status: str
    total_documents: int
    message: str


class AnalysisStatusResponse(BaseModel):
    """Current status of analysis session"""
    session_id: int
    status: str
    documents_analyzed: int
    total_documents: int
    current_document: Optional[str]
    progress_percentage: int
    completeness_score: int


class AnalysisResultsResponse(BaseModel):
    """Complete analysis results"""
    session_id: int
    status: str
    completeness_score: int
    extracted_data: Dict[str, Any]
    missing_fields: List[str]
    completed_at: Optional[datetime]


class QuestionResponse(BaseModel):
    """Single question schema"""
    key: str
    text: str
    category: str
    data_type: str
    is_required: bool
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None


class QuestionnaireGenerateResponse(BaseModel):
    """Generated questionnaire grouped by category"""
    personal: List[QuestionResponse]
    employment: List[QuestionResponse] = []
    business: List[QuestionResponse] = []
    travel_purpose: List[QuestionResponse]
    financial: List[QuestionResponse]
    assets: List[QuestionResponse]
    home_ties: List[QuestionResponse]
    total_questions: int


class SaveQuestionnaireResponse(BaseModel):
    """Single questionnaire response"""
    question_key: str
    answer: str


class SaveQuestionnaireRequest(BaseModel):
    """Request to save questionnaire responses"""
    responses: List[SaveQuestionnaireResponse]


class QuestionnaireProgressResponse(BaseModel):
    """Questionnaire completion progress"""
    total_questions: int
    answered_questions: int
    completion_percentage: int
    categories_completed: List[str]
    categories_pending: List[str]


class ExtractedDataResponse(BaseModel):
    """Extracted data from a single document"""
    document_type: str
    data: Dict[str, Any]
    confidence_score: int
    extracted_at: datetime
    
    class Config:
        from_attributes = True

