"""
Gemini AI Service - AI-powered document analysis and generation
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from loguru import logger

from app.config import settings


class GeminiService:
    """Service for Gemini AI operations"""
    
    def __init__(self):
        """Initialize Gemini API"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"Gemini AI initialized with model: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            raise
    
    async def analyze_document(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """
        Analyze a document and extract relevant information
        
        Args:
            document_text: Extracted text from the document
            document_type: Type of document (passport, NID, etc.)
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            prompt = f"""
            You are an expert visa document analyzer. Analyze the following {document_type} document 
            and extract all relevant information.
            
            Document Text:
            {document_text}
            
            Please extract and structure the information in a clear, organized JSON format.
            Include fields like name, date of birth, passport number, issue date, expiry date, etc.
            based on the document type.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            extracted_data = self._parse_response(response.text)
            
            logger.info(f"Successfully analyzed {document_type}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    async def identify_missing_information(
        self, 
        extracted_data: Dict[str, Any],
        required_fields: List[str]
    ) -> List[Dict[str, str]]:
        """
        Identify missing information needed for document generation
        
        Args:
            extracted_data: Data extracted from uploaded documents
            required_fields: List of required fields for visa application
            
        Returns:
            List of missing information with questions to ask user
        """
        try:
            prompt = f"""
            You are a visa application assistant. Based on the extracted information below,
            identify what information is missing for a complete Iceland tourist visa application.
            
            Extracted Information:
            {extracted_data}
            
            Required Fields:
            {required_fields}
            
            For each missing field, generate a clear, user-friendly question to ask the applicant.
            Return the response as a JSON array with objects containing 'field_name', 'question', 
            and 'data_type' (text/date/number).
            """
            
            response = self.model.generate_content(prompt)
            
            missing_info = self._parse_response(response.text)
            
            logger.info(f"Identified {len(missing_info)} missing information fields")
            return missing_info
            
        except Exception as e:
            logger.error(f"Error identifying missing information: {str(e)}")
            raise
    
    async def generate_document_content(
        self,
        document_type: str,
        user_data: Dict[str, Any]
    ) -> str:
        """
        Generate content for a missing document
        
        Args:
            document_type: Type of document to generate
            user_data: All available user information
            
        Returns:
            Generated document content as string
        """
        try:
            prompt = self._get_generation_prompt(document_type, user_data)
            
            response = self.model.generate_content(prompt)
            
            logger.info(f"Successfully generated content for {document_type}")
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating document content: {str(e)}")
            raise
    
    def _get_generation_prompt(self, document_type: str, user_data: Dict[str, Any]) -> str:
        """
        Get appropriate prompt for document generation based on type
        """
        base_prompt = f"""
        Generate a professional {document_type} document for a visa application.
        
        User Information:
        {user_data}
        
        """
        
        if document_type == "cover_letter":
            return base_prompt + """
            Create a formal cover letter for Iceland tourist visa application.
            Include: purpose of visit, travel dates, accommodation details, financial stability,
            and intent to return to home country. Make it compelling and professional.
            """
        
        elif document_type == "travel_itinerary":
            return base_prompt + """
            Create a detailed travel itinerary based on the air ticket and hotel bookings.
            Include daily plans, places to visit, and activities. Make it realistic and detailed.
            """
        
        elif document_type == "home_tie_statement":
            return base_prompt + """
            Create a home tie statement letter explaining the applicant's ties to Bangladesh
            and reasons for returning after the trip. Include family, employment, property, etc.
            """
        
        elif document_type == "financial_statement":
            return base_prompt + """
            Create a financial statement summary based on bank solvency and income tax documents.
            Show financial stability and ability to fund the trip.
            """
        
        elif document_type == "travel_history":
            return base_prompt + """
            Create a travel history document based on visa stamps and passport copies.
            List all previous international travels with dates and countries.
            """
        
        else:
            return base_prompt + f"Generate appropriate content for {document_type}."
    
    def _parse_response(self, response_text: str) -> Any:
        """
        Parse Gemini response text to structured data
        TODO: Implement proper JSON parsing
        """
        # For now, return raw text
        # In Phase 3, we'll implement proper JSON parsing
        return {"raw_response": response_text}
