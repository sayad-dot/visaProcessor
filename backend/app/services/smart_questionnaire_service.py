"""
Smart Questionnaire Service - Enhanced questionnaire with conditional logic
Based on sample analysis and all 13 generated documents
"""
from typing import Dict, List, Any
from datetime import datetime

# Complete Smart Questionnaire Structure
SMART_QUESTIONNAIRE_STRUCTURE = {
    "personal_info": {
        "title": "Personal Information",
        "description": "Basic details about you (as per your passport and NID)",
        "icon": "👤",
        "order": 1,
        "questions": [
            {
                "key": "full_name",
                "label": "Full Name (exactly as shown in passport)",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "John Michael Doe",
                "validation": {"min_length": 2, "max_length": 100},
                "hint": "Must match your passport"
            },
            {
                "key": "email",
                "label": "Email Address",
                "type": "email",
                "required": True,
                "level": "required",
                "placeholder": "john.doe@example.com",
                "validation": {"pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"}
            },
            {
                "key": "phone",
                "label": "Phone Number (with country code)",
                "type": "tel",
                "required": False,
                "level": "suggested",
                "placeholder": "+1-555-0123",
                "validation": {"pattern": "^\\+?[0-9]{10,15}$"}
            },
            {
                "key": "date_of_birth",
                "label": "Date of Birth",
                "type": "date",
                "required": True,
                "level": "required",
                "validation": {"max_date": "today", "min_age": 18}
            },
            {
                "key": "father_name",
                "label": "Father's Full Name",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "Robert Smith"
            },
            {
                "key": "mother_name",
                "label": "Mother's Full Name",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "Mary Johnson"
            },
            {
                "key": "permanent_address",
                "label": "Permanent Address",
                "type": "textarea",
                "required": True,
                "level": "required",
                "placeholder": "123 Main Street, Apt 4B, City, State, ZIP",
                "rows": 3
            },
            {
                "key": "present_address",
                "label": "Present/Current Address",
                "type": "textarea",
                "required": True,
                "level": "required",
                "placeholder": "Same as permanent or different",
                "rows": 3,
                "hint": "If same as permanent, just type 'Same as above'"
            },
            {
                "key": "passport_number",
                "label": "Passport Number",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "BE0123456",
                "validation": {"pattern": "^[A-Z]{1,2}[0-9]{7,9}$"}
            },
            {
                "key": "nid_number",
                "label": "NID Number",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "1234567890",
                "validation": {"pattern": "^[0-9]{10,17}$"}
            },
            {
                "key": "is_married",
                "label": "Are you married?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "spouse_name",
                "label": "Spouse's Full Name",
                "type": "text",
                "required": False,
                "level": "suggested",
                "placeholder": "Jane Doe",
                "show_if": {"is_married": "Yes"}
            },
            {
                "key": "number_of_children",
                "label": "How many children do you have?",
                "type": "number",
                "required": False,
                "level": "suggested",
                "placeholder": "0",
                "validation": {"min": 0, "max": 20},
                "show_if": {"is_married": "Yes"}
            },
            {
                "key": "blood_group",
                "label": "Blood Group",
                "type": "select",
                "required": False,
                "level": "optional",
                "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            }
        ]
    },
    
    "employment_business": {
        "title": "Employment & Business Information",
        "description": "Details about your job or business",
        "icon": "💼",
        "order": 2,
        "questions": [
            {
                "key": "employment_status",
                "label": "What is your employment status?",
                "type": "select",
                "required": True,
                "level": "required",
                "options": [
                    "Business Owner",
                    "Employed (Job Holder)",
                    "Self-Employed",
                    "Retired",
                    "Student",
                    "Other"
                ]
            },
            {
                "key": "job_title",
                "label": "Your Job Title/Designation",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "Managing Director, Sales Manager, etc.",
                "show_if": {"employment_status": ["Employed (Job Holder)", "Business Owner", "Self-Employed"]}
            },
            {
                "key": "company_name",
                "label": "Company/Business Name",
                "type": "text",
                "required": True,
                "level": "required",
                "placeholder": "Osman Trading International",
                "show_if": {"employment_status": ["Employed (Job Holder)", "Business Owner", "Self-Employed"]}
            },
            {
                "key": "business_type",
                "label": "Type of Business",
                "type": "text",
                "required": False,
                "level": "suggested",
                "placeholder": "Import/Export, Retail, Manufacturing, IT Services, etc.",
                "show_if": {"employment_status": ["Business Owner", "Self-Employed"]}
            },
            {
                "key": "business_address",
                "label": "Business/Office Address",
                "type": "textarea",
                "required": False,
                "level": "suggested",
                "placeholder": "Office location",
                "rows": 2,
                "show_if": {"employment_status": ["Employed (Job Holder)", "Business Owner", "Self-Employed"]}
            },
            {
                "key": "business_start_year",
                "label": "Business Established Year",
                "type": "number",
                "required": False,
                "level": "suggested",
                "placeholder": "2015",
                "validation": {"min": 1950, "max": 2026},
                "show_if": {"employment_status": ["Business Owner", "Self-Employed"]}
            },
            {
                "key": "number_of_employees",
                "label": "Number of Employees",
                "type": "number",
                "required": False,
                "level": "optional",
                "placeholder": "8",
                "validation": {"min": 0},
                "show_if": {"employment_status": ["Business Owner"]}
            },
            {
                "key": "company_website",
                "label": "Company Website (if any)",
                "type": "url",
                "required": False,
                "level": "optional",
                "placeholder": "https://www.company.com"
            }
        ]
    },
    
    "travel_info": {
        "title": "Travel Details",
        "description": "Information about your planned trip to Iceland",
        "icon": "✈️",
        "order": 3,
        "questions": [
            {
                "key": "travel_purpose",
                "label": "What is your purpose of travel?",
                "type": "select",
                "required": True,
                "level": "required",
                "options": [
                    "Tourism",
                    "Business",
                    "Study",
                    "Medical Treatment",
                    "Family Visit",
                    "Conference/Event",
                    "Other"
                ]
            },
            {
                "key": "has_previous_travel",
                "label": "Have you previously visited any other country?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "previous_travels",
                "label": "Previous Travel History",
                "type": "array",
                "required": False,
                "level": "suggested",
                "show_if": {"has_previous_travel": "Yes"},
                "fields": [
                    {
                        "key": "country",
                        "label": "Country Name",
                        "type": "text",
                        "placeholder": "Thailand"
                    },
                    {
                        "key": "visa_type",
                        "label": "Visa Type",
                        "type": "select",
                        "options": ["Tourism", "Business", "Student", "Work", "Transit", "Other"],
                        "placeholder": "Tourism"
                    },
                    {
                        "key": "from_date",
                        "label": "From Date",
                        "type": "date",
                        "placeholder": "2023-06-01"
                    },
                    {
                        "key": "to_date",
                        "label": "To Date",
                        "type": "date",
                        "placeholder": "2023-06-15"
                    }
                ],
                "hint": "Click 'Add Country' to add more travel entries"
            },
            {
                "key": "duration_days",
                "label": "How many days do you want to stay in Iceland?",
                "type": "number",
                "required": True,
                "level": "required",
                "placeholder": "14",
                "validation": {"min": 1, "max": 90},
                "hint": "Maximum 90 days for tourist visa"
            },
            {
                "key": "departure_date",
                "label": "Departure Date (from Bangladesh)",
                "type": "date",
                "required": True,
                "level": "required",
                "validation": {"min_date": "today"}
            },
            {
                "key": "return_date",
                "label": "Return Date (to Bangladesh)",
                "type": "date",
                "required": True,
                "level": "required",
                "validation": {"min_date": "departure_date"}
            },
            {
                "key": "has_air_ticket",
                "label": "Have you already bought the air ticket?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "airline_preference",
                "label": "Do you have any particular airline in mind?",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Biman Bangladesh Airlines, Emirates, Turkish Airlines, etc.",
                "show_if": {"has_air_ticket": "No"},
                "hint": "Otherwise our system will decide for you"
            },
            {
                "key": "departure_airport",
                "label": "Departure Airport",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Hazrat Shahjalal International Airport (DAC)",
                "show_if": {"has_air_ticket": "No"}
            },
            {
                "key": "has_hotel_booking",
                "label": "Have you booked any hotel room?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "hotel_name",
                "label": "Hotel Name",
                "type": "text",
                "required": False,
                "level": "suggested",
                "placeholder": "Reykjavik Grand Hotel",
                "show_if": {"has_hotel_booking": "Yes"}
            },
            {
                "key": "hotel_address",
                "label": "Hotel Address",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Downtown Reykjavik, Iceland",
                "show_if": {"has_hotel_booking": "Yes"}
            },
            {
                "key": "room_type",
                "label": "Room Type",
                "type": "select",
                "required": False,
                "level": "optional",
                "options": ["Standard Single", "Standard Double", "Deluxe Room", "Suite", "Other"],
                "show_if": {"has_hotel_booking": "Yes"}
            },
            {
                "key": "hotel_preference_name",
                "label": "Do you have any particular hotel in mind?",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Hotel Iceland or any preferred hotel name",
                "show_if": {"has_hotel_booking": "No"},
                "hint": "Otherwise our system will suggest one for you"
            },
            {
                "key": "hotel_preference_location",
                "label": "Preferred Hotel Location/Area",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Downtown Reykjavik, Near airport, etc.",
                "show_if": {"has_hotel_booking": "No"}
            },
            {
                "key": "has_travel_plan",
                "label": "Do you have any specific plans for what to do in Iceland?",
                "type": "boolean",
                "required": False,
                "level": "optional",
                "options": ["Yes, I have a plan", "No, let the system plan for me"]
            },
            {
                "key": "places_to_visit",
                "label": "Places/Cities You Want to Visit",
                "type": "textarea",
                "required": False,
                "level": "optional",
                "placeholder": "Reykjavik, Golden Circle, Blue Lagoon, Northern Lights, etc.",
                "rows": 3,
                "show_if": {"has_travel_plan": "Yes, I have a plan"}
            },
            {
                "key": "travel_activities",
                "label": "Activities You Plan to Do",
                "type": "array",
                "required": False,
                "level": "optional",
                "show_if": {"has_travel_plan": "Yes, I have a plan"},
                "fields": [
                    {
                        "key": "city",
                        "label": "Place/City",
                        "type": "text",
                        "placeholder": "Reykjavik"
                    },
                    {
                        "key": "date",
                        "label": "Date",
                        "type": "date"
                    },
                    {
                        "key": "activity",
                        "label": "Activity",
                        "type": "text",
                        "placeholder": "Visit Hallgrimskirkja Church"
                    }
                ],
                "hint": "Click 'Add Activity' to add more"
            }
        ]
    },
    
    "financial_assets": {
        "title": "Financial & Assets Information",
        "description": "Your financial status and assets",
        "icon": "💰",
        "order": 4,
        "questions": [
            {
                "key": "banks",
                "label": "Bank Account Details",
                "type": "array",
                "required": True,
                "level": "required",
                "fields": [
                    {
                        "key": "bank_name",
                        "label": "Bank Name",
                        "type": "text",
                        "placeholder": "Dutch-Bangla Bank"
                    },
                    {
                        "key": "account_type",
                        "label": "Account Type",
                        "type": "select",
                        "options": ["Savings", "Current", "Fixed Deposit"]
                    },
                    {
                        "key": "account_number",
                        "label": "Account Number",
                        "type": "text",
                        "placeholder": "123-456-789012"
                    },
                    {
                        "key": "balance",
                        "label": "Current Balance (BDT)",
                        "type": "number",
                        "placeholder": "850000",
                        "validation": {"min": 0}
                    }
                ],
                "hint": "Click 'Add Bank Account' to add more accounts",
                "min_items": 1
            },
            {
                "key": "monthly_income",
                "label": "Monthly Income (BDT)",
                "type": "number",
                "required": False,
                "level": "suggested",
                "placeholder": "120000",
                "validation": {"min": 0}
            },
            {
                "key": "monthly_expenses",
                "label": "Average Monthly Expenses (BDT)",
                "type": "number",
                "required": False,
                "level": "suggested",
                "placeholder": "80000",
                "validation": {"min": 0}
            },
            {
                "key": "income_sources",
                "label": "Annual Income (Last 3 Years)",
                "type": "array",
                "required": False,
                "level": "suggested",
                "fields": [
                    {
                        "key": "year",
                        "label": "Year",
                        "type": "number",
                        "placeholder": "2023",
                        "validation": {"min": 2020, "max": 2026}
                    },
                    {
                        "key": "income",
                        "label": "Annual Income (BDT)",
                        "type": "number",
                        "placeholder": "1800000"
                    },
                    {
                        "key": "tax_paid",
                        "label": "Tax Paid (BDT)",
                        "type": "number",
                        "placeholder": "45000"
                    }
                ],
                "hint": "Add income details for last 3 years"
            },
            {
                "key": "has_assets",
                "label": "Do you have any assets (property, vehicles, etc.)?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "assets",
                "label": "Asset Details",
                "type": "array",
                "required": False,
                "level": "suggested",
                "show_if": {"has_assets": "Yes"},
                "fields": [
                    {
                        "key": "asset_type",
                        "label": "Asset Type",
                        "type": "select",
                        "options": ["Land", "Building", "House", "Vehicle"]
                    },
                    {
                        "key": "location",
                        "label": "Location/Address",
                        "type": "text",
                        "placeholder": "123 Street Name, City",
                        "show_if_asset": ["Land", "Building", "House"]
                    },
                    {
                        "key": "area",
                        "label": "Area (sq ft)",
                        "type": "number",
                        "placeholder": "15000",
                        "validation": {"min": 0},
                        "show_if_asset": ["Land", "Building", "House"]
                    },
                    {
                        "key": "vehicle_name",
                        "label": "Vehicle Name/Brand",
                        "type": "text",
                        "placeholder": "Toyota Camry",
                        "show_if_asset": ["Vehicle"]
                    },
                    {
                        "key": "vehicle_model",
                        "label": "Model/Year",
                        "type": "text",
                        "placeholder": "2020",
                        "show_if_asset": ["Vehicle"]
                    },
                    {
                        "key": "estimated_value",
                        "label": "Estimated Value (BDT)",
                        "type": "number",
                        "placeholder": "5000000",
                        "validation": {"min": 0}
                    }
                ],
                "hint": "Click 'Add Asset' to add more"
            },
            {
                "key": "rental_income",
                "label": "Monthly Rental Income (if any)",
                "type": "number",
                "required": False,
                "level": "optional",
                "placeholder": "215000",
                "validation": {"min": 0},
                "show_if": {"has_assets": "Yes"}
            }
        ]
    },
    
    "other_info": {
        "title": "Additional Information",
        "description": "Tax details and other information",
        "icon": "📋",
        "order": 5,
        "questions": [
            {
                "key": "has_tin",
                "label": "Do you have a TIN (Tax Identification Number)?",
                "type": "boolean",
                "required": False,
                "level": "suggested",
                "options": ["Yes", "No"]
            },
            {
                "key": "tin_number",
                "label": "TIN Number (12 digits)",
                "type": "text",
                "required": False,
                "level": "suggested",
                "placeholder": "789-456-123-0147",
                "validation": {"pattern": "^[0-9\\-]{12,16}$"},
                "show_if": {"has_tin": "Yes"}
            },
            {
                "key": "tin_circle",
                "label": "Tax Circle",
                "type": "text",
                "required": False,
                "level": "optional",
                "placeholder": "Dhaka Taxes Circle-1",
                "show_if": {"has_tin": "Yes"}
            },
            {
                "key": "has_tax_certificates",
                "label": "Do you have tax certificates for previous years?",
                "type": "boolean",
                "required": False,
                "level": "optional",
                "options": ["Yes", "No"]
            },
            {
                "key": "tax_certificates",
                "label": "Tax Certificate Details",
                "type": "array",
                "required": False,
                "level": "optional",
                "show_if": {"has_tax_certificates": "Yes"},
                "fields": [
                    {
                        "key": "year",
                        "label": "Assessment Year",
                        "type": "text",
                        "placeholder": "2023-2024"
                    },
                    {
                        "key": "certificate_number",
                        "label": "Certificate Number",
                        "type": "text",
                        "placeholder": "TAX/2023/NBR/1234"
                    }
                ],
                "hint": "Add details for last 3 years if available",
                "max_items": 3
            },
            {
                "key": "reasons_to_return",
                "label": "Why will you return to Bangladesh after your trip?",
                "type": "textarea",
                "required": False,
                "level": "suggested",
                "placeholder": "My family depends on me, I own a business, I have property, etc.",
                "rows": 4,
                "hint": "This is important for your visa application. Mention family, business, property, responsibilities, etc."
            },
            {
                "key": "additional_info",
                "label": "Any other information you want to share?",
                "type": "textarea",
                "required": False,
                "level": "optional",
                "placeholder": "Community involvement, special circumstances, etc.",
                "rows": 3
            }
        ]
    }
}


def get_questionnaire_structure() -> Dict[str, Any]:
    """Get the complete smart questionnaire structure"""
    return SMART_QUESTIONNAIRE_STRUCTURE


def get_section_by_key(section_key: str) -> Dict[str, Any]:
    """Get a specific section of the questionnaire"""
    return SMART_QUESTIONNAIRE_STRUCTURE.get(section_key, {})


def get_all_questions() -> List[Dict[str, Any]]:
    """Get all questions as a flat list"""
    all_questions = []
    for section_key, section in SMART_QUESTIONNAIRE_STRUCTURE.items():
        for question in section.get("questions", []):
            question_with_section = question.copy()
            question_with_section["section"] = section_key
            all_questions.append(question_with_section)
    return all_questions


def get_required_questions() -> List[Dict[str, Any]]:
    """Get only required questions"""
    all_questions = get_all_questions()
    return [q for q in all_questions if q.get("required", False)]


def validate_answer(question: Dict[str, Any], answer: Any) -> tuple[bool, str]:
    """Validate an answer against question validation rules"""
    if question.get("required") and not answer:
        return False, f"{question.get('label')} is required"
    
    if not answer:
        return True, ""  # Optional field with no answer is valid
    
    validation = question.get("validation", {})
    
    # Type-specific validation
    if question["type"] == "email":
        import re
        pattern = validation.get("pattern", "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
        if not re.match(pattern, str(answer)):
            return False, "Invalid email format"
    
    elif question["type"] == "number":
        try:
            num = float(answer)
            if "min" in validation and num < validation["min"]:
                return False, f"Must be at least {validation['min']}"
            if "max" in validation and num > validation["max"]:
                return False, f"Must be at most {validation['max']}"
        except (ValueError, TypeError):
            return False, "Must be a valid number"
    
    elif question["type"] == "text":
        if "min_length" in validation and len(str(answer)) < validation["min_length"]:
            return False, f"Must be at least {validation['min_length']} characters"
        if "max_length" in validation and len(str(answer)) > validation["max_length"]:
            return False, f"Must be at most {validation['max_length']} characters"
    
    return True, ""


def calculate_progress(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate questionnaire completion progress"""
    all_questions = get_all_questions()
    required_questions = get_required_questions()
    
    total_questions = len(all_questions)
    total_required = len(required_questions)
    
    answered_total = sum(1 for q in all_questions if answers.get(q["key"]))
    answered_required = sum(1 for q in required_questions if answers.get(q["key"]))
    
    # Section-wise progress
    section_progress = {}
    for section_key, section in SMART_QUESTIONNAIRE_STRUCTURE.items():
        section_questions = section.get("questions", [])
        section_required = [q for q in section_questions if q.get("required")]
        
        section_answered = sum(1 for q in section_questions if answers.get(q["key"]))
        section_required_answered = sum(1 for q in section_required if answers.get(q["key"]))
        
        section_progress[section_key] = {
            "total": len(section_questions),
            "answered": section_answered,
            "required": len(section_required),
            "required_answered": section_required_answered,
            "percentage": (section_answered / len(section_questions) * 100) if section_questions else 0,
            "required_percentage": (section_required_answered / len(section_required) * 100) if section_required else 100
        }
    
    return {
        "total_questions": total_questions,
        "answered_questions": answered_total,
        "total_required": total_required,
        "answered_required": answered_required,
        "overall_percentage": (answered_total / total_questions * 100) if total_questions else 0,
        "required_percentage": (answered_required / total_required * 100) if total_required else 0,
        "is_complete": answered_required == total_required,
        "section_progress": section_progress
    }
