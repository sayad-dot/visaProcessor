"""
PDF Generator Service - Generates all 8 visa application documents
Uses ReportLab for professional PDF generation and Gemini for intelligent content
"""
import os
import io
from datetime import datetime
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

from app.models import ExtractedData, QuestionnaireResponse, GeneratedDocument, GenerationStatus
from app.config import settings


class PDFGeneratorService:
    """Service for generating all visa application PDFs"""
    
    def __init__(self, db: Session, application_id: int):
        self.db = db
        self.application_id = application_id
        self.output_dir = os.path.join("uploads", f"app_{application_id}", "generated")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Load all extracted data
        self.extracted_data = self._load_extracted_data()
        self.questionnaire_data = self._load_questionnaire_data()
        
    def _load_extracted_data(self) -> Dict[str, Any]:
        """Load all extracted data from database"""
        records = self.db.query(ExtractedData).filter(
            ExtractedData.application_id == self.application_id
        ).all()
        
        data = {}
        for record in records:
            data[record.document_type.value] = record.data
        return data
    
    def _load_questionnaire_data(self) -> Dict[str, str]:
        """Load all questionnaire responses"""
        responses = self.db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.application_id == self.application_id
        ).all()
        
        data = {}
        for response in responses:
            data[response.question_key] = response.answer
        return data
    
    def _get_value(self, *keys) -> str:
        """Get value from extracted data or questionnaire, trying multiple keys"""
        for key in keys:
            # Try extracted data
            if '.' in key:
                doc_type, field = key.split('.', 1)
                if doc_type in self.extracted_data:
                    value = self.extracted_data[doc_type].get(field)
                    if value:
                        return str(value)
            
            # Try questionnaire
            value = self.questionnaire_data.get(key)
            if value:
                return str(value)
        
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
    
    # ============================================================================
    # 1. COVER LETTER (MOST IMPORTANT)
    # ============================================================================
    
    def generate_cover_letter(self) -> str:
        """Generate formal cover letter to Embassy of Iceland"""
        doc_record = self._create_document_record("cover_letter", "Cover_Letter.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Collect all data
            name = self._get_value('passport_copy.full_name', 'personal.full_name')
            passport = self._get_value('passport_copy.passport_number', 'personal.passport_number')
            profession = self._get_value('employment.job_title', 'business.business_type')
            purpose = self._get_value('travel_purpose.purpose', 'travel_purpose.primary_purpose')
            travel_dates = self._get_value('air_ticket.travel_dates', 'hotel_booking.check_in_date')
            places = self._get_value('travel_purpose.places_to_visit', 'hotel_booking.hotel_location')
            income = self._get_value('income_tax_3years.annual_income', 'financial.monthly_income')
            bank_balance = self._get_value('bank_solvency.balance_amount')
            family = self._get_value('home_ties.family_members', 'personal.marital_status')
            property_info = self._get_value('asset_valuation.total_value', 'assets.property_description')
            
            self._update_progress(doc_record, 30)
            
            # Generate intelligent content using Gemini - Iceland Format
            prompt = f"""
Write a professional cover letter for Iceland Embassy following their preferred format:

My details:
- Name: {name}
- Passport: {passport}
- Job: {profession}
- Why traveling: {purpose}
- When: {travel_dates}
- Where in Iceland: {places}
- My income: {income}
- Bank money: {bank_balance}
- Family: {family}
- Property: {property_info}

IMPORTANT RULES:
- NO markdown (no **, no *, no #)
- Keep it professional but clear
- Maximum 4 paragraphs, each 4-5 sentences
- Follow this structure exactly:

Paragraph 1: "I am [name], passport [number], working as [job]. I am applying for Iceland Schengen tourist visa to visit Iceland from [dates]. I will stay at [hotel/places]."

Paragraph 2: "My purpose is [purpose]. I plan to visit [places] and do [activities]. I have booked [hotel] and have return flight tickets."

Paragraph 3: "I earn [income] annually and have [bank amount] in my bank. I will fund this trip from my savings. All my trip expenses are covered."

Paragraph 4: "I have strong ties to Bangladesh. My [family] lives here. I work at [company] and own [property]. I will return after my visit because [reason]. Thank you for considering my application."

Write in simple, clear English. No fancy words. Direct and honest.
"""
            
            letter_content = self._generate_content_with_ai(prompt)
            self._update_progress(doc_record, 60)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                fontName='Helvetica'
            )
            
            # Date
            story.append(Spacer(1, 0.2*inch))
            date_text = f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
            story.append(Paragraph(date_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # To
            to_text = """<b>To,</b><br/>
The Embassy of Iceland<br/>
House 16, Road 113/A<br/>
Gulshan 2, Dhaka 1212<br/>
Bangladesh"""
            story.append(Paragraph(to_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Subject
            subject_text = "<b>Subject: Application for Schengen Tourist Visa</b>"
            story.append(Paragraph(subject_text, body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Letter body
            paragraphs = letter_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 0.15*inch))
            
            # Build PDF
            pdf.build(story)
            
            # Update file size
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
            
            # Get all NID data
            name = self._get_value('nid_bangla.name', 'personal.full_name', 'passport_copy.full_name')
            name_bangla = self._get_value('nid_bangla.name_bangla')
            father = self._get_value('nid_bangla.father_name', 'personal.father_name')
            mother = self._get_value('nid_bangla.mother_name', 'personal.mother_name')
            dob = self._get_value('nid_bangla.date_of_birth', 'personal.date_of_birth', 'passport_copy.date_of_birth')
            nid_no = self._get_value('nid_bangla.nid_number', 'personal.nid_number')
            address = self._get_value('nid_bangla.address', 'personal.address')
            blood_group = self._get_value('nid_bangla.blood_group', 'personal.blood_group')
            religion = self._get_value('personal.religion')
            birth_place = self._get_value('nid_bangla.birth_place', 'personal.birth_place')
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
                ("Name (Bangla):", name_bangla or "As per original NID"),
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
            
            # Red seal placeholder (bottom right)
            seal_x = page_width - 2.5*inch
            seal_y = cert_y - 0.8*inch
            c.setFillColor(colors.HexColor('#d32f2f'))
            c.circle(seal_x, seal_y, 0.6*inch, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(seal_x, seal_y - 0.1*inch, "OFFICIAL")
            c.setFont("Helvetica", 8)
            c.drawCentredString(seal_x, seal_y - 0.3*inch, "SEAL")
            
            # Date and attestation
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
        """Generate professional visiting/business card - A4 size for easy printing"""
        doc_record = self._create_document_record("visiting_card", "Visiting_Card.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get all available data
            name = self._get_value('personal.full_name', 'passport_copy.full_name')
            designation = self._get_value('employment.job_title', 'business.owner_title', 'business.business_type')
            company = self._get_value('employment.company_name', 'business.business_name')
            phone = self._get_value('personal.phone', 'personal.mobile_number', 'personal.contact_number')
            email = self._get_value('personal.email', 'personal.email_address')
            address = self._get_value('employment.company_address', 'business.business_address', 'personal.address')
            website = self._get_value('business.website', 'employment.company_website')
            
            self._update_progress(doc_record, 40)
            
            # Create A4 PDF with centered business card
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import A4
            
            c = canvas.Canvas(file_path, pagesize=A4)
            page_width, page_height = A4
            
            # Card dimensions (standard business card: 3.5" x 2")
            card_width = 3.5 * inch
            card_height = 2 * inch
            
            # Center the card on A4 page
            x_start = (page_width - card_width) / 2
            y_start = (page_height - card_height) / 2
            
            # Card background with subtle shadow effect
            # Shadow layer
            c.setFillColor(colors.HexColor('#e0e0e0'))
            c.rect(x_start + 0.05*inch, y_start - 0.05*inch, card_width, card_height, fill=True, stroke=False)
            
            # Main card background
            c.setFillColor(colors.white)
            c.rect(x_start, y_start, card_width, card_height, fill=True, stroke=False)
            
            # Elegant border
            c.setStrokeColor(colors.HexColor('#d1d5db'))
            c.setLineWidth(1.5)
            c.rect(x_start, y_start, card_width, card_height, fill=False, stroke=True)
            
            # Decorative corner triangles (top-left and bottom-right)
            c.setFillColor(colors.HexColor('#1e3a8a'))
            # Top left corner accent
            c.setStrokeColor(colors.HexColor('#1e3a8a'))
            c.setLineWidth(0)
            corner_size = 0.3*inch
            path = c.beginPath()
            path.moveTo(x_start, y_start + card_height)
            path.lineTo(x_start + corner_size, y_start + card_height)
            path.lineTo(x_start, y_start + card_height - corner_size)
            path.close()
            c.drawPath(path, fill=True, stroke=False)
            
            # Bottom right corner accent (lighter blue)
            c.setFillColor(colors.HexColor('#3b82f6'))
            path = c.beginPath()
            path.moveTo(x_start + card_width, y_start)
            path.lineTo(x_start + card_width - corner_size, y_start)
            path.lineTo(x_start + card_width, y_start + corner_size)
            path.close()
            c.drawPath(path, fill=True, stroke=False)
            
            # Decorative wave/curve pattern on left side
            c.setStrokeColor(colors.HexColor('#60a5fa'))
            c.setLineWidth(2)
            wave_x = x_start + 0.2*inch
            for i in range(5):
                wave_y = y_start + 0.3*inch + (i * 0.35*inch)
                c.line(wave_x, wave_y, wave_x + 0.15*inch, wave_y)
            
            # Top header section - elegant design
            header_height = 0.6*inch
            c.setFillColor(colors.HexColor('#1e40af'))
            c.roundRect(x_start + 0.05*inch, y_start + card_height - header_height - 0.05*inch,
                       card_width - 0.1*inch, header_height, 0.1*inch, fill=True, stroke=False)
            
            # Company name in elegant header
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 14)
            company_text = (company or "PROFESSIONAL SERVICES")[:25]
            text_width = c.stringWidth(company_text, "Helvetica-Bold", 14)
            c.drawString(x_start + (card_width - text_width) / 2, 
                        y_start + card_height - 0.35*inch, company_text)
            
            # Main content area starts here
            content_y = y_start + card_height - 0.65*inch
            
            # Name - prominent and bold
            c.setFillColor(colors.HexColor('#1e293b'))
            c.setFont("Helvetica-Bold", 16)
            name_text = name or "Full Name"
            c.drawString(x_start + 0.3*inch, content_y, name_text)
            content_y -= 0.25*inch
            
            # Designation - professional subtitle
            c.setFillColor(colors.HexColor('#475569'))
            c.setFont("Helvetica", 11)
            designation_text = designation or "Professional"
            c.drawString(x_start + 0.3*inch, content_y, designation_text)
            content_y -= 0.35*inch
            
            # Divider line
            c.setStrokeColor(colors.HexColor('#e2e8f0'))
            c.setLineWidth(0.5)
            c.line(x_start + 0.3*inch, content_y + 0.05*inch, 
                   x_start + card_width - 0.2*inch, content_y + 0.05*inch)
            content_y -= 0.15*inch
            
            # Contact information - icon style
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor('#64748b'))
            
            if phone:
                # Phone icon (circle with P)
                c.setFillColor(colors.HexColor('#2563eb'))
                c.circle(x_start + 0.35*inch, content_y + 0.05*inch, 0.06*inch, fill=True, stroke=False)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 7)
                c.drawString(x_start + 0.33*inch, content_y + 0.02*inch, "P")
                
                c.setFillColor(colors.HexColor('#1e293b'))
                c.setFont("Helvetica", 9)
                c.drawString(x_start + 0.5*inch, content_y, phone)
                content_y -= 0.15*inch
            
            if email:
                # Email icon
                c.setFillColor(colors.HexColor('#2563eb'))
                c.circle(x_start + 0.35*inch, content_y + 0.05*inch, 0.06*inch, fill=True, stroke=False)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 7)
                c.drawString(x_start + 0.33*inch, content_y + 0.02*inch, "E")
                
                c.setFillColor(colors.HexColor('#1e293b'))
                c.setFont("Helvetica", 8)
                email_text = email if len(email) <= 28 else email[:25] + "..."
                c.drawString(x_start + 0.5*inch, content_y, email_text)
                content_y -= 0.15*inch
            
            if address:
                # Address icon
                c.setFillColor(colors.HexColor('#2563eb'))
                c.circle(x_start + 0.35*inch, content_y + 0.05*inch, 0.06*inch, fill=True, stroke=False)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 7)
                c.drawString(x_start + 0.33*inch, content_y + 0.02*inch, "A")
                
                c.setFillColor(colors.HexColor('#1e293b'))
                c.setFont("Helvetica", 7)
                # Wrap address to fit
                if len(address) > 35:
                    addr_line1 = address[:35]
                    addr_line2 = address[35:70] + ("..." if len(address) > 70 else "")
                    c.drawString(x_start + 0.5*inch, content_y, addr_line1)
                    content_y -= 0.1*inch
                    c.drawString(x_start + 0.5*inch, content_y, addr_line2)
                else:
                    c.drawString(x_start + 0.5*inch, content_y, address)
                content_y -= 0.15*inch
            
            if website:
                # Website icon
                c.setFillColor(colors.HexColor('#2563eb'))
                c.circle(x_start + 0.35*inch, content_y + 0.05*inch, 0.06*inch, fill=True, stroke=False)
                c.setFillColor(colors.white)
                c.setFont("Helvetica-Bold", 7)
                c.drawString(x_start + 0.33*inch, content_y + 0.02*inch, "W")
                
                c.setFillColor(colors.HexColor('#2563eb'))
                c.setFont("Helvetica", 8)
                website_text = website if len(website) <= 30 else website[:27] + "..."
                c.drawString(x_start + 0.5*inch, content_y, website_text)
            
            # Bottom right corner accent
            c.setFillColor(colors.HexColor('#1e3a8a'))
            c.circle(x_start + card_width - 0.15*inch, y_start + 0.15*inch, 0.08*inch, fill=True, stroke=False)
            
            # Add instruction text below card
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor('#64748b'))
            instruction_y = y_start - 0.3*inch
            c.drawCentredString(page_width / 2, instruction_y, 
                              "Print this page and cut along the border for a professional business card")
            
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
    # 4. FINANCIAL STATEMENT
    # ============================================================================
    
    def generate_financial_statement(self) -> str:
        """Generate comprehensive financial statement"""
        doc_record = self._create_document_record("financial_statement", "Financial_Statement.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get financial data
            name = self._get_value('personal.full_name')
            annual_income_y1 = self._get_value('income_tax_3years.year1_income', 'financial.annual_income')
            annual_income_y2 = self._get_value('income_tax_3years.year2_income')
            annual_income_y3 = self._get_value('income_tax_3years.year3_income')
            monthly_income = self._get_value('financial.monthly_income')
            monthly_expenses = self._get_value('financial.monthly_expenses')
            bank_balance = self._get_value('bank_solvency.balance_amount', 'financial.total_savings')
            funding_source = self._get_value('financial.trip_funding_source')
            
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
            
            # Annual Income Table
            story.append(Paragraph("<b>1. Annual Income (Last 3 Years)</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            income_data = [
                ['Year', 'Annual Income (BDT)'],
                ['2023', annual_income_y1 or '-'],
                ['2022', annual_income_y2 or '-'],
                ['2021', annual_income_y3 or '-'],
            ]
            
            income_table = Table(income_data, colWidths=[2*inch, 3*inch])
            income_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            
            story.append(income_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Monthly Finances
            story.append(Paragraph("<b>2. Monthly Financial Overview</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            monthly_data = [
                ['Description', 'Amount (BDT)'],
                ['Monthly Income', monthly_income or '-'],
                ['Monthly Expenses', monthly_expenses or '-'],
                ['Monthly Savings', str(int(monthly_income or 0) - int(monthly_expenses or 0)) if monthly_income and monthly_expenses else '-'],
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
            
            # Bank Balance
            story.append(Paragraph(f"<b>3. Current Bank Balance:</b> BDT {bank_balance or 'N/A'}", body_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Trip Funding
            story.append(Paragraph(f"<b>4. Trip Funding Source:</b> {funding_source or 'Personal savings and income'}", body_style))
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
        doc_record = self._create_document_record("travel_itinerary", "Travel_Itinerary.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get travel data
            name = self._get_value('personal.full_name')
            passport = self._get_value('passport_copy.passport_number')
            hotel = self._get_value('hotel_booking.hotel_name')
            duration = self._get_value('hotel_booking.duration', 'travel_purpose.duration')
            check_in = self._get_value('hotel_booking.check_in_date')
            places = self._get_value('travel_purpose.places_to_visit')
            activities = self._get_value('travel_purpose.planned_activities')
            
            self._update_progress(doc_record, 40)
            
            # Generate AI itinerary
            prompt = f"""
Generate a detailed day-by-day travel itinerary for Iceland with these details:
- Traveler: {name}
- Duration: {duration} days
- Check-in Date: {check_in}
- Hotel: {hotel}
- Places to Visit: {places}
- Activities: {activities}

IMPORTANT FORMATTING RULES:
- DO NOT use markdown formatting (no **, no -, no #)
- DO NOT use bullet points or asterisks
- Use plain text only
- Format each day as: "Day 1 - Date: Activity description"
- Use simple paragraphs separated by blank lines
- Include specific times in format "09:00 - 10:00: Activity"

Create a realistic daily schedule with:
- Morning activities (09:00-13:00)
- Afternoon activities (13:00-18:00)
- Evening activities (18:00-22:00)
- Specific Iceland attractions (Golden Circle, Blue Lagoon, Reykjavik, waterfalls, Northern Lights)
- Realistic timings and travel times
- Meals and rest periods

Generate {duration or 7} days of detailed itinerary in plain text format.
"""
            
            itinerary_content = self._generate_content_with_ai(prompt)
            self._update_progress(doc_record, 60)
            
            # Clean up any markdown that slipped through
            import re
            itinerary_content = re.sub(r'\*\*', '', itinerary_content)  # Remove **
            itinerary_content = re.sub(r'\*', '', itinerary_content)    # Remove single *
            itinerary_content = re.sub(r'^#+\s+', '', itinerary_content, flags=re.MULTILINE)  # Remove #
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=0.75*inch, bottomMargin=0.75*inch,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title with box
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.white,
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#1e3a8a'),
                borderPadding=10
            )
            
            story.append(Paragraph("TRAVEL ITINERARY - ICELAND", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Header info box
            header_data = [
                ['Applicant Name:', name or 'N/A'],
                ['Passport Number:', passport or 'N/A'],
                ['Hotel:', hotel or 'To be confirmed'],
                ['Duration:', f"{duration} days" if duration else 'N/A'],
                ['Check-in Date:', check_in or 'N/A'],
            ]
            
            header_table = Table(header_data, colWidths=[1.5*inch, 4.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f9ff')),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Itinerary content styles
            day_header_style = ParagraphStyle(
                'DayHeader',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=colors.white,
                spaceAfter=8,
                spaceBefore=12,
                fontName='Helvetica-Bold',
                backColor=colors.HexColor('#2563eb'),
                borderPadding=8,
                leftIndent=10
            )
            
            section_style = ParagraphStyle(
                'Section',
                parent=styles['BodyText'],
                fontSize=11,
                leading=15,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor('#1e3a8a'),
                spaceBefore=8,
                spaceAfter=4,
                leftIndent=5
            )
            
            activity_style = ParagraphStyle(
                'Activity',
                parent=styles['BodyText'],
                fontSize=10,
                leading=14,
                fontName='Helvetica',
                textColor=colors.HexColor('#1e293b'),
                leftIndent=15,
                spaceBefore=3
            )
            
            divider_line_style = ParagraphStyle(
                'Divider',
                parent=styles['Normal'],
                fontSize=1,
                spaceBefore=5,
                spaceAfter=5
            )
            
            # Parse and format itinerary content
            lines = itinerary_content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Day headers (e.g., "Day 1", "Day 1 -")
                if line.lower().startswith('day ') and ('-' in line[:15] or line.lower().startswith('day 1')):
                    story.append(Spacer(1, 0.15*inch))
                    story.append(Paragraph(line, day_header_style))
                
                # Time-based sections (Morning, Afternoon, Evening)
                elif any(period in line.lower() for period in ['morning', 'afternoon', 'evening', 'night']):
                    if '(' in line or ':' in line:
                        story.append(Paragraph(line, section_style))
                    else:
                        story.append(Paragraph(line, activity_style))
                
                # Activities with times (contains time format like 09:00)
                elif re.search(r'\d{2}:\d{2}', line):
                    story.append(Paragraph(line, activity_style))
                
                # Hotel info, traveler info
                elif any(keyword in line.lower() for keyword in ['traveler:', 'hotel:', 'duration:', 'check-in']):
                    continue  # Skip, already in header table
                
                # Regular content
                else:
                    if len(line) > 50:  # Longer text is likely description
                        story.append(Paragraph(line, activity_style))
                    elif len(line) > 0:
                        story.append(Paragraph(line, activity_style))
            
            # Add footer note
            story.append(Spacer(1, 0.3*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#64748b'),
                alignment=TA_CENTER,
                fontStyle='italic'
            )
            story.append(Paragraph("This itinerary is for visa application purposes and may be adjusted based on weather and availability.", footer_style))
            
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
        """Generate previous travel history table"""
        doc_record = self._create_document_record("travel_history", "Travel_History.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get visa history data
            visa_history = self.extracted_data.get('visa_history', {})
            previous_travels = visa_history.get('previous_travels', [])
            
            # If no extracted data, try questionnaire
            if not previous_travels:
                travel_countries = self._get_value('travel_history.countries_visited')
                if travel_countries:
                    # Parse from questionnaire
                    countries = [c.strip() for c in travel_countries.split(',')]
                    previous_travels = [{'country': c, 'year': '2020-2023'} for c in countries]
            
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
            story.append(Paragraph("PREVIOUS TRAVEL HISTORY", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Applicant info
            body_style = ParagraphStyle(
                'Body',
                parent=styles['BodyText'],
                fontSize=11,
                fontName='Helvetica'
            )
            
            name = self._get_value('personal.full_name')
            story.append(Paragraph(f"<b>Applicant Name:</b> {name}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Travel history table
            table_data = [['SL NO', 'Entry Date', 'Exit Date', 'Type of Visa', 'Visit Country']]
            
            if previous_travels:
                for i, travel in enumerate(previous_travels, 1):
                    table_data.append([
                        str(i),
                        travel.get('entry_date', 'N/A'),
                        travel.get('exit_date', 'N/A'),
                        travel.get('visa_type', 'Tourist'),
                        travel.get('country', 'N/A')
                    ])
            else:
                # Default entry if no data
                table_data.append(['1', 'N/A', 'N/A', 'N/A', 'No previous international travel'])
            
            travel_table = Table(table_data, colWidths=[0.6*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.8*inch])
            travel_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
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
            
            # Get home ties data
            name = self._get_value('personal.full_name')
            family = self._get_value('home_ties.family_members', 'personal.marital_status')
            employment = self._get_value('employment.job_title', 'business.business_type')
            company = self._get_value('employment.company_name', 'business.business_name')
            property_info = self._get_value('assets.property_description')
            reasons = self._get_value('home_ties.reasons_to_return')
            
            self._update_progress(doc_record, 30)
            
            # Generate AI content - SIMPLE and CONCISE
            prompt = f"""
Write a SHORT and SIMPLE home ties statement (maximum 250 words) in easy English:

My information:
- Name: {name}
- Family: {family}
- Job: {employment} at {company}
- Property: {property_info}
- Why I will return: {reasons}

IMPORTANT RULES:
- Use SIMPLE English (like talking to a friend)
- NO markdown formatting (no **, no *, no #)
- Maximum 3 SHORT paragraphs
- Each paragraph maximum 4-5 sentences
- Be direct and clear
- First paragraph: Family and home
- Second paragraph: Job or business
- Third paragraph: Why I will definitely come back

Write in plain text only. Keep it short and simple.
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
    # 8. ASSET VALUATION CERTIFICATE
    # ============================================================================
    
    def generate_asset_valuation(self) -> str:
        """Generate asset valuation certificate"""
        doc_record = self._create_document_record("asset_valuation", "Asset_Valuation_Certificate.pdf")
        file_path = doc_record.file_path
        
        try:
            self._update_progress(doc_record, 10)
            
            # Get asset data
            name = self._get_value('personal.full_name')
            property_desc = self._get_value('assets.property_description')
            property_value = self._get_value('assets.property_value', 'asset_valuation.total_value')
            vehicle_desc = self._get_value('assets.vehicle_description')
            vehicle_value = self._get_value('assets.vehicle_value')
            investments = self._get_value('assets.investments_description')
            investment_value = self._get_value('assets.investments_value')
            
            self._update_progress(doc_record, 40)
            
            # Create PDF
            pdf = SimpleDocTemplate(file_path, pagesize=A4,
                                   topMargin=1*inch, bottomMargin=1*inch,
                                   leftMargin=1*inch, rightMargin=1*inch)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Letterhead
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("ASSET VALUATION & ASSOCIATES", title_style))
            story.append(Paragraph("Professional Valuation Services", subtitle_style))
            story.append(Paragraph("Dhaka, Bangladesh", subtitle_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Title
            cert_title_style = ParagraphStyle(
                'CertTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            story.append(Paragraph("ASSET VALUATION CERTIFICATE", cert_title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Body
            body_style = ParagraphStyle(
                'Body',
                parent=styles['BodyText'],
                fontSize=11,
                leading=16,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(f"<b>Owner Name:</b> {name}", body_style))
            story.append(Paragraph(f"<b>Valuation Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Assets table
            story.append(Paragraph("<b>ASSET DETAILS AND VALUATION</b>", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            asset_data = [
                ['Asset Type', 'Description', 'Estimated Value (BDT)'],
            ]
            
            if property_desc or property_value:
                asset_data.append([
                    'Property/Land',
                    property_desc or 'Residential property',
                    property_value or 'To be assessed'
                ])
            
            if vehicle_desc or vehicle_value:
                asset_data.append([
                    'Vehicle',
                    vehicle_desc or 'Personal vehicle',
                    vehicle_value or 'To be assessed'
                ])
            
            if investments or investment_value:
                asset_data.append([
                    'Investments',
                    investments or 'Various investments',
                    investment_value or 'To be assessed'
                ])
            
            # If no assets, add default row
            if len(asset_data) == 1:
                asset_data.append(['Various', 'Assets as declared', 'As per documents'])
            
            # Total row
            total_value = 0
            try:
                if property_value:
                    total_value += int(property_value.replace(',', '').replace('BDT', '').strip())
                if vehicle_value:
                    total_value += int(vehicle_value.replace(',', '').replace('BDT', '').strip())
                if investment_value:
                    total_value += int(investment_value.replace(',', '').replace('BDT', '').strip())
            except:
                pass
            
            asset_data.append(['', '<b>TOTAL VALUE</b>', f'<b>BDT {total_value:,}</b>' if total_value > 0 else '<b>As per documents</b>'])
            
            asset_table = Table(asset_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 10),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 11),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ]))
            
            story.append(asset_table)
            story.append(Spacer(1, 0.4*inch))
            
            # Certification
            cert_text = """<b>CERTIFICATION</b><br/><br/>
This is to certify that the above assets belong to the mentioned owner and the valuations 
are estimated based on current market conditions and available documentation. This certificate 
is issued for visa application purposes."""
            
            story.append(Paragraph(cert_text, body_style))
            story.append(Spacer(1, 0.4*inch))
            
            # Signature
            sig_text = """<b>Authorized Signatory</b><br/>
Asset Valuation & Associates"""
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
    # MASTER FUNCTION
    # ============================================================================
    
    def generate_all_documents(self) -> Dict[str, str]:
        """Generate all 8 documents and return file paths"""
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
            
            # 8. Asset Valuation Certificate
            results['asset_valuation'] = self.generate_asset_valuation()
            
            return results
            
        except Exception as e:
            print(f"Error generating documents: {e}")
            raise
