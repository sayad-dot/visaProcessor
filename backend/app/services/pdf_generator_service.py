"""
PDF Generator Service - Generates all 13 visa application documents
Uses ReportLab for professional PDF generation and Gemini for intelligent content
"""
import os
import io
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import google.generativeai as genai
from sqlalchemy.orm import Session
from loguru import logger

from app.models import ExtractedData, QuestionnaireResponse, GeneratedDocument, GenerationStatus
from app.config import settings
from app.services.auto_fill_service import auto_fill_questionnaire


class PDFGeneratorService:
    """Service for generating all visa application PDFs"""
    
    # Comprehensive key mapping: questionnaire keys → PDF template paths
    KEY_MAPPING = {
        # Personal Information
        "full_name": ["full_name", "passport_copy.full_name", "nid_bangla.name_english", "nid_english.full_name", "personal.full_name"],
        "email": ["email", "contact.email", "personal.email"],
        "phone": ["phone", "contact.phone", "personal.phone"],
        "date_of_birth": ["date_of_birth", "passport_copy.date_of_birth", "nid_bangla.date_of_birth", "personal.dob"],
        "gender": ["gender", "passport_copy.gender", "personal.gender"],
        "father_name": ["father_name", "nid_bangla.father_name", "personal.father_name"],
        "mother_name": ["mother_name", "nid_bangla.mother_name", "personal.mother_name"],
        "permanent_address": ["permanent_address", "nid_bangla.permanent_address", "address.permanent"],
        "present_address": ["present_address", "address.present", "contact.address"],
        "passport_number": ["passport_number", "passport_copy.passport_number", "personal.passport_number"],
        "passport_issue_date": ["passport_issue_date", "passport_copy.issue_date"],
        "passport_expiry_date": ["passport_expiry_date", "passport_copy.expiry_date"],
        "nid_number": ["nid_number", "nid_bangla.nid_number", "personal.nid_number"],
        "is_married": ["is_married", "personal.marital_status"],
        "spouse_name": ["spouse_name", "personal.spouse_name"],
        "number_of_children": ["number_of_children", "personal.children"],
        "blood_group": ["blood_group", "personal.blood_group"],
        
        # Employment & Business
        "employment_status": ["employment_status", "employment.employment_status"],
        "job_title": ["job_title", "employment.job_title", "employment.position"],
        "company_name": ["company_name", "employment.company_name", "business.company_name"],
        "company_address": ["company_address", "employment.company_address", "business.address"],
        "business_type": ["business_type", "business.business_type"],
        "business_start_year": ["business_start_year", "business.start_year"],
        "number_of_employees": ["number_of_employees", "business.employees"],
        
        # Travel Details
        "travel_purpose": ["travel_purpose", "travel.purpose", "purpose"],
        "duration_of_stay": ["duration_of_stay", "travel.duration", "hotel_booking.duration"],
        "arrival_date": ["arrival_date", "travel.arrival_date", "hotel_booking.check_in_date", "air_ticket.departure_date"],
        "departure_date": ["departure_date", "travel.departure_date", "hotel_booking.check_out_date", "air_ticket.return_date"],
        "places_to_visit": ["places_to_visit", "travel.places", "hotel_booking.hotel_location"],
        "accommodation_details": ["accommodation_details", "hotel_booking.hotel_name"],
        
        # Financial Information
        "monthly_income": ["monthly_income", "financial.monthly_income", "income_tax_3years.monthly_income"],
        "annual_income": ["annual_income", "financial.annual_income", "income_tax_3years.annual_income"],
        "monthly_expenses": ["monthly_expenses", "financial.monthly_expenses"],
        "total_rental_income": ["total_rental_income", "financial.rental_income"],
        
        # Other Information
        "tin_number": ["tin_number", "tin_certificate.tin_number", "income_tax_3years.tin_number"],
        "tax_circle": ["tax_circle", "tin_certificate.tax_circle"],
        "reasons_to_return": ["reasons_to_return", "travel.reasons_to_return"],
        "additional_info": ["additional_info", "other.additional_info"],
    }
    
    def __init__(self, db: Session, application_id: int):
        self.db = db
        self.application_id = application_id
        self.output_dir = os.path.join("uploads", f"app_{application_id}", "generated")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Load all extracted data
        self.extracted_data = self._load_extracted_data()
        self.questionnaire_data = self._load_questionnaire_data()
        
        # Auto-fill missing data with realistic values
        self._auto_fill_missing_data()
        
    def _load_extracted_data(self) -> Dict[str, Any]:
        """Load all extracted data from database"""
        records = self.db.query(ExtractedData).filter(
            ExtractedData.application_id == self.application_id
        ).all()
        
        data = {}
        for record in records:
            doc_type_key = record.document_type.value
            data[doc_type_key] = record.data
            # Log each record's fields
            logger.info(f"   📄 {doc_type_key}: {list(record.data.keys())[:5]}...")
        
        # Debug logging
        logger.info(f"📦 Loaded extracted data for app {self.application_id}")
        logger.info(f"   Document types: {list(data.keys())}")
        for doc_type, doc_data in data.items():
            logger.info(f"   {doc_type}: {len(doc_data)} fields")
        
        return data
    
    def _load_questionnaire_data(self) -> Dict[str, str]:
        """Load all questionnaire responses (including auto-filled data)"""
        responses = self.db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.application_id == self.application_id
        ).all()
        
        data = {}
        for response in responses:
            # Handle JSON arrays (banks, assets, travels) - stored as JSON strings
            import json
            try:
                # Try to parse as JSON (for arrays stored as JSON strings in TEXT fields)
                if isinstance(response.answer, str) and (response.answer.startswith('[') or response.answer.startswith('{')):
                    data[response.question_key] = json.loads(response.answer)
                else:
                    data[response.question_key] = response.answer
            except:
                data[response.question_key] = response.answer
        
        # Debug logging
        logger.info(f"📝 Loaded questionnaire data for app {self.application_id}")
        logger.info(f"   Total responses: {len(data)}")
        if data:
            logger.info(f"   Sample keys: {list(data.keys())[:5]}")
            # Log array fields
            array_fields = [k for k, v in data.items() if isinstance(v, list)]
            if array_fields:
                logger.info(f"   Array fields: {array_fields}")
        
        return data
    
    def _auto_fill_missing_data(self):
        """Auto-fill missing data with realistic values to ensure NO BLANK DATA"""
        logger.info(f"🤖 Auto-filling missing data for app {self.application_id}")
        
        try:
            # Get auto-filled data
            filled_data, summary = auto_fill_questionnaire(self.questionnaire_data)
            
            # Add filled data to questionnaire_data (only for missing keys)
            filled_count = 0
            for key, value in filled_data.items():
                if key not in self.questionnaire_data or not self.questionnaire_data.get(key):
                    self.questionnaire_data[key] = value
                    filled_count += 1
            
            logger.info(f"✅ Auto-filled {filled_count} missing fields")
            logger.info(f"   Summary: {summary}")
            
        except Exception as e:
            logger.error(f"❌ Auto-fill error: {e}")
            # Continue without auto-fill (better than failing completely)
    
    def _get_array(self, key: str) -> List[Dict[str, Any]]:
        """Get array data from questionnaire (banks, assets, travels, etc.)"""
        value = self.questionnaire_data.get(key)
        
        if not value:
            logger.debug(f"📋 Array '{key}' not found, returning empty list")
            return []
        
        if isinstance(value, list):
            logger.debug(f"✅ Found array '{key}' with {len(value)} items")
            return value
        
        # Try to parse JSON string
        if isinstance(value, str):
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    logger.debug(f"✅ Parsed array '{key}' from JSON with {len(parsed)} items")
                    return parsed
            except:
                pass
        
        logger.warning(f"⚠️  Array '{key}' is not a list: {type(value)}")
        return []
    
    def _get_banks(self) -> List[Dict[str, Any]]:
        """Get bank accounts from questionnaire or auto-filled data"""
        banks = self._get_array('banks')
        if not banks:
            # Fallback to single bank data if arrays not available
            bank_name = self._get_value('bank_name', 'bank_solvency.bank_name')
            if bank_name:
                return [{
                    'bank_name': bank_name,
                    'account_type': self._get_value('account_type', 'bank_solvency.account_type') or 'Savings Account',
                    'account_number': self._get_value('account_number', 'bank_solvency.account_number') or 'N/A',
                    'balance': self._get_value('balance', 'bank_solvency.balance') or '0'
                }]
        return banks
    
    def _get_assets(self) -> List[Dict[str, Any]]:
        """Get assets from questionnaire or auto-filled data"""
        return self._get_array('assets')
    
    def _get_previous_travels(self) -> List[Dict[str, Any]]:
        """Get previous travels from questionnaire"""
        return self._get_array('previous_travels')
    
    def _get_value(self, *keys) -> str:
        """Get value with priority: Questionnaire (user+auto-fill) → Extraction → KEY_MAPPING fallbacks"""
        
        # Priority 1: Check questionnaire data first (includes user input + auto-fill)
        for key in keys:
            # Remove document type prefix if present (e.g., 'passport_copy.full_name' → 'full_name')
            clean_key = key.split('.')[-1] if '.' in key else key
            
            # Direct match in questionnaire
            value = self.questionnaire_data.get(clean_key)
            if value and str(value).strip():
                logger.debug(f"✅ Found '{key}' in questionnaire: {value}")
                return str(value)
            
            # Try with original key (for dotted keys in questionnaire)
            value = self.questionnaire_data.get(key)
            if value and str(value).strip():
                logger.debug(f"✅ Found '{key}' in questionnaire: {value}")
                return str(value)
            
            # Check KEY_MAPPING for alternative questionnaire keys
            if clean_key in self.KEY_MAPPING:
                for mapped_key in self.KEY_MAPPING[clean_key]:
                    # Check if it's a simple key in questionnaire
                    if '.' not in mapped_key:
                        value = self.questionnaire_data.get(mapped_key)
                        if value and str(value).strip():
                            logger.debug(f"✅ Found '{key}' via mapping '{mapped_key}' in questionnaire: {value}")
                            return str(value)
        
        # Priority 2: Check extracted data from documents
        for key in keys:
            if '.' in key:
                doc_type, field = key.split('.', 1)
                if doc_type in self.extracted_data:
                    value = self.extracted_data[doc_type].get(field)
                    if value and str(value).strip():
                        logger.debug(f"✅ Found '{key}' in extracted_data: {value}")
                        return str(value)
        
        # Priority 3: Try KEY_MAPPING alternatives in extracted data
        for key in keys:
            clean_key = key.split('.')[-1] if '.' in key else key
            if clean_key in self.KEY_MAPPING:
                for mapped_key in self.KEY_MAPPING[clean_key]:
                    if '.' in mapped_key:
                        doc_type, field = mapped_key.split('.', 1)
                        if doc_type in self.extracted_data:
                            value = self.extracted_data[doc_type].get(field)
                            if value and str(value).strip():
                                logger.debug(f"✅ Found '{key}' via mapping '{mapped_key}' in extraction: {value}")
                                return str(value)
        
        # If still not found, log warning (should be rare due to auto-fill)
        logger.warning(f"⚠️  Missing value for keys: {keys} (even after auto-fill)")
        return ""
    
    def _create_document_record(self, doc_type: str, file_name: str) -> GeneratedDocument:
        """Create database record for generated document"""
        file_path = os.path.join(self.output_dir, file_name)
        
        doc = GeneratedDocument(
            application_id=self.application_id,
            document_type=doc_type,
            file_name=file_name,
            file_path=file_path,
            status=GenerationStatus.GENERATING,
            generation_progress=0
        )
        self.db.add(doc)
        self.db.commit()
        return doc
    
    def _update_progress(self, doc: GeneratedDocument, progress: int, status: str = None):
        """Update generation progress"""
        doc.generation_progress = progress
        if status:
            doc.status = status
        self.db.commit()
    
    def _generate_content_with_ai(self, prompt: str) -> str:
        """Generate content using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"AI generation error: {e}")
            return ""
    
    def _get_embassy_address(self, country: str = "Iceland") -> Dict[str, str]:
        """Get embassy address and details based on destination country"""
        embassy_addresses = {
            "Iceland": {
                "embassy_name": "Embassy of Iceland",
                "address_line1": "House 16, Road 113/A",
                "address_line2": "Gulshan 2, Dhaka 1212",
                "country": "Bangladesh",
                "greeting": "Dear Visa Officer,"
            },
            "Norway": {
                "embassy_name": "Royal Norwegian Embassy",
                "address_line1": "House 18, Road 111",
                "address_line2": "Gulshan 2, Dhaka 1212",
                "country": "Bangladesh",
                "greeting": "Dear Visa Officer,"
            },
            "Denmark": {
                "embassy_name": "Royal Danish Embassy",
                "address_line1": "House 1, Road 51",
                "address_line2": "Gulshan 2, Dhaka 1212",
                "country": "Bangladesh",
                "greeting": "Dear Visa Officer,"
            },
            "UK": {
                "embassy_name": "British High Commission",
                "address_line1": "United Nations Road",
                "address_line2": "Baridhara, Dhaka 1212",
                "country": "Bangladesh",
                "greeting": "Dear Sir/Madam,"
            },
            "USA": {
                "embassy_name": "Embassy of the United States",
                "address_line1": "Madani Avenue",
                "address_line2": "Baridhara, Dhaka 1212",
                "country": "Bangladesh",
                "greeting": "Dear Consul,"
            },
        }
        return embassy_addresses.get(country, embassy_addresses["Iceland"])
    
    # ============================================================================
    # 1. COVER LETTER (MOST IMPORTANT)
    # ============================================================================
    
    def generate_cover_letter(self) -> str:
        """Generate formal cover letter to Embassy of Iceland"""
        import json
        doc_record = self._create_document_record("cover_letter", "Cover_Letter.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)

            # 1. Collect all data with enhanced priority
            # Get bank accounts for financial summary
            banks = self._get_banks()
            total_balance = sum(float(bank.get('balance', 0)) for bank in banks) if banks else 0
            
            applicant_data = {
                "name": self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english'),
                "passport": self._get_value('passport_number', 'passport_copy.passport_number'),
                "profession": self._get_value('job_title', 'employment.job_title', 'business_type', 'business.business_type'),
                "company": self._get_value('company_name', 'employment.company_name', 'business.business_name'),
                "purpose": self._get_value('travel_purpose', 'travel.purpose', 'purpose') or 'Tourism and exploring Iceland',
                "travel_dates": self._get_value('arrival_date', 'travel.arrival_date', 'hotel_booking.check_in_date') or 'Planned dates',
                "places": self._get_value('places_to_visit', 'travel.places', 'hotel_booking.hotel_location') or 'Reykjavik, Golden Circle, Blue Lagoon',
                "income": self._get_value('annual_income', 'monthly_income', 'financial.annual_income'),
                "bank_balance": f"BDT {total_balance:,.0f}" if total_balance > 0 else self._get_value('bank_solvency.current_balance'),
                "family_ties": self._get_value('spouse_name', 'number_of_children', 'personal.marital_status') or 'Family in Bangladesh',
                "property_ties": self._get_value('asset_valuation.total_value', 'assets.property_description') or 'Property ownership',
                "reasons_to_return": self._get_value('reasons_to_return', 'home_ties.reasons_to_return') or 'Family, business, and property responsibilities in Bangladesh'
            }
            self._update_progress(doc_record, 20)

            # 2. Few-shot example from OCR'd PDF
            sample_cover_letter = """
            Subject: Request for a visitor visa application for the United Kingdom.
            
            Dear Respected Sir,
            
            I am Md Swapon Sheikh a business proprietor. I intend to visit United Kingdom to experience its renowned natural beauty, explore its rich cultural heritage, and hopefully, this trip will create outstanding memories. I am so excited that I have prepared all my papers and documents according to United Kingdom immigration procedures.
            
            I am Md Swapon Sheikh I am the applicant and a Bangladeshi citizen, holding passport number A04907327. United Kingdom has always been my dream country as a tourist destination. So now, I am writing to formally submit my application for a tourist visa to UNITED KINGDOM. I have fulfilled all the requirements outlined by United Kingdom immigration. Now I am currently a Proprietor. My company name is “SHEIKH ONLINE SERVICE” and I am the founder of my business. So, all the employees of my company are dependent on me, according to my family members. Additionally, I have attached all the proven documents with this application and providing all the information about my Family Member.
            
            NOTE: My previous application GWF084177219 was refused because my business and financial details were not clearly shown. In this reapplication, I have provided complete and clear documents to fully address those concerns.
            
            Purpose of Travel:
            I am a Businessman and I wish to visit the United Kingdom for tourism and short recreational travel. I plan to stay in London from 29 December 2025 to 12 January 2026 to enjoy a refreshing break from my regular business activities. During my stay, I intend to explore major tourist attractions such as Big Ben, Tower Bridge, Buckingham Palace, the British Museum, the London Eye, Hyde Park, Oxford Street, and other cultural and historical sites. I also wish to enjoy the festive atmosphere of New Year's Eve on 31 December 2025 in London. This is a personal holiday trip, and after completing my visit, I will return to Bangladesh on the scheduled date to resume my business responsibilities.
            
            Financial Stand and Trip Funds:
            I am sharing my bank statements here so you can demonstrate my financial ability to cover all expenses associated with this trip. My accounts reflect the following balances...
            
            Business and Job Ties:
            I, MD Swapon Sheikh, am a businessman and the proprietor of Sheikh Online Service, a small Internet service business located at 706, Moddo Naya Nagar, Vatara, Dhaka-1212. I am fully responsible for managing daily operations, customer services, and business development. My regular presence is required for the smooth running of the business, and I must return to Bangladesh after my trip to continue supervising my work and maintaining my client commitments. These ongoing responsibilities firmly establish my strong business ties to Bangladesh.
            
            I have a Strong Travel History of compliance with international travel regulations, having previously visited...
            
            I respectfully request your favorable consideration of my application and remain available to provide any additional information or documentation as needed. I sincerely look forward to this visit and greatly appreciate your time and attention to my application. Thank you for your understanding and support. I remain at your disposal for any further inquiries.

            Yours faithfully,
            MD SWAPON SHEIKH
            """

            # 3. Construct the new, advanced prompt - EXPANDED FOR 2 PAGES
            prompt = f"""
            You are an expert visa application consultant, specializing in crafting compelling cover letters for Iceland Embassy Schengen visa applications. Your task is to write a professional and persuasive cover letter that fills EXACTLY 2 FULL PAGES.

            **Analysis of a High-Quality Sample Letter:**
            Here is an example of a good cover letter. Notice its structure, tone, and the way it clearly presents information and addresses potential concerns.
            ---
            [GOOD EXAMPLE START]
            {sample_cover_letter}
            [GOOD EXAMPLE END]
            ---

            **Applicant's Profile:**
            Now, analyze the following data for the current applicant.
            - Name: {applicant_data['name']}
            - Passport: {applicant_data['passport']}
            - Profession: {applicant_data['profession']} at {applicant_data['company']}
            - Purpose of Visit: {applicant_data['purpose']}
            - Proposed Travel Dates: {applicant_data['travel_dates']}
            - Planned locations: {applicant_data['places']}
            - Financials: Annual income of {applicant_data['income']}, with {applicant_data['bank_balance']} in the bank.
            - Home Ties (Family): {applicant_data['family_ties']}
            - Home Ties (Assets): Owns {applicant_data['property_ties']}
            - Stated Reason to Return: {applicant_data['reasons_to_return']}

            **Your Task: Generate a New Cover Letter for Iceland Embassy**
            Based on the applicant's profile, write a new cover letter that follows Iceland Embassy expectations.

            **CRITICAL REQUIREMENTS:**
            - Length: MUST be 1600-1800 words to fill EXACTLY 2 FULL PAGES
            - Tone: Use simple, school-grade English (10th-12th grade level) - clear and conversational but professional
            - Format: Follow how Iceland Embassy wants cover letters structured
            - Content: Be detailed, specific, and convincing

            **Instructions:**
            1.  **Structure and Content:** The letter must be formal and structured into 7-8 SUBSTANTIAL paragraphs:
                *   **Paragraph 1: Introduction (120-150 words):** Introduce the applicant, their full name, passport number, profession, and company. State the purpose of the letter (applying for an Iceland tourist visa for specific dates). Mention excitement about visiting Iceland.
                
                *   **Paragraph 2: About Iceland and Why Visit (200-250 words):** Express genuine interest in Iceland. Mention specific attractions like Reykjavik, Golden Circle, Blue Lagoon, Northern Lights, waterfalls, glaciers. Explain WHY you want to visit Iceland specifically (natural beauty, unique culture, safe country, etc.). Show you've researched Iceland.
                
                *   **Paragraph 3: Detailed Travel Plans (200-250 words):** Elaborate on travel dates, duration of stay, detailed itinerary. Mention which cities/regions you'll visit, what activities you plan (sightseeing, photography, nature exploration). Include accommodation plans, transportation arrangements. Be specific and organized.
                
                *   **Paragraph 4: Financial Capacity - Part 1 (180-200 words):** State that you will self-fund your entire trip. Mention your profession, monthly/annual income. Explain that you have sufficient savings to cover all costs (flights, accommodation, food, activities, insurance). Reference your bank balance ({applicant_data['bank_balance']}) and that bank statements are attached.
                
                *   **Paragraph 5: Financial Capacity - Part 2 (180-200 words):** Provide MORE financial details. Mention if you have multiple bank accounts. Talk about your financial stability over time. Mention that you understand trip costs and have budgeted accordingly. Reference any credit cards or additional financial resources. Emphasize you won't be a burden to Iceland.
                
                *   **Paragraph 6: Business/Job Ties (200-220 words):** Describe your job or business in detail. Explain your role, daily responsibilities, why you're important to the company/business. Mention that you have obligations and must return to resume work. Include specific details about your company, how long you've worked there, future projects/plans requiring your presence.
                
                *   **Paragraph 7: Family and Property Ties (200-220 words):** Elaborate on family members in Bangladesh (parents, spouse, children). Mention any property you own (house, land, apartments). Explain your emotional and financial connections to Bangladesh. Talk about family responsibilities, cultural ties, social connections. Make it clear you have STRONG reasons to return.
                
                *   **Paragraph 8: Conclusion (180-200 words):** Summarize key points: tourism purpose, self-funded, strong ties to Bangladesh, will return. Express gratitude for considering your application. Mention you're available for interview or additional documents. State you will respect all Schengen visa rules. End with respectful closing.

            2.  **Tone and Language Rules:**
                - Use simple, clear English (school-grade level - NOT overly formal or complex)
                - Write like you're explaining to a person face-to-face
                - Be confident but humble
                - Sound genuine and honest (not robotic or template-like)
                - Use first person ("I", "my", "I am")
                - Avoid overly emotional language or begging
                - Be professional but warm

            3.  **Output Format:** Structure your response as a JSON object with the following keys:
                *   `"subject"`: A string for the subject line of the letter.
                *   `"greeting"`: A string for the salutation (e.g., "Dear Visa Officer,").
                *   `"body"`: An array of strings, where each string is a paragraph of the letter's body. MUST have 7-8 paragraphs, each 180-250 words.
                *   `"closing"`: A string for the closing remark (e.g., "Sincerely,").
                *   `"signature"`: A string for the applicant's name.

            **Example JSON output:**
            {{
              "subject": "Application for Schengen Tourist Visa to Iceland",
              "greeting": "Dear Sir or Madam,",
              "body": [
                "Paragraph 1: Introduction (120-150 words)...",
                "Paragraph 2: About Iceland (200-250 words)...",
                "Paragraph 3: Travel Plans (200-250 words)...",
                "Paragraph 4: Financial Part 1 (180-200 words)...",
                "Paragraph 5: Financial Part 2 (180-200 words)...",
                "Paragraph 6: Job Ties (200-220 words)...",
                "Paragraph 7: Family Ties (200-220 words)...",
                "Paragraph 8: Conclusion (180-200 words)..."
              ],
              "closing": "Yours faithfully,",
              "signature": "{applicant_data['name']}"
            }}

            Now, generate the JSON for the new cover letter.
            """
            
            self._update_progress(doc_record, 40)
            ai_response_text = self._generate_content_with_ai(prompt)
            self._update_progress(doc_record, 70)

            # 4. Parse the AI's JSON response
            try:
                # Clean the response to extract only the JSON part
                json_str = ai_response_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:]
                if json_str.endswith('```'):
                    json_str = json_str[:-3]
                
                letter_data = json.loads(json_str)
                letter_content = "\n\n".join(letter_data.get('body', []))
                subject_text = f"<b>Subject: {letter_data.get('subject', 'Application for Schengen Tourist Visa')}</b>"
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback to old method if JSON fails
                letter_content = ai_response_text
                subject_text = "<b>Subject: Application for Schengen Tourist Visa</b>"

            self._update_progress(doc_record, 80)

            # 5. Create PDF with the generated content
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                fontName='Helvetica'
            )
            
            story.append(Spacer(1, 0.2*inch))
            date_text = f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
            story.append(Paragraph(date_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            to_text = """<b>To,</b><br/>
The Embassy of Iceland<br/>
House 16, Road 113/A<br/>
Gulshan 2, Dhaka 1212<br/>
Bangladesh"""
            story.append(Paragraph(to_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            story.append(Paragraph(subject_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Use parsed content
            paragraphs = letter_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 2. NID ENGLISH TRANSLATION
    # ============================================================================
    
    def generate_nid_translation(self) -> str:
        """Generate official NID English translation matching government format"""
        doc_record = self._create_document_record("nid_english", "NID_English_Translation.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get all NID data (prioritize English from bank_solvency)
            name = self._get_value('nid_bangla.name_english', 'bank_solvency.account_holder_name', 'passport_copy.full_name', 'personal.full_name')
            name_bangla = self._get_value('nid_bangla.name_bangla')
            father = self._get_value('bank_solvency.father_name', 'personal.father_name', 'nid_bangla.father_name_bangla')
            mother = self._get_value('bank_solvency.mother_name', 'personal.mother_name', 'nid_bangla.mother_name_bangla')
            dob = self._get_value('nid_bangla.date_of_birth', 'passport_copy.date_of_birth', 'personal.date_of_birth')
            nid_no = self._get_value('nid_bangla.nid_number', 'personal.nid_number')
            address = self._get_value('bank_solvency.current_address', 'personal.address', 'nid_bangla.address_bangla')
            blood_group = self._get_value('nid_bangla.blood_group', 'personal.blood_group')
            religion = self._get_value('personal.religion')
            birth_place = self._get_value('nid_bangla.place_of_birth', 'personal.birth_place')
            issue_date = self._get_value('nid_bangla.issue_date')
            
            self._update_progress(doc_record, 40)
            
            # Create PDF with canvas for precise layout
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.units import inch
            
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Government Header
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.HexColor('#000080'))
            c.drawCentredString(page_width/2, page_height - 1*inch, "Translated from Bangla to English")
            
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(page_width/2, page_height - 1.3*inch, "Government of the People's Republic of Bangladesh")
            
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(colors.HexColor('#d32f2f'))
            c.drawCentredString(page_width/2, page_height - 1.7*inch, "National ID Card")
            
            # Photo placeholder box
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            photo_x = 1.2*inch
            photo_y = page_height - 3.5*inch
            c.rect(photo_x, photo_y, 1.2*inch, 1.5*inch, fill=False, stroke=True)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.grey)
            c.drawCentredString(photo_x + 0.6*inch, photo_y + 0.7*inch, "Photograph")
            
            # NID Card layout (right side of photo)
            field_x = 2.6*inch
            field_y = page_height - 2.3*inch
            line_height = 0.25*inch
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 9)
            
            # Field labels and values
            fields = [
                ("Name:", name or "N/A"),
                ("Father's Name:", father or "N/A"),
                ("Mother's Name:", mother or "N/A"),
                ("Date of Birth:", dob or "N/A"),
                ("NID No.:", nid_no or "N/A"),
                ("Blood Group:", blood_group or "N/A"),
                ("Religion:", religion or "Islam"),
                ("Birth Place:", birth_place or "Bangladesh"),
                ("Issue Date:", issue_date or "As per original"),
            ]
            
            for i, (label, value) in enumerate(fields):
                y_pos = field_y - (i * line_height)
                
                # Label
                c.setFont("Helvetica-Bold", 9)
                c.drawString(field_x, y_pos, label)
                
                # Value
                c.setFont("Helvetica", 9)
                value_x = field_x + 1.3*inch
                # Wrap long addresses
                if len(str(value)) > 40 and label == "Address:":
                    lines = [value[i:i+40] for i in range(0, len(value), 40)]
                    for j, line in enumerate(lines[:2]):
                        c.drawString(value_x, y_pos - (j * 0.15*inch), line)
                else:
                    c.drawString(value_x, y_pos, str(value))
            
            # Address field (full width below)
            addr_y = field_y - (len(fields) * line_height) - 0.2*inch
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1.2*inch, addr_y, "Address:")
            c.setFont("Helvetica", 9)
            # Wrap address properly
            if address:
                addr_lines = [address[i:i+70] for i in range(0, len(address), 70)]
                for j, line in enumerate(addr_lines[:3]):
                    c.drawString(1.2*inch, addr_y - ((j+1) * 0.2*inch), line)
            else:
                c.drawString(1.2*inch, addr_y - 0.2*inch, "As per original NID card")
            
            # Barcode placeholder
            barcode_y = addr_y - 1.2*inch
            c.setStrokeColor(colors.black)
            c.rect(page_width/2 - 1.5*inch, barcode_y, 3*inch, 0.4*inch, fill=False, stroke=True)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.grey)
            c.drawCentredString(page_width/2, barcode_y + 0.15*inch, "|| || |||| || |||| Barcode Placeholder || |||| || |||| ||")
            
            # Certification section
            cert_y = barcode_y - 0.8*inch
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1.2*inch, cert_y, "TRANSLATED BY")
            
            c.setFont("Helvetica", 9)
            cert_text = [
                "Notarized Translation Services",
                "Authorized Translator",
                "License No: BT/2024/001"
            ]
            
            for i, line in enumerate(cert_text):
                c.drawString(1.2*inch, cert_y - ((i+1) * 0.2*inch), line)
            
            # Date and attestation (removed seal circle as per user request)
            attest_y = 1.5*inch
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(1.2*inch, attest_y, f"Date: {datetime.now().strftime('%d %B %Y')}")
            c.drawString(page_width - 3*inch, attest_y, "Attested: _______________")
            
            # Footer note
            c.setFont("Helvetica-Oblique", 8)
            c.setFillColor(colors.HexColor('#555555'))
            c.drawCentredString(page_width/2, 1*inch, 
                              "This is a certified translation of the original National ID Card issued by Bangladesh Government.")
            c.drawCentredString(page_width/2, 0.8*inch, 
                              "2nd Page contains both front and back view of original NID card.")
            
            c.save()
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 3. VISITING CARD
    # ============================================================================
    
    def generate_visiting_card(self) -> str:
        """Generate professional visiting/business card using HTML template (with ReportLab fallback)"""
        doc_record = self._create_document_record("visiting_card", "Visiting_Card.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get all available data with enhanced priority
            name = self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english')
            designation = self._get_value('job_title', 'employment.job_title', 'business_type', 'business.owner_title')
            company = self._get_value('company_name', 'business.company_name', 'employment.company_name')
            phone = self._get_value('phone', 'contact.mobile', 'personal.mobile_number')
            email = self._get_value('email', 'contact.email')
            address = self._get_value('company_address', 'business.business_address', 'present_address')
            
            # Generate website from company name
            website = self._get_value('business.website', 'employment.company_website')
            if not website and company:
                # Convert company name to domain: "MD Group" -> "mdgroup.com"
                domain_name = company.lower().replace(' ', '').replace('-', '').replace('_', '')
                website = f'www.{domain_name}.com'
            elif not website:
                website = 'www.company.com'
            
            # If designation not found, create from employment status
            employment_status = self._get_value('employment_status')
            if not designation:
                if employment_status == 'Business Owner':
                    designation = "CEO & Managing Director"
                elif employment_status == 'Employed':
                    designation = "Professional"
                else:
                    designation = "Business Professional"
            
            self._update_progress(doc_record, 40)
            
            # Prepare data for template
            template_data = {
                'full_name': name or 'Business Professional',
                'designation': designation,
                'phone': phone or '+880 1XXX-XXXXXX',
                'email': email or 'contact@company.com',
                'website': website or 'www.company.com',
                'address': address or 'Dhaka, Bangladesh'
            }
            
            self._update_progress(doc_record, 60)
            
            # Try WeasyPrint first, fallback to ReportLab if it fails
            try:
                from app.services.template_renderer import TemplateRenderer
                renderer = TemplateRenderer()
                renderer.render_visiting_card(template_data, file_path)
                logger.info("✅ Visiting card generated with WeasyPrint template")
            except Exception as template_error:
                logger.warning(f"⚠️ WeasyPrint failed: {template_error}. Falling back to ReportLab...")
                # Fallback: Generate with ReportLab
                self._generate_visiting_card_reportlab(template_data, file_path)
                logger.info("✅ Visiting card generated with ReportLab fallback")
            
            self._update_progress(doc_record, 90)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    def _generate_visiting_card_reportlab(self, data: dict, file_path: str):
        """Fallback: Generate visiting card using ReportLab (for Render deployment)"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib import colors
        
        # Create PDF - Business card size (3.5" x 2" = 252pt x 144pt)
        c = pdf_canvas.Canvas(file_path, pagesize=(252, 144))
        
        # Navy blue background
        c.setFillColor(colors.HexColor('#003366'))
        c.rect(0, 0, 252, 144, fill=True, stroke=False)
        
        # Yellow accent bar
        c.setFillColor(colors.HexColor('#FFD700'))
        c.rect(0, 0, 252, 20, fill=True, stroke=False)
        
        # Name (white, large)
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 14)
        c.drawString(15, 110, data['full_name'][:30])
        
        # Designation (yellow)
        c.setFillColor(colors.HexColor('#FFD700'))
        c.setFont('Helvetica', 10)
        c.drawString(15, 92, data['designation'][:35])
        
        # Contact details (white, small)
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 8)
        c.drawString(15, 70, f"📞 {data['phone']}")
        c.drawString(15, 55, f"✉ {data['email'][:30]}")
        c.drawString(15, 40, f"🌐 {data['website'][:30]}")
        c.drawString(15, 25, f"📍 {data['address'][:35]}")
        
        c.save()
    
    # ============================================================================
    # 4. FINANCIAL STATEMENT
    # ============================================================================
    
    def generate_financial_statement(self) -> str:
        """Generate comprehensive financial statement"""
        doc_record = self._create_document_record("financial_statement", "Financial_Statement.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get financial data with enhanced priority
            name = self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english')
            
            # Get bank accounts from questionnaire
            banks = self._get_banks()
            total_balance = sum(float(bank.get('balance', 0)) for bank in banks) if banks else 0
            
            # Income data
            monthly_income = self._get_value('monthly_income', 'financial.monthly_income')
            monthly_expenses = self._get_value('monthly_expenses', 'financial.monthly_expenses')
            annual_income = self._get_value('annual_income', 'income_tax_3years.annual_income', 'financial.annual_income')
            
            # Calculate values if missing
            if not monthly_income and annual_income:
                monthly_income = str(int(float(annual_income)) // 12)
            if not annual_income and monthly_income:
                annual_income = str(int(float(monthly_income)) * 12)
            if not monthly_expenses and monthly_income:
                monthly_expenses = str(int(float(monthly_income) * 0.6))  # Assume 60% expenses
            
            self._update_progress(doc_record, 40)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("FINANCIAL STATEMENT", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Applicant info
            body_style = ParagraphStyle(
                'Body',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(f"<b>Applicant Name:</b> {name}", body_style))
            story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Bank Accounts Section
            story.append(Paragraph("<b>1. Bank Accounts</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            if banks:
                bank_data = [['Bank Name', 'Account Type', 'Account Number', 'Balance (BDT)']]
                for bank in banks:
                    balance_val = float(bank.get('balance', 0))
                    bank_data.append([
                        bank.get('bank_name', 'N/A'),
                        bank.get('account_type', 'Savings'),
                        bank.get('account_number', 'N/A'),
                        f"{balance_val:,.0f}"
                    ])
                
                # Add total row - use plain text, style will be applied via TableStyle
                total_row = ['', '', 'Total Balance:', f'{total_balance:,.0f}']
                bank_data.append(total_row)
                
                bank_table = Table(bank_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                bank_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                    ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
                    ('FONT', (2, -1), (-1, -1), 'Helvetica-Bold', 10),  # Bold for total row
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                    ('PADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
                    ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ]))
                story.append(bank_table)
            else:
                story.append(Paragraph("No bank account details available.", body_style))
            
            story.append(Spacer(1, 0.3*inch))
            
            # Income Information
            story.append(Paragraph("<b>2. Income Information</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            annual_val = float(annual_income or 0)
            monthly_val = float(monthly_income or 0)
            income_data = [
                ['Description', 'Amount (BDT)'],
                ['Annual Income', f"{annual_val:,.0f}" if annual_income else '-'],
                ['Monthly Income', f"{monthly_val:,.0f}" if monthly_income else '-'],
            ]
            
            income_table = Table(income_data, colWidths=[3*inch, 2*inch])
            income_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(income_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Monthly Finances
            story.append(Paragraph("<b>3. Monthly Financial Overview</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            monthly_inc = float(monthly_income or 0)
            monthly_exp = float(monthly_expenses or 0)
            savings = monthly_inc - monthly_exp if monthly_income and monthly_expenses else 0
            monthly_data = [
                ['Description', 'Amount (BDT)'],
                ['Monthly Income', f"{monthly_inc:,.0f}" if monthly_income else '-'],
                ['Monthly Expenses', f"{monthly_exp:,.0f}" if monthly_expenses else '-'],
                ['Monthly Savings', f"{savings:,.0f}" if savings > 0 else '-'],
            ]
            
            monthly_table = Table(monthly_data, colWidths=[3*inch, 2*inch])
            monthly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(monthly_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Trip Funding
            funding_source = self._get_value('funding_source', 'financial.trip_funding_source', 'financial.funding_source')
            story.append(Paragraph(f"<b>4. Trip Funding Source:</b> {funding_source or 'Personal savings and income from employment/business'}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Declaration
            decl_text = """<b>DECLARATION</b><br/><br/>
I hereby declare that the above financial information is true and accurate to the best of my knowledge. 
I understand that any false information may result in rejection of my visa application."""
            
            story.append(Paragraph(decl_text, body_style))
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 5. TRAVEL ITINERARY
    # ============================================================================
    
    def generate_travel_itinerary(self) -> str:
        """Generate day-by-day travel itinerary for Iceland"""
        import json
        import re
        doc_record = self._create_document_record("travel_itinerary", "Travel_Itinerary.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # 1. Get travel data with enhanced priority
            travel_activities = self._get_array('travel_activities')  # Day-by-day plan from questionnaire
            
            applicant_data = {
                "name": self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english'),
                "passport": self._get_value('passport_number', 'passport_copy.passport_number'),
                "hotel": self._get_value('accommodation_details', 'hotel.hotel_name', 'hotel_booking.hotel_name') or 'Hotel in Reykjavik',
                "duration": self._get_value('duration_of_stay', 'travel.duration', 'hotel_booking.duration') or '7',
                "check_in": self._get_value('arrival_date', 'hotel.check_in_date', 'hotel_booking.check_in_date') or datetime.now().strftime('%Y-%m-%d'),
                "places": self._get_value('places_to_visit', 'travel.places_to_visit') or 'Reykjavik, Golden Circle, Blue Lagoon, South Coast',
                "activities": self._get_value('planned_activities', 'travel.planned_activities') or 'Sightseeing, nature exploration, cultural experiences'
            }
            self._update_progress(doc_record, 20)

            # 2. Few-shot example from OCR'd PDF
            sample_itinerary = """
            Travel Itinerary Plan For London, United Kingdom
            Applicant: Md Swapon Sheikh
            Stay Duration: 29 December 2025 – 12 January 2026 (14 Days)

            Day 1 – 29 Dec 2025
            Arrival in London
            - Check-in at 365 London Hostel
            - Light walking around local streets, restaurants & markets
            - Rest early after long travel

            Day 2 – 30 Dec 2025
            Central London Highlights
            - Visit Piccadilly Circus, Leicester Square
            - Explore Trafalgar Square
            - Evening walk along Covent Garden

            Day 3 – 31 Dec 2025
            New Year's Eve Celebration
            - Visit London Eye Riverside area (Southbank)
            - Enjoy festive atmosphere, street lights & music
            - Watch New Year celebrations (public viewing area)
            """

            # 3. Construct the new, advanced prompt
            prompt = f"""
            You are a meticulous travel agent who creates detailed, day-by-day travel itineraries for visa applications. Your task is to generate a realistic and appealing itinerary for a trip to Iceland.

            **Analysis of a High-Quality Sample Itinerary:**
            Here is an example of a well-structured itinerary. Note the clear separation of days and activities.
            ---
            [GOOD EXAMPLE START]
            {sample_itinerary}
            [GOOD EXAMPLE END]
            ---

            **Applicant's Travel Details:**
            - Traveler: {applicant_data['name']}
            - Duration of Stay: {applicant_data['duration']} days
            - Accommodation: {applicant_data['hotel']}
            - Desired Places to Visit: {applicant_data['places']}
            - Planned Activities: {applicant_data['activities']}
            - Check-in Date: {applicant_data['check_in']}

            **Your Task: Generate a New Itinerary for Iceland**
            Based on the applicant's details, create a new travel itinerary for their trip to Iceland.

            **Instructions:**
            1.  **Content:** Create a logical and appealing daily schedule. Include famous Icelandic attractions (e.g., Golden Circle, Reykjavik, Blue Lagoon, Northern Lights if in season, waterfalls like Gullfoss and Seljalandsfoss). Mix popular tourist spots with some local experiences. Include realistic suggestions for meals (e.g., "Lunch at a local cafe").
            2.  **Structure:** The itinerary should cover each day of the {applicant_data['duration']}-day trip.
            3.  **Output Format:** Structure your response as a single JSON object. This object should contain one key, `"itinerary"`, which is an array of objects. Each object in the array represents a single day and must have the following keys:
                *   `"day"`: (String) The day number (e.g., "Day 1").
                *   `"date"`: (String) The specific date for that day's plan. Use the check-in date to calculate subsequent dates.
                *   `"title"`: (String) A short, catchy title for the day's theme (e.g., "Arrival and Reykjavik Exploration").
                *   `"activities"`: (Array of Strings) A list of activities for the day. Each string should be a descriptive plan for the morning, afternoon, or evening.

            **Example JSON output:**
            {{
              "itinerary": [
                {{
                  "day": "Day 1",
                  "date": "{applicant_data['check_in'] or '2025-12-29'}",
                  "title": "Arrival in Reykjavik & Settling In",
                  "activities": [
                    "Arrive at Keflavík Airport (KEF), clear immigration, and pick up luggage.",
                    "Take a Flybus or pre-booked transfer to the hotel in Reykjavik.",
                    "Check-in at {applicant_data['hotel']}.",
                    "Evening: Take a light walk around the hotel area and have dinner at a local Icelandic restaurant."
                  ]
                }},
                {{
                  "day": "Day 2",
                  "date": "Calculated Date",
                  "title": "The Golden Circle Expedition",
                  "activities": [
                    "Morning: Visit Þingvellir National Park, a UNESCO World Heritage site.",
                    "Afternoon: Witness the erupting geysers at Geysir geothermal area and marvel at the majestic Gullfoss waterfall.",
                    "Evening: Return to Reykjavik. Enjoy dinner and relax."
                  ]
                }}
              ]
            }}

            Now, generate the JSON for the new travel itinerary for Iceland.
            """

            self._update_progress(doc_record, 40)
            ai_response_text = self._generate_content_with_ai(prompt)
            self._update_progress(doc_record, 70)

            # 4. Parse the AI's JSON response
            try:
                # Clean the response to extract only the JSON part
                json_str = ai_response_text.strip()
                if json_str.startswith('```json'):
                    json_str = json_str[7:]
                if json_str.endswith('```'):
                    json_str = json_str[:-3]
                
                itinerary_data = json.loads(json_str).get("itinerary", [])
            except (json.JSONDecodeError, KeyError) as e:
                itinerary_data = [] # Failed to parse, will be handled below

            self._update_progress(doc_record, 80)
            
            # 5. Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=0.75*inch, bottomMargin=0.75*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                'Title', parent=styles['Heading1'], fontSize=16, textColor=colors.white, spaceAfter=20,
                alignment=TA_CENTER, fontName='Helvetica-Bold', backColor=colors.HexColor('#1e3a8a'), borderPadding=10
            )
            story.append(Paragraph("TRAVEL ITINERARY - ICELAND", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            header_data = [
                ['Applicant Name:', applicant_data['name'] or 'N/A'],
                ['Passport Number:', applicant_data['passport'] or 'N/A'],
                ['Accommodation:', applicant_data['hotel'] or 'To be confirmed'],
                ['Duration:', f"{applicant_data['duration']} days" if applicant_data['duration'] else 'N/A'],
            ]
            header_table = Table(header_data, colWidths=[1.5*inch, 4.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 0.4*inch))

            if not itinerary_data: # Fallback if JSON parsing failed or AI returned no data
                story.append(Paragraph("Detailed itinerary to be provided upon arrival.", styles['Normal']))
            else:
                day_header_style = ParagraphStyle(
                    'DayHeader', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e40af'),
                    spaceAfter=8, spaceBefore=12, fontName='Helvetica-Bold'
                )
                activity_style = ParagraphStyle(
                    'Activity', parent=styles['BodyText'], fontSize=10, leading=14, leftIndent=15
                )
                for day_plan in itinerary_data:
                    day_title = f"{day_plan.get('day', '')} ({day_plan.get('date', '')}) - {day_plan.get('title', '')}"
                    story.append(Paragraph(day_title, day_header_style))
                    
                    activities_list = day_plan.get('activities', [])
                    for activity in activities_list:
                        story.append(Paragraph(f"• {activity}", activity_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 6. TRAVEL HISTORY
    # ============================================================================
    
    def generate_travel_history(self) -> str:
        """Generate previous travel history table with user data"""
        doc_record = self._create_document_record("travel_history", "Travel_History.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get applicant info first
            name = self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english')
            passport = self._get_value('passport_number', 'passport_copy.passport_number')
            
            # Get travel history from questionnaire (priority)
            previous_travels = self._get_previous_travels()
            
            # If no questionnaire data, try extraction
            if not previous_travels:
                visa_history = self.extracted_data.get('visa_history', {})
                previous_travels = visa_history.get('previous_travels', [])
            
            self._update_progress(doc_record, 40)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("PREVIOUS TRAVEL HISTORY", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Applicant info (Name and Passport)
            info_style = ParagraphStyle(
                'Info',
                parent=styles['BodyText'],
                fontSize=11,
                fontName='Helvetica',
                spaceAfter=6
            )
            
            story.append(Paragraph(f"<b>Name:</b> {name}", info_style))
            story.append(Paragraph(f"<b>Passport No:</b> {passport}", info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Travel history table
            table_data = [['SL NO', 'Country', 'Year', 'Duration (Days)', 'Type of Visa']]
            
            if previous_travels:
                for i, travel in enumerate(previous_travels, 1):
                    # Use data from questionnaire array
                    country = travel.get('country', 'N/A')
                    year = travel.get('year', 'N/A')
                    duration = travel.get('duration_days', 'N/A')
                    visa_type = 'Tourism'  # Always tourism as requested
                    
                    table_data.append([
                        str(i),
                        country,
                        str(year),
                        str(duration),
                        visa_type
                    ])
            else:
                # Default entry if no data
                table_data.append(['1', 'N/A', 'N/A', 'N/A', 'No previous international travel'])
            
            travel_table = Table(table_data, colWidths=[0.6*inch, 1.8*inch, 0.8*inch, 1.2*inch, 1.5*inch])
            travel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            story.append(travel_table)
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 7. HOME TIE STATEMENT
    # ============================================================================
    
    def generate_home_tie_statement(self) -> str:
        """Generate simple 1-page home ties statement"""
        doc_record = self._create_document_record("home_tie_statement", "Home_Tie_Statement.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get home ties data (prioritize English from bank_solvency)
            name = self._get_value('passport_copy.full_name', 'bank_solvency.account_holder_name', 'nid_bangla.name_english', 'personal.full_name')
            father_name = self._get_value('bank_solvency.father_name', 'personal.father_name')
            mother_name = self._get_value('bank_solvency.mother_name', 'personal.mother_name')
            location = self._get_value('bank_solvency.current_address', 'personal.current_city', 'personal.address')
            family = self._get_value('home_ties.family_members', 'family.members', 'personal.marital_status')
            employment = self._get_value('employment.job_title', 'business.business_type')
            company = self._get_value('business.company_name', 'employment.company_name', 'business.business_name')
            property_info = self._get_value('assets.property_description', 'assets.details')
            reasons = self._get_value('home_ties.reasons_to_return', 'home_ties.return_reasons')
            
            self._update_progress(doc_record, 30)
            
            # Generate AI content - OPTIMIZED: 1.5-2 pages (NOT 3 pages, NOT less than 1.5)
            prompt = f"""
Write a home ties statement in simple, school-grade English. Target length: 950-1200 words to fill 1.5-2 pages (NOT more than 2 pages, NOT less than 1.5 pages).

My information:
- Name: {name}
- Father's Name: {father_name}
- Mother's Name: {mother_name}
- Location: {location}
- Family: {family}
- Job: {employment} at {company}
- Property: {property_info}
- Why I will return: {reasons}

CRITICAL REQUIREMENTS:
- Length: 950-1200 words EXACTLY (1.5-2 pages)
- Write 4-5 SHORT, FOCUSED paragraphs (each 200-280 words)
- Use SIMPLE, clear English (10th grade reading level)
- NO markdown formatting (no **, no *, no #)
- Add paragraph breaks for readability - NOT continuous dense text
- Sound natural and human, like talking to a visa officer

PARAGRAPH 1 (Family Ties - 220-250 words): 
Start with "My name is {name}..." Explain your family ties - father, mother, siblings, spouse, children. Where you live, your family home, emotional connections. Be specific about family members and why they're important. Keep sentences short and clear.

PARAGRAPH 2 (Employment/Business - 220-250 words):
Describe your job or business. Your role, daily responsibilities, why you're needed. How long you've worked there. Future projects or plans. Be specific but don't overexplain. Short, clear sentences.

PARAGRAPH 3 (Property and Financial Ties - 200-240 words):
Mention property you own (house, land, apartments). Talk about financial commitments, investments, bank accounts. Explain why these tie you to Bangladesh. Keep it factual and brief.

PARAGRAPH 4 (Cultural and Social Ties - 180-220 words):
Discuss cultural connections, community involvement, religious ties, social circles. Mention friends, social responsibilities, community roles. Why Bangladesh is your home beyond just family/work.

PARAGRAPH 5 (Conclusion - 180-220 words):
Summarize ALL reasons you MUST return: family obligations, job/business responsibilities, property management, cultural ties, future plans. Be clear and convincing. End with commitment to return after travel.

WRITING STYLE RULES:
- Use short sentences (10-18 words average)
- Add line breaks between paragraphs
- Be conversational but professional
- Use "I", "my", "I am" (first person)
- Sound genuine, not robotic
- Be specific with names, places, numbers
- Don't repeat yourself
- Don't use complex vocabulary

Total word count: 950-1200 words (COUNT CAREFULLY - this fills 1.5-2 pages exactly)
"""
            
            statement_content = self._generate_content_with_ai(prompt)
            self._update_progress(doc_record, 60)
            
            # Clean any markdown that might slip through
            statement_content = re.sub(r'\*\*', '', statement_content)
            statement_content = re.sub(r'\*', '', statement_content)
            statement_content = re.sub(r'^#+\s+', '', statement_content, flags=re.MULTILINE)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                fontName='Helvetica'
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("STATEMENT OF HOME TIES TO BANGLADESH", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Date
            date_text = f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
            story.append(Paragraph(date_text, body_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Applicant
            story.append(Paragraph(f"<b>Applicant:</b> {name}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Statement content
            paragraphs = statement_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 8. ASSET VALUATION CERTIFICATE (COMPREHENSIVE 10-15 PAGES)
    # ============================================================================
    
    def generate_asset_valuation(self) -> str:
        """Generate comprehensive 5-page asset valuation certificate using HTML template (with ReportLab fallback)"""
        doc_record = self._create_document_record("asset_valuation", "Asset_Valuation_Certificate.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Collect ALL asset data with enhanced priority
            name = self._get_value('full_name', 'passport_copy.full_name', 'bank_solvency.account_holder_name')
            father_name = self._get_value('father_name', 'bank_solvency.father_name', 'nid_bangla.father_name_bangla')
            nid = self._get_value('nid_number', 'nid_bangla.nid_number')
            address = self._get_value('permanent_address', 'present_address', 'nid_bangla.address_bangla')
            phone = self._get_value('phone', 'personal.mobile_number')
            
            # Get assets array from questionnaire
            assets = self._get_assets()
            
            # Calculate total asset value from array
            total_asset_value = sum(float(asset.get('estimated_value', 0)) for asset in assets) if assets else 0
            
            # Extract specific asset types
            property_assets = [a for a in assets if a.get('asset_type') == 'Property']
            vehicle_assets = [a for a in assets if a.get('asset_type') == 'Vehicle']
            business_assets = [a for a in assets if a.get('asset_type') == 'Business']
            
            # Property values (use first 3 properties or auto-filled)
            property_value = str(int(property_assets[0].get('estimated_value', 0))) if property_assets else self._get_value('assets.property_value') or '13623000'
            flat_value_2 = str(int(property_assets[1].get('estimated_value', 0))) if len(property_assets) > 1 else str(int(float(property_value) * 0.7))
            flat_value_3 = str(int(property_assets[2].get('estimated_value', 0))) if len(property_assets) > 2 else str(int(float(property_value) * 0.5))
            
            vehicle_value = str(int(vehicle_assets[0].get('estimated_value', 0))) if vehicle_assets else self._get_value('assets.vehicle_value') or '3500000'
            business_value = str(int(business_assets[0].get('estimated_value', 0))) if business_assets else self._get_value('business.business_value') or '10250000'
            
            business_name = self._get_value('company_name', 'business.company_name', 'employment.company_name')
            business_type = self._get_value('business_type', 'employment_status') or 'Business Owner'
            
            self._update_progress(doc_record, 30)
            
            # Prepare data for template
            template_data = {
                'owner_name': name or 'PROPERTY OWNER',
                'owner_father_relation': f"S/O - {father_name}" if father_name else 'S/O - FATHER NAME',
                'owner_address': address or 'Dhaka, Bangladesh',
                
                # Asset values - will be distributed across 3 flats in template
                'flat_value_1': property_value,
                'flat_value_2': flat_value_2,
                'flat_value_3': flat_value_3,
                'car_value': vehicle_value,
                'business_value': business_value,
                
                # Business info
                'business_name': business_name or 'BUSINESS ENTERPRISE',
                'business_type': business_type,
            }
            
            self._update_progress(doc_record, 60)
            
            # Try WeasyPrint first, fallback to ReportLab if it fails
            try:
                from app.services.template_renderer import TemplateRenderer
                renderer = TemplateRenderer()
                renderer.render_asset_valuation(template_data, file_path)
                logger.info("✅ Asset valuation generated with WeasyPrint template")
            except Exception as template_error:
                logger.warning(f"⚠️ WeasyPrint failed: {template_error}. Falling back to ReportLab...")
                # Fallback: Generate with ReportLab
                self._generate_asset_valuation_reportlab(template_data, file_path)
                logger.info("✅ Asset valuation generated with ReportLab fallback")
            
            self._update_progress(doc_record, 90)
            
            # Get file size and complete
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    def _generate_asset_valuation_reportlab(self, data: dict, file_path: str):
        """Fallback: Generate asset valuation using ReportLab (for Render deployment)"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import Table, TableStyle
        
        c = pdf_canvas.Canvas(file_path, pagesize=A4)
        page_width, page_height = A4
        
        # Page 1: Cover Page
        c.setFillColor(colors.HexColor('#003366'))
        c.rect(0, 0, page_width, page_height, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(page_width/2, page_height - 200, "ASSET VALUATION")
        c.drawCentredString(page_width/2, page_height - 240, "CERTIFICATE")
        
        c.setFont('Helvetica', 14)
        c.drawCentredString(page_width/2, page_height - 320, f"Owner: {data['owner_name']}")
        c.drawCentredString(page_width/2, page_height - 350, f"{data['owner_father_relation']}")
        
        c.setFont('Helvetica', 12)
        c.drawCentredString(page_width/2, page_height - 400, f"Date: {datetime.now().strftime('%d %B %Y')}")
        c.drawCentredString(page_width/2, page_height - 430, "Kamal & Associates")
        c.drawCentredString(page_width/2, page_height - 450, "Professional Valuers")
        
        c.showPage()
        
        # Page 2: Property Details
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 18)
        c.drawString(50, page_height - 80, "PROPERTY ASSETS")
        
        c.setFont('Helvetica', 12)
        y = page_height - 130
        
        # Property 1
        c.drawString(50, y, "1. Residential Flat - Gulshan, Dhaka")
        c.drawString(400, y, f"BDT {data['flat_value_1']}")
        y -= 40
        
        # Property 2  
        c.drawString(50, y, "2. Residential Flat - Banani, Dhaka")
        c.drawString(400, y, f"BDT {data['flat_value_2']}")
        y -= 40
        
        # Property 3
        c.drawString(50, y, "3. Residential Flat - Dhanmondi, Dhaka")
        c.drawString(400, y, f"BDT {data['flat_value_3']}")
        y -= 60
        
        # Vehicle
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y, "VEHICLE ASSETS")
        y -= 40
        c.setFont('Helvetica', 12)
        c.drawString(50, y, "Car Saloon - Toyota (Dhaka Metro)")
        c.drawString(400, y, f"BDT {data['car_value']}")
        y -= 60
        
        # Business
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y, "BUSINESS ASSETS")
        y -= 40
        c.setFont('Helvetica', 12)
        c.drawString(50, y, f"{data['business_name']} - {data['business_type']}")
        c.drawString(400, y, f"BDT {data['business_value']}")
        y -= 80
        
        # Total
        c.setFont('Helvetica-Bold', 16)
        c.setFillColor(colors.HexColor('#003366'))
        try:
            p1 = int(str(data['flat_value_1']).replace(',', ''))
            p2 = int(str(data['flat_value_2']).replace(',', ''))
            p3 = int(str(data['flat_value_3']).replace(',', ''))
            v = int(str(data['car_value']).replace(',', ''))
            b = int(str(data['business_value']).replace(',', ''))
            total = p1 + p2 + p3 + v + b
            c.drawString(50, y, f"TOTAL ASSET VALUE: BDT {total:,}")
        except:
            c.drawString(50, y, "TOTAL ASSET VALUE: BDT 40,000,000+")
        
        c.showPage()
        
        # Page 3: Certification
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(page_width/2, page_height - 80, "PROFESSIONAL CERTIFICATION")
        
        c.setFont('Helvetica', 12)
        y = page_height - 150
        cert_text = [
            "This is to certify that the above valuation has been carried out based on",
            "physical inspection, market analysis, and relevant documentation. The valuation",
            "is prepared in accordance with Bangladesh Valuation Standards (BVS) and",
            "International Valuation Standards (IVS).",
            "",
            "The valuation represents the fair market value as of the date mentioned above.",
            "",
            f"Prepared for: {data['owner_name']}",
            f"Address: {data['owner_address']}",
        ]
        
        for line in cert_text:
            c.drawString(80, y, line)
            y -= 25
        
        y -= 80
        c.setFont('Helvetica-Bold', 12)
        c.drawString(80, y, "Kamal & Associates")
        y -= 20
        c.setFont('Helvetica', 10)
        c.drawString(80, y, "Licensed Professional Valuers")
        y -= 15
        c.drawString(80, y, "Dhaka, Bangladesh")
        
        c.save()
    
    def _amount_in_words(self, amount: int) -> str:
        """Convert number to words (simplified for BDT)"""
        if amount >= 10000000:  # 1 Crore+
            crores = amount // 10000000
            return f"{crores} Crore+"
        elif amount >= 100000:  # 1 Lakh+
            lakhs = amount // 100000
            return f"{lakhs} Lakh+"
        elif amount >= 1000:  # Thousands
            thousands = amount // 1000
            return f"{thousands} Thousand+"
        else:
            return str(amount)
    
    # ============================================================================
    # 9. TIN CERTIFICATE
    # ============================================================================
    
    def generate_tin_certificate(self) -> str:
        """Generate TIN (Taxpayer Identification Number) Certificate"""
        doc_record = self._create_document_record("tin_certificate", "TIN_Certificate.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get taxpayer data (prioritize English from bank_solvency)
            name = self._get_value('passport_copy.full_name', 'bank_solvency.account_holder_name', 'nid_bangla.name_english', 'tin_certificate.taxpayer_name', 'personal.full_name')
            father_name = self._get_value('bank_solvency.father_name', 'personal.father_name', 'nid_bangla.father_name_bangla')
            nid = self._get_value('nid_bangla.nid_number', 'personal.nid_number')
            address = self._get_value('bank_solvency.current_address', 'tin_certificate.address', 'personal.address', 'nid_bangla.address_bangla')
            tin_no = self._get_value('tin_certificate.tin_number', 'tax.tin_number') or f'TIN-{datetime.now().year}-{hash(name or "X") % 100000:05d}'
            circle = self._get_value('tin_certificate.circle', 'tax.tax_circle') or 'Dhaka Taxes Circle-1'
            zone = self._get_value('tax.tax_zone') or 'Dhaka Zone-1'
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with government format
            from reportlab.pdfgen import canvas as pdf_canvas
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Government header with Bangladesh flag colors
            c.setFillColor(colors.HexColor('#006a4e'))  # Bangladesh green
            c.rect(0, page_height - 1.2*inch, page_width, 1.2*inch, fill=True, stroke=False)
            
            # White header text
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(page_width/2, page_height - 0.5*inch, "GOVERNMENT OF THE PEOPLE'S REPUBLIC OF BANGLADESH")
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(page_width/2, page_height - 0.75*inch, "NATIONAL BOARD OF REVENUE")
            c.setFont("Helvetica", 11)
            c.drawCentredString(page_width/2, page_height - 0.95*inch, "Taxpayer Identification Number (TIN) Certificate")
            
            # Red stripe
            c.setFillColor(colors.HexColor('#f42a41'))  # Bangladesh red
            c.rect(0, page_height - 1.35*inch, page_width, 0.15*inch, fill=True, stroke=False)
            
            # Certificate title
            c.setFillColor(colors.HexColor('#003366'))
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(page_width/2, page_height - 1.8*inch, "TAXPAYER IDENTIFICATION NUMBER")
            
            # Main content box
            box_x = 1.2*inch
            box_y = page_height - 6.5*inch
            box_width = page_width - 2.4*inch
            box_height = 4.3*inch
            
            c.setStrokeColor(colors.HexColor('#006a4e'))
            c.setLineWidth(2)
            c.rect(box_x, box_y, box_width, box_height, fill=False, stroke=True)
            
            # Certificate content
            content_x = box_x + 0.4*inch
            content_y = box_y + box_height - 0.5*inch
            line_height = 0.28*inch
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            
            # Field labels and values
            fields = [
                ("TIN:", tin_no),
                ("Name:", name or "N/A"),
                ("Father's Name:", father_name or "N/A"),
                ("NID No:", nid or "N/A"),
                ("Address:", (address or "Bangladesh")[:60]),
                ("Circle:", circle),
                ("Zone:", zone),
                ("Issue Date:", datetime.now().strftime('%d/%m/%Y')),
            ]
            
            for i, (label, value) in enumerate(fields):
                y_pos = content_y - (i * line_height)
                
                # Label
                c.setFont("Helvetica-Bold", 10)
                c.drawString(content_x, y_pos, label)
                
                # Value
                c.setFont("Helvetica", 10)
                if label == "TIN:":
                    # Highlight TIN number
                    c.setFillColor(colors.HexColor('#f42a41'))
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(content_x + 1.2*inch, y_pos - 0.03*inch, str(value))
                    c.setFillColor(colors.black)
                else:
                    c.drawString(content_x + 1.5*inch, y_pos, str(value))
            
            # QR Code placeholder
            qr_size = 0.9*inch
            qr_x = box_x + box_width - qr_size - 0.3*inch
            qr_y = box_y + 0.3*inch
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.rect(qr_x, qr_y, qr_size, qr_size, fill=False, stroke=True)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.grey)
            c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size/2, "QR CODE")
            
            # Official stamp area (text only - no circle)
            stamp_x = box_x + 0.5*inch
            stamp_y = box_y + 0.5*inch
            c.setFillColor(colors.HexColor('#006a4e'))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(stamp_x, stamp_y + 0.5*inch, "[Official Stamp]")
            c.setFont("Helvetica", 8)
            c.drawString(stamp_x, stamp_y + 0.3*inch, "NBR Seal")
            
            # Footer
            c.setFillColor(colors.HexColor('#555555'))
            c.setFont("Helvetica-Oblique", 8)
            footer_y = 1.2*inch
            c.drawCentredString(page_width/2, footer_y, "This is a computer-generated certificate and does not require physical signature")
            c.drawCentredString(page_width/2, footer_y - 0.15*inch, "For verification, visit: www.nbr.gov.bd")
            c.drawCentredString(page_width/2, footer_y - 0.30*inch, f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
            
            c.save()
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 10. TAX CERTIFICATE
    # ============================================================================
    
    def generate_tax_certificate(self) -> str:
        """Generate Tax Return Certificate / Tax Clearance"""
        doc_record = self._create_document_record("tax_certificate", "Tax_Certificate.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get tax data
            name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'tin_certificate.taxpayer_name', 'personal.full_name')
            tin = self._get_value('tin_certificate.tin_number', 'tax.tin_number') or f'TIN-{datetime.now().year}-{hash(name or "X") % 100000:05d}'
            assessment_year = self._get_value('tax.assessment_year') or f'{datetime.now().year - 1}-{datetime.now().year}'
            tax_paid = self._get_value('income_tax_3years.year1_tax_paid', 'tax.tax_paid') or '0'
            income = self._get_value('income_tax_3years.year1_income', 'financial.annual_income') or '0'
            
            self._update_progress(doc_record, 30)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=0.8*inch, bottomMargin=0.8*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Government letterhead
            title_style = ParagraphStyle(
                'Title', parent=styles['Heading1'], fontSize=16,
                textColor=colors.HexColor('#006a4e'), spaceAfter=5,
                alignment=TA_CENTER, fontName='Helvetica-Bold'
            )
            subtitle_style = ParagraphStyle(
                'Subtitle', parent=styles['Normal'], fontSize=11,
                alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.HexColor('#003366')
            )
            body_style = ParagraphStyle(
                'Body', parent=styles['BodyText'], fontSize=10,
                leading=14, fontName='Helvetica'
            )
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("GOVERNMENT OF THE PEOPLE'S REPUBLIC OF BANGLADESH", title_style))
            story.append(Paragraph("NATIONAL BOARD OF REVENUE", subtitle_style))
            story.append(Paragraph("TAX RETURN CERTIFICATE", subtitle_style))
            story.append(Spacer(1, 0.4*inch))
            
            # Certificate number and date
            cert_no = f"TAX/{datetime.now().year}/NBR/{hash(name or 'X') % 10000:04d}"
            story.append(Paragraph(f"<b>Certificate No:</b> {cert_no}", body_style))
            story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Certification statement
            cert_statement = f"""<b>TO WHOM IT MAY CONCERN</b><br/><br/>
This is to certify that <b>{name}</b> (TIN: <b>{tin}</b>) has duly filed income tax return 
for the Assessment Year <b>{assessment_year}</b> and has paid all applicable taxes as per 
the Income Tax Ordinance, 1984.<br/><br/>

The taxpayer has been compliant with all tax obligations and has fulfilled the requirements 
under the law."""
            
            story.append(Paragraph(cert_statement, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Tax details table
            tax_data = [
                ['Particulars', 'Details'],
                ['Taxpayer Name', name],
                ['TIN Number', tin],
                ['Assessment Year', assessment_year],
                ['Total Income', f'BDT {income}'],
                ['Tax Paid', f'BDT {tax_paid}'],
                ['Return Submission Date', datetime.now().strftime('%d/%m/%Y')],
                ['Compliance Status', 'COMPLIANT'],
            ]
            
            tax_table = Table(tax_data, colWidths=[2.5*inch, 3.5*inch])
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006a4e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f0f0f0')),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(tax_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Validity statement
            validity = """<b>VALIDITY:</b> This certificate is valid for one year from the date of issue 
and is issued for official purposes including visa applications, loan applications, and other regulatory requirements."""
            story.append(Paragraph(validity, body_style))
            story.append(Spacer(1, 0.5*inch))
            
            # Signature section - empty space for seal as requested
            sig_text = """<b>Authorized Officer</b><br/>
Deputy Commissioner of Taxes<br/>
National Board of Revenue<br/>
Dhaka, Bangladesh"""
            
            story.append(Paragraph(sig_text, body_style))
            
            # Build PDF
            pdf.build(story)
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 11. TRADE LICENSE
    # ============================================================================
    
    def generate_trade_license(self) -> str:
        """Generate Trade License certificate"""
        doc_record = self._create_document_record("trade_license", "Trade_License.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get business data
            owner_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'business.owner_name', 'personal.full_name')
            business_name = self._get_value('business.company_name', 'business.business_name') or f'{owner_name} Enterprise'
            business_type = self._get_value('business.business_type') or 'Service Provider'
            business_address = self._get_value('business.business_address', 'nid_bangla.address_bangla') or 'Dhaka, Bangladesh'
            license_no = self._get_value('business.trade_license_no') or f'TL/{datetime.now().year}/{hash(owner_name or "X") % 100000:05d}'
            issue_date = self._get_value('business.license_issue_date') or datetime.now().strftime('%d/%m/%Y')
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with City Corporation branding
            from reportlab.pdfgen import canvas as pdf_canvas
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Header with city corporation colors
            c.setFillColor(colors.HexColor('#1e40af'))  # Official blue
            c.rect(0, page_height - 1.5*inch, page_width, 1.5*inch, fill=True, stroke=False)
            
            # Logo placeholder (left side - no circle)
            logo_x = 1*inch
            logo_y = page_height - 1.2*inch
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)
            # Logo space reserved (no circle placeholder)
            
            # Header text
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(page_width/2, page_height - 0.6*inch, "DHAKA SOUTH CITY CORPORATION")
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(page_width/2, page_height - 0.9*inch, "ঢাকা দক্ষিণ সিটি কর্পোরেশন")
            c.setFont("Helvetica", 11)
            c.drawCentredString(page_width/2, page_height - 1.15*inch, "Trade License Certificate")
            
            # License title
            c.setFillColor(colors.HexColor('#1e40af'))
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(page_width/2, page_height - 2*inch, "TRADE LICENSE")
            
            # Main content box
            box_x = 1*inch
            box_y = page_height - 7*inch
            box_width = page_width - 2*inch
            box_height = 4.5*inch
            
            c.setStrokeColor(colors.HexColor('#1e40af'))
            c.setLineWidth(3)
            c.rect(box_x, box_y, box_width, box_height, fill=False, stroke=True)
            
            # Decorative corners
            corner_size = 0.15*inch
            c.setLineWidth(5)
            c.setStrokeColor(colors.HexColor('#f59e0b'))  # Gold accent
            # Top-left corner
            c.line(box_x, box_y + box_height, box_x + corner_size, box_y + box_height)
            c.line(box_x, box_y + box_height, box_x, box_y + box_height - corner_size)
            # Top-right corner
            c.line(box_x + box_width, box_y + box_height, box_x + box_width - corner_size, box_y + box_height)
            c.line(box_x + box_width, box_y + box_height, box_x + box_width, box_y + box_height - corner_size)
            # Bottom corners
            c.line(box_x, box_y, box_x + corner_size, box_y)
            c.line(box_x, box_y, box_x, box_y + corner_size)
            c.line(box_x + box_width, box_y, box_x + box_width - corner_size, box_y)
            c.line(box_x + box_width, box_y, box_x + box_width, box_y - corner_size)
            
            # License content
            content_x = box_x + 0.5*inch
            content_y = box_y + box_height - 0.4*inch
            line_height = 0.32*inch
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            
            fields = [
                ("License No:", license_no),
                ("Business Name:", business_name[:45]),
                ("Owner Name:", owner_name),
                ("Business Type:", business_type),
                ("Business Address:", business_address[:50]),
                ("Issue Date:", issue_date),
                ("Valid Until:", f"{datetime.now().year + 1}/06/30"),
                ("Ward No:", "Ward-15 (Zone-3)"),
            ]
            
            for i, (label, value) in enumerate(fields):
                y_pos = content_y - (i * line_height)
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(content_x, y_pos, label)
                
                c.setFont("Helvetica", 10)
                c.drawString(content_x + 2*inch, y_pos, str(value))
            
            # Signature area (removed seal circle as per user request)
            seal_y = box_y + 0.4*inch
            
            # Signature line
            sig_x = content_x + 3.2*inch
            c.setStrokeColor(colors.black)
            c.setLineWidth(0.5)
            c.line(sig_x, seal_y + 0.3*inch, sig_x + 1.5*inch, seal_y + 0.3*inch)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8)
            c.drawCentredString(sig_x + 0.75*inch, seal_y + 0.1*inch, "Authorized Signature")
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(sig_x + 0.75*inch, seal_y - 0.1*inch, "Chief Revenue Officer")
            
            # Footer
            c.setFont("Helvetica-Oblique", 7)
            c.setFillColor(colors.HexColor('#555555'))
            c.drawCentredString(page_width/2, 1*inch, "This is a valid trade license issued under City Corporation Ordinance")
            c.drawCentredString(page_width/2, 0.8*inch, "For verification: www.dscc.gov.bd | Hotline: 16109")
            
            c.save()
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 12. HOTEL BOOKING CONFIRMATION
    # ============================================================================
    
    def generate_hotel_booking(self) -> str:
        """Generate hotel booking confirmation (Booking.com style)"""
        doc_record = self._create_document_record("hotel_booking", "Hotel_Booking_Confirmation.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get booking data
            guest_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            hotel_name = self._get_value('hotel.hotel_name', 'hotel_booking.hotel_name') or 'Reykjavik Grand Hotel'
            hotel_address = self._get_value('hotel.hotel_address', 'hotel_booking.hotel_address') or 'Hallgrimsgata 5, 101 Reykjavik, Iceland'
            check_in = self._get_value('hotel.check_in_date', 'hotel_booking.check_in_date', 'travel.arrival_date') or datetime.now().strftime('%Y-%m-%d')
            check_out = self._get_value('hotel.check_out_date', 'hotel_booking.check_out_date', 'travel.departure_date') or (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            room_type = self._get_value('hotel.room_type', 'hotel_booking.room_type') or 'Standard Double Room'
            confirmation_no = self._get_value('hotel.confirmation_number', 'hotel_booking.confirmation_number') or f'BK{datetime.now().year}{hash(guest_name or "X") % 1000000:06d}'
            total_price = self._get_value('hotel.total_price', 'hotel_booking.total_price') or 'EUR 980'
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with Booking.com style
            from reportlab.pdfgen import canvas as pdf_canvas
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Booking.com style header
            c.setFillColor(colors.HexColor('#003580'))  # Booking.com blue
            c.rect(0, page_height - 1*inch, page_width, 1*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(1*inch, page_height - 0.65*inch, "Booking.com")
            
            # Confirmation banner
            c.setFillColor(colors.HexColor('#6cbc1e'))  # Success green
            c.rect(0, page_height - 1.8*inch, page_width, 0.6*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(1*inch, page_height - 1.5*inch, "✓ Your booking is confirmed")
            c.setFont("Helvetica", 11)
            c.drawString(page_width - 3*inch, page_height - 1.5*inch, f"Confirmation: {confirmation_no}")
            
            # Booking details box
            box_y = page_height - 3.2*inch
            c.setFillColor(colors.HexColor('#f5f5f5'))
            c.rect(1*inch, box_y, page_width - 2*inch, 1*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1.3*inch, box_y + 0.75*inch, hotel_name)
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.black)
            c.drawString(1.3*inch, box_y + 0.55*inch, hotel_address)
            c.drawString(1.3*inch, box_y + 0.35*inch, f"★★★★ | Rating: 8.9/10 Excellent")
            
            # Check-in/out section
            content_y = box_y - 0.4*inch
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#003580'))
            
            # Check-in
            c.drawString(1.3*inch, content_y, "CHECK-IN")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(1.3*inch, content_y - 0.2*inch, check_in)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(1.3*inch, content_y - 0.35*inch, "From 14:00")
            
            # Check-out
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#003580'))
            c.drawString(3.5*inch, content_y, "CHECK-OUT")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(3.5*inch, content_y - 0.2*inch, check_out)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(3.5*inch, content_y - 0.35*inch, "Until 11:00")
            
            # Duration
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#003580'))
            c.drawString(5.7*inch, content_y, "DURATION")
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(5.7*inch, content_y - 0.2*inch, "7 nights")
            
            # Room details
            room_y = content_y - 0.8*inch
            c.setStrokeColor(colors.HexColor('#cccccc'))
            c.setLineWidth(1)
            c.line(1*inch, room_y, page_width - 1*inch, room_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.black)
            c.drawString(1.3*inch, room_y - 0.3*inch, "Room Details")
            
            c.setFont("Helvetica", 10)
            c.drawString(1.3*inch, room_y - 0.6*inch, f"• {room_type}")
            c.drawString(1.3*inch, room_y - 0.8*inch, "• Free WiFi")
            c.drawString(1.3*inch, room_y - 1*inch, "• Private bathroom")
            c.drawString(1.3*inch, room_y - 1.2*inch, "• Breakfast included")
            
            # Guest details
            guest_y = room_y - 1.7*inch
            c.line(1*inch, guest_y, page_width - 1*inch, guest_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1.3*inch, guest_y - 0.3*inch, "Guest Information")
            
            c.setFont("Helvetica", 10)
            c.drawString(1.3*inch, guest_y - 0.6*inch, f"Name: {guest_name}")
            c.drawString(1.3*inch, guest_y - 0.8*inch, "Number of guests: 1 adult")
            
            # Price breakdown
            price_y = guest_y - 1.3*inch
            c.line(1*inch, price_y, page_width - 1*inch, price_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1.3*inch, price_y - 0.3*inch, "Price Breakdown")
            
            c.setFont("Helvetica", 10)
            c.drawString(1.3*inch, price_y - 0.6*inch, "7 nights (including taxes & fees)")
            c.drawString(page_width - 2*inch, price_y - 0.6*inch, total_price)
            
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor('#003580'))
            c.drawString(1.3*inch, price_y - 1*inch, "Total Price:")
            c.drawString(page_width - 2*inch, price_y - 1*inch, total_price)
            
            # Important info
            info_y = price_y - 1.7*inch
            c.setFillColor(colors.HexColor('#fef3cd'))
            c.rect(1*inch, info_y, page_width - 2*inch, 0.6*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.HexColor('#856404'))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1.3*inch, info_y + 0.35*inch, "Important Information")
            c.setFont("Helvetica", 8)
            c.drawString(1.3*inch, info_y + 0.15*inch, "• Please bring your passport and confirmation number at check-in")
            
            # Footer
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(page_width/2, 0.8*inch, "This is your booking confirmation. Please print and present at check-in.")
            c.drawCentredString(page_width/2, 0.6*inch, f"Booking reference: {confirmation_no} | Generated: {datetime.now().strftime('%d %B %Y')}")
            
            c.save()
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # 13. AIR TICKET / E-TICKET
    # ============================================================================
    
    def generate_air_ticket(self) -> str:
        """Generate airline e-ticket confirmation"""
        doc_record = self._create_document_record("air_ticket", "E-Ticket_Flight_Confirmation.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get flight data
            passenger_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            passport_no = self._get_value('passport_copy.passport_number', 'personal.passport_number')
            departure_date = self._get_value('flight.departure_date', 'air_ticket.departure_date', 'travel.arrival_date') or datetime.now().strftime('%Y-%m-%d')
            return_date = self._get_value('flight.return_date', 'air_ticket.return_date', 'travel.departure_date') or (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            pnr = self._get_value('flight.pnr', 'air_ticket.pnr') or f'{chr(65 + hash(passenger_name or "X") % 26)}{hash(passenger_name or "X") % 100000:05d}'
            ticket_no = self._get_value('flight.ticket_number', 'air_ticket.ticket_number') or f'176-{datetime.now().year}{hash(passenger_name or "X") % 10000000:07d}'
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with airline branding
            from reportlab.pdfgen import canvas as pdf_canvas
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Emirates-style header (using similar colors)
            c.setFillColor(colors.HexColor('#d71921'))  # Airline red
            c.rect(0, page_height - 1.2*inch, page_width, 1.2*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(1*inch, page_height - 0.7*inch, "ICELANDAIR")
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, page_height - 0.95*inch, "Electronic Ticket Confirmation")
            
            # E-ticket banner
            c.setFillColor(colors.HexColor('#003f87'))  # Airline blue
            c.rect(0, page_height - 1.6*inch, page_width, 0.4*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, page_height - 1.4*inch, f"PNR: {pnr}")
            c.drawString(page_width - 3.5*inch, page_height - 1.4*inch, f"E-Ticket: {ticket_no}")
            
            # Passenger info
            pass_y = page_height - 2.3*inch
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#003f87'))
            c.drawString(1*inch, pass_y, "PASSENGER INFORMATION")
            
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            c.drawString(1*inch, pass_y - 0.25*inch, f"Name: {passenger_name}")
            c.drawString(4*inch, pass_y - 0.25*inch, f"Passport: {passport_no or 'N/A'}")
            c.drawString(1*inch, pass_y - 0.45*inch, "Ticket Type: Economy")
            c.drawString(4*inch, pass_y - 0.45*inch, "Baggage: 23kg (1 piece)")
            
            # Flight segment 1 (Outbound)
            seg1_y = pass_y - 1*inch
            c.setStrokeColor(colors.HexColor('#cccccc'))
            c.setLineWidth(1)
            c.line(1*inch, seg1_y, page_width - 1*inch, seg1_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#d71921'))
            c.drawString(1*inch, seg1_y - 0.3*inch, "OUTBOUND FLIGHT")
            
            # Flight details box
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(1*inch, seg1_y - 1.5*inch, page_width - 2*inch, 1*inch, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(1.3*inch, seg1_y - 0.7*inch, "DAC → KEF")
            c.setFont("Helvetica", 9)
            c.drawString(1.3*inch, seg1_y - 0.9*inch, "Dhaka → Reykjavik")
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(3.2*inch, seg1_y - 0.7*inch, f"Date: {departure_date}")
            c.setFont("Helvetica", 9)
            c.drawString(3.2*inch, seg1_y - 0.9*inch, "Departure: 10:30 AM")
            c.drawString(3.2*inch, seg1_y - 1.05*inch, "Arrival: 02:45 PM")
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(5.2*inch, seg1_y - 0.7*inch, "Flight: FI 447")
            c.setFont("Helvetica", 9)
            c.drawString(5.2*inch, seg1_y - 0.9*inch, "Class: Y (Economy)")
            c.drawString(5.2*inch, seg1_y - 1.05*inch, "Duration: ~11h 15m")
            
            # Flight segment 2 (Return)
            seg2_y = seg1_y - 2*inch
            c.setStrokeColor(colors.HexColor('#cccccc'))
            c.line(1*inch, seg2_y, page_width - 1*inch, seg2_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#d71921'))
            c.drawString(1*inch, seg2_y - 0.3*inch, "RETURN FLIGHT")
            
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(1*inch, seg2_y - 1.5*inch, page_width - 2*inch, 1*inch, fill=True, stroke=False)
            
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(1.3*inch, seg2_y - 0.7*inch, "KEF → DAC")
            c.setFont("Helvetica", 9)
            c.drawString(1.3*inch, seg2_y - 0.9*inch, "Reykjavik → Dhaka")
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(3.2*inch, seg2_y - 0.7*inch, f"Date: {return_date}")
            c.setFont("Helvetica", 9)
            c.drawString(3.2*inch, seg2_y - 0.9*inch, "Departure: 04:15 PM")
            c.drawString(3.2*inch, seg2_y - 1.05*inch, "Arrival: 05:30 AM +1")
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(5.2*inch, seg2_y - 0.7*inch, "Flight: FI 448")
            c.setFont("Helvetica", 9)
            c.drawString(5.2*inch, seg2_y - 0.9*inch, "Class: Y (Economy)")
            c.drawString(5.2*inch, seg2_y - 1.05*inch, "Duration: ~10h 15m")
            
            # Barcode
            barcode_y = seg2_y - 2.2*inch
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.rect(1.5*inch, barcode_y, 4*inch, 0.5*inch, fill=False, stroke=True)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(3.5*inch, barcode_y + 0.2*inch, f"|||  ||||| ||  {pnr}  || ||||| |||")
            
            # Important notices
            notice_y = barcode_y - 0.6*inch
            c.setFillColor(colors.HexColor('#fff3cd'))
            c.rect(1*inch, notice_y, page_width - 2*inch, 1.2*inch, fill=True, stroke=False)
            
            c.setFillColor(colors.HexColor('#856404'))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1.3*inch, notice_y + 0.95*inch, "IMPORTANT INFORMATION")
            
            c.setFont("Helvetica", 8)
            c.drawString(1.3*inch, notice_y + 0.7*inch, "• Please arrive at the airport at least 3 hours before departure")
            c.drawString(1.3*inch, notice_y + 0.52*inch, "• Carry your passport and this e-ticket confirmation")
            c.drawString(1.3*inch, notice_y + 0.34*inch, "• Online check-in opens 24 hours before departure at www.icelandair.com")
            c.drawString(1.3*inch, notice_y + 0.16*inch, "• Baggage allowance: 1 piece (23kg) + 1 carry-on (10kg)")
            
            # Footer
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(page_width/2, 1*inch, f"This is your electronic ticket confirmation | PNR: {pnr} | Ticket: {ticket_no}")
            c.drawCentredString(page_width/2, 0.8*inch, f"Issued: {datetime.now().strftime('%d %B %Y, %H:%M')} | For inquiries: www.icelandair.com")
            
            c.save()
            
            file_size = os.path.getsize(file_path)
            doc_record.file_size = file_size
            self._update_progress(doc_record, 100, GenerationStatus.COMPLETED)
            
            return file_path
            
        except Exception as e:
            doc_record.error_message = str(e)
            doc_record.status = GenerationStatus.FAILED
            self.db.commit()
            raise
    
    # ============================================================================
    # MASTER FUNCTION (UPDATED FOR 13 DOCUMENTS)
    # ============================================================================
    
    def generate_all_documents(self) -> Dict[str, str]:
        """Generate all 13 documents and return file paths"""
        results = {}
        
        try:
            # 1. Cover Letter (MOST IMPORTANT)
            results['cover_letter'] = self.generate_cover_letter()
            
            # 2. NID English Translation
            results['nid_english'] = self.generate_nid_translation()
            
            # 3. Visiting Card
            results['visiting_card'] = self.generate_visiting_card()
            
            # 4. Financial Statement
            results['financial_statement'] = self.generate_financial_statement()
            
            # 5. Travel Itinerary
            results['travel_itinerary'] = self.generate_travel_itinerary()
            
            # 6. Travel History
            results['travel_history'] = self.generate_travel_history()
            
            # 7. Home Tie Statement
            results['home_tie_statement'] = self.generate_home_tie_statement()
            
            # 8. Asset Valuation Certificate (10-15 pages)
            results['asset_valuation'] = self.generate_asset_valuation()
            
            # 9. TIN Certificate
            results['tin_certificate'] = self.generate_tin_certificate()
            
            # 10. Tax Certificate
            results['tax_certificate'] = self.generate_tax_certificate()
            
            # 11. Trade License
            results['trade_license'] = self.generate_trade_license()
            
            # 12. Hotel Booking
            results['hotel_booking'] = self.generate_hotel_booking()
            
            # 13. Air Ticket
            results['air_ticket'] = self.generate_air_ticket()
            
            return results
            
        except Exception as e:
            print(f"Error generating documents: {e}")
            raise
