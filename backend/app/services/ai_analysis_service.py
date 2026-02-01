"""
AI Analysis Service - Enhanced version with robust prompts and better error handling
"""
import json
import re
from typing import Dict, Optional
from loguru import logger
import google.generativeai as genai

from app.config import settings
from app.models import DocumentType


class AIAnalysisService:
    """Enhanced service for analyzing documents and extracting structured information"""
    
    def __init__(self):
        """Initialize Gemini AI client with optimized settings"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use Gemini 2.5 Flash with optimized configuration for extraction
        generation_config = {
            "temperature": 0.05,  # Very low temperature for maximum consistency
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.model = genai.GenerativeModel(
            'models/gemini-2.5-flash',  # Optimized for structured extraction
            generation_config=generation_config
        )
        
        logger.info("✅ AIAnalysisService initialized with Gemini 2.5 Flash (temperature=0.05 for consistency)")
    
    async def analyze_document(
        self,
        document_type: DocumentType,
        extracted_text: str
    ) -> Dict:
        """
        Main entry point - routes to specific analyzer based on document type
        
        Args:
            document_type: Type of document to analyze
            extracted_text: Text extracted from PDF/image
            
        Returns:
            Dict with extracted structured data and confidence score
        """
        try:
            logger.info(f"🔍 Starting analysis for {document_type.value}")
            
            # Validate input
            text_length = len(extracted_text.strip()) if extracted_text else 0
            
            if not extracted_text or text_length < 10:
                logger.warning(f"⚠️ Insufficient text for {document_type.value}: {text_length} chars")
                logger.warning(f"📝 Text preview: '{extracted_text[:100]}'")
                return {
                    "error": f"Insufficient text extracted from document. Only {text_length} characters found. The document may be blank, scanned incorrectly, or needs better OCR.",
                    "confidence": 0,
                    "raw_text_length": text_length,
                    "suggestion": "Please re-upload a clearer image/PDF or ensure the document contains readable text."
                }
            
            logger.info(f"📝 Analyzing {text_length} characters of text from {document_type.value}")
            logger.info(f"📄 Text preview (first 200 chars): {extracted_text[:200]}")
            
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
            elif document_type == DocumentType.ASSET_VALUATION:
                return await self.analyze_asset_valuation(extracted_text)
            else:
                logger.warning(f"⚠️ No specific analyzer for {document_type.value}, using generic extraction")
                return await self.analyze_generic_document(extracted_text, document_type.value)
                
        except Exception as e:
            logger.error(f"❌ Error analyzing {document_type.value}: {str(e)}", exc_info=True)
            return {
                "error": f"Analysis failed: {str(e)}",
                "confidence": 0
            }
    
    async def analyze_passport(self, text: str) -> Dict:
        """Enhanced passport analysis with OCR noise handling"""
        
        prompt = f"""You are an expert document analyst specializing in passport data extraction.

IMPORTANT INSTRUCTIONS:
1. The text below may come from OCR (Optical Character Recognition) and may contain errors, noise, or formatting issues
2. Look for passport-specific keywords: "Passport", "P<", "Surname", "Given Names", "Nationality", "Date of Birth", etc.
3. Passport numbers are usually 7-9 alphanumeric characters
4. Dates may be in various formats: DD MMM YYYY, DD/MM/YYYY, YYYY-MM-DD
5. Be flexible with spelling variations due to OCR errors
6. If you can't find a field with high confidence, use null

PASSPORT TEXT (may contain OCR noise):
{text}

Extract the following information and return ONLY valid JSON (no markdown, no code blocks, no extra text):

{{
    "full_name": "Full name as it appears on passport",
    "passport_number": "Passport number (alphanumeric)",
    "date_of_birth": "YYYY-MM-DD format (convert if needed)",
    "nationality": "Nationality/Country",
    "gender": "M or F",
    "issue_date": "YYYY-MM-DD format",
    "expiry_date": "YYYY-MM-DD format",
    "place_of_issue": "Place where passport was issued",
    "passport_type": "Type (e.g., P for Personal)",
    "confidence": 85
}}

CONFIDENCE SCORING GUIDE:
- 90-100: All major fields found clearly
- 70-89: Most fields found, some minor uncertainty
- 50-69: Several fields found, significant gaps
- 0-49: Very few fields found reliably

CRITICAL: Return ONLY the JSON object. No markdown, no explanations, no code blocks.
Use null for any missing fields. Base confidence on text quality and fields found.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Validate and enhance result
            result = self._validate_passport_data(result, text)
            
            logger.info(f"✅ Passport analyzed - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing passport: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_nid_bangla(self, text: str) -> Dict:
        """Enhanced NID analysis with Bengali text support"""
        
        prompt = f"""You are an expert in analyzing Bangladesh National ID cards.

IMPORTANT INSTRUCTIONS:
1. The text contains BENGALI (বাংলা) script - preserve it EXACTLY as it appears
2. NID cards have both Bengali and English text
3. OCR may have errors - be flexible with formatting
4. NID numbers are 10, 13, or 17 digits
5. Look for Bengali keywords: নাম (name), পিতা (father), মাতা (mother), জন্ম তারিখ (date of birth)

NID TEXT (Contains Bengali):
{text}

Extract information and PRESERVE BENGALI TEXT exactly. Return ONLY valid JSON:

{{
    "name_bangla": "নাম (keep Bangla text exactly as it appears)",
    "name_english": "Name in English if available",
    "father_name_bangla": "পিতার নাম (keep Bangla text)",
    "mother_name_bangla": "মাতার নাম (keep Bangla text)",
    "date_of_birth": "YYYY-MM-DD format",
    "nid_number": "NID number (10, 13, or 17 digits)",
    "address_bangla": "ঠিকানা (full Bangla address)",
    "blood_group": "Blood group if available",
    "place_of_birth": "Place of birth if available",
    "confidence": 80
}}

CRITICAL RULES:
- Keep ALL Bangla text in original script - DO NOT translate or transliterate
- Return ONLY JSON - no markdown, no code blocks
- Use null for missing fields
- Confidence based on text quality and fields found

"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ NID Bangla analyzed - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing NID: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_income_tax(self, text: str) -> Dict:
        """Enhanced income tax analysis"""
        
        prompt = f"""You are a financial document analyst specializing in Bangladesh income tax returns.

IMPORTANT INSTRUCTIONS:
1. Text may come from OCR with potential errors
2. Look for assessment years (e.g., 2023-2024) and corresponding tax years
3. Income figures may be in various formats (1,200,000 or 12,00,000)
4. Remove currency symbols and commas when extracting amounts
5. TIN is usually 12 digits

TAX RETURN TEXT (may contain OCR noise):
{text}

Extract information for all available years. Return ONLY valid JSON:

{{
    "taxpayer_name": "Name of taxpayer",
    "tin_number": "12-digit TIN number",
    "tax_years": [
        {{
            "year": "2023",
            "assessment_year": "2023-2024",
            "annual_income": 1200000,
            "tax_paid": 45000
        }}
    ],
    "total_income_3years": 3600000,
    "total_tax_paid_3years": 135000,
    "average_annual_income": 1200000,
    "confidence": 85
}}

AMOUNT EXTRACTION RULES:
- Remove all commas, currency symbols (৳, BDT, Tk)
- Convert to pure numbers
- If amounts are in lakhs, convert to full amount (e.g., 12L = 1200000)

CRITICAL: Return ONLY JSON. Use null for missing fields.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            # Calculate derived fields
            if result.get('tax_years'):
                total_income = sum(year.get('annual_income', 0) for year in result['tax_years'])
                total_tax = sum(year.get('tax_paid', 0) for year in result['tax_years'])
                result['total_income_3years'] = total_income
                result['total_tax_paid_3years'] = total_tax
                if result['tax_years']:
                    result['average_annual_income'] = total_income // len(result['tax_years'])
            
            logger.info(f"✅ Income tax analyzed - Years: {len(result.get('tax_years', []))}, Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing income tax: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_tin_certificate(self, text: str) -> Dict:
        """Enhanced TIN certificate analysis"""
        
        prompt = f"""You are an expert at analyzing TIN (Tax Identification Number) certificates from Bangladesh.

INSTRUCTIONS:
1. TIN number is 12 digits
2. Look for keywords: "TIN", "Tax Circle", "Zone", "Taxpayer"
3. Handle OCR errors flexibly

TIN CERTIFICATE TEXT:
{text}

Return ONLY valid JSON:

{{
    "tin_number": "12-digit TIN",
    "taxpayer_name": "Full name",
    "circle": "Tax circle/zone",
    "issue_date": "YYYY-MM-DD",
    "taxpayer_category": "Individual/Company/etc",
    "address": "Registered address",
    "certificate_number": "Certificate number if available",
    "confidence": 90
}}

CRITICAL: Return ONLY JSON. No markdown, no code blocks.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ TIN analyzed - Confidence: {result.get('confidence', 0)}%")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing TIN: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_bank_solvency(self, text: str) -> Dict:
        """Enhanced bank solvency analysis"""
        
        prompt = f"""You are a financial document analyst specializing in bank solvency certificates from Bangladesh.

INSTRUCTIONS:
1. Look for account holder name, account number, balance
2. Amounts may be in various formats - extract the number
3. Bank names: Common banks in BD include DBBL, City Bank, BRAC, etc.

BANK CERTIFICATE TEXT:
{text}

Return ONLY valid JSON:

{{
    "account_holder_name": "Account holder name",
    "account_number": "Full account number",
    "bank_name": "Bank name",
    "branch_name": "Branch name",
    "branch_address": "Branch address",
    "account_type": "Savings/Current/etc",
    "current_balance": 500000,
    "balance_in_words": "Balance in words if available",
    "account_opening_date": "YYYY-MM-DD",
    "certificate_issue_date": "YYYY-MM-DD",
    "certificate_reference": "Reference number if available",
    "confidence": 85
}}

AMOUNT RULES: Remove currency symbols (৳, BDT, Tk) and commas. Return pure number.
CRITICAL: Return ONLY JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Bank solvency analyzed - Balance: {result.get('current_balance', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing bank solvency: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_hotel_booking(self, text: str) -> Dict:
        """Enhanced hotel booking analysis"""
        
        prompt = f"""Analyze this hotel booking confirmation from booking.com, Hotels.com, Agoda, or direct hotel booking.

HOTEL BOOKING TEXT:
{text}

Return ONLY valid JSON:

{{
    "hotel_name": "Hotel name",
    "hotel_address": "Hotel address",
    "city": "City",
    "country": "Country (should be Iceland for this visa)",
    "check_in_date": "YYYY-MM-DD",
    "check_out_date": "YYYY-MM-DD",
    "number_of_nights": 5,
    "room_type": "Room type",
    "guest_name": "Guest name",
    "booking_reference": "Booking reference/confirmation number",
    "total_price": 50000,
    "currency": "ISK/EUR/USD",
    "cancellation_policy": "Free cancellation/Non-refundable/etc",
    "booking_platform": "Booking.com/Hotels.com/etc",
    "confidence": 85
}}

Calculate number_of_nights from check-in and check-out dates if not explicitly stated.
CRITICAL: Return ONLY JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Hotel booking analyzed - Hotel: {result.get('hotel_name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing hotel booking: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_air_ticket(self, text: str) -> Dict:
        """Enhanced air ticket analysis"""
        
        prompt = f"""Analyze this air ticket/flight booking confirmation.

FLIGHT BOOKING TEXT:
{text}

Return ONLY valid JSON:

{{
    "passenger_name": "Passenger name",
    "booking_reference": "PNR/Booking reference",
    "ticket_number": "Ticket number if available",
    "outbound_flight": {{
        "airline": "Airline name",
        "flight_number": "Flight number",
        "departure_airport": "Airport code/name",
        "departure_city": "Departure city (should be Dhaka/Bangladesh)",
        "arrival_airport": "Airport code/name",
        "arrival_city": "Arrival city (should be in Iceland)",
        "departure_date": "YYYY-MM-DD",
        "departure_time": "HH:MM",
        "arrival_date": "YYYY-MM-DD",
        "arrival_time": "HH:MM"
    }},
    "return_flight": {{
        "airline": "Airline name",
        "flight_number": "Flight number",
        "departure_airport": "Airport code/name",
        "departure_city": "Departure city (Iceland)",
        "arrival_airport": "Airport code/name",
        "arrival_city": "Arrival city (Bangladesh)",
        "departure_date": "YYYY-MM-DD",
        "departure_time": "HH:MM",
        "arrival_date": "YYYY-MM-DD",
        "arrival_time": "HH:MM"
    }},
    "travel_class": "Economy/Business/First",
    "ticket_price": 120000,
    "currency": "BDT/USD/EUR",
    "booking_status": "Confirmed/Pending/etc",
    "confidence": 85
}}

CRITICAL: Return ONLY JSON. Use null for missing fields.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Air ticket analyzed - Passenger: {result.get('passenger_name', 'Unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing air ticket: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_visa_history(self, text: str) -> Dict:
        """Enhanced visa history analysis from passport stamps"""
        
        prompt = f"""Analyze passport visa stamps and entry/exit stamps to create travel history.

PASSPORT STAMPS TEXT:
{text}

Return ONLY valid JSON:

{{
    "countries_visited": [
        {{
            "country": "Country name",
            "visa_type": "Tourist/Business/Transit/etc",
            "entry_date": "YYYY-MM-DD",
            "exit_date": "YYYY-MM-DD",
            "duration_days": 15,
            "purpose": "Tourism/Business/etc",
            "stamp_details": "Any relevant stamp details"
        }}
    ],
    "total_countries": 5,
    "schengen_visits": 2,
    "recent_travels": "Summary of recent 2-3 years travel",
    "has_schengen_experience": true,
    "confidence": 80
}}

Look for entry/exit stamps, visa stickers, and calculate duration. 
Note Schengen countries separately.
CRITICAL: Return ONLY JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Visa history analyzed - Countries: {result.get('total_countries', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing visa history: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Enhanced JSON parsing with multiple fallback strategies
        """
        try:
            # Clean the response
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if '```json' in cleaned:
                # Extract JSON from code block
                match = re.search(r'```json\s*(.*?)\s*```', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1).strip()
            elif '```' in cleaned:
                # Generic code block
                match = re.search(r'```\s*(.*?)\s*```', cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1).strip()
            
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
            
            # Parse JSON
            result = json.loads(cleaned)
            
            # Ensure confidence exists
            if 'confidence' not in result:
                result['confidence'] = 50  # Default medium confidence
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {str(e)}")
            logger.error(f"📄 Response text: {response_text[:500]}")
            
            # Return error with raw response
            return {
                "error": f"Failed to parse JSON: {str(e)}",
                "confidence": 0,
                "raw_response": response_text[:1000]
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in JSON parsing: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0
            }
    
    def _validate_passport_data(self, data: Dict, original_text: str) -> Dict:
        """Validate and enhance passport data"""
        
        # If parsing failed, don't process further
        if "error" in data:
            return data
        
        # Ensure key fields
        required_fields = ['full_name', 'passport_number', 'date_of_birth', 'nationality']
        missing_count = sum(1 for field in required_fields if not data.get(field))
        
        # Adjust confidence based on missing critical fields
        if 'confidence' in data:
            if missing_count > 2:
                data['confidence'] = min(data['confidence'], 40)
            elif missing_count > 0:
                data['confidence'] = min(data['confidence'], 70)
        
        return data
    
    async def analyze_asset_valuation(self, text: str) -> Dict:
        """Analyze asset valuation certificate (if user uploads their own)"""
        
        prompt = f"""Analyze this asset valuation certificate or property document.

ASSET VALUATION TEXT:
{text}

Extract all asset information. Return ONLY valid JSON:

{{
    "owner_name": "Property owner name",
    "properties": [
        {{
            "type": "Land/Apartment/House",
            "location": "Address/location",
            "size": "Size with unit",
            "value": 5000000,
            "description": "Description"
        }}
    ],
    "vehicles": [
        {{
            "type": "Car/Motorcycle",
            "model": "Make and model",
            "year": 2020,
            "value": 2000000
        }}
    ],
    "other_assets": [
        {{
            "type": "Business/Investment/etc",
            "description": "Description",
            "value": 1000000
        }}
    ],
    "total_value": 8000000,
    "valuation_date": "YYYY-MM-DD",
    "confidence": 75
}}

CRITICAL: Return ONLY JSON. Numbers without currency symbols.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Asset valuation analyzed - Total: {result.get('total_value', 0)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing asset valuation: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }
    
    async def analyze_generic_document(self, text: str, document_type: str) -> Dict:
        """Generic analyzer for any document type not specifically handled"""
        
        prompt = f"""You are analyzing a {document_type} document.

DOCUMENT TEXT:
{text}

Extract ALL relevant information you can find. Return ONLY valid JSON:

{{
    "document_type": "{document_type}",
    "extracted_info": {{
        "key_1": "value_1",
        "key_2": "value_2"
    }},
    "dates": [],
    "amounts": [],
    "names": [],
    "addresses": [],
    "confidence": 70
}}

Extract any dates, monetary amounts, names, addresses, and other relevant information.
CRITICAL: Return ONLY JSON.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            logger.info(f"✅ Generic document analyzed - Type: {document_type}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing generic document: {str(e)}")
            return {
                "error": str(e), 
                "confidence": 0,
                "raw_text_sample": text[:500] if text else ""
            }


# Singleton instance
_analysis_service = None

def get_analysis_service() -> AIAnalysisService:
    """Get or create AI analysis service instance"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AIAnalysisService()
    return _analysis_service