# Phase 2: Document Upload & Management System

## 🎯 Phase 2 Objectives

### Primary Goals
1. Allow users to upload all 9 required documents for Iceland tourist visa
2. Display uploaded documents with preview capability
3. Track which documents are uploaded vs. missing
4. Validate uploaded files (type, size, format)
5. Extract text from uploaded PDFs automatically
6. Provide visual progress indicator
7. Enable document deletion/replacement

### Success Criteria
- ✅ All 9 document types can be uploaded
- ✅ PDF files are validated (max 10MB)
- ✅ Text extraction works for all PDFs
- ✅ Progress bar shows completion percentage
- ✅ Users can see preview of uploaded documents
- ✅ Uploaded documents are stored securely
- ✅ Error handling for all edge cases

---

## 📊 Phase 2 Scope

### Documents Users Must Upload (9 Required):
1. **Passport Copy** (passport_copy)
2. **NID Bangla** (nid_bangla)
3. **Visa History** (visa_history)
4. **TIN Certificate** (tin_certificate)
5. **Income Tax 3 Years** (income_tax_3years)
6. **Asset Valuation** (asset_valuation)
7. **Hotel Booking** (hotel_booking)
8. **Air Ticket** (air_ticket)
9. **Bank Solvency** (bank_solvency)

### File Requirements
- **Accepted formats**: PDF, JPG, JPEG, PNG
- **Max file size**: 10MB per file
- **Storage**: Backend `/uploads` folder
- **Naming**: `{application_number}_{document_type}_{uuid}.{ext}`

---

## 🏗️ Technical Architecture

### Backend Components to Build/Update

#### 1. Enhanced Document Upload API
**File**: `backend/app/api/endpoints/documents.py`

**Existing**: Basic upload endpoint
**Need to Add**:
- Better error messages
- File validation
- Thumbnail generation for images
- Progress tracking in database

#### 2. Document Processing Service
**File**: `backend/app/services/pdf_service.py`

**Existing**: Basic PDF text extraction
**Need to Add**:
- Image to text (OCR) using pytesseract
- Better error handling
- PDF page count
- File size optimization

#### 3. File Storage Management
**New File**: `backend/app/services/storage_service.py`

**Functions**:
- Save uploaded file
- Generate unique filename
- Check storage space
- Delete file
- Get file path

### Frontend Components to Build

#### 1. Document Upload Component
**File**: `frontend/src/components/DocumentUpload/DocumentUploader.jsx`

**Features**:
- Drag & drop zone
- File type validation
- Upload progress bar
- Multiple file selection
- Preview before upload

#### 2. Document List Component
**File**: `frontend/src/components/DocumentUpload/DocumentList.jsx`

**Features**:
- Show all required documents
- Mark uploaded vs. missing
- Preview uploaded docs
- Delete/replace option
- Download option

#### 3. Document Card Component
**File**: `frontend/src/components/DocumentUpload/DocumentCard.jsx`

**Features**:
- Document type label
- Upload status badge
- File name & size
- Action buttons (view, delete)
- Upload button if missing

#### 4. Progress Tracker Component
**File**: `frontend/src/components/DocumentUpload/ProgressTracker.jsx`

**Features**:
- Circular progress indicator
- X of 9 documents uploaded
- Percentage completion
- Next steps guidance

---

## 📝 Implementation Steps (Precise Order)

### **Step 1: Backend - Storage Service** (15 min)
- Create `storage_service.py`
- Implement file save/delete functions
- Add file validation utilities
- Test with sample files

### **Step 2: Backend - Enhanced PDF Service** (20 min)
- Add OCR capability for images
- Improve error handling
- Add file metadata extraction
- Test with various PDFs

### **Step 3: Backend - Update Document API** (20 min)
- Enhance upload endpoint
- Add batch upload support
- Improve error responses
- Add document status endpoint

### **Step 4: Frontend - Document Card Component** (15 min)
- Create reusable card component
- Add status badges
- Implement action buttons
- Style with Material-UI

### **Step 5: Frontend - Document Uploader Component** (30 min)
- Implement drag & drop
- Add file validation
- Create upload progress UI
- Handle multiple files

### **Step 6: Frontend - Document List Component** (20 min)
- Display all required docs
- Show upload status
- Add preview modal
- Implement delete functionality

### **Step 7: Frontend - Progress Tracker** (15 min)
- Create circular progress
- Calculate completion %
- Add guidance text
- Integrate with state

### **Step 8: Frontend - Update Application Details Page** (20 min)
- Integrate all upload components
- Add state management
- Connect to API
- Add error handling

### **Step 9: Testing & Bug Fixes** (30 min)
- Test all document types
- Test edge cases
- Fix any bugs
- Optimize performance

### **Step 10: Documentation & Polish** (15 min)
- Update README
- Add comments
- Create user guide
- Final testing

**Total Estimated Time: ~3 hours**

---

## 🎨 UI/UX Design Specifications

### Application Details Page Layout

```
┌─────────────────────────────────────────────────────────┐
│  Application Details Header                              │
│  [Application Number] [Status Badge]                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Progress Tracker (Top Right)                           │
│  ⭕ 5/9 Documents Uploaded (55%)                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Upload Zone (Drag & Drop)                              │
│  📁 Drag & drop files here or click to browse          │
│  Supported: PDF, JPG, PNG (Max 10MB)                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Required Documents (Grid Layout)                       │
│                                                          │
│  [Card: Passport Copy]        [Card: NID Bangla]       │
│  ✅ Uploaded                   ⏳ Upload Required       │
│  passport.pdf (2.3 MB)                                  │
│  [View] [Delete]              [Upload]                  │
│                                                          │
│  [Card: Visa History]         [Card: TIN Certificate]  │
│  ✅ Uploaded                   ✅ Uploaded              │
│  ...                          ...                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Action Buttons (Bottom)                                │
│  [Process Documents] [Continue to Next Step]           │
└─────────────────────────────────────────────────────────┘
```

### Document Card States

**1. Not Uploaded (Empty State)**
```
┌────────────────────────┐
│ 📄 Passport Copy       │
│ ⏳ Upload Required     │
│                        │
│   [Upload Document]    │
└────────────────────────┘
```

**2. Uploading (Progress State)**
```
┌────────────────────────┐
│ 📄 Passport Copy       │
│ ⏳ Uploading...        │
│ ▓▓▓▓▓▓░░░░ 60%        │
│                        │
└────────────────────────┘
```

**3. Uploaded (Success State)**
```
┌────────────────────────┐
│ 📄 Passport Copy       │
│ ✅ Uploaded           │
│ passport.pdf           │
│ 2.3 MB • Just now      │
│ [View] [Delete]        │
└────────────────────────┘
```

**4. Error State**
```
┌────────────────────────┐
│ 📄 Passport Copy       │
│ ❌ Upload Failed       │
│ File too large         │
│                        │
│   [Try Again]          │
└────────────────────────┘
```

---

## 🔧 API Endpoints Required

### Existing (Already Built)
✅ `POST /api/documents/upload/{application_id}`
✅ `GET /api/documents/application/{application_id}`
✅ `DELETE /api/documents/{document_id}`
✅ `POST /api/documents/process/{application_id}`

### New/Enhanced
🔨 `GET /api/applications/{application_id}/progress` - Get upload progress
🔨 `POST /api/documents/upload-batch/{application_id}` - Upload multiple files
🔨 `GET /api/documents/{document_id}/preview` - Get document preview/thumbnail

---

## 📦 New Dependencies Needed

### Backend
```python
# Already in requirements.txt:
# - PyPDF2 (PDF text extraction)
# - reportlab (PDF generation)
# - Pillow (Image processing)

# Need to ensure these are working:
# - pytesseract (OCR for images)
# - pdf2image (PDF to image conversion)

# System dependencies:
# sudo apt-get install tesseract-ocr
# sudo apt-get install poppler-utils
```

### Frontend
```javascript
// Already installed:
// - react-dropzone (drag & drop)
// - @mui/material (UI components)
// - axios (API calls)

// May need to add:
// - react-pdf (PDF preview) - Optional for Phase 2
// - react-file-viewer (File preview) - Optional
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] File validation (size, type)
- [ ] PDF text extraction
- [ ] File storage/deletion
- [ ] API response formatting

### Integration Tests
- [ ] Complete upload flow
- [ ] Multiple file upload
- [ ] Document deletion and re-upload
- [ ] Progress calculation

### User Acceptance Tests
- [ ] Upload all 9 document types
- [ ] Upload with drag & drop
- [ ] Upload with file picker
- [ ] View uploaded documents
- [ ] Delete and replace documents
- [ ] See accurate progress
- [ ] Handle errors gracefully

### Edge Cases
- [ ] File too large (>10MB)
- [ ] Wrong file type
- [ ] Corrupted PDF
- [ ] Network failure during upload
- [ ] Duplicate uploads
- [ ] Special characters in filename
- [ ] Very large PDFs (100+ pages)

---

## 🚨 Error Handling Strategy

### Backend Errors
1. **File too large**: Return 400 with clear message
2. **Invalid file type**: Return 400 with allowed types
3. **PDF extraction failed**: Log error, continue with empty text
4. **Storage full**: Return 500 with storage issue message
5. **Database error**: Rollback transaction, return 500

### Frontend Errors
1. **Upload failed**: Show toast notification, allow retry
2. **Network error**: Show connection message, queue retry
3. **Validation error**: Show inline error on card
4. **Server error**: Show generic error, log details

---

## 📈 Progress Tracking

### Database Updates Needed
- Add `upload_progress` field to `visa_applications` table
- Track individual document upload timestamps
- Store upload attempt count

### Progress Calculation
```
Progress % = (Uploaded Documents / Total Required) × 100
Status = "Complete" when all 9 docs uploaded
```

---

## 🎯 Phase 2 Deliverables

### Code Files
1. ✅ `backend/app/services/storage_service.py`
2. ✅ Enhanced `backend/app/services/pdf_service.py`
3. ✅ Enhanced `backend/app/api/endpoints/documents.py`
4. ✅ `frontend/src/components/DocumentUpload/DocumentUploader.jsx`
5. ✅ `frontend/src/components/DocumentUpload/DocumentList.jsx`
6. ✅ `frontend/src/components/DocumentUpload/DocumentCard.jsx`
7. ✅ `frontend/src/components/DocumentUpload/ProgressTracker.jsx`
8. ✅ Enhanced `frontend/src/pages/ApplicationDetailsPage.jsx`

### Documentation
1. ✅ Phase 2 implementation notes
2. ✅ API documentation updates
3. ✅ User guide for document upload

### Testing
1. ✅ All tests passing
2. ✅ Edge cases handled
3. ✅ Performance optimized

---

## 🎬 Phase 2 Completion Criteria

Before moving to Phase 3, we must have:

1. ✅ All 9 document types can be uploaded
2. ✅ Upload UI is intuitive and responsive
3. ✅ Progress tracking works accurately
4. ✅ File validation prevents bad uploads
5. ✅ PDF text extraction works reliably
6. ✅ Documents can be previewed
7. ✅ Documents can be deleted/replaced
8. ✅ Error messages are clear and helpful
9. ✅ No critical bugs
10. ✅ Code is documented and clean

---

## 🔄 Integration with Phase 3

Phase 2 prepares for Phase 3 (AI Analysis) by:
- Storing extracted text for each document
- Tracking document processing status
- Providing clean data structure for AI analysis
- Ensuring all required documents are present

Once Phase 2 is complete, Phase 3 will use the uploaded documents to:
- Extract structured data with Gemini AI
- Identify missing information
- Cross-reference between documents
- Prepare for document generation

---

## ⚡ Quick Start for Implementation

**Ready to start? Here's the order:**

1. **Backend First** (60 min)
   - Storage service
   - Enhanced PDF service
   - API improvements

2. **Frontend Components** (80 min)
   - Document cards
   - Upload UI
   - Progress tracker

3. **Integration** (40 min)
   - Connect frontend to backend
   - Test complete flow
   - Fix bugs

4. **Polish** (20 min)
   - Improve styling
   - Add loading states
   - Final testing

**Total: ~3 hours to complete Phase 2**

---

## 💡 Pro Tips

1. **Test incrementally**: Test each component as you build it
2. **Use sample PDFs**: Create test PDFs for each document type
3. **Handle loading states**: Always show user what's happening
4. **Mobile responsive**: Test on different screen sizes
5. **Console logging**: Use for debugging, remove before commit
6. **Error boundaries**: Wrap components in error boundaries
7. **Optimistic UI**: Show upload success before server confirms

---

## ✅ Ready to Start Implementation?

Review this plan and confirm:
- [ ] Plan is clear and detailed
- [ ] Time estimates seem reasonable
- [ ] Technical approach makes sense
- [ ] UI/UX design is approved
- [ ] Ready to proceed step-by-step

**Once approved, we'll start with Step 1: Backend Storage Service!** 🚀
