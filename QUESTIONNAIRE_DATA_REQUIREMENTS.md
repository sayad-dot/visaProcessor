# 📋 QUESTIONNAIRE DATA REQUIREMENTS FOR ALL 13 GENERATED DOCUMENTS

**Analysis Date:** February 4, 2026  
**Purpose:** Define what data each generated document needs  
**Status:** ✅ RESEARCH COMPLETE - Awaiting User Review

---

## 📊 EXECUTIVE SUMMARY

This document analyzes all **13 generated documents** and categorizes required data into:
- **🔴 REQUIRED** - Must have for document to be valid
- **🟡 SUGGESTED** - Makes document much stronger (highly recommended)
- **🟢 OPTIONAL** - Nice to have, improves quality

---

## 🗂️ DATA CATEGORIES

Based on your structure, I've organized data into logical groups:

1. **PERSONAL INFO** → Used in: Cover Letter, NID English, Visiting Card, Home Tie, All documents
2. **EMPLOYMENT/BUSINESS INFO** → Used in: Cover Letter, Visiting Card, Home Tie, Trade License
3. **TRAVEL INFO** → Used in: Cover Letter, Travel Itinerary, Air Ticket, Hotel Booking
4. **FINANCIAL INFO** → Used in: Cover Letter, Financial Statement, Tax Certificate
5. **ASSETS INFO** → Used in: Asset Valuation, Home Tie
6. **TRAVEL HISTORY** → Used in: Travel History, Cover Letter
7. **TAX INFO** → Used in: TIN Certificate, Tax Certificate

---

## 📄 DOCUMENT-BY-DOCUMENT DATA REQUIREMENTS

---

### **1. COVER LETTER** (Most Important - 2-3 pages)

#### 🔴 REQUIRED (Must Have):
- **Full Name** - Applicant's complete name
- **Passport Number** - Valid passport number
- **Purpose of Travel** - Why going to Iceland (tourism/business)
- **Bank Balance** - Current savings amount
- **Reason to Return** - Why will return to Bangladesh

#### 🟡 SUGGESTED (Highly Recommended):
- **Profession** - Job title or business type
- **Company Name** - Employer or business name
- **Travel Dates** - Departure and return dates
- **Places to Visit** - Reykjavik, Golden Circle, etc.
- **Annual Income** - Yearly earnings
- **Family Ties** - Marital status, dependents
- **Property/Assets** - Owned properties value

#### 🟢 OPTIONAL (Nice to Have):
- **Previous Travel** - Countries visited before
- **Monthly Income** - For detailed financial picture
- **Specific Activities** - Detailed travel plans

**Current Code Uses:**
```python
'passport_copy.full_name', 'personal.full_name'  # ← Need to map to questionnaire keys
'passport_copy.passport_number'
'employment.job_title', 'business.business_type'
'travel_purpose', 'travel.purpose'
'bank_solvency.current_balance'
```

---

### **2. NID ENGLISH TRANSLATION** (1 page)

#### 🔴 REQUIRED:
- **Full Name (English)** - Name in English
- **Father's Name** - Father's full name in English
- **Mother's Name** - Mother's full name in English
- **Date of Birth** - DD/MM/YYYY format
- **NID Number** - 10/13/17 digit NID

#### 🟡 SUGGESTED:
- **Address** - Current residential address in English
- **Blood Group** - A+, B+, O+, etc.

#### 🟢 OPTIONAL:
- **Place of Birth** - Birth city/district

**Current Code Uses:**
```python
'passport_copy.full_name', 'bank_solvency.account_holder_name'
'bank_solvency.father_name', 'personal.father_name'
'bank_solvency.mother_name', 'personal.mother_name'
'passport_copy.date_of_birth'
'nid_bangla.nid_number'
```

---

### **3. VISITING CARD** (1 page - Business Card)

#### 🔴 REQUIRED:
- **Full Name** - Person's name
- **Phone Number** - Mobile/Contact number

#### 🟡 SUGGESTED:
- **Designation/Job Title** - CEO, Manager, Business Owner, etc.
- **Company Name** - Business/Employer name
- **Email** - Professional email address

#### 🟢 OPTIONAL:
- **Website** - Company website
- **Address** - Office/Business address

**Current Code Uses:**
```python
'passport_copy.full_name'
'employment.job_title', 'business.business_type'
'business.company_name', 'employment.company_name'
'personal.phone', 'contact.mobile'
'personal.email'
```

---

### **4. FINANCIAL STATEMENT** (2 pages)

#### 🔴 REQUIRED:
- **Full Name** - Account holder name
- **Current Bank Balance** - Total savings

#### 🟡 SUGGESTED:
- **Annual Income (Year 1)** - Most recent year's income
- **Annual Income (Year 2)** - Previous year
- **Annual Income (Year 3)** - 3rd year
- **Monthly Income** - Current monthly earnings
- **Monthly Expenses** - Average monthly spending

#### 🟢 OPTIONAL:
- **Trip Funding Source** - How trip will be funded

**Current Code Uses:**
```python
'passport_copy.full_name'
'income_tax_3years.year1_income', 'financial.annual_income'
'income_tax_3years.year2_income'
'income_tax_3years.year3_income'
'financial.monthly_income'
'financial.monthly_expenses'
'bank_solvency.current_balance'
```

---

### **5. TRAVEL ITINERARY** (3-5 pages)

#### 🔴 REQUIRED:
- **Full Name** - Traveler name
- **Duration** - Number of days (e.g., "14 days")
- **Check-in Date** - First day of travel

#### 🟡 SUGGESTED:
- **Places to Visit** - Golden Circle, Blue Lagoon, Reykjavik, etc.
- **Accommodation** - Hotel name
- **Planned Activities** - Sightseeing, hiking, etc.

#### 🟢 OPTIONAL:
- **Passport Number** - For header details

**Current Code Uses:**
```python
'passport_copy.full_name'
'travel.duration', 'hotel_booking.duration'
'hotel.check_in_date', 'travel.arrival_date'
'travel.places_to_visit'
'travel.planned_activities'
```

---

### **6. TRAVEL HISTORY** (1-2 pages)

#### 🔴 REQUIRED:
- **Full Name** - Applicant name

#### 🟡 SUGGESTED (If Applicable):
- **Countries Visited** - List of countries
- **Entry/Exit Dates** - For each country
- **Visa Type** - Tourist, Business, etc.

#### 🟢 OPTIONAL:
- **Duration of Stay** - How long in each country
- **Purpose** - Why visited

**Current Code Uses:**
```python
'personal.full_name'
'travel_history.countries_visited'  # ← Can be comma-separated
```

**Note:** If no travel history, document shows "No previous international travel"

---

### **7. HOME TIE STATEMENT** (1-2 pages)

#### 🔴 REQUIRED:
- **Full Name** - Applicant name
- **Reasons to Return** - Why must return to Bangladesh

#### 🟡 SUGGESTED:
- **Father's Name** - Family tie
- **Mother's Name** - Family tie
- **Address/Location** - Where they live
- **Family Members** - Spouse, children, parents
- **Property Ownership** - Owned properties

#### 🟢 OPTIONAL:
- **Business Responsibilities** - If business owner
- **Employment Obligations** - If employed

**Current Code Uses:**
```python
'passport_copy.full_name', 'bank_solvency.account_holder_name'
'bank_solvency.father_name'
'bank_solvency.mother_name'
'bank_solvency.current_address'
'home_ties.family_members', 'personal.marital_status'
'home_ties.reasons_to_return'
```

---

### **8. ASSET VALUATION CERTIFICATE** (5 pages)

#### 🔴 REQUIRED:
- **Owner Name** - Property owner
- **Total Asset Value** - Sum of all assets

#### 🟡 SUGGESTED:
- **Father's Relation** - "S/O [Father Name]"
- **Property Details** - Addresses, sizes
- **Property Values** - Individual property values
- **Vehicle Details** - Car/motorcycle info
- **Vehicle Values** - Individual vehicle values

#### 🟢 OPTIONAL:
- **Business Assets** - Business valuation
- **Investment Details** - Stocks, bonds, etc.

**Current Code Uses:**
```python
'passport_copy.full_name'
'personal.father_name'
'assets.property_description'
'assets.property_value'
'assets.vehicle_details'
'assets.total_value'
```

**Note:** Currently has HARDCODED sample data - needs real data!

---

### **9. TIN CERTIFICATE** (1 page)

#### 🔴 REQUIRED:
- **Full Name** - Taxpayer name
- **TIN Number** - 12-digit TIN

#### 🟡 SUGGESTED:
- **Father's Name** - For identification
- **NID Number** - National ID
- **Address** - Registered address

#### 🟢 OPTIONAL:
- **Tax Circle** - Dhaka Taxes Circle-1, etc.
- **Tax Zone** - Dhaka Zone-1, etc.

**Current Code Uses:**
```python
'passport_copy.full_name', 'bank_solvency.account_holder_name'
'bank_solvency.father_name'
'nid_bangla.nid_number'
'bank_solvency.current_address'
'tin_certificate.tin_number', 'tax.tin_number'
'tin_certificate.circle'
```

**Note:** Auto-generates TIN if not provided

---

### **10. TAX CERTIFICATE** (2-3 pages)

#### 🔴 REQUIRED:
- **Full Name** - Taxpayer name
- **TIN Number** - Tax ID

#### 🟡 SUGGESTED:
- **Assessment Year** - 2024-2025, etc.
- **Total Income** - Annual taxable income
- **Tax Paid** - Amount of tax paid

#### 🟢 OPTIONAL:
- **Tax Circle** - Circle/Zone details

**Current Code Uses:**
```python
'passport_copy.full_name'
'tin_certificate.tin_number', 'tax.tin_number'
'tax.assessment_year'
'income_tax_3years.year1_income', 'financial.annual_income'
'tax.tax_paid'
```

---

### **11. TRADE LICENSE** (1 page)

#### 🔴 REQUIRED:
- **Owner Name** - Business owner
- **Business Name** - Company/Enterprise name

#### 🟡 SUGGESTED:
- **Business Type** - Service Provider, Trading, Manufacturing
- **Business Address** - Office location

#### 🟢 OPTIONAL:
- **License Number** - If already have one
- **Issue Date** - Previous license date

**Current Code Uses:**
```python
'passport_copy.full_name'
'business.company_name', 'business.business_name'
'business.business_type'
'business.business_address'
```

**Note:** Auto-generates license number if not provided

---

### **12. HOTEL BOOKING CONFIRMATION** (1 page)

#### 🔴 REQUIRED:
- **Guest Name** - Who's staying
- **Hotel Name** - Where staying
- **Check-in Date** - Arrival date
- **Check-out Date** - Departure date

#### 🟡 SUGGESTED:
- **Hotel Address** - Reykjavik, Iceland
- **Room Type** - Double, Single, Suite
- **Total Price** - Booking cost

#### 🟢 OPTIONAL:
- **Confirmation Number** - Booking reference
- **Cancellation Policy** - Free/Non-refundable

**Current Code Uses:**
```python
'passport_copy.full_name'
'hotel_booking.hotel_name', 'hotel.hotel_name'
'hotel_booking.hotel_address'
'hotel.check_in_date'
'hotel.check_out_date'
'hotel_booking.room_type'
'hotel.total_price'
```

**Note:** Auto-generates confirmation number

---

### **13. AIR TICKET / E-TICKET** (1 page)

#### 🔴 REQUIRED:
- **Passenger Name** - Traveler name
- **Departure Date** - Outbound flight date
- **Return Date** - Return flight date

#### 🟡 SUGGESTED:
- **Passport Number** - For ticket
- **PNR** - Booking reference

#### 🟢 OPTIONAL:
- **Ticket Number** - E-ticket number
- **Flight Numbers** - Specific flights
- **Airline Preference** - Which airline

**Current Code Uses:**
```python
'passport_copy.full_name'
'passport_copy.passport_number'
'flight.departure_date', 'air_ticket.departure_date'
'flight.return_date', 'air_ticket.return_date'
'flight.pnr'
```

**Note:** Auto-generates PNR and ticket number

---

## 🎯 RECOMMENDED QUESTIONNAIRE STRUCTURE

Based on analysis, here's the SMART questionnaire flow:

### **SECTION 1: PERSONAL INFO** (Always Required)
1. ✅ **Full Name** (REQUIRED - all documents)
2. ✅ **Father's Name** (REQUIRED - NID, TIN, Home Tie)
3. ✅ **Mother's Name** (REQUIRED - NID, Home Tie)
4. ✅ **Date of Birth** (REQUIRED - NID, Cover Letter)
5. ✅ **NID Number** (REQUIRED - NID, TIN)
6. ✅ **Passport Number** (REQUIRED - Cover Letter, Air Ticket)
7. ✅ **Phone Number** (REQUIRED - Visiting Card)
8. ⭐ **Email** (SUGGESTED - Visiting Card)
9. ⭐ **Current Address** (SUGGESTED - NID, TIN, Home Tie)
10. 💡 **Blood Group** (OPTIONAL - NID)

### **SECTION 2: EMPLOYMENT/BUSINESS** (Show if Business Owner or Employed)
11. ✅ **Profession/Job Title** (REQUIRED - Cover Letter, Visiting Card)
12. ✅ **Company/Business Name** (REQUIRED - Visiting Card, Trade License)
13. ⭐ **Business Type** (SUGGESTED - Trade License)
14. ⭐ **Business Address** (SUGGESTED - Trade License)
15. 💡 **Company Website** (OPTIONAL - Visiting Card)

### **SECTION 3: TRAVEL DETAILS** (Always Required)
16. ✅ **Purpose of Travel** (REQUIRED - Cover Letter)
17. ✅ **Travel Duration (Days)** (REQUIRED - Itinerary)
18. ✅ **Departure Date** (REQUIRED - Air Ticket, Itinerary)
19. ✅ **Return Date** (REQUIRED - Air Ticket)
20. ✅ **Hotel Name** (REQUIRED - Hotel Booking)
21. ⭐ **Places to Visit** (SUGGESTED - Cover Letter, Itinerary)
22. 💡 **Planned Activities** (OPTIONAL - Itinerary)

### **SECTION 4: FINANCIAL INFO** (Always Required)
23. ✅ **Current Bank Balance** (REQUIRED - Cover Letter, Financial)
24. ⭐ **Annual Income (Year 1)** (SUGGESTED - Financial, Cover Letter)
25. ⭐ **Annual Income (Year 2)** (SUGGESTED - Financial)
26. ⭐ **Annual Income (Year 3)** (SUGGESTED - Financial)
27. ⭐ **Monthly Income** (SUGGESTED - Financial)
28. ⭐ **TIN Number** (SUGGESTED - TIN Cert, Tax Cert)
29. 💡 **Monthly Expenses** (OPTIONAL - Financial)
30. 💡 **Tax Paid** (OPTIONAL - Tax Certificate)

### **SECTION 5: ASSETS** (Suggested Section)
31. ⭐ **Do you own property?** (Yes/No)
32. ⭐ **Property Details** (If Yes - location, type)
33. ⭐ **Property Value** (If Yes)
34. ⭐ **Do you own vehicle?** (Yes/No)
35. ⭐ **Vehicle Details** (If Yes)
36. 💡 **Total Asset Value** (OPTIONAL - can calculate)

### **SECTION 6: FAMILY & HOME TIES** (Critical for Visa)
37. ✅ **Marital Status** (REQUIRED - Home Tie, Cover Letter)
38. ⭐ **Family Members in Bangladesh** (SUGGESTED - Home Tie)
39. ⭐ **Reasons to Return** (SUGGESTED - Home Tie, Cover Letter)

### **SECTION 7: TRAVEL HISTORY** (Optional Section)
40. 💡 **Previous Countries Visited** (OPTIONAL - Travel History)
41. 💡 **Previous Visa Details** (OPTIONAL - Travel History)

---

## 🔍 KEY FINDINGS & RECOMMENDATIONS

### **Problem Identified:**
The system currently looks for keys like:
- `'passport_copy.full_name'` 
- `'employment.job_title'`
- `'bank_solvency.current_balance'`

But questionnaire saves as:
- `'father_name'`
- `'job_title'`
- `'travel_purpose'`

### **Solution:**
Create a **KEY MAPPING** in `_get_value()` method:

```python
# Map simple questionnaire keys to what documents expect
KEY_MAP = {
    'father_name': 'personal.father_name',
    'mother_name': 'personal.mother_name',
    'job_title': 'employment.job_title',
    'company_name': 'business.company_name',
    'travel_purpose': 'travel.purpose',
    # ... etc for all 40+ fields
}
```

---

## ✅ NEXT STEPS (After Your Review)

1. **You Review This Document** - Check if categories make sense
2. **Confirm Questionnaire Structure** - Adjust sections as needed
3. **I Implement Fix** - Update `_get_value()` with mapping
4. **Test with Real Data** - Generate documents, verify data appears
5. **Deploy** - Push to Render when working

---

## 📝 YOUR FEEDBACK NEEDED

Please review and let me know:

1. **Are the 7 sections logical?** (Personal, Employment, Travel, Financial, Assets, Home Ties, History)
2. **Are Required/Suggested/Optional categorizations correct?**
3. **Any fields missing that should be included?**
4. **Any fields included that aren't needed?**
5. **Ready to proceed with implementation?**

Once you approve, I'll implement the fix **safely** without breaking existing system! 🚀

---

**Total Fields Identified:** ~40 fields across 7 categories  
**Documents Covered:** All 13 generated documents  
**Current System Status:** ✅ Working but not using questionnaire data properly  
**Fix Complexity:** Medium - needs key mapping + `_get_value()` update  
**Estimated Implementation Time:** 2-3 hours  
**Risk Level:** LOW - additive changes only
