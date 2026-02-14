"""
PDF Generator Service - Generates all 13 visa application documents
Uses ReportLab for professional PDF generation and Gemini for intelligent content
"""
import os
import io
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import google.generativeai as genai
from sqlalchemy.orm import Session
from loguru import logger

from app.models import ExtractedData, QuestionnaireResponse, GeneratedDocument, GenerationStatus, VisaApplication
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
        
        # Load application data (for name, email, phone)
        self.application = self.db.query(VisaApplication).filter(
            VisaApplication.id == application_id
        ).first()
        
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
    
    def _get_applicant_type_info(self) -> Dict[str, str]:
        """
        Determine if applicant is Job Holder or Business Owner and return appropriate text.
        Returns a dictionary with keys:
        - is_job_holder: bool
        - type_label: "Job Holder" or "Business Owner"
        - profession_desc: "employed professional" or "business owner/entrepreneur"
        - work_tie_desc: Detailed description of work ties
        - occupation_intro: Introduction sentence for documents
        """
        # Get application_type from model (set during application creation)
        app_type = getattr(self.application, 'application_type', 'business')
        
        # Get employment_status from questionnaire as backup
        employment_status = self._get_value('employment_status') or ''
        
        # Determine if job holder based on multiple signals
        is_job_holder = (
            app_type == 'job' or 
            'Employed' in employment_status or 
            'Job Holder' in employment_status or
            'Employee' in employment_status
        )
        
        # Get common data
        company_name = self._get_value('company_name', 'employment.company_name', 'business.company_name') or 'Company Name'
        profession = self._get_value('job_title', 'employment.job_title', 'business_type', 'business.business_type') or 'Professional'
        
        if is_job_holder:
            return {
                'is_job_holder': True,
                'type_label': 'Job Holder',
                'profession_desc': 'employed professional',
                'work_tie_desc': f"I am employed at {company_name} as {profession}. My employer expects my return after the trip, and I have ongoing responsibilities and work contracts. My position requires my regular presence, and I must return to Bangladesh to continue my duties. My company depends on my contributions and I have clear obligations to fulfill.",
                'occupation_intro': f"I am currently employed as {profession} at {company_name}",
                'business_section_title': 'Employment Details',
                'business_desc': f"I work as {profession} at {company_name}. I have been with this company for a considerable time and hold an important position. My role involves daily responsibilities that require my presence. I receive a regular monthly salary and have job security. My employer has granted me leave for this travel, expecting my return to continue work.",
            }
        else:
            return {
                'is_job_holder': False,
                'type_label': 'Business Owner',
                'profession_desc': 'business owner/entrepreneur',
                'work_tie_desc': f"I am the proprietor of {company_name} and responsible for daily operations. My business requires my presence and I must return to continue operations. All employees depend on me for management and decision-making. Without my oversight, the business cannot function properly.",
                'occupation_intro': f"I am currently a Business Owner. My company name is \"{company_name}\" and I am the founder of my business",
                'business_section_title': 'Business Details',
                'business_desc': f"I own and operate {company_name}, a {profession} business. I established this company and have been running it for several years. As the owner, I am responsible for all major decisions, daily operations, employee management, and business development. My business requires my constant attention and supervision. All employees depend on me for their livelihood.",
            }
    
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
        """Get value with priority: Application (name/email/phone) → Questionnaire → Extraction → KEY_MAPPING"""
        
        # PRIORITY 0: Use application data for name, email, phone (ALWAYS)
        for key in keys:
            clean_key = key.split('.')[-1] if '.' in key else key
            
            if self.application:
                # Map questionnaire keys to application fields
                if clean_key in ['full_name', 'applicant_name', 'name']:
                    if self.application.applicant_name:
                        return self.application.applicant_name
                elif clean_key in ['email', 'applicant_email']:
                    if self.application.applicant_email:
                        return self.application.applicant_email
                elif clean_key in ['phone', 'phone_number', 'applicant_phone']:
                    if self.application.applicant_phone:
                        return self.application.applicant_phone
        
        # Priority 1: Check questionnaire data (includes user input + auto-fill)
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
        
        # If still not found, log at debug level (these are optional fields)
        logger.debug(f"⚠️  Missing value for keys: {keys} (even after auto-fill)")
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
        """Generate formal cover letter to Embassy of Iceland - NEW STRUCTURED FORMAT"""
        doc_record = self._create_document_record("cover_letter", "Cover_Letter.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)

            # 1. Collect all required data
            banks = self._get_banks()
            total_balance = sum(float(bank.get('balance', 0)) for bank in banks) if banks else 0
            
            # Personal data
            name = self._get_value('full_name', 'passport_copy.full_name', 'nid_bangla.name_english') or 'Applicant Name'
            passport = self._get_value('passport_number', 'passport_copy.passport_number') or 'A00000000'
            dob = self._get_value('date_of_birth', 'passport_copy.date_of_birth', 'nid_bangla.date_of_birth') or '01 Jan 1990'
            address = self._get_value('current_address', 'bank_solvency.current_address', 'nid_bangla.address_bangla') or 'Dhaka, Bangladesh'
            mobile = self._get_value('phone', 'contact.phone', 'personal.phone') or '+880XXXXXXXXXX'
            email = self._get_value('email', 'contact.email', 'personal.email') or 'email@example.com'
            
            # Employment/Business data
            type_info = self._get_applicant_type_info()
            is_job_holder = type_info['is_job_holder']
            occupation = self._get_value('job_title', 'employment.job_title') if is_job_holder else 'Business Owner'
            if not occupation or occupation == 'N/A':
                occupation = self._get_value('business_type', 'business.business_type') or 'Entrepreneur'
            company = self._get_value('company_name', 'employment.company_name', 'business.business_name') or 'Company Name'
            company_address = self._get_value('company_address', 'employment.company_address', 'business.business_address') or 'Dhaka, Bangladesh'
            monthly_income = self._get_value('monthly_income', 'financial.monthly_income', 'employment.monthly_salary')
            
            # Travel data
            arrival_date = self._get_value('arrival_date', 'travel.arrival_date', 'hotel_booking.check_in_date') or '01 May 2026'
            departure_date = self._get_value('departure_date', 'travel.departure_date', 'hotel_booking.check_out_date') or '15 May 2026'
            places = self._get_value('places_to_visit', 'travel.places', 'hotel_booking.hotel_location') or 'Reykjavik'
            hotel_name = self._get_value('hotel_booking.hotel_name', 'accommodation_name') or 'Hotel in Iceland'
            
            # Leave dates (for job holders)
            leave_from = self._get_value('leave_from_date', 'employment.leave_start_date') or arrival_date
            leave_to = self._get_value('leave_to_date', 'employment.leave_end_date') or departure_date
            
            # Travel history
            previous_travels = self._get_previous_travels()
            travel_history_text = ", ".join([t.get('country', 'N/A') for t in previous_travels[:3]]) if previous_travels else "N/A"
            
            self._update_progress(doc_record, 30)

            # 2. Create PDF with structured format matching the template
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=0.75*inch, bottomMargin=0.75*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                leading=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=12
            )
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                alignment=TA_LEFT,
                fontName='Helvetica'
            )
            
            section_header_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=11,
                leading=14,
                fontName='Helvetica-Bold',
                spaceAfter=6,
                spaceBefore=12
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['BodyText'],
                fontSize=10,
                leading=14,
                alignment=TA_JUSTIFY,
                fontName='Helvetica'
            )
            
            bullet_style = ParagraphStyle(
                'Bullet',
                parent=styles['BodyText'],
                fontSize=10,
                leading=14,
                leftIndent=20,
                fontName='Helvetica',
                bulletIndent=10
            )
            
            self._update_progress(doc_record, 50)
            
            # === DOCUMENT HEADER ===
            story.append(Paragraph("<b>COVER LETTER</b>", title_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Applicant info header
            story.append(Paragraph(f"<b>Applicant:</b> {name}", header_style))
            story.append(Paragraph(f"<b>Passport No.:</b> {passport}", header_style))
            story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %b %Y')}", header_style))
            story.append(Spacer(1, 0.2*inch))
            
            # TO section
            story.append(Paragraph("<b>TO</b>", header_style))
            story.append(Paragraph("The Visa Officer", body_style))
            story.append(Paragraph("Embassy of the Kingdom of Iceland/VFS Dhaka,", body_style))
            story.append(Paragraph("Bangladesh", body_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Subject
            story.append(Paragraph("<b>Subject: Application for Short-Stay Schengen Tourist Visa</b>", body_style))
            story.append(Spacer(1, 0.15*inch))
            
            # Greeting
            story.append(Paragraph("Dear Sir/Madam,", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Opening paragraph
            opening_text = f"I, {name}, holder of Bangladesh Passport No. {passport}, respectfully submit my application for a short-stay Schengen (tourist) visa to visit Iceland."
            story.append(Paragraph(opening_text, body_style))
            story.append(Spacer(1, 0.1*inch))
            
            travel_text = f"I intend to travel for tourism purposes from {arrival_date} to {departure_date}. During my stay, I plan to explore the cultural and historical attractions of Iceland, mainly in {places}. I will be staying at {hotel_name}."
            story.append(Paragraph(travel_text, body_style))
            story.append(Spacer(1, 0.15*inch))
            
            self._update_progress(doc_record, 65)
            
            # === PERSONAL & EMPLOYMENT INFORMATION SECTION ===
            story.append(Paragraph("<b>Personal &amp; Employment Information:</b>", section_header_style))
            
            bullet_items = [
                f"<b>Full Name:</b> {name}",
                f"<b>Date of Birth:</b> {dob}",
                f"<b>Address:</b> {address}",
                f"<b>Mobile:</b> {mobile}",
                f"<b>Email:</b> {email}",
                f"<b>Occupation:</b> {occupation}",
                f"<b>Employer:</b> {company}, {company_address}",
            ]
            
            if monthly_income:
                bullet_items.append(f"<b>Monthly Income:</b> BDT {monthly_income}")
            
            if is_job_holder:
                bullet_items.append(f"My employer has granted official leave from {leave_from} to {leave_to}, and I will return to work immediately after my trip.")
            else:
                bullet_items.append(f"As a business owner, I have arranged for temporary management during my absence and will return to resume operations.")
            
            for item in bullet_items:
                story.append(Paragraph(f"• {item}", bullet_style))
            
            story.append(Spacer(1, 0.15*inch))
            
            # === FINANCIAL & TRAVEL DETAILS SECTION ===
            story.append(Paragraph("<b>Financial &amp; Travel Details:</b>", section_header_style))
            
            financial_text = f"This trip is entirely self-financed. I have attached proof of financial stability, including bank statements"
            if monthly_income:
                financial_text += ", salary documents"
            financial_text += ", and supporting records."
            
            if total_balance > 0:
                financial_text += f" My current bank balance totals BDT {total_balance:,.0f}, which is sufficient to cover all travel expenses."
            
            story.append(Paragraph(financial_text, body_style))
            story.append(Spacer(1, 0.1*inch))
            
            if travel_history_text != "N/A":
                travel_history_para = f"I have previously traveled to {travel_history_text}, demonstrating my compliance with international travel regulations."
                story.append(Paragraph(travel_history_para, body_style))
            
            story.append(Spacer(1, 0.15*inch))
            
            # === REASON TO RETURN SECTION ===
            story.append(Paragraph("<b>Reason to Return to Bangladesh:</b>", section_header_style))
            story.append(Paragraph("I have strong ties to Bangladesh, including:", body_style))
            story.append(Spacer(1, 0.05*inch))
            
            return_reasons = []
            if is_job_holder:
                return_reasons.append("A stable full-time job")
            else:
                return_reasons.append("An established business requiring my management")
            
            return_reasons.extend([
                "Family responsibilities",
                "Personal assets and long-term commitments"
            ])
            
            for reason in return_reasons:
                story.append(Paragraph(f"• {reason},", bullet_style))
            
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("These ensure that I will return to Bangladesh within the permitted period.", body_style))
            story.append(Spacer(1, 0.15*inch))
            
            self._update_progress(doc_record, 80)
            
            # === COMMITMENT SECTION ===
            story.append(Paragraph("<b>Commitment</b>", section_header_style))
            commitment_text = f"I fully understand the visa conditions and assure you that I will abide by all the rules of the Schengen area. I will return to Bangladesh on or before {departure_date}."
            story.append(Paragraph(commitment_text, body_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Closing
            closing_text = "I kindly request you to consider my application and grant me a Schengen tourist visa."
            story.append(Paragraph(closing_text, body_style))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("Thank you for your time and kind consideration.", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Signature block
            story.append(Paragraph("<b>Sincerely,</b>", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            story.append(Paragraph(f"<b>{name}</b>", body_style))
            story.append(Paragraph(address, body_style))
            story.append(Paragraph(f"Mobile: {mobile}", body_style))
            story.append(Paragraph(f"Email: {email}", body_style))
            
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

    def generate_nid_translation(self) -> str:
        """Generate official NID English translation with real barcode and government format"""
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
            nid_no = self._get_value('nid_bangla.nid_number', 'personal.nid_number') or '1234567897'
            address = self._get_value('bank_solvency.current_address', 'personal.address', 'nid_bangla.address_bangla')
            blood_group = self._get_value('nid_bangla.blood_group', 'personal.blood_group') or 'O+'
            religion = self._get_value('personal.religion') or 'Islam'
            birth_place = self._get_value('nid_bangla.place_of_birth', 'personal.birth_place')
            issue_date = self._get_value('nid_bangla.issue_date') or 'As per original'
            
            self._update_progress(doc_record, 40)
            
            # Create PDF with professional government layout
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.units import cm
            from reportlab.graphics.barcode import code128
            from reportlab.graphics import renderPDF
            
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # === GOVERNMENT HEADER ===
            # Top seal placeholders (left and right)
            c.setStrokeColor(colors.HexColor('#666666'))
            c.setLineWidth(2)
            c.circle(2*cm, page_height - 2.5*cm, 1*cm, fill=False, stroke=True)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#999999'))
            c.drawCentredString(2*cm, page_height - 2.5*cm, "[Gov Seal]")
            
            c.circle(page_width - 2*cm, page_height - 2.5*cm, 1*cm, fill=False, stroke=True)
            c.drawCentredString(page_width - 2*cm, page_height - 2.5*cm, "[Notary]")
            
            # Title
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(colors.HexColor('#000080'))
            c.drawCentredString(page_width/2, page_height - 1.8*cm, "Translated from Bangla to English")
            
            c.setFont("Helvetica-Bold", 11)
            c.drawCentredString(page_width/2, page_height - 2.4*cm, "Government of the People's Republic of Bangladesh")
            
            c.setFont("Helvetica-Bold", 15)
            c.setFillColor(colors.HexColor('#d32f2f'))
            c.drawCentredString(page_width/2, page_height - 3.2*cm, "National ID Card")
            
            # === PHOTO & INFO SECTION ===
            content_start_y = page_height - 5*cm
            
            # Photo placeholder box (left side)
            c.setStrokeColor(colors.black)
            c.setLineWidth(1.5)
            photo_x = 2*cm
            photo_y = content_start_y
            c.rect(photo_x, photo_y - 3*cm, 2.5*cm, 3*cm, fill=False, stroke=True)
            c.setFillColor(colors.HexColor('#f0f0f0'))
            c.rect(photo_x, photo_y - 3*cm, 2.5*cm, 3*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.black)
            c.rect(photo_x, photo_y - 3*cm, 2.5*cm, 3*cm, fill=False, stroke=True)
            
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(photo_x + 1.25*cm, photo_y - 1.5*cm, "Photograph")
            
            # === NID INFORMATION (Right side of photo) ===
            field_x = 5*cm
            field_y = content_start_y - 0.3*cm
            line_height = 0.5*cm
            
            c.setFillColor(colors.black)
            
            # Field labels and values with better alignment
            fields = [
                ("Name:", name or "N/A"),
                ("Father's Name:", father or "N/A"),
                ("Mother's Name:", mother or "N/A"),
                ("Date of Birth:", dob or "N/A"),
                ("NID No.:", nid_no),
                ("Blood Group:", blood_group),
                ("Religion:", religion),
                ("Birth Place:", birth_place or "Bangladesh"),
                ("Issue Date:", issue_date),
            ]
            
            for i, (label, value) in enumerate(fields):
                y_pos = field_y - (i * line_height)
                
                # Label (bold)
                c.setFont("Helvetica-Bold", 9)
                c.drawString(field_x, y_pos, label)
                
                # Value
                c.setFont("Helvetica", 9)
                value_x = field_x + 3*cm
                c.drawString(value_x, y_pos, str(value))
            
            # === ADDRESS (Full width) ===
            addr_y = field_y - (len(fields) * line_height) - 0.5*cm
            
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2*cm, addr_y, "Address:")
            
            c.setFont("Helvetica", 9)
            # Wrap address properly
            if address:
                addr_lines = [address[i:i+80] for i in range(0, len(address), 80)]
                for j, line in enumerate(addr_lines[:3]):
                    c.drawString(2*cm, addr_y - ((j+1) * 0.4*cm), line)
            else:
                c.drawString(2*cm, addr_y - 0.4*cm, "As per original NID card")
            
            # === REAL BARCODE (Code128) ===
            barcode_y = addr_y - 2.5*cm
            
            try:
                # Generate real Code128 barcode with NID number
                barcode_data = str(nid_no)
                barcode_obj = code128.Code128(barcode_data, barHeight=1.2*cm, barWidth=1.2)
                barcode_obj.drawOn(c, page_width/2 - 4*cm, barcode_y - 0.8*cm)
                
                # Barcode label
                c.setFont("Helvetica", 7)
                c.setFillColor(colors.HexColor('#666666'))
                c.drawCentredString(page_width/2, barcode_y - 1.3*cm, f"NID: {nid_no}")
            except Exception as e:
                logger.warning(f"Barcode generation failed: {e}. Using placeholder.")
                # Fallback: barcode placeholder
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.rect(page_width/2 - 4*cm, barcode_y - 0.8*cm, 8*cm, 1*cm, fill=False, stroke=True)
                c.setFont("Helvetica", 7)
                c.setFillColor(colors.HexColor('#666666'))
                c.drawCentredString(page_width/2, barcode_y - 0.3*cm, f"|| || |||| || {nid_no} || |||| || ||")
            
            # === PAGE 2 NOTE ===
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.HexColor('#003f87'))
            c.drawCentredString(page_width/2, barcode_y - 2.5*cm, "2nd Page")
            
            # === CERTIFICATION SECTION ===
            cert_y = barcode_y - 4*cm
            
            # Box around certification
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(2*cm, cert_y - 2*cm, page_width - 4*cm, 2*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#dee2e6'))
            c.setLineWidth(0.5)
            c.rect(2*cm, cert_y - 2*cm, page_width - 4*cm, 2*cm, fill=False, stroke=True)
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2.5*cm, cert_y - 0.5*cm, "TRANSLATED BY")
            
            c.setFont("Helvetica", 9)
            cert_lines = [
                "Notarized Translation Services",
                "Authorized Translator",
                "License No: BT/2024/001"
            ]
            
            for i, line in enumerate(cert_lines):
                c.drawString(2.5*cm, cert_y - 0.9*cm - (i * 0.35*cm), line)
            
            # === RED SEAL PLACEHOLDER (Bottom left) ===
            seal_y = 4*cm
            c.setStrokeColor(colors.HexColor('#d32f2f'))
            c.setLineWidth(3)
            c.circle(4*cm, seal_y, 1.5*cm, fill=False, stroke=True)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#d32f2f'))
            c.drawCentredString(4*cm, seal_y, "[Red Seal]")
            
            # === ATTESTATION (Bottom right) ===
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(page_width - 8*cm, seal_y + 0.5*cm, "Attested: _______________")
            c.drawString(page_width - 8*cm, seal_y, f"Date: {datetime.now().strftime('%d %B %Y')}")
            
            # === FOOTER NOTE ===
            c.setFont("Helvetica-Oblique", 8)
            c.setFillColor(colors.HexColor('#555555'))
            c.drawCentredString(page_width/2, 2*cm, 
                              "This is a certified translation of the original National ID Card issued by Bangladesh Government.")
            c.drawCentredString(page_width/2, 1.5*cm, 
                              "2nd Page contains both front and back view of original NID card")
            
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
            
            # Get applicant type info (job holder vs business owner)
            type_info = self._get_applicant_type_info()
            
            # If designation not found, use type-appropriate default
            employment_status = self._get_value('employment_status')
            if not designation:
                if type_info['is_job_holder']:
                    designation = self._get_value('job_title', 'employment.job_title') or "Professional"
                else:
                    designation = "CEO & Managing Director"
            
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
        """Fallback: Generate ULTRA-PREMIUM luxury visiting card using ReportLab"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib import colors
        
        c = pdf_canvas.Canvas(file_path, pagesize=(252, 144))
        
        # === LUXURY DESIGN ===
        # Deep charcoal luxury background
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.rect(0, 0, 252, 144, fill=True, stroke=False)
        
        # Gold top & bottom borders
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 136, 252, 8, fill=True, stroke=False)
        c.rect(0, 0, 252, 8, fill=True, stroke=False)
        
        # LEFT: LUXURY PANEL
        c.setFillColor(colors.HexColor('#0F3460'))
        c.rect(0, 8, 90, 128, fill=True, stroke=False)
        
        # Gold decorative lines
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        for y_pos in [120, 110, 100]:
            c.line(15, y_pos, 75, y_pos)
        
        # Premium logo circle
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2.5)
        c.circle(45, 70, 22, fill=False, stroke=True)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(45, 70, 5, fill=True, stroke=False)
        
        # Corner decorations
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1.5)
        c.line(10, 130, 30, 130)
        c.line(10, 130, 10, 110)
        c.line(60, 14, 80, 14)
        c.line(80, 14, 80, 34)
        
        # RIGHT: WHITE PANEL with pattern
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(90, 8, 162, 128, fill=True, stroke=False)
        
        c.setStrokeColor(colors.HexColor('#E8E9EA'))
        c.setLineWidth(0.3)
        for i in range(5):
            c.line(95 + i*30, 136, 95 + i*30, 8)
        
        # NAME - LARGE & BOLD
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.setFont('Helvetica-Bold', 18)
        c.drawString(100, 108, data['full_name'][:25])
        
        # Designation with gold background
        designation_text = data['designation'][:20].upper()
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(100, 88, len(designation_text) * 5.5, 14, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(103, 92, designation_text)
        
        # Dotted separator
        c.setFillColor(colors.HexColor('#D4AF37'))
        for x in range(100, 240, 8):
            c.circle(x, 80, 0.8, fill=True, stroke=False)
        
        # Contact details
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(102, 67, 2, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(107, 65, "Phone:")
        c.setFont('Helvetica', 8)
        c.drawString(138, 65, data['phone'][:20])
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(102, 54, 2, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(107, 52, "Email:")
        c.setFont('Helvetica', 8)
        c.drawString(138, 52, data['email'][:23])
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(102, 41, 2, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A2E'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(107, 39, "Web:")
        c.setFont('Helvetica', 8)
        c.drawString(138, 39, data['website'][:25])
        
        # Footer
        c.setFillColor(colors.HexColor('#666666'))
        c.setFont('Helvetica-Oblique', 7)
        c.drawString(100, 18, "Dhaka, Bangladesh  |  Professional Visa Consultancy")
        
        # Corner decoration
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1.5)
        c.line(240, 14, 240, 34)
        c.line(220, 14, 240, 14)
        
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
            
            # Get applicant type info for funding source description
            type_info = self._get_applicant_type_info()
            default_funding = "Personal savings and income from employment" if type_info['is_job_holder'] else "Personal savings and business income"
            
            # Trip Funding
            funding_source = self._get_value('funding_source', 'financial.trip_funding_source', 'financial.funding_source')
            story.append(Paragraph(f"<b>4. Trip Funding Source:</b> {funding_source or default_funding}", body_style))
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
            
            # Get applicant type info (job holder vs business owner)
            type_info = self._get_applicant_type_info()
            business_section_title = type_info['business_section_title']
            business_desc = type_info['business_desc']
            
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
- Work: {business_desc}
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

PARAGRAPH 2 ({business_section_title} - 220-250 words):
{business_desc} Explain why you need to return - your responsibilities, ongoing commitments, people depending on you. Be specific but don't overexplain. Short, clear sentences.

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
    # 8. ASSET VALUATION CERTIFICATE (COMPREHENSIVE 10 PAGES)
    # ============================================================================
    
    def generate_asset_valuation(self) -> str:
        """Generate comprehensive 13-page asset valuation certificate using HTML template (with ReportLab fallback)"""
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
            
            # Get property details from assets or questionnaire
            prop_1 = property_assets[0] if property_assets else {}
            prop_2 = property_assets[1] if len(property_assets) > 1 else {}
            prop_3 = property_assets[2] if len(property_assets) > 2 else {}
            
            # Get vehicle details
            vehicle = vehicle_assets[0] if vehicle_assets else {}
            
            # Get business details
            business = business_assets[0] if business_assets else {}
            
            self._update_progress(doc_record, 30)
            
            # Prepare comprehensive data for 13-page template
            template_data = {
                # Basic owner info
                'owner_name': (name or 'PROPERTY OWNER').upper(),
                'father_name': father_name or 'FATHER NAME',
                'owner_father_relation': f"S/O - {father_name}" if father_name else 'S/O - FATHER NAME',
                'owner_address': address or 'Dhaka, Bangladesh',
                
                # Asset values
                'flat_value_1': property_value,
                'flat_value_2': flat_value_2,
                'flat_value_3': flat_value_3,
                'car_value': vehicle_value,
                'business_value': business_value,
                
                # Property details with questionnaire fallback
                'property_location_1': prop_1.get('description') or self._get_value('property_location_1') or 
                    'House – 38, Level 07, Road – 01, Sector – 02, Block – F, Aftabnagar, Badda, Gulshan – 1212, Dhaka, Bangladesh.',
                'property_size_1': prop_1.get('size') or self._get_value('property_size_1') or '1,434',
                'property_size_1_decimal': self._get_value('property_size_1_decimal') or '0.72116',
                
                'property_location_2': prop_2.get('description') or self._get_value('property_location_2') or 
                    '"Priyanka Runway City" Flat Size -2,220 sqft Flat A: 5 (North aild Level/Floor 2d',
                'property_size_2': prop_2.get('size') or self._get_value('property_size_2') or '2,220',
                
                'property_location_3': prop_3.get('description') or self._get_value('property_location_3') or 
                    '"Basundhara Riverview" 1.4428 Decimal 3 Flat Size 1,625x3= 4,875 sqft Mouza at Badda.',
                'property_size_3': prop_3.get('size') or self._get_value('property_size_3') or '4,875',
                'property_size_3_decimal': self._get_value('property_size_3_decimal') or '1.4428',
                
                # Vehicle details
                'vehicle_type': vehicle.get('vehicle_type') or self._get_value('vehicle_type') or 'Car Saloon',
                'vehicle_reg': vehicle.get('registration_number') or self._get_value('vehicle_reg'),
                'vehicle_chassis': vehicle.get('chassis_number') or self._get_value('vehicle_chassis'),
                'vehicle_engine': vehicle.get('engine_number') or self._get_value('vehicle_engine'),
                'vehicle_manufacturer': vehicle.get('manufacturer') or self._get_value('vehicle_manufacturer') or 'TOYOTA',
                
                # Business details
                'business_name': (business_name or business.get('business_name') or 'BUSINESS ENTERPRISE').upper(),
                'business_type': business_type or business.get('business_type') or 'Proprietor',
                'business_ownership': business.get('ownership_percentage') or self._get_value('business_ownership') or '100',
                'business_location': business.get('location') or self._get_value('business_location'),
                
                # Property deed details (from questionnaire or defaults)
                'deed_a_number': self._get_value('deed_a_number') or '6334',
                'deed_a_dist': self._get_value('deed_a_dist') or 'DHAKA',
                'deed_a_ps': self._get_value('deed_a_ps') or 'Tejgaon',
                'deed_a_sro': self._get_value('deed_a_sro') or 'BADDA',
                'deed_a_mouza': self._get_value('deed_a_mouza') or 'North Meradia - 23',
                'deed_a_khatian': self._get_value('deed_a_khatian') or '4874',
                'deed_a_dag': self._get_value('deed_a_dag') or '609',
                
                'deed_c_number': self._get_value('deed_c_number') or '6240',
                'deed_c_dist': self._get_value('deed_c_dist') or 'DHAKA',
                'deed_c_ps': self._get_value('deed_c_ps') or 'KERANIGANJ',
                'deed_c_sro': self._get_value('deed_c_sro') or 'KUNDA',
                'deed_c_mouza': self._get_value('deed_c_mouza') or 'BEYARA - 94',
                'deed_c_khatian': self._get_value('deed_c_khatian') or '4253',
                'deed_c_dag': self._get_value('deed_c_dag') or '1116/1122',
                
                # Area information
                'area_thana_1': self._get_value('area_thana_1') or 'Badda',
                'area_thana_3': self._get_value('area_thana_3') or 'Keraniganj',
                'flat_floor_1': self._get_value('flat_floor_1') or '8th Floor Aftab Nagar, Badda, Gulshan – 1212, Dhaka',
            }
            
            self._update_progress(doc_record, 60)
            
            # Try WeasyPrint first, fallback to ReportLab if it fails
            try:
                from app.services.template_renderer import TemplateRenderer
                renderer = TemplateRenderer()
                renderer.render_asset_valuation(template_data, file_path)
                logger.info("✅ Asset valuation generated with WeasyPrint 13-page template")
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
        """Fallback: Generate ULTRA-PREMIUM LUXURY asset valuation using ReportLab"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        
        c = pdf_canvas.Canvas(file_path, pagesize=A4)
        page_width, page_height = A4
        
        # === PAGE 1: STUNNING LUXURY COVER ===
        
        # Deep luxury background - charcoal gradient effect
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, 0, page_width, page_height, fill=True, stroke=False)
        
        # Gold decorative top border with double layer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 25, page_width, 25, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#B8941E'))
        c.rect(0, page_height - 30, page_width, 5, fill=True, stroke=False)
        
        # Gold decorative bottom border
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 25, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#B8941E'))
        c.rect(0, 25, page_width, 5, fill=True, stroke=False)
        
        # Decorative corner elements - Top Left
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(3)
        c.line(40, page_height - 50, 120, page_height - 50)
        c.line(40, page_height - 50, 40, page_height - 130)
        
        # Top Right corner
        c.line(page_width - 40, page_height - 50, page_width - 120, page_height - 50)
        c.line(page_width - 40, page_height - 50, page_width - 40, page_height - 130)
        
        # Bottom Left corner
        c.line(40, 50, 120, 50)
        c.line(40, 50, 40, 130)
        
        # Bottom Right corner
        c.line(page_width - 40, 50, page_width - 120, 50)
        c.line(page_width - 40, 50, page_width - 40, 130)
        
        # Premium center frame with double border
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(4)
        c.rect(60, page_height - 550, page_width - 120, 380, fill=False, stroke=True)
        c.setLineWidth(1.5)
        c.rect(70, page_height - 540, page_width - 140, 360, fill=False, stroke=True)
        
        # Decorative pattern inside frame
        c.setStrokeColor(colors.HexColor('#2A3F5F'))
        c.setLineWidth(0.5)
        for i in range(10):
            y = page_height - 200 - (i * 15)
            c.line(100, y, page_width - 100, y)
        
        # Decorative emblem/seal area
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(3)
        c.circle(page_width/2, page_height - 220, 45, fill=False, stroke=True)
        c.setLineWidth(1.5)
        c.circle(page_width/2, page_height - 220, 38, fill=False, stroke=True)
        
        # Inner star pattern
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(page_width/2, page_height - 220, 8, fill=True, stroke=False)
        
        # Title - LARGE & LUXURIOUS
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 38)
        c.drawCentredString(page_width/2, page_height - 310, "ASSET VALUATION")
        
        c.setFont('Helvetica-Bold', 32)
        c.drawCentredString(page_width/2, page_height - 355, "CERTIFICATE")
        
        # Elegant double separator lines
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.line(120, page_height - 380, page_width - 120, page_height - 380)
        c.setLineWidth(0.8)
        c.line(120, page_height - 386, page_width - 120, page_height - 386)
        
        # Owner details - Elegant white with gold labels
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawCentredString(page_width/2, page_height - 430, "PROPERTY OWNER")
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(page_width/2, page_height - 460, data['owner_name'])
        c.setFont('Helvetica', 12)
        c.drawCentredString(page_width/2, page_height - 482, f"{data['owner_father_relation']}")
        
        # Date with elegant styling - positioned inside frame
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(page_width/2, page_height - 508, "VALUATION DATE")
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 13)
        c.drawCentredString(page_width/2, page_height - 530, datetime.now().strftime('%d %B %Y'))
        
        # Professional seal/stamp area - increased height to fit all text
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(page_width/2 - 100, 140, 200, 100, fill=False, stroke=True)
        
        # Valuer information - Premium style inside stamp box
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 15)
        c.drawCentredString(page_width/2, 215, "Kamal & Associates")
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 10)
        c.drawCentredString(page_width/2, 195, "Licensed Professional Valuers & Consultants")
        c.drawCentredString(page_width/2, 175, "Dhaka, Bangladesh")
        
        c.showPage()
        
        # === PAGE 2: PREMIUM ASSET BREAKDOWN WITH LUXURY CARDS ===
        
        # Luxury header background
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        
        # Gold top accent
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        # Decorative pattern
        c.setStrokeColor(colors.HexColor('#2A3F5F'))
        c.setLineWidth(0.5)
        for i in range(15):
            c.line(i * 40, page_height - 120, i * 40, page_height - 15)
        
        # Title with shadow effect
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 26)
        c.drawString(52, page_height - 68, "DETAILED ASSET VALUATION")
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 26)
        c.drawString(50, page_height - 70, "DETAILED ASSET VALUATION")
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Comprehensive Property & Business Assessment")
        
        y = page_height - 160
        
        # REAL ESTATE - Premium section header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(40, y - 15, page_width - 80, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 16)
        c.drawString(55, y + 5, "REAL ESTATE PROPERTIES")
        c.setFont('Helvetica', 9)
        c.drawString(55, y - 8, "Premium Residential Holdings")
        
        y -= 70
        
        # Property 1 - Luxury card
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(45, y - 35, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 35, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(60, y - 12, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(70, y - 8, "Residential Flat - Premium")
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(70, y - 23, "📍 Gulshan, Dhaka  |  High-End Residential Area")
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawRightString(page_width - 60, y - 15, f"BDT {int(float(data['flat_value_1'])):,}")
        y -= 65
        
        # Property 2 - Luxury card
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(45, y - 35, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 35, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(60, y - 12, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(70, y - 8, "Residential Flat - Exclusive")
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(70, y - 23, "📍 Banani, Dhaka  |  Elite Residential Zone")
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawRightString(page_width - 60, y - 15, f"BDT {int(float(data['flat_value_2'])):,}")
        y -= 65
        
        # Property 3 - Luxury card
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(45, y - 35, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 35, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(60, y - 12, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(70, y - 8, "Residential Flat - Luxury")
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(70, y - 23, "📍 Dhanmondi, Dhaka  |  Prime Location")
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawRightString(page_width - 60, y - 15, f"BDT {int(float(data['flat_value_3'])):,}")
        y -= 85
        
        # VEHICLE - Premium section header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(40, y - 15, page_width - 80, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 16)
        c.drawString(55, y + 5, "VEHICLE ASSETS")
        c.setFont('Helvetica', 9)
        c.drawString(55, y - 8, "Automobile Holdings")
        
        y -= 70
        
        # Vehicle card
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(45, y - 35, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 35, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(60, y - 12, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(70, y - 8, "Private Car (Saloon)")
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(70, y - 23, "🚗 Toyota - Dhaka Metro Registration")
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawRightString(page_width - 60, y - 15, f"BDT {int(float(data['car_value'])):,}")
        y -= 85
        
        # BUSINESS - Premium section header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(40, y - 15, page_width - 80, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 16)
        c.drawString(55, y + 5, "BUSINESS ASSETS")
        c.setFont('Helvetica', 9)
        c.drawString(55, y - 8, "Commercial & Enterprise Holdings")
        
        y -= 70
        
        # Business card
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(45, y - 35, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 35, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(60, y - 12, 4, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(70, y - 8, data['business_name'])
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(70, y - 23, f"🏢 Type: {data['business_type']}")
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawRightString(page_width - 60, y - 15, f"BDT {int(float(data['business_value'])):,}")
        y -= 100
        
        # TOTAL - LUXURY HIGHLIGHT
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(30, y - 25, page_width - 60, 70, fill=True, stroke=False)
        
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(35, y - 20, page_width - 70, 60, fill=True, stroke=False)
        
        c.setStrokeColor(colors.HexColor('#B8941E'))
        c.setLineWidth(3)
        c.rect(35, y - 20, page_width - 70, 60, fill=False, stroke=True)
        
        # Diamond decorations
        c.setFillColor(colors.HexColor('#0F1419'))
        c.circle(45, y + 30, 5, fill=True, stroke=False)
        c.circle(page_width - 45, y + 30, 5, fill=True, stroke=False)
        c.circle(45, y - 10, 5, fill=True, stroke=False)
        c.circle(page_width - 45, y - 10, 5, fill=True, stroke=False)
        
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica-Bold', 18)
        c.drawString(55, y + 15, "TOTAL ASSET VALUE")
        
        c.setFont('Helvetica-Bold', 20)
        try:
            p1 = int(float(str(data['flat_value_1']).replace(',', '')))
            p2 = int(float(str(data['flat_value_2']).replace(',', '')))
            p3 = int(float(str(data['flat_value_3']).replace(',', '')))
            v = int(float(str(data['car_value']).replace(',', '')))
            b = int(float(str(data['business_value']).replace(',', '')))
            total = p1 + p2 + p3 + v + b
            c.drawRightString(page_width - 55, y - 8, f"BDT {total:,}")
        except:
            c.drawRightString(page_width - 55, y - 8, "BDT 40,000,000+")
        
        # Premium footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 2")
        
        c.showPage()
        
        # === PAGE 3: PROPERTY DETAILS & SPECIFICATIONS ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "PROPERTY SPECIFICATIONS")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Detailed Property Analysis & Measurements")
        
        y = page_height - 160
        
        # Property 1 Detailed Specs
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, "PROPERTY 1 - GULSHAN RESIDENCE")
        
        y -= 55
        specs_1 = [
            ("Location:", "Plot 45, Road 12, Block A, Gulshan-2, Dhaka-1212"),
            ("Property Type:", "Residential Apartment (High-Rise Building)"),
            ("Floor:", "7th Floor, South-East Facing"),
            ("Total Area:", "2,150 sq ft (199.7 sq m)"),
            ("Bedrooms:", "4 Bedrooms with attached bathrooms"),
            ("Living Space:", "Spacious drawing & dining room"),
            ("Kitchen:", "Modern fitted kitchen with appliances"),
            ("Balconies:", "2 balconies with city view"),
            ("Parking:", "2 dedicated car parking spaces"),
            ("Condition:", "Excellent - Recently renovated (2023)"),
            ("Amenities:", "Generator backup, CCTV, 24/7 security"),
            ("Age:", "Building constructed in 2018 (5 years old)"),
        ]
        
        for label, value in specs_1:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(50, y, label)
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(155, y, value)
            y -= 18
        
        # Market Value Breakdown
        y -= 20
        c.setFillColor(colors.HexColor('#F0F0F0'))
        c.rect(45, y - 55, page_width - 90, 60, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 55, page_width - 90, 60, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(55, y - 15, "VALUATION BREAKDOWN:")
        c.setFont('Helvetica', 9)
        c.drawString(55, y - 32, "Base Land Value:")
        c.drawRightString(page_width - 60, y - 32, f"BDT {int(float(data['flat_value_1']) * 0.60):,}")
        c.drawString(55, y - 46, "Construction & Development:")
        c.drawRightString(page_width - 60, y - 46, f"BDT {int(float(data['flat_value_1']) * 0.40):,}")
        
        y -= 75
        
        # Property 2 Detailed Specs
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, "PROPERTY 2 - BANANI RESIDENCE")
        
        y -= 55
        specs_2 = [
            ("Location:", "House 78, Road 11, Block E, Banani, Dhaka-1213"),
            ("Property Type:", "Residential Apartment (Mid-Rise)"),
            ("Floor:", "5th Floor, West Facing"),
            ("Total Area:", "1,850 sq ft (171.9 sq m)"),
            ("Bedrooms:", "3 Bedrooms with attached bathrooms"),
            ("Living Space:", "Open concept living and dining"),
            ("Kitchen:", "Modular kitchen with modern fittings"),
            ("Balconies:", "1 large balcony"),
            ("Parking:", "1 car parking space"),
            ("Condition:", "Very good - Well maintained"),
            ("Age:", "Building constructed in 2015 (8 years old)"),
        ]
        
        for label, value in specs_2:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(50, y, label)
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(155, y, value)
            y -= 18
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 3")
        
        c.showPage()
        
        # === PAGE 4: PROPERTY 3 & VEHICLE DETAILS ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "ADDITIONAL ASSETS")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Property & Vehicle Portfolio Continued")
        
        y = page_height - 160
        
        # Property 3 Detailed Specs
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, "PROPERTY 3 - DHANMONDI RESIDENCE")
        
        y -= 55
        specs_3 = [
            ("Location:", "House 23, Road 5/A, Dhanmondi R/A, Dhaka-1209"),
            ("Property Type:", "Residential Apartment"),
            ("Floor:", "3rd Floor, North Facing"),
            ("Total Area:", "1,650 sq ft (153.3 sq m)"),
            ("Bedrooms:", "3 Bedrooms with attached bathrooms"),
            ("Living Space:", "Combined living and dining area"),
            ("Kitchen:", "Standard kitchen with pantry"),
            ("Balconies:", "1 front balcony"),
            ("Parking:", "1 car parking space"),
            ("Condition:", "Good - Standard maintenance"),
            ("Age:", "Building constructed in 2012 (11 years old)"),
        ]
        
        for label, value in specs_3:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(50, y, label)
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(155, y, value)
            y -= 18
        
        y -= 30
        
        # Vehicle Detailed Specs
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, "VEHICLE ASSET - PRIVATE CAR")
        
        y -= 55
        vehicle_specs = [
            ("Make & Model:", "Toyota Corolla XLi 1.8"),
            ("Year:", "2021 Model (2 years old)"),
            ("Registration:", "Dhaka Metro - GA-12-3456"),
            ("Engine:", "1800cc Petrol Engine"),
            ("Color:", "Silver Metallic"),
            ("Mileage:", "45,000 km (Excellent condition)"),
            ("Ownership:", "First owner - Single handed"),
            ("Service History:", "Regular servicing at authorized dealer"),
            ("Insurance:", "Comprehensive coverage - Valid till 2024"),
            ("Condition:", "Excellent - Well maintained, no accidents"),
        ]
        
        for label, value in vehicle_specs:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(50, y, label)
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(155, y, value)
            y -= 18
        
        y -= 20
        c.setFillColor(colors.HexColor('#F0F0F0'))
        c.rect(45, y - 40, page_width - 90, 45, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 40, page_width - 90, 45, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(55, y - 12, "VEHICLE VALUATION FACTORS:")
        c.setFont('Helvetica', 9)
        c.drawString(55, y - 26, "Market depreciation, condition, mileage, and current market trends considered")
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 4")
        
        c.showPage()
        
        # === PAGE 5: BUSINESS ASSET DETAILS ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "BUSINESS ASSET VALUATION")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Commercial Enterprise Assessment")
        
        y = page_height - 160
        
        # Business Overview
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, f"BUSINESS: {data['business_name'].upper()}")
        
        y -= 55
        business_specs = [
            ("Business Type:", data['business_type']),
            ("Registration:", "RJSC Registered - Trade License Valid"),
            ("Established:", "Operating since 2015 (8+ years)"),
            ("Location:", "Motijheel C/A, Dhaka (Prime Commercial Area)"),
            ("Business Premises:", "Owned office space - 1,200 sq ft"),
            ("Employees:", "15+ Full-time employees"),
            ("Annual Revenue:", "BDT 25,00,000+ (FY 2022-23)"),
            ("Client Base:", "50+ Regular corporate clients"),
            ("Market Position:", "Established presence in industry"),
            ("Assets Include:", "Office equipment, inventory, goodwill"),
        ]
        
        for label, value in business_specs:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(50, y, label)
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 9)
            c.drawString(155, y, value)
            y -= 18
        
        y -= 30
        
        # Business Valuation Components
        c.setFillColor(colors.HexColor('#F0F0F0'))
        c.rect(45, y - 150, page_width - 90, 160, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 150, page_width - 90, 160, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, y - 20, "BUSINESS VALUATION BREAKDOWN:")
        
        y -= 45
        business_breakdown = [
            ("Tangible Assets (Equipment, Inventory):", int(float(data['business_value']) * 0.30)),
            ("Intangible Assets (Goodwill, Brand):", int(float(data['business_value']) * 0.25)),
            ("Revenue Potential (3-Year Projection):", int(float(data['business_value']) * 0.25)),
            ("Market Position & Client Base:", int(float(data['business_value']) * 0.20)),
        ]
        
        c.setFont('Helvetica', 10)
        for label, value in business_breakdown:
            c.setFillColor(colors.black)
            c.drawString(65, y, label)
            c.setFillColor(colors.HexColor('#006400'))
            c.setFont('Helvetica-Bold', 10)
            c.drawRightString(page_width - 60, y, f"BDT {value:,}")
            c.setFont('Helvetica', 10)
            y -= 24
        
        y -= 10
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.line(65, y, page_width - 60, y)
        y -= 20
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(65, y, "TOTAL BUSINESS VALUE:")
        c.setFillColor(colors.HexColor('#006400'))
        c.setFont('Helvetica-Bold', 12)
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['business_value'])):,}")
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 5")
        
        c.showPage()
        
        # === PAGE 6: MARKET ANALYSIS ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "MARKET ANALYSIS")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Current Real Estate & Asset Market Trends")
        
        y = page_height - 160
        
        # Market Overview
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 35, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 14)
        c.drawString(50, y - 5, "DHAKA REAL ESTATE MARKET OVERVIEW")
        
        y -= 55
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 10)
        
        market_text = [
            "The Dhaka real estate market has shown consistent growth over the past 5 years.",
            "Premium areas like Gulshan, Banani, and Baridhara command the highest prices.",
            "",
            "Average Price per Square Foot (2023-24):",
        ]
        
        for line in market_text:
            c.drawString(50, y, line)
            y -= 18
        
        y -= 10
        areas_pricing = [
            ("Gulshan Area:", "BDT 6,500 - 8,500 per sq ft"),
            ("Banani Area:", "BDT 5,500 - 7,500 per sq ft"),
            ("Dhanmondi Area:", "BDT 4,500 - 6,500 per sq ft"),
        ]
        
        for area, price in areas_pricing:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.circle(60, y + 4, 2, fill=True, stroke=False)
            c.setFillColor(colors.black)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(70, y, area)
            c.setFont('Helvetica', 10)
            c.drawString(190, y, price)
            y -= 20
        
        y -= 30
        
        # Comparative Analysis - Increased box height to fit all content
        c.setFillColor(colors.HexColor('#F0F0F0'))
        c.rect(45, y - 260, page_width - 90, 270, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 260, page_width - 90, 270, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, y - 20, "COMPARATIVE MARKET ANALYSIS:")
        
        y -= 50
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.black)
        
        comparison_data = [
            "Similar properties in Gulshan area (2,000-2,500 sq ft):",
            "Recent sale: BDT 1.35 Cr - 1.55 Cr (Q4 2023)",
            "",
            "Similar properties in Banani area (1,800-2,000 sq ft):",
            "Recent sale: BDT 95 Lakh - 1.15 Cr (Q4 2023)",
            "",
            "Similar properties in Dhanmondi area (1,500-1,800 sq ft):",
            "Recent sale: BDT 75 Lakh - 95 Lakh (Q4 2023)",
            "",
            "Vehicle Market Trends:",
            "Toyota Corolla 2021 models trading at BDT 32-37 Lakh",
            "",
            "Business Valuation Factors:",
            "Established businesses with 8+ years operation typically valued at",
            "3-5x annual profit or 1-1.5x annual revenue, whichever is higher.",
        ]
        
        for line in comparison_data:
            c.drawString(65, y, line)
            y -= 15
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 6")
        
        c.showPage()
        
        # === PAGE 7: VALUATION METHODOLOGY ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "VALUATION METHODOLOGY")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Professional Standards & Procedures Applied")
        
        y = page_height - 160
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 10)
        
        methodology_intro = [
            "This valuation has been conducted using internationally recognized valuation",
            "methodologies and standards. Multiple approaches have been employed to ensure",
            "accuracy and reliability of the assessed values.",
        ]
        
        for line in methodology_intro:
            c.drawString(50, y, line)
            y -= 18
        
        y -= 20
        
        # Method 1
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 30, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(50, y - 3, "1. COMPARABLE SALES APPROACH")
        
        y -= 50
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        method_1_text = [
            "Properties with similar characteristics in the same area are analyzed.",
            "Recent transaction prices are adjusted for differences in size, condition,",
            "age, and amenities. This provides a market-based valuation benchmark.",
        ]
        
        for line in method_1_text:
            c.drawString(60, y, line)
            y -= 15
        
        y -= 20
        
        # Method 2
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 30, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(50, y - 3, "2. COST APPROACH")
        
        y -= 50
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        method_2_text = [
            "Calculates the current cost of replacing the property, considering land value",
            "and construction costs, less depreciation. Useful for newer properties and",
            "special-purpose assets where comparable sales are limited.",
        ]
        
        for line in method_2_text:
            c.drawString(60, y, line)
            y -= 15
        
        y -= 20
        
        # Method 3
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 30, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(50, y - 3, "3. INCOME CAPITALIZATION APPROACH")
        
        y -= 50
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        method_3_text = [
            "For income-generating properties and businesses, potential rental income",
            "or business revenue is capitalized to determine present value. Market rent",
            "rates and cap rates for similar properties are used as reference.",
        ]
        
        for line in method_3_text:
            c.drawString(60, y, line)
            y -= 15
        
        y -= 30
        
        # Factors Considered
        c.setFillColor(colors.HexColor('#F0F0F0'))
        c.rect(45, y - 155, page_width - 90, 165, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1)
        c.rect(45, y - 155, page_width - 90, 165, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(55, y - 20, "KEY FACTORS CONSIDERED IN VALUATION:")
        
        y -= 45
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.black)
        
        factors = [
            "✓ Location and neighborhood quality",
            "✓ Property size, layout, and specifications",
            "✓ Age, condition, and maintenance status",
            "✓ Current market trends and demand-supply dynamics",
            "✓ Infrastructure and accessibility",
            "✓ Legal documentation and clear title",
            "✓ Future development potential",
            "✓ Economic conditions and interest rates",
        ]
        
        for factor in factors:
            c.drawString(65, y, factor)
            y -= 16
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 7")
        
        c.showPage()
        
        # === PAGE 8: ASSUMPTIONS & LIMITATIONS ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "ASSUMPTIONS & LIMITATIONS")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Conditions & Scope of Valuation Report")
        
        y = page_height - 160
        
        # Assumptions
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 30, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(50, y - 3, "GENERAL ASSUMPTIONS")
        
        y -= 50
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        assumptions = [
            "1. All title deeds and ownership documents are assumed to be genuine and legally valid.",
            "",
            "2. Properties are assumed to be free from encumbrances, liens, and legal disputes",
            "   unless specifically stated otherwise.",
            "",
            "3. No hidden defects exist in the properties that are not apparent during",
            "   physical inspection and document verification.",
            "",
            "4. Market conditions are assumed to remain relatively stable over the short term.",
            "",
            "5. All information provided by the client regarding assets is assumed to be",
            "   accurate and complete.",
            "",
            "6. Measurements and specifications are based on available documents and",
            "   physical inspection.",
        ]
        
        for line in assumptions:
            c.drawString(50, y, line)
            y -= 14
        
        y -= 25
        
        # Limitations
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(40, y - 15, page_width - 80, 30, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(50, y - 3, "LIMITATIONS OF VALUATION")
        
        y -= 50
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        
        limitations = [
            "1. This valuation is valid as of the date mentioned and may change with",
            "   market conditions over time.",
            "",
            "2. The report is prepared specifically for visa/immigration purposes and may",
            "   not be suitable for other purposes without review.",
            "",
            "3. Physical inspection was conducted externally. Internal structural survey",
            "   was not part of this assignment.",
            "",
            "4. No environmental or soil testing was conducted as part of this valuation.",
            "",
            "5. This report should be considered as a whole; individual sections should not",
            "   be relied upon independently.",
        ]
        
        for line in limitations:
            c.drawString(50, y, line)
            y -= 14
        
        y -= 30
        
        # Disclaimer Box - Increased height to fit all content
        c.setFillColor(colors.HexColor('#FFF8DC'))
        c.rect(45, y - 110, page_width - 90, 120, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(45, y - 110, page_width - 90, 120, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#8B0000'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(55, y - 15, "IMPORTANT DISCLAIMER:")
        
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 9)
        disclaimer_text = [
            "This valuation report is prepared for the specific purpose of supporting visa/immigration",
            "applications. The valuations represent professional opinion based on market analysis,",
            "physical inspection, and documentation review. Actual sale prices may vary depending on",
            "market conditions at the time of sale, negotiation skills, urgency of sale, and other factors.",
            "Kamal & Associates accepts no liability for losses arising from market fluctuations or",
            "transactions conducted based on this report.",
        ]
        
        y -= 32
        for line in disclaimer_text:
            c.drawString(55, y, line)
            y -= 13
        
        # Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 8")
        
        c.showPage()
        
        # === PAGE 9: PROFESSIONAL CERTIFICATION ===
        
        # Premium header background
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 150, page_width, 150, fill=True, stroke=False)
        
        # Gold accent borders
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        c.rect(0, page_height - 150, page_width, 5, fill=True, stroke=False)
        
        # Decorative emblem at top - smaller to avoid overlap
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(3)
        c.circle(page_width/2, page_height - 75, 28, fill=False, stroke=True)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.circle(page_width/2, page_height - 75, 8, fill=True, stroke=False)
        
        # Title with elegant styling
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 26)
        c.drawCentredString(page_width/2, page_height - 125, "PROFESSIONAL CERTIFICATION")
        
        # Double separator lines - Premium
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2.5)
        c.line(80, page_height - 165, page_width - 80, page_height - 165)
        c.setLineWidth(1)
        c.line(80, page_height - 172, page_width - 80, page_height - 172)
        
        c.setFont('Helvetica', 12)
        y = page_height - 200
        
        # Premium content box - increased height to fit all content
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(1.5)
        c.rect(60, y - 310, page_width - 120, 350, fill=False, stroke=True)
        
        c.setFillColor(colors.black)
        y -= 20
        
        cert_text = [
            "This is to certify that the above valuation has been carried out based on physical",
            "inspection, comprehensive market analysis, and thorough verification of all relevant",
            "documentation including title deeds, registration papers, and supporting records.",
            "",
            "The valuation is prepared in strict accordance with:",
            "",
        ]
        
        for line in cert_text:
            c.drawString(80, y, line)
            y -= 20
        
        # Standards list with gold bullets
        standards = [
            "Bangladesh Valuation Standards (BVS)",
            "International Valuation Standards (IVS)",
            "Professional Ethics and Guidelines",
            "Real Estate Valuation Methodology"
        ]
        
        for std in standards:
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.circle(90, y + 4, 2, fill=True, stroke=False)
            c.setFillColor(colors.black)
            c.drawString(100, y, std)
            y -= 20
        
        y -= 10
        c.setFont('Helvetica', 12)
        c.drawString(80, y, "The valuation represents the fair market value as of the date mentioned above")
        y -= 18
        c.drawString(80, y, "and is valid for official visa application and immigration purposes.")
        
        y -= 30
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.drawString(80, y, f"Prepared for: {data['owner_name']}")
        y -= 18
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(80, y, f"Permanent Address: {data['owner_address']}")
        
        # Premium signature section
        y -= 80
        
        # Signature box - increased height to fit all content
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(70, y - 85, 220, 105, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(70, y - 85, 220, 105, fill=False, stroke=True)
        
        # Signature line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(90, y - 10, 270, y - 10)
        
        y -= 30
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(90, y, "Authorized Signature")
        y -= 22
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.drawString(90, y, "Kamal & Associates")
        y -= 16
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(90, y, "Licensed Professional Valuers & Consultants")
        y -= 14
        c.drawString(90, y, "Registration No: BPV-2024-1234")
        
        # Company Seal/Stamp box (right side)
        c.setFillColor(colors.HexColor('#F8F9FA'))
        c.rect(page_width - 290, 120, 220, 95, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(page_width - 290, 120, 220, 95, fill=False, stroke=True)
        
        # Seal circle
        c.setStrokeColor(colors.HexColor('#8B0000'))
        c.setLineWidth(3)
        c.circle(page_width - 180, 167, 30, fill=False, stroke=True)
        c.setLineWidth(1)
        c.circle(page_width - 180, 167, 25, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#8B0000'))
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(page_width - 180, 172, "KAMAL &")
        c.drawCentredString(page_width - 180, 164, "ASSOCIATES")
        c.setFont('Helvetica', 6)
        c.drawCentredString(page_width - 180, 156, "Professional Valuers")
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(page_width - 180, 130, "Company Seal")
        
        # Premium footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 9")
        
        c.showPage()
        
        # === PAGE 10: EXECUTIVE SUMMARY & CONTACT ===
        
        # Premium header
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(0, page_height - 120, page_width, 120, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, page_height - 15, page_width, 15, fill=True, stroke=False)
        
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 24)
        c.drawString(50, page_height - 70, "EXECUTIVE SUMMARY")
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica', 11)
        c.drawString(50, page_height - 95, "Complete Asset Portfolio Overview")
        
        y = page_height - 160
        
        # Summary Box - increased height to prevent overflow
        c.setFillColor(colors.HexColor('#F0F8FF'))
        c.rect(45, y - 240, page_width - 90, 250, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(45, y - 240, page_width - 90, 250, fill=False, stroke=True)
        
        c.setFillColor(colors.HexColor('#1A1A1A'))
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(page_width/2, y - 25, "COMPLETE ASSET PORTFOLIO SUMMARY")
        
        y -= 60
        c.setFont('Helvetica-Bold', 11)
        c.drawString(60, y, "REAL ESTATE ASSETS:")
        y -= 22
        c.setFont('Helvetica', 10)
        c.drawString(75, y, f"Property 1 (Gulshan):")
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['flat_value_1'])):,}")
        y -= 18
        c.drawString(75, y, f"Property 2 (Banani):")
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['flat_value_2'])):,}")
        y -= 18
        c.drawString(75, y, f"Property 3 (Dhanmondi):")
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['flat_value_3'])):,}")
        
        y -= 30
        c.setFont('Helvetica-Bold', 11)
        c.drawString(60, y, "VEHICLE ASSETS:")
        y -= 22
        c.setFont('Helvetica', 10)
        c.drawString(75, y, f"Private Car (Toyota):")
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['car_value'])):,}")
        
        y -= 30
        c.setFont('Helvetica-Bold', 11)
        c.drawString(60, y, "BUSINESS ASSETS:")
        y -= 22
        c.setFont('Helvetica', 10)
        c.drawString(75, y, f"{data['business_name']}:")
        c.drawRightString(page_width - 60, y, f"BDT {int(float(data['business_value'])):,}")
        
        y -= 30
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.line(60, y, page_width - 60, y)
        
        y -= 25
        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#006400'))
        c.drawString(60, y, "TOTAL ASSET VALUE:")
        try:
            p1 = int(float(str(data['flat_value_1']).replace(',', '')))
            p2 = int(float(str(data['flat_value_2']).replace(',', '')))
            p3 = int(float(str(data['flat_value_3']).replace(',', '')))
            v = int(float(str(data['car_value']).replace(',', '')))
            b = int(float(str(data['business_value']).replace(',', '')))
            total = p1 + p2 + p3 + v + b
            c.setFont('Helvetica-Bold', 15)
            c.drawRightString(page_width - 60, y, f"BDT {total:,}")
        except:
            c.setFont('Helvetica-Bold', 15)
            c.drawRightString(page_width - 60, y, "BDT 40,000,000+")
        
        y -= 70
        
        # Valuation Date
        c.setFillColor(colors.black)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(60, y, "Valuation Date:")
        c.setFont('Helvetica', 10)
        c.drawString(170, y, datetime.now().strftime('%d %B %Y'))
        y -= 18
        c.setFont('Helvetica-Bold', 10)
        c.drawString(60, y, "Report Validity:")
        c.setFont('Helvetica', 10)
        c.drawString(170, y, "6 months from valuation date")
        
        y -= 60
        
        # Contact Information Box
        c.setFillColor(colors.HexColor('#0F1419'))
        c.rect(45, y - 140, page_width - 90, 150, fill=True, stroke=False)
        c.setStrokeColor(colors.HexColor('#D4AF37'))
        c.setLineWidth(2)
        c.rect(45, y - 140, page_width - 90, 150, fill=False, stroke=True)
        
        y -= 20
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(page_width/2, y, "KAMAL & ASSOCIATES")
        
        y -= 25
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 10)
        c.drawCentredString(page_width/2, y, "Licensed Professional Valuers & Consultants")
        
        y -= 25
        c.setFont('Helvetica', 9)
        c.drawCentredString(page_width/2, y, "📍 Address: House 45, Road 12, Mohakhali C/A, Dhaka-1212, Bangladesh")
        
        y -= 18
        c.drawCentredString(page_width/2, y, "📞 Phone: +880-2-9876543  |  📱 Mobile: +880-171-234-5678")
        
        y -= 18
        c.drawCentredString(page_width/2, y, "✉️ Email: info@kamal-associates.com  |  🌐 Web: www.kamal-associates.com")
        
        y -= 25
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(page_width/2, y, "Registration No: BPV-2024-1234  |  License: NBR/VAL/2024/567")
        
        y -= 20
        c.setFillColor(colors.white)
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, y, "Member: Bangladesh Association of Professional Valuers (BAPV)")
        c.drawCentredString(page_width/2, y - 12, "Affiliated: International Valuation Standards Council (IVSC)")
        
        # Final Footer
        c.setFillColor(colors.HexColor('#D4AF37'))
        c.rect(0, 0, page_width, 15, fill=True, stroke=False)
        c.setFillColor(colors.HexColor('#0F1419'))
        c.setFont('Helvetica', 8)
        c.drawCentredString(page_width/2, 4, "Kamal & Associates | Professional Asset Valuation Services | Page 10 - END OF REPORT")
        
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
    # 11B. JOB NO OBJECTION CERTIFICATE (NOC)
    # ============================================================================
    
    def generate_job_noc(self) -> str:
        """Generate Job No Objection Certificate from employer"""
        doc_record = self._create_document_record("job_noc", "Job_NOC.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get employee and company data
            employee_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            employee_id = self._get_value('employee_id') or f'EMP{hash(employee_name or "X") % 10000:04d}'
            job_title = self._get_value('job_title', 'employment.job_title') or 'Senior Executive'
            company_name = self._get_value('company_name', 'employment.company_name') or 'Bangladesh Trading Corporation'
            joining_date = self._get_value('joining_date', 'employment.joining_date') or datetime.now().strftime('%d %B %Y')
            supervisor_name = self._get_value('supervisor_name', 'employment.supervisor_name') or 'HR Manager'
            supervisor_designation = self._get_value('supervisor_designation', 'employment.supervisor_designation') or 'Human Resources Manager'
            company_address = self._get_value('business_address', 'employment.company_address') or 'Dhaka, Bangladesh'
            
            self._update_progress(doc_record, 30)
            
            # Create professional NOC PDF
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.utils import simpleSplit
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Company letterhead header
            c.setFillColor(colors.HexColor('#0066CC'))
            c.setFont('Helvetica-Bold', 20)
            c.drawCentredString(page_width/2, page_height - inch, company_name[:40].upper())
            
            c.setFillColor(colors.HexColor('#333333'))
            c.setFont('Helvetica', 9)
            c.drawCentredString(page_width/2, page_height - 1.25*inch, company_address[:60])
            
            # Horizontal line
            c.setStrokeColor(colors.HexColor('#0066CC'))
            c.setLineWidth(2)
            c.line(inch, page_height - 1.4*inch, page_width - inch, page_height - 1.4*inch)
            
            # Date and Reference
            c.setFillColor(colors.black)
            c.setFont('Helvetica', 11)
            c.drawString(inch, page_height - 1.8*inch, f"Date: {datetime.now().strftime('%d %B %Y')}")
            c.drawString(inch, page_height - 2*inch, f"Ref: NOC/{datetime.now().year}/{employee_id}")
            
            # To Address
            c.setFont('Helvetica-Bold', 12)
            c.drawString(inch, page_height - 2.5*inch, "To Whom It May Concern")
            
            # Subject
            c.setFont('Helvetica-Bold', 11)
            c.drawString(inch, page_height - 2.9*inch, "Subject: No Objection Certificate for Iceland Tourist Visa Application")
            
            # Body paragraphs
            y_position = page_height - 3.5*inch
            paragraphs = [
                f"This is to certify that {employee_name} (Employee ID: {employee_id}) is a full-time employee of {company_name}, currently serving as {job_title}.",
                
                f"{employee_name} has been working with our organization since {joining_date} and has been a valuable and dedicated member of our team.",
                
                f"We hereby grant permission to {employee_name} to travel to Iceland for tourism purposes during the proposed travel dates. The company has NO OBJECTION to this travel request.",
                
                f"We confirm that {employee_name}'s position will remain secure during the travel period, and employment will continue upon return to Bangladesh after completing the trip.",
                
                "This certificate is issued upon the employee's request for the purpose of Iceland tourist visa application.",
                
                "Should you require any further information or clarification, please feel free to contact our office."
            ]
            
            c.setFont('Helvetica', 11)
            for para in paragraphs:
                # Word wrap paragraphs
                lines = simpleSplit(para, 'Helvetica', 11, page_width - 2*inch)
                for line in lines:
                    c.drawString(inch, y_position, line)
                    y_position -= 0.22*inch
                y_position -= 0.15*inch  # Extra space between paragraphs
            
            # Signature section
            y_position -= 0.3*inch
            c.setFont('Helvetica-Bold', 11)
            c.drawString(inch, y_position, "Sincerely,")
            
            # Signature line
            y_position -= inch
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            c.line(inch, y_position, 3*inch, y_position)
            
            y_position -= 0.25*inch
            c.setFont('Helvetica-Bold', 11)
            c.drawString(inch, y_position, supervisor_name[:30])
            
            y_position -= 0.2*inch
            c.setFont('Helvetica', 10)
            c.drawString(inch, y_position, supervisor_designation[:40])
            
            y_position -= 0.2*inch
            c.drawString(inch, y_position, company_name[:40])
            
            # Company stamp placeholder
            stamp_x = page_width - 2.5*inch
            stamp_y = y_position - 0.3*inch
            c.setStrokeColor(colors.HexColor('#0066CC'))
            c.setLineWidth(2)
            c.circle(stamp_x, stamp_y, 0.8*inch, stroke=True, fill=False)
            c.setFont('Helvetica-Bold', 9)
            c.setFillColor(colors.HexColor('#0066CC'))
            c.drawCentredString(stamp_x, stamp_y + 0.1*inch, "COMPANY")
            c.drawCentredString(stamp_x, stamp_y - 0.1*inch, "SEAL")
            
            # Footer
            c.setFont('Helvetica', 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(page_width/2, 0.5*inch, "This is an officially generated document by the company")
            
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
    # 11C. JOB ID CARD (EMPLOYEE ID CARD)
    # ============================================================================
    
    def generate_job_id_card(self) -> str:
        """Generate Employee ID Card (business card size)"""
        doc_record = self._create_document_record("job_id_card", "Employee_ID_Card.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get employee data
            employee_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            employee_id = self._get_value('employee_id') or f'EMP{hash(employee_name or "X") % 10000:04d}'
            job_title = self._get_value('job_title', 'employment.job_title') or 'Senior Executive'
            company_name = self._get_value('company_name', 'employment.company_name') or 'Bangladesh Trading Corporation'
            phone = self._get_value('phone', 'personal.phone') or '+880-1234-567890'
            email = self._get_value('email', 'personal.email') or 'employee@company.com'
            
            self._update_progress(doc_record, 30)
            
            # Create ID card (business card size: 252pt x 144pt = 3.5" x 2")
            from reportlab.pdfgen import canvas as pdf_canvas
            c = pdf_canvas.Canvas(file_path, pagesize=(252, 144))
            
            # === PROFESSIONAL ID CARD DESIGN ===
            
            # Dark background
            c.setFillColor(colors.HexColor('#1A1A2E'))
            c.rect(0, 0, 252, 144, fill=True, stroke=False)
            
            # Gold top border
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.rect(0, 136, 252, 8, fill=True, stroke=False)
            
            # Company section (top)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold', 12)
            c.drawCentredString(126, 118, company_name[:30])
            
            # ID Card label
            c.setFont('Helvetica', 8)
            c.drawCentredString(126, 105, "EMPLOYEE IDENTIFICATION CARD")
            
            # Photo placeholder (left side)
            c.setFillColor(colors.HexColor('#0F3460'))
            c.rect(15, 30, 60, 65, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#D4AF37'))
            c.setLineWidth(2)
            c.rect(15, 30, 60, 65, fill=False, stroke=True)
            
            c.setFillColor(colors.white)
            c.setFont('Helvetica', 8)
            c.drawCentredString(45, 60, "EMPLOYEE")
            c.drawCentredString(45, 52, "PHOTO")
            
            # Employee details (right side)
            c.setFillColor(colors.white)
            c.setFont('Helvetica-Bold', 14)
            name_text = employee_name[:20] if len(employee_name) <= 20 else employee_name[:17] + "..."
            c.drawString(85, 85, name_text)
            
            c.setFont('Helvetica', 10)
            job_text = job_title[:25] if len(job_title) <= 25 else job_title[:22] + "..."
            c.drawString(85, 70, job_text)
            
            c.setFont('Helvetica-Bold', 9)
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.drawString(85, 55, f"ID: {employee_id}")
            
            c.setFillColor(colors.white)
            c.setFont('Helvetica', 8)
            phone_text = phone[:18] if len(phone) <= 18 else phone[:15] + "..."
            c.drawString(85, 40, f"📱 {phone_text}")
            
            email_text = email[:23] if len(email) <= 23 else email[:20] + "..."
            c.drawString(85, 28, f"✉ {email_text}")
            
            # Bottom gold border
            c.setFillColor(colors.HexColor('#D4AF37'))
            c.rect(0, 0, 252, 8, fill=True, stroke=False)
            
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
        """Generate professional 1-page Booking.com hotel confirmation"""
        doc_record = self._create_document_record("hotel_booking", "Hotel_Booking_Confirmation.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get booking data from user input
            guest_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            hotel_name = self._get_value('hotel.hotel_name', 'hotel_booking.hotel_name') or 'Canopy by Hilton Reykjavik City Centre'
            hotel_address = self._get_value('hotel.hotel_address', 'hotel_booking.hotel_address') or 'Smaratorg 1, 201 Reykjavik'
            check_in = self._get_value('hotel.check_in_date', 'hotel_booking.check_in_date', 'travel.arrival_date') or datetime.now().strftime('%Y-%m-%d')
            check_out = self._get_value('hotel.check_out_date', 'hotel_booking.check_out_date', 'travel.departure_date') or (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d')
            room_type = self._get_value('hotel.room_type', 'hotel_booking.room_type') or 'Standard Double'
            guests_count = self._get_value('hotel.number_of_guests', 'hotel_booking.guests') or '1'
            
            # Generate unique confirmation number and PIN for this booking
            confirmation_no = self._get_value('hotel.confirmation_number', 'hotel_booking.confirmation_number') or f'BK{datetime.now().year}{hash(str(guest_name) + str(check_in)) % 100000000:08d}'[:15]
            pin_code = self._get_value('hotel.pin_code', 'hotel_booking.pin_code') or f'{hash(confirmation_no) % 10000:04d}'
            
            total_price = self._get_value('hotel.total_price', 'hotel_booking.total_price') or '980'
            email = self._get_value('personal.email', 'passport_copy.email', 'contact.email') or 'guest@example.com'
            phone = self._get_value('hotel.phone', 'hotel_booking.phone') or '0174193690'
            
            # Calculate nights
            try:
                from datetime import datetime as dt
                cin = dt.strptime(check_in, '%Y-%m-%d')
                cout = dt.strptime(check_out, '%Y-%m-%d')
                nights = (cout - cin).days
            except:
                nights = 24
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with professional 1-page Booking.com design
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.units import cm
            
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # === HEADER: Booking.com logo ===
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 20)
            c.drawString(1*cm, page_height - 1.3*cm, "Booking.com")
            
            # Top right: Confirmation number
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.black)
            c.drawRightString(page_width - 1*cm, page_height - 0.7*cm, "Booking confirmation")
            
            c.setFillColor(colors.HexColor('#0071c2'))
            c.setFont("Helvetica-Bold", 9)
            c.drawRightString(page_width - 1*cm, page_height - 1*cm, f"CONFIRMATION NUMBER: {confirmation_no}")
            
            c.setFillColor(colors.HexColor('#666666'))
            c.setFont("Helvetica", 7)
            c.drawRightString(page_width - 1*cm, page_height - 1.3*cm, f"PIN CODE: {pin_code}")
            
            # === GREEN BANNER ===
            c.setFillColor(colors.HexColor('#6cbc1e'))
            c.rect(0, page_height - 2.5*cm, page_width, 1*cm, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*cm, page_height - 2.2*cm, "✓ Your booking is confirmed")
            c.setFont("Helvetica", 9)
            c.drawRightString(page_width - 1*cm, page_height - 2.2*cm, f"Confirmation: {confirmation_no}")
            
            # === HOTEL INFO WITH PHOTO ===
            hotel_y = page_height - 3.8*cm
            
            # Hotel photo
            try:
                hotel_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'assets', 'download.jpeg')
                
                if os.path.exists(hotel_image_path):
                    img = Image.open(hotel_image_path)
                    max_width = 3*cm
                    max_height = 2.5*cm
                    aspect = img.width / img.height
                    
                    if aspect > (max_width / max_height):
                        img_width = max_width
                        img_height = max_width / aspect
                    else:
                        img_height = max_height
                        img_width = max_height * aspect
                    
                    x_offset = 1*cm + (max_width - img_width) / 2
                    y_offset = (hotel_y - 2.7*cm) + (max_height - img_height) / 2
                    
                    c.drawImage(hotel_image_path, x_offset, y_offset, 
                               width=img_width, height=img_height, mask='auto')
                else:
                    c.setFillColor(colors.HexColor('#e0e0e0'))
                    c.rect(1*cm, hotel_y - 2.7*cm, 3*cm, 2.5*cm, fill=True, stroke=False)
                
                c.setStrokeColor(colors.HexColor('#cccccc'))
                c.setLineWidth(0.5)
                c.rect(1*cm, hotel_y - 2.7*cm, 3*cm, 2.5*cm, fill=False, stroke=True)
                
            except Exception as e:
                logger.warning(f"Failed to load hotel image: {e}")
                c.setFillColor(colors.HexColor('#e0e0e0'))
                c.rect(1*cm, hotel_y - 2.7*cm, 3*cm, 2.5*cm, fill=True, stroke=False)
                c.setStrokeColor(colors.HexColor('#cccccc'))
                c.setLineWidth(0.5)
                c.rect(1*cm, hotel_y - 2.7*cm, 3*cm, 2.5*cm, fill=False, stroke=True)
            
            # Hotel details
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(4.5*cm, hotel_y - 0.5*cm, hotel_name)
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7)
            c.drawString(4.5*cm, hotel_y - 0.85*cm, f"{hotel_address}")
            c.drawString(4.5*cm, hotel_y - 1.15*cm, f"Phone: {phone}")
            
            rating = self._get_value('hotel.rating', 'hotel_booking.rating') or '8.9/10 Excellent'
            c.setFillColor(colors.HexColor('#febb02'))
            c.setFont("Helvetica", 8)
            c.drawString(4.5*cm, hotel_y - 1.5*cm, f"★★★★ | Rating: {rating}")
            
            # === BOOKING DETAILS BOX ===
            details_y = hotel_y - 3.8*cm
            
            # Light gray box
            c.setFillColor(colors.HexColor('#f5f8fa'))
            c.rect(1*cm, details_y - 3.5*cm, page_width - 2*cm, 3.5*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#d0d0d0'))
            c.setLineWidth(0.5)
            c.rect(1*cm, details_y - 3.5*cm, page_width - 2*cm, 3.5*cm, fill=False, stroke=True)
            
            # Guest name
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1.5*cm, details_y - 0.6*cm, "GUEST NAME")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(1.5*cm, details_y - 1*cm, guest_name or 'Guest')
            
            # Check-in
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1.5*cm, details_y - 1.7*cm, "CHECK-IN")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(1.5*cm, details_y - 2.1*cm, check_in)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(1.5*cm, details_y - 2.4*cm, "from 15:00")
            
            # Check-out
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(8*cm, details_y - 1.7*cm, "CHECK-OUT")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 9)
            c.drawString(8*cm, details_y - 2.1*cm, check_out)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(8*cm, details_y - 2.4*cm, "until 11:00")
            
            # Room type
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1.5*cm, details_y - 3*cm, "ROOM TYPE")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8)
            c.drawString(1.5*cm, details_y - 3.3*cm, room_type)
            
            # Nights
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(8*cm, details_y - 3*cm, f"{nights} NIGHT{'S' if nights > 1 else ''}")
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 8)
            c.drawString(8*cm, details_y - 3.3*cm, f"{guests_count} adult")
            
            # === TOTAL PRICE BOX ===
            price_y = details_y - 4.8*cm
            
            c.setFillColor(colors.HexColor('#fff4e6'))
            c.rect(1*cm, price_y - 1.8*cm, page_width - 2*cm, 1.8*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#ffe0b2'))
            c.setLineWidth(0.5)
            c.rect(1*cm, price_y - 1.8*cm, page_width - 2*cm, 1.8*cm, fill=False, stroke=True)
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1.5*cm, price_y - 0.6*cm, "TOTAL PRICE")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 16)
            c.drawRightString(page_width - 1.5*cm, price_y - 0.7*cm, f"€ {total_price}")
            
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(1.5*cm, price_y - 1*cm, f"For {nights} night{'s' if nights > 1 else ''} • {guests_count} adult")
            c.drawRightString(page_width - 1.5*cm, price_y - 1*cm, "Includes taxes and fees")
            
            # === IMPORTANT INFORMATION (Brief) ===
            info_y = price_y - 2.8*cm
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 9)
            c.drawString(1*cm, info_y, "Important information:")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7)
            c.drawString(1*cm, info_y - 0.4*cm, "• Please bring this confirmation and a valid ID when checking in")
            c.drawString(1*cm, info_y - 0.7*cm, "• Payment will be collected at the property  • Cancellation policy: Free cancellation until 24 hours before check-in")
            c.drawString(1*cm, info_y - 1*cm, f"• For questions, contact the hotel at: {phone}")
            
            # === CANCELLATION POLICY (Brief) ===
            cancel_y = info_y - 1.8*cm
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1*cm, cancel_y, "Cancellation policy:")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7)
            c.drawString(1*cm, cancel_y - 0.35*cm, "Free cancellation until 7 days before arrival. After that, you will be charged 100% of the booking if canceled or in case of no-show.")
            
            # === ADDITIONAL INFO (Brief) ===
            addinfo_y = cancel_y - 1.2*cm
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1*cm, addinfo_y, "Additional information:")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7)
            c.drawString(1*cm, addinfo_y - 0.35*cm, "Meal Plan: No meals included. Facilities: Shower, Toilet, Linen, Socket near bed, Shared bathroom.")
            
            # === NEED HELP SECTION (Brief) ===
            help_y = addinfo_y - 1.2*cm
            
            c.setFillColor(colors.HexColor('#003580'))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(1*cm, help_y, "Need help?")
            
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 7)
            c.drawString(1*cm, help_y - 0.35*cm, f"Contact {hotel_name} directly at {phone} or email: {email}")
            c.drawString(1*cm, help_y - 0.65*cm, "For booking changes: your.booking.com | 24/7 support: +44 20 3320 2609")
            
            # === FOOTER ===
            c.setFillColor(colors.HexColor('#999999'))
            c.setFont("Helvetica", 7)
            c.drawCentredString(page_width / 2, 1.8*cm, f"This confirmation was sent to: {email}")
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(page_width / 2, 1.5*cm, "Booking.com B.V. | Herengracht 597, 1017 CE Amsterdam, Netherlands")
            
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
        """Generate premium airline e-ticket with real barcode"""
        doc_record = self._create_document_record("air_ticket", "E-Ticket_Flight_Confirmation.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get flight data
            passenger_name = self._get_value('passport_copy.full_name', 'nid_bangla.name_english', 'personal.full_name')
            passport_no = self._get_value('passport_copy.passport_number', 'personal.passport_number') or 'A15327894'
            departure_date = self._get_value('flight.departure_date', 'air_ticket.departure_date', 'travel.arrival_date') or datetime.now().strftime('%Y-%m-%d')
            return_date = self._get_value('flight.return_date', 'air_ticket.return_date', 'travel.departure_date') or (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            pnr = self._get_value('flight.pnr', 'air_ticket.pnr') or f'P{hash(passenger_name or "X") % 10000:04d}'
            ticket_no = self._get_value('flight.ticket_number', 'air_ticket.ticket_number') or f'176-{datetime.now().year}{hash(passenger_name or "X") % 100000000:09d}'
            
            self._update_progress(doc_record, 30)
            
            # Create PDF with professional airline style
            from reportlab.pdfgen import canvas as pdf_canvas
            from reportlab.lib.units import cm
            from reportlab.graphics.barcode import code128
            from reportlab.graphics import renderPDF
            
            c = pdf_canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # === HEADER: Icelandair branding ===
            c.setFillColor(colors.HexColor('#d71921'))  # Icelandair red
            c.rect(0, page_height - 2.5*cm, page_width, 2.5*cm, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 24)
            c.drawString(1.5*cm, page_height - 1.7*cm, "ICELANDAIR")
            
            c.setFont("Helvetica", 10)
            c.drawString(1.5*cm, page_height - 2.2*cm, "Electronic Ticket Confirmation")
            
            # === BLUE INFO BANNER ===
            c.setFillColor(colors.HexColor('#003f87'))  # Icelandair blue
            c.rect(0, page_height - 3.5*cm, page_width, 1*cm, fill=True, stroke=False)
            
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(1.5*cm, page_height - 3.1*cm, f"PNR: {pnr}")
            c.drawRightString(page_width - 1.5*cm, page_height - 3.1*cm, f"E-Ticket: {ticket_no}")
            
            # === PASSENGER INFORMATION BOX ===
            pass_y = page_height - 5*cm
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#003f87'))
            c.drawString(1.5*cm, pass_y, "PASSENGER INFORMATION")
            
            # Info grid
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.black)
            c.drawString(1.5*cm, pass_y - 0.7*cm, f"Name: {passenger_name or 'N/A'}")
            c.drawString(1.5*cm, pass_y - 1.2*cm, "Ticket Type: Economy")
            
            c.drawString(10*cm, pass_y - 0.7*cm, f"Passport: {passport_no}")
            c.drawString(10*cm, pass_y - 1.2*cm, "Baggage: 23kg (1 piece)")
            
            # === OUTBOUND FLIGHT SECTION ===
            out_y = pass_y - 2.5*cm
            
            c.setStrokeColor(colors.HexColor('#cccccc'))
            c.setLineWidth(0.5)
            c.line(1.5*cm, out_y, page_width - 1.5*cm, out_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#d71921'))
            c.drawString(1.5*cm, out_y - 0.7*cm, "OUTBOUND FLIGHT")
            
            # Flight details box with table-like structure
            box_y = out_y - 1.5*cm
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(1.5*cm, box_y - 2*cm, page_width - 3*cm, 2*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#dee2e6'))
            c.setLineWidth(0.5)
            c.rect(1.5*cm, box_y - 2*cm, page_width - 3*cm, 2*cm, fill=False, stroke=True)
            
            # Route
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(2*cm, box_y - 0.6*cm, "DAC  →  KEF")
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(2*cm, box_y - 1*cm, "Dhaka  →  Reykjavik")
            
            # Date & Times
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawString(6*cm, box_y - 0.6*cm, f"Date: {departure_date}")
            c.setFont("Helvetica", 8)
            c.drawString(6*cm, box_y - 1*cm, "Departure: 10:30 AM")
            c.drawString(6*cm, box_y - 1.35*cm, "Arrival: 02:45 PM")
            
            # Flight info
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawString(11*cm, box_y - 0.6*cm, "Flight: FI 447")
            c.setFont("Helvetica", 8)
            c.drawString(11*cm, box_y - 1*cm, "Class: Y (Economy)")
            c.drawString(11*cm, box_y - 1.35*cm, "Duration: ~11h 15m")
            
            # === RETURN FLIGHT SECTION ===
            ret_y = box_y - 3.5*cm
            
            c.setStrokeColor(colors.HexColor('#cccccc'))
            c.line(1.5*cm, ret_y, page_width - 1.5*cm, ret_y)
            
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor('#d71921'))
            c.drawString(1.5*cm, ret_y - 0.7*cm, "RETURN FLIGHT")
            
            # Return flight box
            ret_box_y = ret_y - 1.5*cm
            c.setFillColor(colors.HexColor('#f8f9fa'))
            c.rect(1.5*cm, ret_box_y - 2*cm, page_width - 3*cm, 2*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#dee2e6'))
            c.rect(1.5*cm, ret_box_y - 2*cm, page_width - 3*cm, 2*cm, fill=False, stroke=True)
            
            # Route
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.black)
            c.drawString(2*cm, ret_box_y - 0.6*cm, "KEF  →  DAC")
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawString(2*cm, ret_box_y - 1*cm, "Reykjavik  →  Dhaka")
            
            # Date & Times
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawString(6*cm, ret_box_y - 0.6*cm, f"Date: {return_date}")
            c.setFont("Helvetica", 8)
            c.drawString(6*cm, ret_box_y - 1*cm, "Departure: 04:15 PM")
            c.drawString(6*cm, ret_box_y - 1.35*cm, "Arrival: 05:30 AM +1")
            
            # Flight info
            c.setFont("Helvetica-Bold", 9)
            c.setFillColor(colors.black)
            c.drawString(11*cm, ret_box_y - 0.6*cm, "Flight: FI 448")
            c.setFont("Helvetica", 8)
            c.drawString(11*cm, ret_box_y - 1*cm, "Class: Y (Economy)")
            c.drawString(11*cm, ret_box_y - 1.35*cm, "Duration: ~10h 15m")
            
            # === REAL BARCODE GENERATION ===
            barcode_y = ret_box_y - 3.5*cm
            
            try:
                # Generate real Code128 barcode
                barcode_data = f"{ticket_no}"
                barcode_obj = code128.Code128(barcode_data, barHeight=1.2*cm, barWidth=1)
                barcode_obj.drawOn(c, 2*cm, barcode_y - 1*cm)
                
                # Barcode label
                c.setFont("Helvetica", 7)
                c.setFillColor(colors.HexColor('#666666'))
                c.drawCentredString(page_width/2, barcode_y - 1.5*cm, f"E-Ticket: {ticket_no}")
            except Exception as e:
                logger.warning(f"Barcode generation failed: {e}. Using placeholder.")
                # Fallback: barcode placeholder
                c.setStrokeColor(colors.black)
                c.setLineWidth(1)
                c.rect(2*cm, barcode_y - 1*cm, 14*cm, 1.2*cm, fill=False, stroke=True)
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.HexColor('#666666'))
                c.drawCentredString(page_width/2, barcode_y - 0.5*cm, f"|||  ||||| ||  {ticket_no}  || ||||| |||")
            
            # === IMPORTANT INFORMATION BOX ===
            info_y = barcode_y - 3*cm
            
            c.setFillColor(colors.HexColor('#fff3cd'))
            c.rect(1.5*cm, info_y - 2.5*cm, page_width - 3*cm, 2.5*cm, fill=True, stroke=False)
            c.setStrokeColor(colors.HexColor('#ffc107'))
            c.setLineWidth(0.5)
            c.rect(1.5*cm, info_y - 2.5*cm, page_width - 3*cm, 2.5*cm, fill=False, stroke=True)
            
            c.setFillColor(colors.HexColor('#856404'))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, info_y - 0.6*cm, "IMPORTANT INFORMATION")
            
            c.setFont("Helvetica", 8)
            c.drawString(2*cm, info_y - 1.1*cm, "• Please arrive at the airport at least 3 hours before departure")
            c.drawString(2*cm, info_y - 1.5*cm, "• Carry your passport and this e-ticket confirmation")
            c.drawString(2*cm, info_y - 1.9*cm, "• Online check-in opens 24 hours before departure at www.icelandair.com")
            c.drawString(2*cm, info_y - 2.3*cm, "• Baggage allowance: 1 piece (23kg) + 1 carry-on (10kg)")
            
            # === FOOTER ===
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor('#666666'))
            c.drawCentredString(page_width/2, 2*cm, f"This is your electronic ticket confirmation | PNR: {pnr} | Ticket: {ticket_no}")
            c.drawCentredString(page_width/2, 1.5*cm, f"Issued: {datetime.now().strftime('%d %B %Y, %H:%M')} | For inquiries: www.icelandair.com")
            
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
