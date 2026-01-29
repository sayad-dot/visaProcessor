# Phase 3.1 Testing Guide
## Document Analysis & Intelligent Questionnaire System

### 🎯 What We Built

Phase 3.1 is **THE MOST IMPORTANT** feature of the entire project. It consists of:

1. **AI Document Analysis** - Extracts structured information from 8 uploaded documents
2. **Intelligent Questionnaire** - Generates contextual questions based on what's missing
3. **Profession Detection** - Asks different questions for job holders vs businessmen
4. **Complete Data Collection** - Gathers ALL information needed for the cover letter

---

## ✅ Phase 3.1 Complete Implementation

### Backend Components Created:

#### 1. Database Models (`app/models.py`)
- **ExtractedData**: Stores AI-extracted structured data (JSON format)
- **QuestionnaireResponse**: Stores user answers with category grouping
- **AnalysisSession**: Tracks analysis progress and completeness score

#### 2. AI Analysis Service (`app/services/ai_analysis_service.py`)
**8 Document-Specific Analyzers:**
- `analyze_passport()` - Extracts: name, passport#, DOB, nationality, gender, dates
- `analyze_nid_bangla()` - Extracts: Bangla text (preserves script), NID#, DOB, address
- `analyze_income_tax()` - Extracts: 3 years tax data, income, taxpayer info
- `analyze_tin_certificate()` - Extracts: TIN#, circle, issue date
- `analyze_bank_solvency()` - Extracts: account info, balance, bank details
- `analyze_hotel_booking()` - Extracts: hotel, dates, location, booking ref
- `analyze_air_ticket()` - Extracts: flights, dates, passenger, PNR
- `analyze_visa_history()` - Extracts: countries visited, dates, visa types

**Features:**
- Uses Google Gemini 1.5 Flash model
- Structured JSON prompts for accuracy
- Confidence scoring (0-100%)
- Markdown cleanup and error handling

#### 3. Questionnaire Generator (`app/services/questionnaire_generator.py`)
**60+ Contextual Questions Across 7 Categories:**
- **Personal Info**: Name, DOB, address, marital status, dependents
- **Profession Determination**: Detects job holder vs businessman
- **Employment** (Job Holders): Job title, company, salary, duration, supervisor
- **Business** (Businessmen): Business name, type, revenue, employees, registration
- **Travel Purpose**: Purpose, places, activities, previous Schengen visits
- **Financial**: Income, expenses, funding source, sponsor
- **Assets**: Property, vehicles, investments (feeds asset valuation cert)
- **Home Ties**: Family, employment commitments, reasons to return (CRITICAL for visa approval)

**Intelligence:**
- Only asks questions if data missing from analysis
- Different questions based on profession
- Contextual help text for each question

#### 4. API Endpoints

**Analysis Endpoints (`app/api/endpoints/analysis.py`):**
- `POST /api/analysis/start/{application_id}` - Start background analysis
- `GET /api/analysis/status/{application_id}` - Get real-time progress
- `GET /api/analysis/results/{application_id}` - Get extracted data

**Questionnaire Endpoints (`app/api/endpoints/questionnaire.py`):**
- `GET /api/questionnaire/generate/{application_id}` - Generate questions
- `POST /api/questionnaire/response/{application_id}` - Save answers (batch)
- `GET /api/questionnaire/responses/{application_id}` - Get all answers
- `GET /api/questionnaire/progress/{application_id}` - Get completion %

### Frontend Components Created:

#### 1. AnalysisSection Component (`components/AnalysisSection.jsx`)
**Features:**
- Start analysis button
- Real-time progress tracking with progress bar
- Status display (analyzing, completed, failed)
- Completeness score display
- Extracted data summary viewer
- Re-analyze capability
- Auto-polling every 2 seconds during analysis

#### 2. QuestionnaireWizard Component (`components/QuestionnaireWizard.jsx`)
**Features:**
- Multi-step dialog with category stepper
- 7 question types supported:
  * Text input
  * Textarea (multiline)
  * Number input
  * Date picker (MUI X Date Pickers)
  * Select dropdown
  * Boolean (Yes/No radio)
  * Multiselect
- Save progress functionality
- Real-time validation
- Progress percentage display
- Navigation between categories
- Required field enforcement

#### 3. ApplicationDetailsPage Integration
**Updates:**
- AnalysisSection shown after documents uploaded
- Questionnaire wizard opens after analysis complete
- Automatic flow: Upload → Analyze → Questionnaire → Generate
- Toast notifications for user feedback

---

## 🧪 Testing Instructions

### Prerequisites:
1. ✅ Backend running on `http://localhost:8000`
2. ✅ Frontend running on `http://localhost:3000`
3. ✅ PostgreSQL database with Phase 3.1 tables
4. ✅ Google Gemini API key configured in `.env`

### Test Flow:

#### Step 1: Create Test Application
1. Open frontend: `http://localhost:3000`
2. Click "New Application"
3. Fill form:
   - Country: Iceland
   - Visa Type: Tourist
   - Name: Your Test Name
   - Email: test@example.com
   - Phone: +880123456789
4. Submit application

#### Step 2: Upload Test Documents
You need to upload **real documents** for AI analysis to work. The AI will extract text and analyze:

**Required Documents to Upload (8):**
1. **Passport** - Should contain name, passport number, DOB, nationality
2. **NID (Bangla)** - Should contain Bangla text, NID number
3. **Income Tax Certificate** - Should show 3 years tax data
4. **TIN Certificate** - Should show TIN number
5. **Bank Solvency** - Should show account and balance info
6. **Hotel Booking** - Should show hotel, dates, location
7. **Air Ticket** - Should show flight details
8. **Visa History** - Should show previous travel history

**Note:** If you don't have real documents, you can:
- Create sample PDFs with text content
- Use screenshots of sample documents
- Use any documents with visible text (OCR will extract)

#### Step 3: Test AI Analysis

1. After uploading documents, find the **"Document Analysis"** card
2. Click **"Analyze Documents"** button
3. Watch the progress:
   - Progress bar shows percentage
   - Current document being analyzed
   - Documents analyzed count (X of 8)
   - Status updates every 2 seconds
4. Wait for completion (1-2 minutes)
5. Check results:
   - Should show "Analysis Complete! XX% information extracted"
   - Completeness score indicates how much data was extracted
   - Click expand icon to see extracted data summary

**Expected AI Behavior:**
- Passport: Should extract full name, passport number, DOB, nationality
- NID: Should preserve Bangla text (not translate), extract NID number
- Income Tax: Should extract 3 years data with income amounts
- Bank: Should extract balance and account info
- Hotel/Ticket: Should extract dates, locations, booking references

#### Step 4: Test Intelligent Questionnaire

1. After analysis completes, "Next Step: Complete Questionnaire" card appears
2. Click **"Fill Questionnaire"** button
3. Wizard dialog opens with stepper navigation

**Test Each Category:**

**Personal Information:**
- Should only ask for data NOT in passport/NID
- Example: If passport has name/DOB, should skip those questions
- Test: Answer marital status, dependents, phone, email

**Profession Determination:**
- Should ask "Are you a job holder or businessman?"
- Test both paths:
  * Select "Job Holder" → Next category should be Employment
  * Select "Businessman" → Next category should be Business

**Employment Questions (Job Holders):**
- Job title, company name, address
- Employment duration, monthly salary
- Supervisor name, HR contact
- Test: Fill all required fields (marked with *)

**Business Questions (Businessmen):**
- Business name, type, start date
- Registration number, address
- Monthly revenue, number of employees
- Nature of work description
- Test: Different questions than employment

**Travel Purpose:**
- Purpose of visit (select: Tourism, Business, Family Visit, etc.)
- Places to visit in Iceland
- Activities planned
- Previous Schengen visits (Yes/No)
- Contacts in Iceland
- Test: Textarea fields should expand for long text

**Financial:**
- Monthly income (if not in tax docs)
- Monthly expenses
- Trip funding source (select: Self, Sponsor, etc.)
- Sponsor details if applicable
- Test: Number fields should only accept numbers

**Assets:**
- Property ownership (Yes/No)
- Property details if yes
- Vehicle ownership
- Investment details
- Total asset value
- Test: This feeds into AI-generated asset valuation certificate

**Home Ties:**
- Family in Bangladesh (Yes/No)
- Family details
- Employment commitment
- Property ties
- **Reasons to return** (IMPORTANT: Critical for visa approval)
- Test: Convince visa officer you'll return

#### Step 5: Test Questionnaire Features

**Save Progress:**
1. Answer some questions in a category
2. Click "Save Progress" button
3. Should show success message
4. Close wizard
5. Reopen wizard - answers should be preserved

**Navigation:**
1. Click "Next" after completing required fields in category
2. Should move to next category
3. Click "Back" to return
4. Progress bar at top should update

**Validation:**
1. Try clicking "Next" without answering required fields
2. Button should be disabled
3. Fill required fields (marked with *)
4. Button should enable

**Completion:**
1. Answer all required questions across all categories
2. Last category should show "Complete" button (green)
3. Click "Complete"
4. Should close wizard and show success toast
5. Check backend: All answers should be saved in database

---

## 🔍 Verification Checks

### Backend Verification:

```bash
# Check analysis session created
SELECT * FROM analysis_sessions WHERE application_id = YOUR_APP_ID;
# Should show: status='completed', completeness_score=X, documents_analyzed=8

# Check extracted data
SELECT document_type, confidence_score FROM extracted_data WHERE application_id = YOUR_APP_ID;
# Should have 8 rows, one per document

# Check questionnaire responses
SELECT category, COUNT(*) FROM questionnaire_responses WHERE application_id = YOUR_APP_ID GROUP BY category;
# Should show count per category

# Check completeness
SELECT category, COUNT(*) as total, SUM(CASE WHEN answer IS NOT NULL THEN 1 ELSE 0 END) as answered 
FROM questionnaire_responses WHERE application_id = YOUR_APP_ID GROUP BY category;
```

### API Testing:

```bash
# Test analysis start (replace APP_ID)
curl -X POST http://localhost:8000/api/analysis/start/1

# Test analysis status
curl http://localhost:8000/api/analysis/status/1

# Test analysis results
curl http://localhost:8000/api/analysis/results/1

# Test questionnaire generate
curl http://localhost:8000/api/questionnaire/generate/1

# Test questionnaire progress
curl http://localhost:8000/api/questionnaire/progress/1
```

---

## 🎯 Expected Outcomes

### Successful Phase 3.1 Completion:

1. **Analysis Complete:**
   - ✅ All 8 documents analyzed
   - ✅ Completeness score > 60%
   - ✅ Extracted data stored in database
   - ✅ Each document has confidence score

2. **Questionnaire Complete:**
   - ✅ All required questions answered
   - ✅ Different questions for job holder vs businessman
   - ✅ Contextual questions based on extracted data
   - ✅ Progress shows 100% completion
   - ✅ All answers saved in database

3. **Data Ready for Phase 3.2:**
   - ✅ Comprehensive data collected
   - ✅ All information needed for cover letter
   - ✅ Financial details for financial statement
   - ✅ Travel details for itinerary
   - ✅ Asset details for valuation certificate
   - ✅ Home ties for home tie statement

---

## 🐛 Common Issues & Solutions

### Issue 1: Analysis Fails
**Symptoms:** Status shows "failed" or error message
**Solutions:**
- Check if Gemini API key is valid in `.env`
- Check if documents have extractable text (not just images)
- Check backend logs: `tail -f backend.log`
- Verify documents were uploaded with extracted_text

### Issue 2: No Questions Generated
**Symptoms:** Questionnaire is empty
**Solutions:**
- Verify analysis completed successfully first
- Check if extracted_data table has records
- Check backend logs for errors
- Try re-generating questionnaire

### Issue 3: Date Picker Not Working
**Symptoms:** Date fields don't open calendar
**Solutions:**
- Verify MUI X Date Pickers installed: `npm list @mui/x-date-pickers`
- Check browser console for errors
- Ensure date-fns is installed

### Issue 4: Answers Not Saving
**Symptoms:** Answers disappear after closing wizard
**Solutions:**
- Click "Save Progress" before closing
- Check network tab for failed POST requests
- Verify backend endpoint is accessible
- Check database permissions

---

## 📊 Success Metrics

### Phase 3.1 is successful if:

1. **AI Extraction Quality:**
   - Passport: ≥ 90% confidence (name, passport#, DOB correct)
   - Financial docs: ≥ 70% confidence (numbers extracted)
   - Travel docs: ≥ 80% confidence (dates, locations correct)

2. **Questionnaire Intelligence:**
   - ✅ Only asks what's missing from analysis
   - ✅ Profession detection works (job holder vs businessman)
   - ✅ All 7 categories properly grouped
   - ✅ Required fields enforced

3. **User Experience:**
   - ✅ Progress visible in real-time
   - ✅ Save/resume functionality works
   - ✅ Validation prevents incomplete submissions
   - ✅ Clear instructions and help text

4. **Data Completeness:**
   - ✅ Completeness score ≥ 70%
   - ✅ All critical fields captured (name, DOB, income, travel dates)
   - ✅ Home ties information complete (critical for visa approval)
   - ✅ Ready for Phase 3.2 document generation

---

## 🚀 Next Steps After Testing

Once Phase 3.1 testing is complete:

1. **Verify Data Quality:**
   - Check extracted_data table for accuracy
   - Verify questionnaire_responses are complete
   - Calculate overall completeness score

2. **Ready for Phase 3.2:**
   - AI Document Generation Service
   - Generate 8 documents using extracted + questionnaire data:
     * Cover Letter (MOST IMPORTANT - needs ALL data)
     * NID English Translation
     * Visiting Card
     * Financial Statement
     * Travel Itinerary
     * Travel History
     * Home Tie Statement
     * Asset Valuation Certificate

3. **Phase 3.2 Will Use:**
   - All extracted_data from Phase 3.1 analysis
   - All questionnaire_responses from Phase 3.1
   - Gemini AI for intelligent document generation
   - Professional templates for each document type

---

## 📝 Testing Checklist

Use this checklist to verify Phase 3.1:

- [ ] Backend running without errors
- [ ] Frontend running without errors
- [ ] Application created successfully
- [ ] 8 documents uploaded with text
- [ ] Analysis started successfully
- [ ] Progress updates showing in real-time
- [ ] Analysis completed with completeness score
- [ ] Extracted data visible in results
- [ ] Questionnaire wizard opens
- [ ] Personal questions appear (if data missing)
- [ ] Profession determination works
- [ ] Employment questions for job holders
- [ ] Business questions for businessmen
- [ ] Travel purpose questions complete
- [ ] Financial questions complete
- [ ] Assets questions complete
- [ ] Home ties questions complete
- [ ] Save progress functionality works
- [ ] Navigation between categories works
- [ ] Validation prevents incomplete submission
- [ ] Completion saves all answers
- [ ] Database has all extracted_data records
- [ ] Database has all questionnaire_responses
- [ ] Ready to proceed to Phase 3.2

---

## 💡 Tips for Best Results

1. **Use Real Documents:** AI works best with actual documents containing proper text
2. **Clear Text:** Ensure documents are readable (not blurry scans)
3. **Complete Information:** Upload all 8 documents for best completeness score
4. **Accurate Answers:** Questionnaire answers will be used in generated documents
5. **Home Ties:** Spend time on home ties questions - critical for visa approval
6. **Save Often:** Use "Save Progress" button while filling questionnaire

---

## 🎉 Success!

If you've completed all tests successfully:
- ✅ Phase 3.1 is COMPLETE
- ✅ AI can properly analyze documents
- ✅ AI can generate contextual questions
- ✅ System ready for Phase 3.2 (Document Generation)

**Great work! The most important feature is now functional! 🚀**
