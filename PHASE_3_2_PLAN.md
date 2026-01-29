# Phase 3.2 - AI PDF Generation Plan

## Analysis of Sample Documents (UK Visa Samples)

### ✅ Analyzed Documents:

1. **Cover Letter** (5498 chars)
   - Format: Formal business letter
   - Sections: Date, To (Embassy), Subject, Body paragraphs, Closing
   - Key content: Purpose, travel plans, ties to home country, financial ability
   
2. **Asset Valuation** (15833 chars)
   - Format: Professional valuation report
   - Header: Company letterhead, date
   - Sections: Property details, land valuation, flat valuation, total summary
   - Tables: Property specifications with values
   
3. **Travel Itinerary** (2623 chars)
   - Format: Day-by-day schedule
   - Header: Applicant info, passport, hotel, duration
   - Content: Daily activities with dates, times, locations
   
4. **Travel History** (618 chars)
   - Format: Simple table
   - Columns: SL NO, Entry Date, Exit Date, Type of Visa, Visit Country
   - 10+ rows of previous travels

5. **Visiting Card** (13 chars - mostly image-based)
   - Business card format
   - Name, designation, company, contact details

---

## Adaptation Strategy: UK → Iceland

### Key Changes Needed:

1. **Embassy Address:**
   - UK: British High Commission, Dhaka
   - Iceland: Embassy of Iceland (via Danish Embassy, Dhaka or online)

2. **Country-Specific Details:**
   - UK references → Iceland references
   - Schengen visa requirements
   - Iceland tourism/business context

3. **Language & Tone:**
   - Same formal business English
   - Respectful, clear, concise

---

## Phase 3.2 Implementation Plan

### 8 Documents to Generate:

#### 1. **Cover Letter** (MOST IMPORTANT)
**Data Sources:**
- Extracted: Name, passport details, nationality
- Questionnaire: Travel purpose, dates, places to visit, profession
- Financial: Income details, funding source
- Home ties: Family, job, property

**Template Structure:**
```
[Date]

To,
The Visa Officer
Embassy of Iceland
[Address via Danish Embassy or online portal]

Subject: Application for Schengen Tourist/Business Visa to Iceland

Dear Sir/Madam,

Paragraph 1: Self-introduction (name, profession, nationality)
Paragraph 2: Purpose of visit and travel plans
Paragraph 3: Financial capability and trip funding
Paragraph 4: Home country ties and return commitment
Paragraph 5: Closing statement and gratitude

Sincerely,
[Signature Line]
[Name]
[Passport Number]
```

#### 2. **NID English Translation**
**Data Sources:**
- NID Bangla extracted data
- Personal information from questionnaire

**Template Structure:**
```
NATIONAL IDENTITY CARD
(English Translation)

Full Name: [Bangla → English]
Father's Name: [Bangla → English]
Mother's Name: [Bangla → English]
Date of Birth: [DD/MM/YYYY]
NID Number: [17-digit]
Permanent Address: [Bangla → English translation]

[Certification statement]
```

#### 3. **Visiting Card**
**Data Sources:**
- Business info (if businessman)
- Employment info (if job holder)
- Contact details from questionnaire

**Template Structure:**
```
[Professional design with company logo if available]

[Full Name]
[Designation/Position]
[Company Name]

Phone: [Number]
Email: [Email]
Address: [Business/Office Address]
```

#### 4. **Financial Statement**
**Data Sources:**
- Income tax data (3 years)
- Bank solvency data
- Monthly income/expenses from questionnaire

**Template Structure:**
```
FINANCIAL STATEMENT
of
[Full Name]

Income Summary (Last 3 Years):
Year | Annual Income | Tax Paid
2023 | [Amount] | [Amount]
2024 | [Amount] | [Amount]
2025 | [Amount] | [Amount]

Monthly Financial Details:
Income: [Amount]
Expenses: [Amount]
Savings: [Amount]

Bank Account Details:
Bank: [Name]
Balance: [Amount]

Trip Funding: [Self/Sponsor details]
```

#### 5. **Travel Itinerary**
**Data Sources:**
- Hotel booking data
- Air ticket data
- Places to visit from questionnaire
- Activities planned from questionnaire

**Template Structure:**
```
TRAVEL ITINERARY
For
Reykjavik, Iceland

Applicant: [Name]
Passport No.: [Number]
Hotel: [Name & Address]
Stay Duration: [Dates] ([X] Days)

Day 1 – [Date]
- Arrival in Reykjavik
- Check-in at [Hotel]
- [Activity]

Day 2 – [Date]
- [Morning activity]
- [Afternoon activity]
- [Evening activity]

[Continue for all days]

Final Day – [Date]
- Departure from Iceland
```

#### 6. **Travel History Document**
**Data Sources:**
- Visa history extracted data
- Previous travels from questionnaire

**Template Structure:**
```
PREVIOUS TRAVEL HISTORY
Of
[Full Name]

SL NO | Entry Date | Exit Date | Type of Visa | Visit Country
1.    | [DD/MM/YY] | [DD/MM/YY] | [Type]      | [Country]
2.    | [DD/MM/YY] | [DD/MM/YY] | [Type]      | [Country]
[...]

Total Countries Visited: [X]
Schengen Visits: [Details if any]
```

#### 7. **Home Tie Statement**
**Data Sources:**
- Family details from questionnaire
- Employment/business commitments
- Property ownership
- Reasons to return

**Template Structure:**
```
HOME COUNTRY TIES STATEMENT
of
[Full Name]

1. Family Ties:
   [Details about family in Bangladesh]

2. Employment/Business Commitments:
   [Job/business details, position, responsibilities]

3. Property Ownership:
   [Property details if any]

4. Financial Ties:
   [Bank accounts, investments]

5. Reasons to Return:
   [Compelling reasons to return to Bangladesh]

6. Conclusion:
   [Strong commitment statement]

[Signature]
[Date]
```

#### 8. **Asset Valuation Certificate**
**Data Sources:**
- Asset details from questionnaire
- Property ownership
- Vehicle ownership
- Investments

**Template Structure:**
```
PROPERTY & ASSET VALUATION REPORT

Owner: [Full Name]
Father's Name: [Name]
Address: [Full Address]
Date: [Date]

Property Valuation:
1. [Property Type]: [Details] - Value: BDT [Amount]
2. [Vehicle]: [Details] - Value: BDT [Amount]
3. [Investment]: [Details] - Value: BDT [Amount]

TOTAL ASSET VALUE: BDT [Sum]

[Professional certification statement]
[Valuer signature placeholder]
```

---

## Technical Implementation

### Technology Stack:
1. **ReportLab** - PDF generation library
2. **Google Gemini 2.5 Flash** - Content generation
3. **PIL (Pillow)** - Image handling
4. **PyPDF2** - PDF manipulation

### Database Schema (Add to existing):
```sql
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    application_id INT REFERENCES visa_applications(id),
    document_type VARCHAR(50),  -- cover_letter, nid_translation, etc.
    file_path VARCHAR(500),
    file_size INT,
    generation_status VARCHAR(20), -- pending, generating, completed, failed
    generation_progress INT DEFAULT 0, -- 0-100
    generated_at TIMESTAMP,
    error_message TEXT
);
```

### Service Architecture:

```python
# app/services/pdf_generator_service.py
class PDFGeneratorService:
    def __init__(self):
        self.gemini = genai.GenerativeModel('gemini-2.5-flash')
        
    async def generate_all_documents(self, application_id):
        # 1. Load all data (extracted + questionnaire)
        # 2. Generate each document with progress updates
        # 3. Save to database and file system
        # 4. Return download links
        
    async def generate_cover_letter(self, data):
        # Use Gemini to generate content
        # Format with ReportLab
        # Return PDF path
        
    # ... methods for each document type
```

### API Endpoints:

```python
# POST /api/generate/start/{application_id}
# - Starts background generation
# - Returns job_id

# GET /api/generate/status/{application_id}
# - Returns progress (0-100%)
# - Current document being generated
# - Completed documents count

# GET /api/generate/download/{application_id}/{document_type}
# - Download single document

# GET /api/generate/download-all/{application_id}
# - Download ZIP of all 16 documents (8 uploaded + 8 generated)
```

---

## Frontend UI Components

### 1. GenerationSection Component
```jsx
<Card>
  <CardHeader title="Generate Documents" />
  <CardContent>
    {/* Show after questionnaire complete */}
    <Button onClick={startGeneration}>
      Generate All Documents
    </Button>
    
    {/* During generation */}
    <LinearProgress value={progress} />
    <Typography>Generating: {currentDocument}</Typography>
    <Typography>{completedCount} of 8 documents</Typography>
    
    {/* After completion */}
    <Button onClick={downloadAll}>
      Download All Documents (ZIP)
    </Button>
    
    <List>
      {/* Individual download buttons for each doc */}
    </List>
  </CardContent>
</Card>
```

---

## Size Optimization (< 4MB per PDF)

1. **Text-only PDFs** - No images (very small)
2. **Compress images** if needed (for visiting card)
3. **Optimize fonts** - Use standard fonts
4. **No unnecessary graphics**
5. **Efficient ReportLab usage**

Expected sizes:
- Cover Letter: ~100KB
- NID Translation: ~50KB
- Visiting Card: ~200KB (if image)
- Financial Statement: ~150KB
- Travel Itinerary: ~100KB
- Travel History: ~50KB
- Home Tie Statement: ~100KB
- Asset Valuation: ~200KB

**Total: ~950KB for all 8 documents** ✅ Well under 4MB

---

## Gemini Prompts Strategy

### Intelligent Content Generation:

```python
def generate_cover_letter_content(data):
    prompt = f"""
Generate a professional cover letter for an Iceland Schengen visa application.

Applicant Information:
- Name: {data['name']}
- Profession: {data['profession']}
- Purpose: {data['travel_purpose']}
- Dates: {data['travel_dates']}
- Places: {data['places_to_visit']}

Financial Information:
- Income: {data['income']}
- Funding: {data['funding_source']}

Home Ties:
- Family: {data['family_ties']}
- Employment: {data['employment_commitment']}
- Property: {data['property_ownership']}

Generate a formal, professional cover letter with:
1. Proper salutation to Embassy of Iceland
2. Self-introduction paragraph
3. Purpose and travel plans
4. Financial capability
5. Strong home country ties
6. Professional closing

Write in formal business English, 4-5 paragraphs.
"""
    return gemini.generate_content(prompt)
```

---

## Next Steps

1. **Install dependencies:**
   ```bash
   pip install reportlab Pillow PyPDF2
   ```

2. **Create PDF generation service** (600+ lines)

3. **Create Gemini content generators** for each document

4. **Add database migration** for generated_documents table

5. **Create API endpoints** for generation

6. **Build frontend UI** with progress tracking

7. **Test with real data** from Phase 3.1

8. **Implement ZIP download** for all documents

---

## Success Criteria

✅ All 8 documents generated successfully
✅ Content is intelligent and contextual
✅ Format matches professional standards
✅ Each PDF < 4MB
✅ Progress UI shows real-time updates
✅ Download all button works
✅ Individual downloads work
✅ Total generation time < 3 minutes
✅ Documents ready for submission

**Ready to implement Phase 3.2!** 🚀📄
