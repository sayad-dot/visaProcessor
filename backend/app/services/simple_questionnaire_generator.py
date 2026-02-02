"""
Simple Questionnaire Generator - Organized, easy-to-understand questions
"""
from typing import List, Dict, Optional
from loguru import logger

from app.models import QuestionCategory, QuestionDataType, DocumentType


class Question:
    """Question model"""
    def __init__(
        self,
        key: str,
        text: str,
        category: str,
        data_type: QuestionDataType = QuestionDataType.TEXT,
        is_required: bool = True,
        options: Optional[List[str]] = None,
        placeholder: Optional[str] = None,
        help_text: Optional[str] = None,
        conditional_on: Optional[str] = None  # Shows only if this document NOT uploaded
    ):
        self.key = key
        self.text = text
        self.category = category
        self.data_type = data_type
        self.is_required = is_required
        self.options = options or []
        self.placeholder = placeholder
        self.help_text = help_text
        self.conditional_on = conditional_on
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "text": self.text,
            "category": self.category,
            "data_type": self.data_type.value,
            "is_required": self.is_required,
            "options": self.options,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "conditional_on": self.conditional_on
        }


class SimpleQuestionnaireGenerator:
    """Generate simple, organized questionnaire"""
    
    def generate_questions(
        self,
        uploaded_document_types: List[str]
    ) -> Dict[str, List[Question]]:
        """
        Generate organized questionnaire with 4 main sections
        """
        logger.info("Generating simple questionnaire...")
        
        questions = []
        
        # 1. PERSONAL INFORMATION (Always required)
        questions.extend(self._personal_information())
        
        # 2. TRAVEL INFORMATION (3 collapsible boxes)
        questions.extend(self._travel_information(uploaded_document_types))
        
        # 3. FINANCIAL/ASSETS INFORMATION
        questions.extend(self._financial_assets_information())
        
        # 4. OTHER INFORMATION (All optional)
        questions.extend(self._other_information())
        
        # Group by category
        questions_by_category = {}
        for q in questions:
            if q.category not in questions_by_category:
                questions_by_category[q.category] = []
            questions_by_category[q.category].append(q.to_dict())
        
        total_questions = sum(len(q) for q in questions_by_category.values())
        logger.info(f"Generated {total_questions} questions across {len(questions_by_category)} categories")
        
        return questions_by_category
    
    def _personal_information(self) -> List[Question]:
        """Section 1: Personal Information - Always required"""
        return [
            Question(
                key="father_name",
                text="Father's Full Name",
                category="personal",
                data_type=QuestionDataType.TEXT,
                is_required=True,
                placeholder="As per NID/Birth Certificate",
                help_text="Enter your father's name in English"
            ),
            Question(
                key="mother_name",
                text="Mother's Full Name",
                category="personal",
                data_type=QuestionDataType.TEXT,
                is_required=True,
                placeholder="As per NID/Birth Certificate",
                help_text="Enter your mother's name in English"
            ),
            Question(
                key="birthplace",
                text="Place of Birth",
                category="personal",
                data_type=QuestionDataType.TEXT,
                is_required=True,
                placeholder="e.g., Dhaka, Bangladesh",
                help_text="City and country where you were born"
            ),
            Question(
                key="permanent_address",
                text="Permanent Address",
                category="personal",
                data_type=QuestionDataType.TEXTAREA,
                is_required=True,
                placeholder="Full address with house number, road, area, district",
                help_text="Your permanent residential address as per NID"
            ),
            Question(
                key="present_address",
                text="Present Address",
                category="personal",
                data_type=QuestionDataType.TEXTAREA,
                is_required=True,
                placeholder="Same as permanent or provide current address",
                help_text="Your current residential address (can select 'Same as permanent')"
            ),
            # Additional optional personal info
            Question(
                key="marital_status",
                text="Marital Status",
                category="personal",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Single", "Married", "Divorced", "Widowed"],
                help_text="Select your marital status"
            ),
            Question(
                key="spouse_name",
                text="Spouse Name (if married)",
                category="personal",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="Full name of spouse"
            ),
            Question(
                key="number_of_children",
                text="Number of Children",
                category="personal",
                data_type=QuestionDataType.NUMBER,
                is_required=False,
                placeholder="0"
            ),
        ]
    
    def _travel_information(self, uploaded_docs: List[str]) -> List[Question]:
        """Section 2: Travel Information - 3 collapsible boxes"""
        questions = []
        
        # Box 1: Travel Itinerary (skip if uploaded)
        if "travel_itinerary" not in uploaded_docs:
            questions.extend([
                Question(
                    key="travel_purpose",
                    text="Purpose of Travel",
                    category="travel_itinerary",
                    data_type=QuestionDataType.SELECT,
                    is_required=True,
                    options=["Tourism", "Business", "Visit Family/Friends", "Conference/Event", "Other"],
                    conditional_on="travel_itinerary",
                    help_text="Main purpose of your visit"
                ),
                Question(
                    key="travel_start_date",
                    text="Travel Start Date",
                    category="travel_itinerary",
                    data_type=QuestionDataType.DATE,
                    is_required=True,
                    conditional_on="travel_itinerary",
                    help_text="When will you depart?"
                ),
                Question(
                    key="travel_end_date",
                    text="Travel End Date",
                    category="travel_itinerary",
                    data_type=QuestionDataType.DATE,
                    is_required=True,
                    conditional_on="travel_itinerary",
                    help_text="When will you return?"
                ),
                Question(
                    key="days_of_stay",
                    text="Total Days of Stay",
                    category="travel_itinerary",
                    data_type=QuestionDataType.NUMBER,
                    is_required=True,
                    conditional_on="travel_itinerary",
                    placeholder="e.g., 10"
                ),
                Question(
                    key="places_to_visit",
                    text="Top 5-10 Places You Plan to Visit",
                    category="travel_itinerary",
                    data_type=QuestionDataType.TEXTAREA,
                    is_required=True,
                    conditional_on="travel_itinerary",
                    placeholder="List the main tourist attractions, cities, or areas you want to visit (one per line)",
                    help_text="E.g., Reykjavik, Blue Lagoon, Golden Circle, etc."
                ),
                Question(
                    key="previously_visited_countries",
                    text="Countries You Have Previously Visited",
                    category="travel_itinerary",
                    data_type=QuestionDataType.TEXTAREA,
                    is_required=True,
                    conditional_on="travel_itinerary",
                    placeholder="List countries (one per line) or write 'None' if first time abroad",
                    help_text="This shows your travel history and compliance"
                ),
                Question(
                    key="other_travel_details",
                    text="Any Other Travel Details (Optional)",
                    category="travel_itinerary",
                    data_type=QuestionDataType.TEXTAREA,
                    is_required=False,
                    conditional_on="travel_itinerary",
                    placeholder="Additional information about your trip"
                ),
            ])
        
        # Box 2: Hotel Booking (skip if uploaded)
        if "hotel_booking" not in uploaded_docs:
            questions.extend([
                Question(
                    key="hotel_name",
                    text="Hotel Name",
                    category="hotel_booking",
                    data_type=QuestionDataType.TEXT,
                    is_required=True,
                    conditional_on="hotel_booking",
                    placeholder="Name of hotel you plan to stay",
                    help_text="If you have a specific hotel in mind"
                ),
                Question(
                    key="hotel_address",
                    text="Hotel Address",
                    category="hotel_booking",
                    data_type=QuestionDataType.TEXT,
                    is_required=True,
                    conditional_on="hotel_booking",
                    placeholder="Full hotel address with city",
                    help_text="Complete address of the hotel"
                ),
                Question(
                    key="hotel_preferences",
                    text="Any Hotel Preferences (Optional)",
                    category="hotel_booking",
                    data_type=QuestionDataType.TEXT,
                    is_required=False,
                    conditional_on="hotel_booking",
                    placeholder="Budget range, area preference, etc."
                ),
            ])
        
        # Box 3: Air Ticket (skip if uploaded)
        if "air_ticket" not in uploaded_docs:
            questions.extend([
                Question(
                    key="preferred_airline",
                    text="Preferred Airline (Optional)",
                    category="air_ticket",
                    data_type=QuestionDataType.TEXT,
                    is_required=False,
                    conditional_on="air_ticket",
                    placeholder="e.g., Emirates, Qatar Airways"
                ),
                Question(
                    key="departure_airport",
                    text="Departure Airport (Optional)",
                    category="air_ticket",
                    data_type=QuestionDataType.TEXT,
                    is_required=False,
                    conditional_on="air_ticket",
                    placeholder="e.g., Hazrat Shahjalal International Airport, Dhaka"
                ),
                Question(
                    key="arrival_airport",
                    text="Arrival Airport (Optional)",
                    category="air_ticket",
                    data_type=QuestionDataType.TEXT,
                    is_required=False,
                    conditional_on="air_ticket",
                    placeholder="e.g., Keflavik International Airport, Iceland"
                ),
                Question(
                    key="flight_preferences",
                    text="Any Flight Preferences (Optional)",
                    category="air_ticket",
                    data_type=QuestionDataType.TEXT,
                    is_required=False,
                    conditional_on="air_ticket",
                    placeholder="Direct flight, layover preferences, etc."
                ),
            ])
        
        return questions
    
    def _financial_assets_information(self) -> List[Question]:
        """Section 3: Financial & Assets Information"""
        return [
            # Property/Real Estate
            Question(
                key="property_ownership",
                text="Do you own any property in Bangladesh?",
                category="assets",
                data_type=QuestionDataType.SELECT,
                is_required=True,
                options=["Yes", "No"],
                help_text="House, land, apartment, etc."
            ),
            Question(
                key="property_type",
                text="Type of Property",
                category="assets",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Residential House", "Apartment", "Land", "Commercial Property", "Multiple Properties"],
                help_text="What type of property do you own?"
            ),
            Question(
                key="property_location",
                text="Property Location",
                category="assets",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="Area, District, Division",
                help_text="Where is your property located?"
            ),
            Question(
                key="property_value",
                text="Estimated Property Value (BDT)",
                category="assets",
                data_type=QuestionDataType.NUMBER,
                is_required=False,
                placeholder="e.g., 5000000",
                help_text="Approximate current market value"
            ),
            Question(
                key="property_size",
                text="Property Size",
                category="assets",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="e.g., 1500 sq ft or 5 katha",
                help_text="Total area of property"
            ),
            
            # Vehicles
            Question(
                key="vehicle_ownership",
                text="Do you own any vehicles?",
                category="assets",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Yes", "No"],
                help_text="Car, motorcycle, etc."
            ),
            Question(
                key="vehicle_details",
                text="Vehicle Details",
                category="assets",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="Type, model, year, estimated value",
                help_text="List your vehicles with approximate values"
            ),
            
            # Investments & Savings
            Question(
                key="investment_schemes",
                text="Do you have any investments or savings schemes?",
                category="assets",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Yes", "No"],
                help_text="FDR, Savings Certificates, Stocks, etc."
            ),
            Question(
                key="investment_details",
                text="Investment Details",
                category="assets",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="Type of investment and approximate value",
                help_text="Describe your investments and their values"
            ),
            
            # Business/Employment Assets
            Question(
                key="business_ownership",
                text="Do you own a business?",
                category="assets",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Yes", "No"]
            ),
            Question(
                key="business_name",
                text="Business Name",
                category="assets",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="Registered business name"
            ),
            Question(
                key="business_type",
                text="Type of Business",
                category="assets",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="e.g., Import/Export, Retail, IT Services"
            ),
            Question(
                key="business_value",
                text="Estimated Business Value (BDT)",
                category="assets",
                data_type=QuestionDataType.NUMBER,
                is_required=False,
                placeholder="Approximate business worth"
            ),
            
            # Employment (if not business owner)
            Question(
                key="employment_status",
                text="Are you currently employed?",
                category="financial",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["Yes - Full Time", "Yes - Part Time", "Self-Employed", "Business Owner", "Unemployed"]
            ),
            Question(
                key="employer_name",
                text="Employer/Company Name",
                category="financial",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="Current employer"
            ),
            Question(
                key="job_title",
                text="Job Title/Designation",
                category="financial",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="Your current position"
            ),
            Question(
                key="monthly_income",
                text="Monthly Income (BDT)",
                category="financial",
                data_type=QuestionDataType.NUMBER,
                is_required=False,
                placeholder="Average monthly income"
            ),
            
            # Home Ties
            Question(
                key="family_members_in_bangladesh",
                text="Family Members Living in Bangladesh",
                category="home_ties",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="List family members (parents, siblings, spouse, children) who will remain in Bangladesh",
                help_text="This shows your strong ties to return home"
            ),
            Question(
                key="reasons_to_return",
                text="Reasons You Must Return to Bangladesh",
                category="home_ties",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="e.g., Family responsibilities, business commitments, property management, job",
                help_text="What obligations require you to come back?"
            ),
        ]
    
    def _other_information(self) -> List[Question]:
        """Section 4: Other Information - All optional"""
        return [
            Question(
                key="tin_number",
                text="TIN (Tax Identification Number)",
                category="other",
                data_type=QuestionDataType.TEXT,
                is_required=False,
                placeholder="12-digit TIN number",
                help_text="If you have a TIN certificate"
            ),
            Question(
                key="previous_visa_rejections",
                text="Have you ever been rejected for any visa?",
                category="other",
                data_type=QuestionDataType.SELECT,
                is_required=False,
                options=["No", "Yes - please explain below"]
            ),
            Question(
                key="rejection_details",
                text="Visa Rejection Details (if any)",
                category="other",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="Country, year, and reason for rejection"
            ),
            Question(
                key="additional_information",
                text="Any Additional Information",
                category="other",
                data_type=QuestionDataType.TEXTAREA,
                is_required=False,
                placeholder="Anything else you'd like to add to support your application",
                help_text="Any relevant details not covered above"
            ),
        ]
