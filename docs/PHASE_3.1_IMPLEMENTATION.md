# Phase 3.1 Implementation Plan - Document Analysis & Intelligent Questionnaire

## 🎯 Goal
Extract maximum information from uploaded documents and generate intelligent, contextual questions to gather remaining information needed for AI document generation.

---

## 📊 Current Situation Analysis

### What We Have ✅
1. **8 uploaded documents** with extracted text (Phase 2)
2. **PDF text extraction** with OCR support
3. **Database models** for applications and documents
4. **Gemini AI service** ready to use
5. **Frontend** with document upload UI

### What We Need ❌
1. **Structured data extraction** from PDF text
2. **Database models** for extracted data and questionnaire
3. **AI Analysis Service** with document-specific prompts
4. **Dynamic Question Generator** based on extracted data
5. **API endpoints** for analysis and questionnaire
6. **Frontend UI** for analysis trigger and questionnaire

---

## 🏗️ Architecture Design

### Phase 3.1 Flow
```
User uploads 8 documents
    ↓
Clicks "Analyze Documents"
    ↓
Backend: AI Analysis Service
    ├─ Analyze Passport → Extract name, passport#, dates, nationality
    ├─ Analyze NID Bangla → Extract name, NID#, DOB, address (Bangla)
    ├─ Analyze Income Tax → Extract income, tax paid, years
    ├─ Analyze TIN → Extract TIN number, taxpayer name
    ├─ Analyze Hotel Booking → Extract hotel, dates, location
    ├─ Analyze Air Ticket → Extract flights, dates, destinations
    ├─ Analyze Bank Solvency → Extract balance, account info
    └─ Analyze Visa History → Extract countries visited, dates
    ↓
Store extracted data in database
    ↓
Intelligent Question Generator analyzes:
    ├─ What information is complete?
    ├─ What information is missing?
    ├─ What documents will be generated?
    └─ User's profession (businessman/job holder/other)
    ↓
Generate contextual questions:
    ├─ Personal Details (if missing)
    ├─ Employment/Business Details
    ├─ Travel Purpose & Plans
    ├─ Financial Information
    ├─ Asset Details
    └─ Home Ties
    ↓
Frontend: Show questionnaire wizard
    ↓
User answers questions
    ↓
Store responses in database
    ↓
Ready for Phase 3.2 (Document Generation)
```

---

## 🗄️ Database Schema Design

### 1. ExtractedData Table
```python
class ExtractedData(Base):
    """Store structured data extracted from uploaded documents"""
    __tablename__ = "extracted_data"
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    document_type = Column(Enum(DocumentType))
    
    # Structured extracted information
    data = Column(JSON)  # Flexible JSON structure
    
    # Extraction metadata
    confidence_score = Column(Float)  # AI confidence (0-1)
    extracted_at = Column(DateTime, default=func.now())
    
    # Relationships
    application = relationship("VisaApplication")
    document = relationship("Document")
```

### 2. QuestionnaireResponse Table
```python
class QuestionnaireResponse(Base):
    """Store user's responses to questionnaire"""
    __tablename__ = "questionnaire_responses"
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"))
    
    # Question details
    category = Column(String(100))  # 'personal', 'employment', 'travel', etc.
    question_key = Column(String(200))  # Unique identifier
    question_text = Column(Text)  # Actual question shown to user
    
    # Response
    answer = Column(Text)
    data_type = Column(String(50))  # 'text', 'date', 'number', 'select', etc.
    
    # Metadata
    is_required = Column(Boolean, default=True)
    answered_at = Column(DateTime)
    
    # Relationships
    application = relationship("VisaApplication")
```

### 3. AnalysisSession Table
```python
class AnalysisSession(Base):
    """Track analysis sessions"""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"))
    
    # Analysis status
    status = Column(String(50))  # 'started', 'analyzing', 'completed', 'failed'
    documents_analyzed = Column(Integer, default=0)
    total_documents = Column(Integer)
    
    # Results
    completeness_score = Column(Float)  # 0-100%
    missing_fields = Column(JSON)  # List of missing information
    
    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Error handling
    error_message = Column(Text)
    
    # Relationships
    application = relationship("VisaApplication")
```

---

## 🤖 AI Analysis Service Design

### Service: `AIAnalysisService`

#### Document-Specific Analysis Methods

**1. Passport Analysis**
```python
async def analyze_passport(self, text: str) -> dict:
    """
    Extract: 
    - Full name
    - Passport number
    - Date of birth
    - Nationality
    - Issue date
    - Expiry date
    - Place of issue
    """
    prompt = f"""
    Analyze this passport text and extract structured information.
    
    Passport Text:
    {text}
    
    Return JSON with:
    {{
        "full_name": "...",
        "passport_number": "...",
        "date_of_birth": "YYYY-MM-DD",
        "nationality": "...",
        "issue_date": "YYYY-MM-DD",
        "expiry_date": "YYYY-MM-DD",
        "place_of_issue": "...",
        "confidence": 0.95
    }}
    """
```

**2. NID Bangla Analysis**
```python
async def analyze_nid_bangla(self, text: str) -> dict:
    """
    Extract from Bangla NID:
    - Name (in Bangla)
    - Father's name (in Bangla)
    - Mother's name (in Bangla)
    - Date of birth
    - NID number
    - Address (in Bangla)
    """
    prompt = f"""
    Analyze this Bangladesh National ID card (in Bangla script).
    Extract information and keep Bangla text as-is.
    
    NID Text:
    {text}
    
    Return JSON with:
    {{
        "name_bangla": "...",
        "father_name_bangla": "...",
        "mother_name_bangla": "...",
        "date_of_birth": "YYYY-MM-DD",
        "nid_number": "...",
        "address_bangla": "...",
        "confidence": 0.90
    }}
    """
```

**3. Income Tax Analysis**
```python
async def analyze_income_tax(self, text: str) -> dict:
    """
    Extract:
    - Tax years
    - Annual income per year
    - Tax paid per year
    - Taxpayer name
    - TIN number
    """
```

**4. Bank Solvency Analysis**
```python
async def analyze_bank_solvency(self, text: str) -> dict:
    """
    Extract:
    - Account holder name
    - Account number
    - Bank name
    - Branch
    - Current balance
    - Account type
    - Certification date
    """
```

**5. Hotel Booking Analysis**
```python
async def analyze_hotel_booking(self, text: str) -> dict:
    """
    Extract:
    - Hotel name
    - Hotel address/location
    - Check-in date
    - Check-out date
    - Number of nights
    - Room type
    - Booking reference
    - Cancellation policy
    """
```

**6. Air Ticket Analysis**
```python
async def analyze_air_ticket(self, text: str) -> dict:
    """
    Extract:
    - Passenger name
    - Booking reference/PNR
    - Outbound flight: airline, flight#, date, from, to, time
    - Return flight: airline, flight#, date, from, to, time
    - Ticket price
    - Travel class
    """
```

**7. Visa History Analysis**
```python
async def analyze_visa_history(self, text: str) -> dict:
    """
    Extract from passport stamps:
    - List of countries visited
    - Entry dates
    - Exit dates
    - Visa types
    - Purpose of visits
    """
```

**8. TIN Certificate Analysis**
```python
async def analyze_tin_certificate(self, text: str) -> dict:
    """
    Extract:
    - TIN number
    - Taxpayer name
    - Circle/zone
    - Issue date
    - Taxpayer category
    """
```

---

## 🎓 Intelligent Question Generator Design

### Service: `QuestionnaireGeneratorService`

#### Logic Flow

```python
class QuestionnaireGeneratorService:
    def generate_questions(
        self,
        application_id: int,
        extracted_data: dict,
        uploaded_docs: list
    ) -> list[Question]:
        """
        Generate intelligent, contextual questions based on:
        1. What was extracted from documents
        2. What's missing
        3. User's profession/situation
        4. Which documents will be generated
        """
        
        questions = []
        
        # Determine user type
        user_type = self._detect_user_type(extracted_data)
        
        # Add questions by category
        questions += self._personal_questions(extracted_data)
        questions += self._employment_questions(extracted_data, user_type)
        questions += self._travel_purpose_questions()
        questions += self._financial_questions(extracted_data)
        questions += self._asset_questions(extracted_data)
        questions += self._home_ties_questions(extracted_data)
        
        return questions
```

#### Question Categories

**1. Personal Details** (only if missing from documents)
- What is your current residential address?
- What is your marital status?
- Do you have any dependents? If yes, how many?
- What is your date of birth? (if not in passport)

**2. Employment/Business Details** (contextual based on user type)

*For Job Holders:*
- What is your current job title?
- What is the name of your employer/company?
- Company address and phone number?
- How long have you been working there?
- What is your monthly salary?
- Supervisor/HR contact information?

*For Business Owners:*
- What is the name of your business?
- What type of business do you run?
- When did you start this business?
- Business registration number?
- Business address and contact?
- What are your monthly business revenues?
- How many employees do you have?

**3. Travel Purpose & Plans**
- Why are you traveling to Iceland?
- What places in Iceland are you planning to visit?
- What activities do you plan to do?
- Have you visited Iceland or other Schengen countries before?
- Do you have any friends or family in Iceland?

**4. Financial Information**
- What is your monthly income?
- What are your monthly expenses?
- Source of funds for this trip?
- Who will sponsor this trip?

**5. Asset Details**
- Do you own any property/real estate? (details)
- Do you own any vehicles? (details)
- Do you have any investments? (details)
- Estimated total value of your assets?

**6. Home Ties (Why you will return)**
- What are your reasons for returning to Bangladesh?
- Do you have family members in Bangladesh?
- Do you have ongoing business commitments?
- Do you own property in Bangladesh?
- Any other strong ties to Bangladesh?

---

## 🔌 API Endpoints Design

### Analysis Endpoints

```python
@router.post("/api/analysis/start/{application_id}")
async def start_analysis(application_id: int):
    """
    Start document analysis for an application
    Returns: analysis_session_id, status
    """

@router.get("/api/analysis/status/{application_id}")
async def get_analysis_status(application_id: int):
    """
    Get current analysis status
    Returns: status, progress, extracted_data summary
    """

@router.get("/api/analysis/results/{application_id}")
async def get_analysis_results(application_id: int):
    """
    Get complete analysis results
    Returns: extracted_data, completeness_score, missing_fields
    """
```

### Questionnaire Endpoints

```python
@router.get("/api/questionnaire/generate/{application_id}")
async def generate_questionnaire(application_id: int):
    """
    Generate intelligent questions based on analysis
    Returns: list of questions grouped by category
    """

@router.post("/api/questionnaire/response/{application_id}")
async def save_response(application_id: int, responses: List[ResponseData]):
    """
    Save user's questionnaire responses
    Returns: saved responses, completion percentage
    """

@router.get("/api/questionnaire/responses/{application_id}")
async def get_responses(application_id: int):
    """
    Get all saved responses
    Returns: responses grouped by category
    """

@router.get("/api/questionnaire/progress/{application_id}")
async def get_progress(application_id: int):
    """
    Get questionnaire completion progress
    Returns: total_questions, answered, percentage
    """
```

---

## 🎨 Frontend UI Design

### 1. Analysis Section (in ApplicationDetailsPage)

```jsx
<Card>
  <CardHeader title="Document Analysis" />
  <CardContent>
    {!analysisStarted && (
      <Button 
        onClick={handleStartAnalysis}
        startIcon={<AnalyticsIcon />}
      >
        Analyze Documents
      </Button>
    )}
    
    {analyzing && (
      <Box>
        <LinearProgress value={analysisProgress} />
        <Typography>
          Analyzing {currentDocument}... ({progress}/{total})
        </Typography>
      </Box>
    )}
    
    {analysisComplete && (
      <Box>
        <Alert severity="success">
          Analysis complete! {completenessScore}% information extracted
        </Alert>
        <Button onClick={handleViewResults}>
          View Extracted Information
        </Button>
      </Box>
    )}
  </CardContent>
</Card>
```

### 2. Questionnaire Wizard Component

```jsx
<QuestionnaireWizard
  applicationId={id}
  questions={questions}
  onComplete={handleQuestionnaireComplete}
>
  {/* Multi-step form */}
  <Step1_PersonalDetails />
  <Step2_Employment />
  <Step3_TravelPurpose />
  <Step4_Financial />
  <Step5_Assets />
  <Step6_HomeTies />
</QuestionnaireWizard>
```

---

## 📋 Implementation Checklist

### Backend Tasks
- [ ] Create new database models (ExtractedData, QuestionnaireResponse, AnalysisSession)
- [ ] Create migration script for new tables
- [ ] Implement AIAnalysisService with 8 document analyzers
- [ ] Implement QuestionnaireGeneratorService
- [ ] Create analysis API endpoints
- [ ] Create questionnaire API endpoints
- [ ] Update application status flow
- [ ] Add error handling and logging

### Frontend Tasks
- [ ] Create AnalysisSection component
- [ ] Create AnalysisProgress component
- [ ] Create ExtractedDataViewer component
- [ ] Create QuestionnaireWizard component
- [ ] Create QuestionForm components for each category
- [ ] Add analysis API integration
- [ ] Add questionnaire API integration
- [ ] Update ApplicationDetailsPage

### Testing Tasks
- [ ] Test each document analyzer with real PDFs
- [ ] Test question generation logic
- [ ] Test questionnaire save/resume
- [ ] Test complete analysis flow
- [ ] Test error scenarios

---

## ⏱️ Estimated Timeline

- Database models & migrations: **30 minutes**
- AI Analysis Service (8 analyzers): **2 hours**
- Questionnaire Generator: **1 hour**
- API endpoints: **1 hour**
- Frontend components: **2 hours**
- Testing & refinement: **1 hour**

**Total: ~7 hours** (1 full working day)

---

## 🚀 Ready to Implement?

This plan ensures:
✅ Proper analysis of all 8 document types
✅ Intelligent, contextual questions
✅ Different questions for businessman vs job holder
✅ Professional web development approach
✅ Scalable, maintainable code

**Shall I proceed with implementation?**
