# Phase 3 & 4 Complete Implementation Plan

## Phase 2 Completion Summary ✅

### Completed Features
1. ✅ Document upload system (drag & drop)
2. ✅ File validation (size: 10MB, types: PDF, JPG, JPEG, PNG)
3. ✅ Progress tracking during upload
4. ✅ Document list with upload status
5. ✅ Required documents display (16 documents for Iceland/Tourist)
6. ✅ PDF text extraction with OCR support
7. ✅ Document storage service
8. ✅ Database models for documents
9. ✅ API endpoints (upload, list, delete)
10. ✅ Error handling and logging

### What Works
- Users can create visa applications
- Users can upload all 9 required documents
- System validates and stores uploaded files
- Frontend displays upload status with progress
- Backend extracts text from PDFs using OCR

---

## Phase 3: AI Document Analysis & Generation

### Overview
Phase 3 implements intelligent document analysis and automated generation of 7 required documents using Google Gemini AI.

### 3.1 Questionnaire System (Most Important)

**Purpose:** Collect additional information needed for document generation

#### Frontend Components
1. **QuestionnaireDialog.jsx**
   - Multi-step form wizard
   - Progress indicator
   - Dynamic questions based on uploaded documents
   - Save/resume capability
   - Validation for each step

2. **Question Categories**
   - **Personal Details** (if not in uploaded docs)
     - Full name, date of birth, address
     - Occupation, employer details
     - Marital status, family information
   
   - **Travel Purpose**
     - Reason for visiting Iceland
     - Places planning to visit
     - Activities planned
     - Travel duration and dates
   
   - **Financial Information**
     - Monthly income
     - Source of funds for trip
     - Dependents
     - Other financial commitments
   
   - **Employment Details**
     - Job title, company name
     - Years of employment
     - Business address, phone
     - Purpose for visiting card design
   
   - **Home Ties**
     - Property ownership
     - Family in Bangladesh
     - Business/employment commitments
     - Reasons to return
   
   - **Asset Information**
     - Real estate details
     - Vehicle ownership
     - Investments
     - Other significant assets

#### Backend API
```
POST /api/questionnaire/{application_id}
GET /api/questionnaire/{application_id}
PUT /api/questionnaire/{application_id}
```

#### Database Schema
```sql
CREATE TABLE questionnaire_responses (
    id SERIAL PRIMARY KEY,
    application_id INT REFERENCES visa_applications(id),
    category VARCHAR(100),
    question VARCHAR(500),
    answer TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3.2 AI Document Analysis Service

**Purpose:** Extract structured information from uploaded documents

#### Service: `AIAnalysisService`

**Methods:**
1. `analyze_passport(file_path)` → Extract name, passport number, issue/expiry dates, nationality
2. `analyze_nid_bangla(file_path)` → Extract name, NID number, DOB, address (Bangla text)
3. `analyze_bank_statement(file_path)` → Extract account holder, balance, transactions
4. `analyze_income_tax(file_path)` → Extract tax years, income, tax paid
5. `analyze_hotel_booking(file_path)` → Extract hotel name, dates, location
6. `analyze_air_ticket(file_path)` → Extract flight dates, destinations, booking reference

**Implementation:**
```python
class AIAnalysisService:
    def __init__(self):
        self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_document(self, file_path: str, document_type: str) -> dict:
        """Analyze document and extract structured data"""
        # Read document text (already extracted in Phase 2)
        # Create AI prompt based on document type
        # Use Gemini to extract structured data
        # Return JSON with extracted information
```

**API Endpoint:**
```
POST /api/documents/analyze/{application_id}
Response: {
    "analysis_complete": true,
    "extracted_data": {
        "passport": {...},
        "nid": {...},
        "bank_statement": {...}
    }
}
```

---

### 3.3 AI Document Generation Service

**Purpose:** Generate 8 professional documents using AI

#### Service: `AIGenerationService`

#### 1. Asset Valuation Certificate
**Input:** 
- Questionnaire responses (assets)
- Bank statements
- Income tax returns
**Process:**
- AI researches typical asset valuation formats
- Calculates total asset value
- Generates professional certificate PDF
**Output:** PDF document with official format

#### 2. NID English Translation
**Input:** Bangla NID (uploaded)
**Process:**
- Extract Bangla text using OCR
- Translate to English maintaining structure
- Generate NID in official Bangladesh format
- Include: Photo, Name, Father's name, Mother's name, DOB, NID number, Address
**Output:** Professional NID translation (English) as PDF

#### 3. Professional Visiting Card
**Input:** 
- Questionnaire responses (job, company)
- Passport photo
**Process:**
- AI creates beautiful, professional design
- Multiple design templates available
- Includes: Name, Title, Company, Phone, Email, Address
- High-quality graphics
**Output:** Print-ready visiting card PDF (both sides)

#### 4. Cover Letter (MOST IMPORTANT)
**Input:**
- ALL uploaded documents
- ALL questionnaire responses
- Extracted data from analysis
**Process:**
- AI generates comprehensive cover letter
- Explains purpose of visit
- Demonstrates financial capacity
- Shows strong home ties
- Professional tone and structure
- Addresses visa officer directly
**Output:** 2-3 page professional cover letter PDF

#### 5. Travel Itinerary
**Input:**
- Hotel booking
- Air ticket
- Questionnaire (places to visit)
**Process:**
- Extract dates and locations
- Research attractions in each location
- Create day-by-day itinerary
- Include activities, timings, costs
**Output:** Detailed travel itinerary PDF

#### 6. Travel History
**Input:** Passport (visa stamps)
**Process:**
- Extract all visa stamps and entry/exit stamps
- Create chronological travel history
- Format as professional document
- Include countries visited, dates, purposes
**Output:** Travel history summary PDF

#### 7. Home Tie Statement
**Input:**
- Questionnaire responses
- Employment details
- Family information
- Property ownership
**Process:**
- AI generates compelling statement
- Demonstrates strong ties to Bangladesh
- Shows reasons to return
- Professional formatting
**Output:** Home tie statement letter PDF

#### 8. Financial Statement Summary
**Input:** Bank statements (all uploaded)
**Process:**
- Extract account balances
- Calculate average balance
- Summarize income sources
- Create professional summary
**Output:** Financial statement PDF

---

### 3.4 Frontend UI for Phase 3

#### Application Detail Page Updates
1. **Analysis Section**
   - "Analyze Documents" button
   - Analysis progress indicator
   - Extracted information display

2. **Questionnaire Section**
   - "Complete Questionnaire" button
   - Progress: X/6 categories completed
   - Edit/resume capability

3. **Generate Documents Section**
   - List of 8 documents to generate
   - "Generate All" button
   - Individual generate buttons
   - Generation progress
   - Preview generated documents
   - Download buttons

#### UI Flow
```
1. Upload 9 documents (Phase 2) ✅
2. Click "Analyze Documents" → AI extracts info
3. Click "Complete Questionnaire" → Multi-step form
4. Click "Generate Documents" → AI creates 8 docs
5. Review and download all documents
6. Submit visa application
```

---

## Phase 4: Document Review & Submission

### Overview
Phase 4 implements quality checks and final submission preparation.

### 4.1 Document Review System

#### Features
1. **Checklist Verification**
   - All 16 documents present
   - All documents meet requirements
   - No errors in generated documents

2. **Document Preview**
   - In-browser PDF viewer
   - Side-by-side comparison
   - Annotation capability

3. **Quality Checks**
   - AI reviews generated documents
   - Checks for consistency
   - Validates all information matches
   - Suggests improvements

#### API Endpoints
```
GET /api/review/{application_id}/checklist
POST /api/review/{application_id}/validate
GET /api/review/{application_id}/suggestions
```

---

### 4.2 Final Package Generation

#### Features
1. **PDF Merger**
   - Combines all 16 documents
   - Creates organized bookmarks
   - Adds table of contents
   - Page numbering

2. **Cover Page**
   - Application summary
   - Document list
   - Submission date
   - Contact information

3. **Download Options**
   - Individual documents (ZIP)
   - Complete package (single PDF)
   - Print-ready format

#### Implementation
```python
class PackageGenerationService:
    async def create_final_package(application_id: int):
        # Collect all 16 documents
        # Add cover page and TOC
        # Merge into single PDF
        # Add bookmarks and page numbers
        # Return download link
```

---

### 4.3 Submission Preparation

#### Features
1. **Email Template**
   - Professional email draft
   - Addressed to embassy
   - Includes all attachments
   - Request for appointment

2. **Checklist PDF**
   - Printable checklist
   - Document organization guide
   - Embassy contact information
   - Submission instructions

3. **Status Tracking**
   - Mark as submitted
   - Add submission date
   - Upload embassy response
   - Track application status

---

## Implementation Timeline

### Phase 3: Estimated 5-7 days
- **Day 1-2:** Questionnaire system (frontend + backend)
- **Day 3:** AI Analysis Service
- **Day 4-5:** AI Generation Service (8 documents)
- **Day 6:** UI integration and testing
- **Day 7:** Bug fixes and refinement

### Phase 4: Estimated 2-3 days
- **Day 1:** Review system and quality checks
- **Day 2:** Package generation and PDF merger
- **Day 3:** Testing and final polish

---

## Technical Requirements

### Backend Dependencies
```
google-generativeai==0.3.0
PyPDF2==3.0.1
reportlab==4.0.7
Pillow==10.1.0
python-docx==1.1.0
```

### Frontend Dependencies
```
react-pdf==7.5.1
react-multi-step-form==1.2.0
pdf-lib==1.17.1
```

### Environment Variables
```
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
MAX_TOKENS=8000
```

---

## Success Criteria

### Phase 3
✅ Users can complete questionnaire
✅ AI successfully extracts data from all uploaded documents
✅ AI generates all 8 documents professionally
✅ Generated documents are accurate and well-formatted
✅ Users can preview and download generated documents

### Phase 4
✅ All 16 documents validated and error-free
✅ Final package generated successfully
✅ Users can download complete package
✅ Application marked as ready for submission

---

## Next Steps

1. **Review this plan** - Confirm approach is correct
2. **Start Phase 3** - Begin with questionnaire system
3. **Implement AI services** - Analysis and generation
4. **Test thoroughly** - Ensure quality output
5. **Move to Phase 4** - Final polish and submission

**Ready to proceed with Phase 3 implementation?**
