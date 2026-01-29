# Testing Phase 3.1 - AI Document Analysis & Questionnaire

## Quick Start Testing

### 1. Verify Backend & Frontend Running

**Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

**Frontend:**
```bash
cd frontend
npm run dev
# Should see: "Local: http://localhost:3000"
```

### 2. Run Quick Test
```bash
python3 test_phase_3_1.py
```

Expected output:
```
✅ Backend is healthy
✅ Analysis start endpoint exists
✅ Analysis status endpoint exists
✅ Questionnaire generate endpoint exists
✅ Questionnaire progress endpoint exists
✅ Found 3 analysis endpoints
✅ Found 4 questionnaire endpoints
```

### 3. Manual UI Testing

#### Step 1: Create Application
1. Open: http://localhost:3000
2. Click "New Application"
3. Fill form:
   - Country: Iceland
   - Visa Type: Tourist
   - Name: Test User
   - Email: test@example.com
   - Phone: +880123456789
4. Submit

#### Step 2: Upload Documents
Upload 8 documents (can be any PDFs with text):
1. Passport
2. NID (Bangla)
3. Income Tax Certificate
4. TIN Certificate
5. Bank Solvency Certificate
6. Hotel Booking Confirmation
7. Air Ticket
8. Visa History Document

**Note:** Documents need to have extractable text for AI to work. You can:
- Use real documents (best)
- Use sample PDFs with text
- Use screenshots of sample documents
- Create simple text documents and convert to PDF

#### Step 3: Analyze Documents
1. Scroll down to "Document Analysis" card
2. Click "Analyze Documents" button
3. Watch progress:
   - Progress bar animates
   - Shows "Processing: [document name]"
   - Shows "X of 8 documents analyzed"
   - Updates every 2 seconds
4. Wait 1-2 minutes for completion
5. Should show: "Analysis Complete! XX% information extracted"

**Expected AI Behavior:**
- Passport → Extracts: name, passport#, DOB, nationality, gender
- NID → Extracts: Bangla text (preserved), NID#, address
- Income Tax → Extracts: 3 years tax data, income amounts
- TIN → Extracts: TIN number, circle, taxpayer info
- Bank Solvency → Extracts: account info, balance, bank details
- Hotel Booking → Extracts: hotel name, dates, location, booking ref
- Air Ticket → Extracts: flight details, dates, passenger name, PNR
- Visa History → Extracts: countries visited, visa types, dates

#### Step 4: Fill Questionnaire
1. After analysis, "Next Step" card appears
2. Click "Fill Questionnaire" button
3. Wizard opens with 7 categories

**Test Each Category:**

**Personal Information:**
- Only asks if not in passport/NID
- Answer: marital status, dependents, phone, email

**Profession Determination:**
- "Are you a job holder or businessman?"
- Select one to test different question flows

**Employment (Job Holders):**
- Job title, company name, address
- Employment duration, salary
- Supervisor, HR contact

**Business (Businessmen):**
- Business name, type, start date
- Registration, revenue
- Employees, nature of work

**Travel Purpose:**
- Purpose (Tourism/Business/Family)
- Places to visit
- Activities planned
- Previous Schengen visits
- Contacts in Iceland

**Financial:**
- Monthly income/expenses
- Trip funding source
- Sponsor details

**Assets:**
- Property ownership (Yes/No)
- Vehicle ownership
- Investments
- Total value

**Home Ties (CRITICAL):**
- Family in Bangladesh
- Employment commitment
- Property ties
- **Reasons to return** (important for visa!)

#### Step 5: Test Features

**Save Progress:**
- Answer some questions
- Click "Save Progress"
- Close wizard
- Reopen - answers preserved ✅

**Navigation:**
- Click "Next" after completing category
- Click "Back" to return
- Progress bar updates ✅

**Validation:**
- Try "Next" without required fields → Disabled ✅
- Fill required fields → Enabled ✅

**Completion:**
- Answer all required questions
- Click "Complete" on last step
- Success message appears ✅

### 4. Verify Results

#### Check Database:
```sql
-- Analysis session
SELECT * FROM analysis_sessions WHERE application_id = YOUR_APP_ID;
-- Should show: status='completed', completeness_score>0

-- Extracted data
SELECT document_type, confidence_score FROM extracted_data WHERE application_id = YOUR_APP_ID;
-- Should have 8 rows

-- Questionnaire responses
SELECT category, COUNT(*) FROM questionnaire_responses WHERE application_id = YOUR_APP_ID GROUP BY category;
-- Should show counts per category
```

#### Check APIs:
```bash
# Get analysis status
curl http://localhost:8000/api/analysis/status/YOUR_APP_ID

# Get analysis results
curl http://localhost:8000/api/analysis/results/YOUR_APP_ID

# Get questionnaire progress
curl http://localhost:8000/api/questionnaire/progress/YOUR_APP_ID

# Get questionnaire responses
curl http://localhost:8000/api/questionnaire/responses/YOUR_APP_ID
```

## Success Criteria

Phase 3.1 is successful if:

1. **Analysis Works:**
   - ✅ All 8 documents analyzed
   - ✅ Progress shown in real-time
   - ✅ Completeness score calculated
   - ✅ Data extracted and stored
   - ✅ Confidence scores reasonable (>60%)

2. **Questionnaire Works:**
   - ✅ Questions generated based on analysis
   - ✅ Only asks what's missing
   - ✅ Different questions for job holder vs businessman
   - ✅ All 7 categories present
   - ✅ Save/resume functionality
   - ✅ Validation prevents incomplete submission

3. **Data Complete:**
   - ✅ All information for cover letter captured
   - ✅ Financial details for financial statement
   - ✅ Travel details for itinerary
   - ✅ Asset details for valuation cert
   - ✅ Home ties for home tie statement

## Common Issues

### Analysis Fails
**Problem:** Status shows "failed"
**Solution:**
- Check Gemini API key in `.env`
- Check documents have extractable text
- Check backend logs: `tail -f backend/backend.log`

### No Questions Generated
**Problem:** Questionnaire is empty
**Solution:**
- Ensure analysis completed first
- Check extracted_data table has records
- Try re-generating questionnaire

### Answers Not Saving
**Problem:** Answers disappear
**Solution:**
- Click "Save Progress" before closing
- Check network tab for failed POST
- Verify backend endpoint accessible

## Files to Review

- **Test Guide:** `PHASE_3_1_TEST_GUIDE.md` (detailed 400+ lines)
- **Completion Summary:** `PHASE_3_1_COMPLETE.md`
- **Test Script:** `test_phase_3_1.py`
- **Backend Code:** `app/services/ai_analysis_service.py`
- **Backend Code:** `app/services/questionnaire_generator.py`
- **Frontend Code:** `src/components/AnalysisSection.jsx`
- **Frontend Code:** `src/components/QuestionnaireWizard.jsx`

## Next Steps

After successful testing:

1. **Phase 3.2:** AI Document Generation
   - Generate 8 documents using collected data
   - Cover Letter (MOST IMPORTANT)
   - NID Translation, Visiting Card, Financial Statement
   - Travel Itinerary, Travel History
   - Home Tie Statement, Asset Valuation

2. **Phase 4:** Review and Submission
   - Review all generated documents
   - Allow edits if needed
   - Final submission

## Questions?

Check:
- Swagger docs: http://localhost:8000/docs
- Backend logs: `backend/backend.log`
- Browser console for frontend errors
- Database queries for data verification

**Happy Testing! 🚀**
