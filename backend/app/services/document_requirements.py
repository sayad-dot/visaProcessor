"""
Document Requirements Mapping - Defines what information is needed to generate each document type
This is the intelligence layer that determines which questions to ask based on missing documents
"""
from typing import Dict, List, Set
from dataclasses import dataclass
from app.models import DocumentType


@dataclass
class FieldRequirement:
    """Represents a field requirement for document generation"""
    field_key: str  # Key to look for in extracted data
    field_name: str  # Human-readable name
    question: str  # Question to ask if missing
    data_type: str  # text, date, number, boolean, etc.
    priority: str  # critical, important, optional
    help_text: str = ""
    placeholder: str = ""
    options: List[str] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = []


class DocumentRequirementsMapping:
    """
    Comprehensive mapping of information requirements for each document type
    for Iceland Tourist Visa (Business Purpose)
    """
    
    @staticmethod
    def get_requirements(document_type: DocumentType) -> List[FieldRequirement]:
        """Get field requirements for a specific document type"""
        
        requirements_map = {
            # ===== MANDATORY DOCUMENTS =====
            DocumentType.PASSPORT_COPY: [
                FieldRequirement(
                    field_key="passport.full_name",
                    field_name="Full Name (as on passport)",
                    question="What is your full name exactly as it appears on your passport?",
                    data_type="text",
                    priority="critical",
                    placeholder="Enter full name from passport"
                ),
                FieldRequirement(
                    field_key="passport.passport_number",
                    field_name="Passport Number",
                    question="What is your passport number?",
                    data_type="text",
                    priority="critical",
                    placeholder="e.g., A12345678"
                ),
                FieldRequirement(
                    field_key="passport.date_of_birth",
                    field_name="Date of Birth",
                    question="What is your date of birth?",
                    data_type="date",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="passport.issue_date",
                    field_name="Passport Issue Date",
                    question="When was your passport issued?",
                    data_type="date",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="passport.expiry_date",
                    field_name="Passport Expiry Date",
                    question="When does your passport expire?",
                    data_type="date",
                    priority="critical",
                    help_text="Must be valid for at least 3 months beyond your intended stay"
                ),
                FieldRequirement(
                    field_key="passport.nationality",
                    field_name="Nationality",
                    question="What is your nationality?",
                    data_type="text",
                    priority="critical"
                )
            ],
            
            DocumentType.NID_BANGLA: [
                FieldRequirement(
                    field_key="nid.name_bangla",
                    field_name="Name in Bengali",
                    question="What is your name in Bengali (বাংলা নাম)?",
                    data_type="text",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="nid.nid_number",
                    field_name="NID Number",
                    question="What is your NID number?",
                    data_type="text",
                    priority="critical",
                    placeholder="10, 13, or 17 digit number"
                ),
                FieldRequirement(
                    field_key="nid.father_name",
                    field_name="Father's Name",
                    question="What is your father's name?",
                    data_type="text",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="nid.mother_name",
                    field_name="Mother's Name",
                    question="What is your mother's name?",
                    data_type="text",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="nid.present_address",
                    field_name="Present Address",
                    question="What is your current residential address?",
                    data_type="textarea",
                    priority="important",
                    placeholder="House/Flat, Street, Area, City, Post Code"
                )
            ],
            
            DocumentType.BANK_SOLVENCY: [
                FieldRequirement(
                    field_key="bank.account_holder_name",
                    field_name="Account Holder Name",
                    question="What is the name on your bank account?",
                    data_type="text",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="bank.account_number",
                    field_name="Account Number",
                    question="What is your bank account number?",
                    data_type="text",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="bank.bank_name",
                    field_name="Bank Name",
                    question="Which bank do you use?",
                    data_type="text",
                    priority="critical",
                    placeholder="e.g., Dutch-Bangla Bank, City Bank"
                ),
                FieldRequirement(
                    field_key="bank.current_balance",
                    field_name="Current Balance",
                    question="What is your current account balance (in BDT)?",
                    data_type="number",
                    priority="critical",
                    placeholder="e.g., 500000",
                    help_text="Minimum 300,000 BDT recommended for Iceland visa"
                ),
                FieldRequirement(
                    field_key="bank.branch_name",
                    field_name="Branch Name",
                    question="Which branch is your account at?",
                    data_type="text",
                    priority="important"
                )
            ],
            
            # ===== OPTIONAL DOCUMENTS =====
            DocumentType.VISA_HISTORY: [
                FieldRequirement(
                    field_key="visa_history.countries_visited",
                    field_name="Countries Visited",
                    question="Which countries have you visited before?",
                    data_type="textarea",
                    priority="important",
                    placeholder="List countries with dates (e.g., Malaysia 2023, Thailand 2022)",
                    help_text="Previous travel history strengthens your application"
                ),
                FieldRequirement(
                    field_key="visa_history.schengen_visits",
                    field_name="Schengen Area Visits",
                    question="Have you visited any Schengen countries before? If yes, which ones and when?",
                    data_type="textarea",
                    priority="important",
                    help_text="Schengen countries include Iceland, France, Germany, Italy, Spain, etc."
                )
            ],
            
            DocumentType.TIN_CERTIFICATE: [
                FieldRequirement(
                    field_key="tin.tin_number",
                    field_name="TIN Number",
                    question="What is your TIN (Tax Identification Number)?",
                    data_type="text",
                    priority="important",
                    placeholder="12-digit TIN"
                ),
                FieldRequirement(
                    field_key="tin.taxpayer_name",
                    field_name="Taxpayer Name",
                    question="What is the name registered with TIN?",
                    data_type="text",
                    priority="important"
                )
            ],
            
            DocumentType.INCOME_TAX_3YEARS: [
                FieldRequirement(
                    field_key="tax.year_2023_income",
                    field_name="2023 Total Income",
                    question="What was your total income in 2023 (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 1200000"
                ),
                FieldRequirement(
                    field_key="tax.year_2023_tax_paid",
                    field_name="2023 Tax Paid",
                    question="How much tax did you pay in 2023 (in BDT)?",
                    data_type="number",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="tax.year_2022_income",
                    field_name="2022 Total Income",
                    question="What was your total income in 2022 (in BDT)?",
                    data_type="number",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="tax.year_2021_income",
                    field_name="2021 Total Income",
                    question="What was your total income in 2021 (in BDT)?",
                    data_type="number",
                    priority="important"
                )
            ],
            
            DocumentType.HOTEL_BOOKING: [
                FieldRequirement(
                    field_key="hotel.hotel_name",
                    field_name="Hotel Name",
                    question="What hotel will you stay at in Iceland?",
                    data_type="text",
                    priority="important",
                    placeholder="e.g., Reykjavik Grand Hotel"
                ),
                FieldRequirement(
                    field_key="hotel.check_in_date",
                    field_name="Check-in Date",
                    question="When will you check in to the hotel?",
                    data_type="date",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="hotel.check_out_date",
                    field_name="Check-out Date",
                    question="When will you check out from the hotel?",
                    data_type="date",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="hotel.hotel_address",
                    field_name="Hotel Address",
                    question="What is the hotel's address in Iceland?",
                    data_type="textarea",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="hotel.confirmation_number",
                    field_name="Booking Confirmation Number",
                    question="What is your booking confirmation number?",
                    data_type="text",
                    priority="optional"
                )
            ],
            
            DocumentType.AIR_TICKET: [
                FieldRequirement(
                    field_key="flight.departure_date",
                    field_name="Departure Date",
                    question="When will you fly to Iceland?",
                    data_type="date",
                    priority="critical"
                ),
                FieldRequirement(
                    field_key="flight.return_date",
                    field_name="Return Date",
                    question="When will you fly back to Bangladesh?",
                    data_type="date",
                    priority="critical",
                    help_text="Must show you will return"
                ),
                FieldRequirement(
                    field_key="flight.airline",
                    field_name="Airline",
                    question="Which airline will you fly with?",
                    data_type="text",
                    priority="important",
                    placeholder="e.g., Turkish Airlines, Qatar Airways"
                ),
                FieldRequirement(
                    field_key="flight.pnr",
                    field_name="PNR / Booking Reference",
                    question="What is your PNR or booking reference?",
                    data_type="text",
                    priority="optional",
                    placeholder="6-character code"
                )
            ],
            
            DocumentType.ASSET_VALUATION: [
                FieldRequirement(
                    field_key="assets.property_ownership",
                    field_name="Property Ownership",
                    question="Do you own any property or real estate in Bangladesh?",
                    data_type="boolean",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="assets.property_address",
                    field_name="Property Address",
                    question="What is the address of your property?",
                    data_type="textarea",
                    priority="important",
                    placeholder="Full address of your property"
                ),
                FieldRequirement(
                    field_key="assets.property_type",
                    field_name="Property Type",
                    question="What type of property do you own?",
                    data_type="select",
                    priority="important",
                    options=["Apartment/Flat", "House", "Land", "Commercial Building", "Other"]
                ),
                FieldRequirement(
                    field_key="assets.property_value",
                    field_name="Property Estimated Value",
                    question="What is the estimated value of your property (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 5000000"
                ),
                FieldRequirement(
                    field_key="assets.vehicle_ownership",
                    field_name="Vehicle Ownership",
                    question="Do you own any vehicles (car, motorcycle, etc.)?",
                    data_type="boolean",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="assets.vehicle_details",
                    field_name="Vehicle Details",
                    question="If yes, what vehicles do you own?",
                    data_type="textarea",
                    priority="optional",
                    placeholder="Make, model, year (e.g., Toyota Corolla 2020)"
                ),
                FieldRequirement(
                    field_key="assets.vehicle_value",
                    field_name="Vehicle Estimated Value",
                    question="What is the estimated value of your vehicle(s) (in BDT)?",
                    data_type="number",
                    priority="optional",
                    placeholder="e.g., 1500000"
                ),
                FieldRequirement(
                    field_key="assets.investments",
                    field_name="Investments",
                    question="Do you have any investments (stocks, bonds, mutual funds, FDR, etc.)?",
                    data_type="boolean",
                    priority="important"
                ),
                FieldRequirement(
                    field_key="assets.investment_details",
                    field_name="Investment Details",
                    question="If yes, describe your investments",
                    data_type="textarea",
                    priority="optional",
                    placeholder="Type and approximate value"
                ),
                FieldRequirement(
                    field_key="assets.total_asset_value",
                    field_name="Total Asset Value",
                    question="What is the estimated total value of ALL your assets (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 10000000",
                    help_text="Sum of property, vehicles, investments, savings, etc."
                )
            ],
            
            # ===== GENERATED DOCUMENTS =====
            DocumentType.NID_ENGLISH: [
                # Requires: NID Bangla data + translation
                FieldRequirement(
                    field_key="nid.name_english",
                    field_name="Name in English",
                    question="What is your name in English (for NID translation)?",
                    data_type="text",
                    priority="critical"
                )
                # Other fields will be translated from Bengali NID
            ],
            
            DocumentType.VISITING_CARD: [
                FieldRequirement(
                    field_key="business.company_name",
                    field_name="Company/Business Name",
                    question="What is the name of your company or business?",
                    data_type="text",
                    priority="critical",
                    placeholder="e.g., ABC Trading Limited"
                ),
                FieldRequirement(
                    field_key="business.designation",
                    field_name="Your Designation/Position",
                    question="What is your designation/position in the company?",
                    data_type="text",
                    priority="critical",
                    placeholder="e.g., Managing Director, CEO, Proprietor"
                ),
                FieldRequirement(
                    field_key="business.company_address",
                    field_name="Business Address",
                    question="What is your company's office address?",
                    data_type="textarea",
                    priority="important",
                    placeholder="Complete office address"
                ),
                FieldRequirement(
                    field_key="business.phone_number",
                    field_name="Business Phone Number",
                    question="What is your business phone number?",
                    data_type="text",
                    priority="important",
                    placeholder="e.g., +880 1711-123456"
                ),
                FieldRequirement(
                    field_key="business.email",
                    field_name="Business Email",
                    question="What is your business email address?",
                    data_type="email",
                    priority="important",
                    placeholder="e.g., info@company.com"
                ),
                FieldRequirement(
                    field_key="business.website",
                    field_name="Company Website",
                    question="Does your company have a website? If yes, what is the URL?",
                    data_type="text",
                    priority="optional",
                    placeholder="e.g., www.company.com"
                )
            ],
            
            DocumentType.COVER_LETTER: [
                # CRITICAL: Most important document
                FieldRequirement(
                    field_key="travel.trip_purpose",
                    field_name="Purpose of Visit",
                    question="What is the main purpose of your visit to Iceland?",
                    data_type="select",
                    priority="critical",
                    options=[
                        "Tourism/Sightseeing",
                        "Business Meetings",
                        "Conference/Seminar",
                        "Visiting Family/Friends",
                        "Medical Treatment",
                        "Other"
                    ],
                    help_text="This will be explained in detail in your cover letter"
                ),
                FieldRequirement(
                    field_key="travel.trip_purpose_details",
                    field_name="Detailed Purpose",
                    question="Explain in detail why you want to visit Iceland",
                    data_type="textarea",
                    priority="critical",
                    placeholder="Be specific about places, activities, business objectives, etc.",
                    help_text="IMPORTANT: Detailed explanation strengthens your application"
                ),
                FieldRequirement(
                    field_key="travel.duration_days",
                    field_name="Duration of Stay",
                    question="How many days will you stay in Iceland?",
                    data_type="number",
                    priority="critical",
                    placeholder="e.g., 10",
                    help_text="Must match your hotel and flight dates"
                ),
                FieldRequirement(
                    field_key="travel.places_to_visit",
                    field_name="Places to Visit",
                    question="Which places/cities do you plan to visit in Iceland?",
                    data_type="textarea",
                    priority="important",
                    placeholder="e.g., Reykjavik, Golden Circle, Blue Lagoon, etc.",
                    help_text="List specific attractions or locations"
                ),
                FieldRequirement(
                    field_key="travel.previous_schengen_visits",
                    field_name="Previous Schengen Visits",
                    question="Have you visited any Schengen countries before? Provide details.",
                    data_type="textarea",
                    priority="important",
                    placeholder="Country, year, purpose (e.g., France 2022 - tourism)",
                    help_text="Previous Schengen travel history is beneficial"
                ),
                FieldRequirement(
                    field_key="travel.funding_source",
                    field_name="How will you fund this trip?",
                    question="How will you finance your travel expenses?",
                    data_type="textarea",
                    priority="critical",
                    placeholder="e.g., Personal savings, business income, family support",
                    help_text="Explain your financial capability"
                ),
                FieldRequirement(
                    field_key="travel.estimated_cost",
                    field_name="Estimated Trip Cost",
                    question="What is the estimated total cost of your trip (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 300000",
                    help_text="Include flights, hotel, food, activities"
                )
            ],
            
            DocumentType.TRAVEL_ITINERARY: [
                FieldRequirement(
                    field_key="itinerary.day_by_day_plan",
                    field_name="Day-by-day Plan",
                    question="Provide a day-by-day itinerary of your trip",
                    data_type="textarea",
                    priority="important",
                    placeholder="Day 1: Arrival in Reykjavik, check-in hotel\nDay 2: Golden Circle tour\nDay 3: ...",
                    help_text="Detail your daily activities in Iceland"
                ),
                FieldRequirement(
                    field_key="itinerary.accommodation_details",
                    field_name="Accommodation Details",
                    question="Where will you stay each night?",
                    data_type="textarea",
                    priority="important",
                    placeholder="Hotel names and locations for each night"
                )
            ],
            
            DocumentType.TRAVEL_HISTORY: [
                FieldRequirement(
                    field_key="history.countries_visited_list",
                    field_name="Countries Visited",
                    question="List ALL countries you have visited (with years)",
                    data_type="textarea",
                    priority="important",
                    placeholder="Country - Year - Purpose\ne.g., Malaysia - 2023 - Business",
                    help_text="Include ALL international travel history"
                ),
                FieldRequirement(
                    field_key="history.visa_refusal",
                    field_name="Visa Refusals",
                    question="Have you ever been refused a visa to any country?",
                    data_type="boolean",
                    priority="critical",
                    help_text="IMPORTANT: Be honest, refusals are recorded"
                ),
                FieldRequirement(
                    field_key="history.visa_refusal_details",
                    field_name="Refusal Details",
                    question="If yes, provide details of the visa refusal",
                    data_type="textarea",
                    priority="critical",
                    placeholder="Which country, when, reason if known"
                )
            ],
            
            DocumentType.HOME_TIE_STATEMENT: [
                FieldRequirement(
                    field_key="home_ties.family_in_bangladesh",
                    field_name="Family in Bangladesh",
                    question="Who are your family members living in Bangladesh?",
                    data_type="textarea",
                    priority="critical",
                    placeholder="Spouse, children, parents - who depends on you",
                    help_text="CRITICAL: Shows you have reasons to return"
                ),
                FieldRequirement(
                    field_key="home_ties.employment_status",
                    field_name="Employment/Business Status",
                    question="Do you have ongoing employment or business in Bangladesh?",
                    data_type="textarea",
                    priority="critical",
                    placeholder="Describe your job or business that requires you to return",
                    help_text="CRITICAL: Shows employment ties to Bangladesh"
                ),
                FieldRequirement(
                    field_key="home_ties.property_in_bangladesh",
                    field_name="Property Ownership",
                    question="Do you own property in Bangladesh?",
                    data_type="textarea",
                    priority="important",
                    placeholder="Address and type of property owned",
                    help_text="Property ownership shows strong ties"
                ),
                FieldRequirement(
                    field_key="home_ties.reasons_to_return",
                    field_name="Reasons to Return",
                    question="Why MUST you return to Bangladesh after your trip?",
                    data_type="textarea",
                    priority="critical",
                    placeholder="List ALL reasons: family, job, business, property, etc.",
                    help_text="MOST IMPORTANT: Convince the embassy you WILL return"
                )
            ],
            
            DocumentType.FINANCIAL_STATEMENT: [
                FieldRequirement(
                    field_key="financial.monthly_income",
                    field_name="Monthly Income",
                    question="What is your average monthly income (in BDT)?",
                    data_type="number",
                    priority="critical",
                    placeholder="e.g., 150000"
                ),
                FieldRequirement(
                    field_key="financial.income_source",
                    field_name="Income Source",
                    question="What is your primary source of income?",
                    data_type="select",
                    priority="critical",
                    options=["Business", "Salaried Job", "Investments", "Rental Income", "Other"]
                ),
                FieldRequirement(
                    field_key="financial.monthly_expenses",
                    field_name="Monthly Expenses",
                    question="What are your average monthly expenses (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 80000"
                ),
                FieldRequirement(
                    field_key="financial.savings",
                    field_name="Total Savings",
                    question="What is your total savings/liquid cash (in BDT)?",
                    data_type="number",
                    priority="important",
                    placeholder="e.g., 800000",
                    help_text="Cash in bank, FDR, etc."
                )
            ]
        }
        
        return requirements_map.get(document_type, [])
    
    @staticmethod
    def get_all_field_keys() -> Set[str]:
        """Get all possible field keys across all documents"""
        all_keys = set()
        for doc_type in DocumentType:
            requirements = DocumentRequirementsMapping.get_requirements(doc_type)
            for req in requirements:
                all_keys.add(req.field_key)
        return all_keys
    
    @staticmethod
    def get_critical_fields() -> Set[str]:
        """Get all critical field keys"""
        critical = set()
        for doc_type in DocumentType:
            requirements = DocumentRequirementsMapping.get_requirements(doc_type)
            for req in requirements:
                if req.priority == "critical":
                    critical.add(req.field_key)
        return critical
