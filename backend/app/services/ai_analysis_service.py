"""
AI Analysis Service - Extract structured information from documents using Gemini AI
"""
import json
from typing import Dict, Optional
from loguru import logger
import google.generativeai as genai

from app.config import settings
from app.models import DocumentType


class AIAnalysisService:
    """Service for analyzing documents and extracting structured information"""
    
    def __init__(self):
        """Initialize Gemini AI client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use latest Gemini model - gemini-2.5-flash is the newest and fastest
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("AIAnalysisService initialized with Gemini 2.5 Flash")
    
    async def analyze_document(
        self,
        document_type: DocumentType,
        extracted_text: str
    ) -> Dict:
        """
        Main entry point - routes to specific analyzer based on document type
        
        Args:
            document_type: Type of document to analyze
            extracted_text: Text extracted from PDF
            
        Returns:
            Dict with extracted structured data and confidence score
        """
        try:
            logger.info(f"Starting analysis for {document_type.value}")
            
            # Route to specific analyzer
            if document_type == DocumentType.PASSPORT_COPY:
                return await self.analyze_passport(extracted_text)
            elif document_type == DocumentType.NID_BANGLA:
                return await self.analyze_nid_bangla(extracted_text)
            elif document_type == DocumentType.INCOME_TAX_3YEARS:
                return await self.analyze_income_tax(extracted_text)
            elif document_type == DocumentType.TIN_CERTIFICATE:
                return await self.analyze_tin_certificate(extracted_text)
            elif document_type == DocumentType.BANK_SOLVENCY:
                return await self.analyze_bank_solvency(extracted_text)
            elif document_type == DocumentType.HOTEL_BOOKING:
                return await self.analyze_hotel_booking(extracted_text)
            elif document_type == DocumentType.AIR_TICKET:
                return await self.analyze_air_ticket(extracted_text)
            elif document_type == DocumentType.VISA_HISTORY:
                return await self.analyze_visa_history(extracted_text)
            else:
                logger.warning(f"No specific analyzer for {document_type.value}")
                return {"error": "No analyzer available for this document type"}
                
        except Exception as e:
            logger.error(f"Error analyzing {document_type.value}: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0
            }
    
    async def analyze_passport(self, text: str) -> Dict:
        """
        Extract structured information from passport
        
        Extracts:
        - Full name
        - Passport number
        - Date of birth
        - Nationality
        - Issue date
        - Expiry date
        - Place of issue
        - Gender
        """
        prompt = f"""
You are an expert document analyst. Analyze this passport text and extract structured information.

PASSPORT TEXT:
{text}

Extract the following information and return ONLY valid JSON (no markdown, no extra text):

{{
    "full_name": "Full name as it appears on passport",
    "passport_number": "Passport number",
    "date_of_birth": "YYYY-MM-DD format",
    "nationality": "Nationality",
    "gender": "M or F",
    "issue_date": "YYYY-MM-DD format",
    "expiry_date": "YYYY-MM-DD format",
    "place_of_issue": "Place where passport was issued",
    "confidence": 85
}}

IMPORTANT: 
- Return ONLY the JSON object, no other text
- Use null for any missing fields
- Set confidence 0-100 based on text clarity
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Passport analyzed successfully - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing passport: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_nid_bangla(self, text: str) -> Dict:
        """
        Extract structured information from Bangladesh National ID (Bangla)
        
        Extracts:
        - Name in Bangla
        - Father's name in Bangla
        - Mother's name in Bangla
        - Date of birth
        - NID number
        - Address in Bangla
        """
        prompt = f"""
You are an expert in analyzing Bangladesh National ID cards written in Bangla script.

NID TEXT (Contains Bangla):
{text}

Extract information and PRESERVE BANGLA TEXT as-is. Return ONLY valid JSON:

{{
    "name_bangla": "নাম (keep Bangla text exactly as it appears)",
    "father_name_bangla": "পিতার নাম (keep Bangla text)",
    "mother_name_bangla": "মাতার নাম (keep Bangla text)",
    "date_of_birth": "YYYY-MM-DD format",
    "nid_number": "NID number (numbers only)",
    "address_bangla": "ঠিকানা (full Bangla address)",
    "blood_group": "Blood group if available",
    "confidence": 80
}}

IMPORTANT:
- Keep ALL Bangla text in original script
- Do NOT translate Bangla to English
- Return ONLY JSON, no markdown
- Use null for missing fields
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"NID Bangla analyzed - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing NID: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_income_tax(self, text: str) -> Dict:
        """
        Extract information from income tax returns (3 years)
        
        Extracts:
        - Tax years covered
        - Annual income per year
        - Tax paid per year
        - Taxpayer name
        - TIN number
        """
        prompt = f"""
Analyze this income tax return document and extract financial information.

TAX RETURN TEXT:
{text}

Extract information for all available years. Return ONLY valid JSON:

{{
    "taxpayer_name": "Name of taxpayer",
    "tin_number": "TIN number",
    "tax_years": [
        {{
            "year": "2023",
            "annual_income": 1200000,
            "tax_paid": 45000,
            "assessment_year": "2023-2024"
        }}
    ],
    "total_income_3years": 3600000,
    "total_tax_paid_3years": 135000,
    "confidence": 85
}}

IMPORTANT:
- Include all years found in document
- Use numbers without currency symbols
- Return ONLY JSON
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Income tax analyzed - Years: {len(result.get('tax_years', []))}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing income tax: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_tin_certificate(self, text: str) -> Dict:
        """
        Extract information from TIN certificate
        """
        prompt = f"""
Analyze this TIN (Tax Identification Number) certificate.

TIN CERTIFICATE TEXT:
{text}

Return ONLY valid JSON:

{{
    "tin_number": "TIN number",
    "taxpayer_name": "Full name",
    "circle": "Tax circle/zone",
    "issue_date": "YYYY-MM-DD",
    "taxpayer_category": "Individual/Company/etc",
    "address": "Registered address",
    "confidence": 90
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"TIN analyzed - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing TIN: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_bank_solvency(self, text: str) -> Dict:
        """
        Extract information from bank solvency certificate
        """
        prompt = f"""
Analyze this bank solvency certificate.

BANK CERTIFICATE TEXT:
{text}

Return ONLY valid JSON:

{{
    "account_holder_name": "Account holder name",
    "account_number": "Account number (last 4 digits only for privacy)",
    "bank_name": "Bank name",
    "branch_name": "Branch name",
    "branch_address": "Branch address",
    "account_type": "Savings/Current/etc",
    "current_balance": 500000,
    "account_opening_date": "YYYY-MM-DD",
    "certificate_issue_date": "YYYY-MM-DD",
    "confidence": 85
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Bank solvency analyzed - Balance: {result.get('current_balance', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing bank solvency: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_hotel_booking(self, text: str) -> Dict:
        """
        Extract information from hotel booking confirmation
        """
        prompt = f"""
Analyze this hotel booking confirmation.

HOTEL BOOKING TEXT:
{text}

Return ONLY valid JSON:

{{
    "hotel_name": "Hotel name",
    "hotel_address": "Hotel address",
    "city": "City",
    "country": "Country",
    "check_in_date": "YYYY-MM-DD",
    "check_out_date": "YYYY-MM-DD",
    "number_of_nights": 5,
    "room_type": "Room type",
    "guest_name": "Guest name",
    "booking_reference": "Booking reference number",
    "total_price": 50000,
    "cancellation_policy": "Free cancellation/Non-refundable/etc",
    "confidence": 85
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Hotel booking analyzed - Hotel: {result.get('hotel_name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing hotel booking: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_air_ticket(self, text: str) -> Dict:
        """
        Extract information from air ticket/flight booking
        """
        prompt = f"""
Analyze this air ticket/flight booking confirmation.

FLIGHT BOOKING TEXT:
{text}

Return ONLY valid JSON:

{{
    "passenger_name": "Passenger name",
    "booking_reference": "PNR/Booking reference",
    "outbound_flight": {{
        "airline": "Airline name",
        "flight_number": "Flight number",
        "departure_airport": "Airport code/name",
        "arrival_airport": "Airport code/name",
        "departure_date": "YYYY-MM-DD",
        "departure_time": "HH:MM",
        "arrival_time": "HH:MM"
    }},
    "return_flight": {{
        "airline": "Airline name",
        "flight_number": "Flight number",
        "departure_airport": "Airport code/name",
        "arrival_airport": "Airport code/name",
        "departure_date": "YYYY-MM-DD",
        "departure_time": "HH:MM",
        "arrival_time": "HH:MM"
    }},
    "travel_class": "Economy/Business/etc",
    "ticket_price": 120000,
    "confidence": 85
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Air ticket analyzed - Passenger: {result.get('passenger_name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing air ticket: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    async def analyze_visa_history(self, text: str) -> Dict:
        """
        Extract visa history from passport stamps
        """
        prompt = f"""
Analyze passport visa stamps and entry/exit stamps to create travel history.

PASSPORT STAMPS TEXT:
{text}

Return ONLY valid JSON:

{{
    "countries_visited": [
        {{
            "country": "Country name",
            "visa_type": "Tourist/Business/etc",
            "entry_date": "YYYY-MM-DD",
            "exit_date": "YYYY-MM-DD",
            "duration_days": 15,
            "purpose": "Tourism/Business/etc"
        }}
    ],
    "total_countries": 5,
    "schengen_visits": 2,
    "recent_travels": "Summary of recent 2-3 years travel",
    "confidence": 80
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            result = json.loads(result_text)
            logger.info(f"Visa history analyzed - Countries: {result.get('total_countries', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing visa history: {str(e)}")
            return {"error": str(e), "confidence": 0}


# Singleton instance
_analysis_service = None

def get_analysis_service() -> AIAnalysisService:
    """Get or create AI analysis service instance"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AIAnalysisService()
    return _analysis_service
