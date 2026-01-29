"""
Questionnaire Generator Service - Generate intelligent, contextual questions
based on extracted data and user profile
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
        category: QuestionCategory,
        data_type: QuestionDataType = QuestionDataType.TEXT,
        is_required: bool = True,
        options: Optional[List[str]] = None,
        placeholder: Optional[str] = None,
        help_text: Optional[str] = None
    ):
        self.key = key
        self.text = text
        self.category = category
        self.data_type = data_type
        self.is_required = is_required
        self.options = options or []
        self.placeholder = placeholder
        self.help_text = help_text
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "text": self.text,
            "category": self.category.value,
            "data_type": self.data_type.value,
            "is_required": self.is_required,
            "options": self.options,
            "placeholder": self.placeholder,
            "help_text": self.help_text
        }


class QuestionnaireGeneratorService:
    """Generate intelligent questionnaire based on extracted data"""
    
    def generate_questions(
        self,
        extracted_data: Dict,
        uploaded_document_types: List[DocumentType]
    ) -> Dict[str, List[Question]]:
        """
        Generate contextual questions based on what was extracted
        and what documents will be generated
        
        Returns dict grouped by category
        """
        logger.info("Generating intelligent questionnaire...")
        
        questions_by_category = {
            "personal": [],
            "employment": [],
            "business": [],
            "travel_purpose": [],
            "financial": [],
            "assets": [],
            "home_ties": []
        }
        
        # Detect user type from extracted data
        user_type = self._detect_user_type(extracted_data)
        logger.info(f"Detected user type: {user_type}")
        
        # Generate questions for each category
        questions_by_category["personal"] = self._personal_questions(extracted_data)
        
        if user_type == "job_holder":
            questions_by_category["employment"] = self._employment_questions(extracted_data)
        elif user_type == "businessman":
            questions_by_category["business"] = self._business_questions(extracted_data)
        else:
            # Ask both to determine
            questions_by_category["employment"] = self._profession_determination_questions()
        
        questions_by_category["travel_purpose"] = self._travel_questions(extracted_data)
        questions_by_category["financial"] = self._financial_questions(extracted_data)
        questions_by_category["assets"] = self._asset_questions(extracted_data)
        questions_by_category["home_ties"] = self._home_ties_questions(extracted_data)
        
        # Convert to dict for JSON serialization
        result = {}
        for category, questions in questions_by_category.items():
            result[category] = [q.to_dict() for q in questions if q is not None]
        
        total_questions = sum(len(q) for q in result.values())
        logger.info(f"Generated {total_questions} questions across {len(result)} categories")
        
        return result
    
    def _detect_user_type(self, extracted_data: Dict) -> str:
        """
        Detect if user is job holder, businessman, or unknown
        based on extracted documents
        """
        # Check if business-related documents exist
        # For now, return unknown - will be determined by questionnaire
        return "unknown"
    
    def _personal_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate personal detail questions for missing information"""
        questions = []
        
        # Check what's missing from passport/NID
        passport_data = extracted_data.get("passport", {})
        nid_data = extracted_data.get("nid_bangla", {})
        
        if not passport_data.get("full_name") and not nid_data.get("name_bangla"):
            questions.append(Question(
                key="personal.full_name",
                text="What is your full name (as it appears on your passport)?",
                category=QuestionCategory.PERSONAL,
                data_type=QuestionDataType.TEXT,
                placeholder="Enter your full name",
                help_text="This should match your passport exactly"
            ))
        
        if not passport_data.get("date_of_birth"):
            questions.append(Question(
                key="personal.date_of_birth",
                text="What is your date of birth?",
                category=QuestionCategory.PERSONAL,
                data_type=QuestionDataType.DATE,
                help_text="Format: DD/MM/YYYY"
            ))
        
        # Always ask these as they're usually not in documents
        questions.append(Question(
            key="personal.current_address",
            text="What is your current residential address?",
            category=QuestionCategory.PERSONAL,
            data_type=QuestionDataType.TEXTAREA,
            placeholder="House/Flat number, Street, Area, City, Post Code",
            help_text="Provide your complete current address"
        ))
        
        questions.append(Question(
            key="personal.marital_status",
            text="What is your marital status?",
            category=QuestionCategory.PERSONAL,
            data_type=QuestionDataType.SELECT,
            options=["Single", "Married", "Divorced", "Widowed"]
        ))
        
        questions.append(Question(
            key="personal.dependents",
            text="How many dependents do you have (children, elderly parents, etc.)?",
            category=QuestionCategory.PERSONAL,
            data_type=QuestionDataType.NUMBER,
            placeholder="0",
            is_required=False,
            help_text="People who financially depend on you"
        ))
        
        questions.append(Question(
            key="personal.phone",
            text="What is your contact phone number?",
            category=QuestionCategory.PERSONAL,
            data_type=QuestionDataType.TEXT,
            placeholder="+880 1XXX-XXXXXX"
        ))
        
        questions.append(Question(
            key="personal.email",
            text="What is your email address?",
            category=QuestionCategory.PERSONAL,
            data_type=QuestionDataType.TEXT,
            placeholder="your.email@example.com"
        ))
        
        return questions
    
    def _profession_determination_questions(self) -> List[Question]:
        """Ask questions to determine if job holder or businessman"""
        return [
            Question(
                key="employment.profession_type",
                text="What is your profession?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.SELECT,
                options=["Job Holder (Employee)", "Business Owner", "Self-Employed", "Student", "Retired", "Other"]
            )
        ]
    
    def _employment_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate employment-related questions for job holders"""
        return [
            Question(
                key="employment.job_title",
                text="What is your current job title/position?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="e.g., Senior Software Engineer, Manager, etc."
            ),
            Question(
                key="employment.company_name",
                text="What is the name of your employer/company?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="Company name"
            ),
            Question(
                key="employment.company_address",
                text="What is your company's full address?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Office address with city and post code"
            ),
            Question(
                key="employment.company_phone",
                text="What is your company's contact phone number?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="+880 XXX-XXXXXXX"
            ),
            Question(
                key="employment.employment_duration",
                text="How long have you been working at this company?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="e.g., 3 years 6 months",
                help_text="This shows job stability"
            ),
            Question(
                key="employment.monthly_salary",
                text="What is your monthly salary (in BDT)?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.NUMBER,
                placeholder="e.g., 80000",
                help_text="This information is needed for financial assessment"
            ),
            Question(
                key="employment.supervisor_name",
                text="Who is your direct supervisor/manager?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="Supervisor's name",
                is_required=False,
                help_text="For verification purposes"
            ),
            Question(
                key="employment.hr_contact",
                text="What is your company's HR contact information?",
                category=QuestionCategory.EMPLOYMENT,
                data_type=QuestionDataType.TEXT,
                placeholder="HR phone/email",
                is_required=False
            )
        ]
    
    def _business_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate business-related questions for business owners"""
        return [
            Question(
                key="business.business_name",
                text="What is the name of your business?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXT,
                placeholder="Business/Company name"
            ),
            Question(
                key="business.business_type",
                text="What type of business do you run?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXT,
                placeholder="e.g., Import/Export, Manufacturing, Retail, Services, etc."
            ),
            Question(
                key="business.business_start_date",
                text="When did you start this business?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.DATE,
                help_text="Business establishment date"
            ),
            Question(
                key="business.registration_number",
                text="What is your business registration number?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXT,
                placeholder="Trade license or registration number",
                is_required=False
            ),
            Question(
                key="business.business_address",
                text="What is your business address?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Complete business address"
            ),
            Question(
                key="business.business_phone",
                text="What is your business contact number?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXT,
                placeholder="+880 XXX-XXXXXXX"
            ),
            Question(
                key="business.monthly_revenue",
                text="What is your average monthly business revenue (in BDT)?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.NUMBER,
                placeholder="e.g., 500000",
                help_text="Approximate monthly income from business"
            ),
            Question(
                key="business.employees",
                text="How many employees work in your business?",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.NUMBER,
                placeholder="Number of employees",
                is_required=False
            ),
            Question(
                key="business.nature_of_work",
                text="Describe the nature of your business activities",
                category=QuestionCategory.BUSINESS,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="What products/services does your business provide?",
                help_text="This will be used in your cover letter"
            )
        ]
    
    def _travel_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate travel purpose and plans questions"""
        return [
            Question(
                key="travel.purpose",
                text="What is the main purpose of your visit to Iceland?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.SELECT,
                options=["Tourism/Vacation", "Visit Friends/Family", "Business Meeting", "Conference/Seminar", "Other"]
            ),
            Question(
                key="travel.purpose_details",
                text="Please provide more details about your visit purpose",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Describe what you plan to do in Iceland",
                help_text="This will be included in your cover letter"
            ),
            Question(
                key="travel.places_to_visit",
                text="Which cities/places in Iceland do you plan to visit?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="e.g., Reykjavik, Blue Lagoon, Golden Circle, etc.",
                help_text="List the places you're interested in visiting"
            ),
            Question(
                key="travel.activities_planned",
                text="What activities do you plan to do during your visit?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="e.g., Sightseeing, Northern Lights tour, hiking, etc."
            ),
            Question(
                key="travel.previous_schengen",
                text="Have you visited Iceland or other Schengen countries before?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="travel.previous_visits_details",
                text="If yes, when and which countries did you visit?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="List previous visits to Schengen area",
                is_required=False,
                help_text="This shows your travel history compliance"
            ),
            Question(
                key="travel.contacts_in_iceland",
                text="Do you have any friends or family in Iceland?",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="travel.contacts_details",
                text="If yes, please provide their contact information",
                category=QuestionCategory.TRAVEL_PURPOSE,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Name, phone number, and relationship",
                is_required=False
            )
        ]
    
    def _financial_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate financial information questions"""
        
        # Check what's already extracted from bank/tax documents
        bank_data = extracted_data.get("bank_solvency", {})
        tax_data = extracted_data.get("income_tax", {})
        
        questions = []
        
        if not tax_data.get("total_income_3years"):
            questions.append(Question(
                key="financial.monthly_income",
                text="What is your total monthly income (in BDT)?",
                category=QuestionCategory.FINANCIAL,
                data_type=QuestionDataType.NUMBER,
                placeholder="e.g., 100000",
                help_text="Include salary, business income, and other sources"
            ))
        
        questions.extend([
            Question(
                key="financial.monthly_expenses",
                text="What are your approximate monthly expenses (in BDT)?",
                category=QuestionCategory.FINANCIAL,
                data_type=QuestionDataType.NUMBER,
                placeholder="e.g., 50000",
                help_text="Include rent, utilities, food, transportation, etc."
            ),
            Question(
                key="financial.trip_funding_source",
                text="What is the source of funds for this trip?",
                category=QuestionCategory.FINANCIAL,
                data_type=QuestionDataType.SELECT,
                options=["Personal Savings", "Salary", "Business Income", "Family Support", "Loan", "Other"]
            ),
            Question(
                key="financial.sponsor",
                text="Who will sponsor/fund this trip?",
                category=QuestionCategory.FINANCIAL,
                data_type=QuestionDataType.SELECT,
                options=["Self-funded", "Family Member", "Company/Employer", "Other"]
            ),
            Question(
                key="financial.sponsor_details",
                text="If sponsored by someone else, provide sponsor details",
                category=QuestionCategory.FINANCIAL,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Sponsor's name, relationship, and contact information",
                is_required=False
            )
        ])
        
        return questions
    
    def _asset_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate questions about assets (for asset valuation document)"""
        return [
            Question(
                key="assets.property_ownership",
                text="Do you own any property or real estate in Bangladesh?",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="assets.property_details",
                text="If yes, please provide details of your property",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Address, type (house/apartment/land), size, estimated value",
                is_required=False,
                help_text="This will be included in your asset valuation certificate"
            ),
            Question(
                key="assets.vehicle_ownership",
                text="Do you own any vehicles?",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="assets.vehicle_details",
                text="If yes, provide vehicle details",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Make, model, year, estimated value",
                is_required=False
            ),
            Question(
                key="assets.investments",
                text="Do you have any investments (stocks, bonds, mutual funds, etc.)?",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="assets.investment_details",
                text="If yes, provide investment details",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Type of investment and approximate value",
                is_required=False
            ),
            Question(
                key="assets.total_value",
                text="What is the estimated total value of all your assets (in BDT)?",
                category=QuestionCategory.ASSETS,
                data_type=QuestionDataType.NUMBER,
                placeholder="e.g., 5000000",
                help_text="Include property, vehicles, investments, savings, etc."
            )
        ]
    
    def _home_ties_questions(self, extracted_data: Dict) -> List[Question]:
        """Generate questions about home ties (reasons to return)"""
        return [
            Question(
                key="home_ties.family_in_bangladesh",
                text="Do you have immediate family members (spouse, children, parents) living in Bangladesh?",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="home_ties.family_details",
                text="Please provide details about your family in Bangladesh",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Who lives with you or depends on you in Bangladesh?",
                help_text="This demonstrates strong ties to Bangladesh"
            ),
            Question(
                key="home_ties.employment_commitment",
                text="Do you have ongoing employment or business commitments in Bangladesh?",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="home_ties.employment_commitment_details",
                text="Describe your employment/business commitments",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="Why you need to return to Bangladesh after your trip",
                help_text="This shows you will return after your visit"
            ),
            Question(
                key="home_ties.property_ties",
                text="Do you own property in Bangladesh that requires your presence?",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.BOOLEAN
            ),
            Question(
                key="home_ties.reasons_to_return",
                text="What are your main reasons for returning to Bangladesh after your trip?",
                category=QuestionCategory.HOME_TIES,
                data_type=QuestionDataType.TEXTAREA,
                placeholder="List all reasons why you will return to Bangladesh",
                help_text="IMPORTANT: This is crucial for visa approval. Be specific and detailed."
            )
        ]


# Singleton instance
_questionnaire_service = None

def get_questionnaire_service() -> QuestionnaireGeneratorService:
    """Get or create questionnaire generator service instance"""
    global _questionnaire_service
    if _questionnaire_service is None:
        _questionnaire_service = QuestionnaireGeneratorService()
    return _questionnaire_service
