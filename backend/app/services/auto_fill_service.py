"""
Auto-fill Service - Generate realistic data for missing questionnaire fields
Based on comprehensive analysis of all 13 document templates
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import string


class AutoFillService:
    """
    Generates realistic data for missing fields in visa application questionnaire
    Ensures NO BLANK DATA in any generated document
    """
    
    # Realistic Bangladeshi names database
    MALE_FIRST_NAMES = [
        "Mohammad", "MD", "Abdul", "Muhammad", "Ahmed", "Ashraf", "Kamal", "Rashid",
        "Fazlur", "Habibur", "Mujibur", "Rafiqul", "Shamsul", "Anwar", "Hafiz"
    ]
    
    MALE_LAST_NAMES = [
        "Rahman", "Islam", "Hossain", "Khan", "Ahmed", "Ali", "Chowdhury", 
        "Mahmud", "Hassan", "Karim", "Miah", "Uddin", "Alam"
    ]
    
    FEMALE_FIRST_NAMES = [
        "Fatima", "Ayesha", "Amina", "Khadija", "Nusrat", "Taslima", "Rashida",
        "Nasrin", "Farzana", "Roksana", "Shahnaz", "Sultana"
    ]
    
    # Business types common in Bangladesh
    BUSINESS_TYPES = [
        "Import/Export Trading",
        "Garment Manufacturing",
        "IT Services & Software",
        "Retail Store Chain",
        "Real Estate Development",
        "Food Processing",
        "Pharmaceutical Distribution",
        "Textile Trading",
        "Electronics Import",
        "Construction Company"
    ]
    
    # Common professions
    PROFESSIONS = [
        "Business Owner",
        "Managing Director",
        "General Manager",
        "Sales Manager",
        "IT Professional",
        "Teacher",
        "Engineer",
        "Doctor",
        "Accountant"
    ]
    
    # Bangladeshi banks
    BANKS = [
        "Dutch-Bangla Bank Limited",
        "City Bank Limited",
        "BRAC Bank Limited",
        "Eastern Bank Limited",
        "Jamuna Bank Limited",
        "Mutual Trust Bank",
        "Prime Bank Limited",
        "Standard Chartered Bank",
        "Islami Bank Bangladesh",
        "Bank Asia Limited"
    ]
    
    # Account types
    ACCOUNT_TYPES = ["Savings Account", "Current Account", "Fixed Deposit"]
    
    # Dhaka areas
    DHAKA_AREAS = [
        "Bashundhara R/A",
        "Gulshan",
        "Banani",
        "Dhanmondi",
        "Uttara",
        "Mirpur",
        "Mohammadpur",
        "Lalmatia"
    ]
    
    # Countries for travel history
    TRAVEL_COUNTRIES = [
        {"name": "Malaysia", "days": [10, 13, 15], "year_range": (2018, 2024)},
        {"name": "Singapore", "days": [3, 5, 7], "year_range": (2018, 2024)},
        {"name": "Dubai, UAE", "days": [5, 7, 10], "year_range": (2019, 2024)},
        {"name": "Thailand", "days": [7, 10, 14], "year_range": (2018, 2023)},
        {"name": "India", "days": [3, 5, 7], "year_range": (2018, 2024)},
        {"name": "Turkey", "days": [7, 10, 12], "year_range": (2019, 2024)}
    ]
    
    # Iceland hotels
    ICELAND_HOTELS = [
        {"name": "Reykjavik Grand Hotel", "address": "Sigtún 38, 105 Reykjavik"},
        {"name": "Hotel Borg by Keahotels", "address": "Pósthússtræti 11, 101 Reykjavik"},
        {"name": "Canopy by Hilton Reykjavik City Centre", "address": "Smáratorgi 1, 201 Reykjavik"},
        {"name": "Fosshotel Reykjavik", "address": "Þórunnartún 1, 105 Reykjavik"},
        {"name": "Center Hotels Plaza", "address": "Aðalstræti 4, 101 Reykjavik"}
    ]
    
    # Airlines
    AIRLINES = [
        "Biman Bangladesh Airlines",
        "Turkish Airlines",
        "Emirates",
        "Qatar Airways",
        "Etihad Airways"
    ]
    
    def __init__(self, base_data: Dict[str, Any]):
        """
        Initialize with existing questionnaire data
        base_data: Dictionary of already filled questionnaire answers
        """
        self.base_data = base_data
        self.filled_data = base_data.copy()
        
    def auto_fill_all(self) -> Dict[str, Any]:
        """
        Auto-fill ALL missing fields with realistic data
        Returns complete dictionary with no missing values
        """
        # Personal info
        self._fill_personal_info()
        
        # Employment/Business
        self._fill_employment_info()
        
        # Travel details
        self._fill_travel_info()
        
        # Financial & Assets
        self._fill_financial_info()
        
        # Other info
        self._fill_other_info()
        
        return self.filled_data
    
    def _fill_personal_info(self):
        """Fill missing personal information fields"""
        
        # Full name - CRITICAL
        if not self.filled_data.get("full_name"):
            gender = random.choice(["male", "female"])
            if gender == "male":
                first = random.choice(self.MALE_FIRST_NAMES)
                last = random.choice(self.MALE_LAST_NAMES)
            else:
                first = random.choice(self.FEMALE_FIRST_NAMES)
                last = random.choice(self.MALE_LAST_NAMES)
            self.filled_data["full_name"] = f"{first} {last}"
        
        # Email
        if not self.filled_data.get("email"):
            name_parts = self.filled_data["full_name"].lower().replace(" ", ".")
            domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])
            self.filled_data["email"] = f"{name_parts}@{domain}"
        
        # Phone - EXACTLY +880 format with realistic Bangladesh operator codes
        # Format: +880-{operator 3 digits}{remaining 7 digits} = +880-1712345678
        if not self.filled_data.get("phone"):
            operator = random.choice(["017", "018", "019", "013", "014", "015", "016"])
            remaining = "".join([str(random.randint(0, 9)) for _ in range(7)])
            self.filled_data["phone"] = f"+880-{operator}{remaining}"
        
        # Date of birth - between 25-55 years old
        if not self.filled_data.get("date_of_birth"):
            age = random.randint(25, 55)
            birth_year = datetime.now().year - age
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            self.filled_data["date_of_birth"] = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        # Father's name
        if not self.filled_data.get("father_name"):
            first = random.choice(self.MALE_FIRST_NAMES)
            last = random.choice(self.MALE_LAST_NAMES)
            self.filled_data["father_name"] = f"{first} {last}"
        
        # Mother's name
        if not self.filled_data.get("mother_name"):
            first = random.choice(self.FEMALE_FIRST_NAMES)
            last = "Begum"
            self.filled_data["mother_name"] = f"{first} {last}"
        
        # Permanent address
        if not self.filled_data.get("permanent_address"):
            house = random.randint(1, 150)
            road = random.randint(1, 30)
            area = random.choice(self.DHAKA_AREAS)
            self.filled_data["permanent_address"] = f"House# {house}, Road# {road}, {area}, Dhaka-1229"
        
        # Present address
        if not self.filled_data.get("present_address"):
            self.filled_data["present_address"] = self.filled_data.get("permanent_address", "Same as permanent")
        
        # Passport number - EXACTLY 2 letters + 7 digits (Bangladesh format)
        if not self.filled_data.get("passport_number"):
            letters = "".join(random.choices(string.ascii_uppercase, k=2))
            digits = "".join([str(random.randint(0, 9)) for _ in range(7)])
            self.filled_data["passport_number"] = f"{letters}{digits}"
        
        # NID number - EXACTLY 10 or 13 or 17 digits (Bangladesh formats)
        if not self.filled_data.get("nid_number"):
            format_choice = random.choice([10, 13, 17])
            nid = "".join([str(random.randint(0, 9)) for _ in range(format_choice)])
            self.filled_data["nid_number"] = nid
        
        # Marital status
        if not self.filled_data.get("is_married"):
            self.filled_data["is_married"] = random.choice(["Yes", "No"])
        
        # If married, add spouse
        if self.filled_data.get("is_married") == "Yes":
            if not self.filled_data.get("spouse_name"):
                # Assume opposite gender
                if "Mohammad" in self.filled_data.get("full_name", "") or "MD" in self.filled_data.get("full_name", ""):
                    first = random.choice(self.FEMALE_FIRST_NAMES)
                    self.filled_data["spouse_name"] = f"Mrs. {first} Begum"
                else:
                    first = random.choice(self.MALE_FIRST_NAMES)
                    last = random.choice(self.MALE_LAST_NAMES)
                    self.filled_data["spouse_name"] = f"Mr. {first} {last}"
            
            if not self.filled_data.get("number_of_children"):
                self.filled_data["number_of_children"] = random.randint(0, 3)
    
    def _fill_employment_info(self):
        """Fill missing employment/business information"""
        
        # Employment status
        if not self.filled_data.get("employment_status"):
            self.filled_data["employment_status"] = random.choice([
                "Business Owner", 
                "Employed (Job Holder)", 
                "Self-Employed"
            ])
        
        # Job title
        if not self.filled_data.get("job_title"):
            status = self.filled_data.get("employment_status", "Business Owner")
            if "Business Owner" in status:
                self.filled_data["job_title"] = "Managing Director"
            elif "Employed" in status:
                self.filled_data["job_title"] = random.choice([
                    "Senior Manager", "General Manager", "Sales Manager", 
                    "IT Manager", "Operations Manager"
                ])
            else:
                self.filled_data["job_title"] = random.choice(self.PROFESSIONS)
        
        # Company name
        if not self.filled_data.get("company_name"):
            name_part = self.filled_data.get("full_name", "").split()[0]
            company_type = random.choice(["Trading", "International", "Corporation", "Group", "Enterprises"])
            self.filled_data["company_name"] = f"{name_part} {company_type}"
        
        # Business type
        if not self.filled_data.get("business_type"):
            self.filled_data["business_type"] = random.choice(self.BUSINESS_TYPES)
        
        # Business address
        if not self.filled_data.get("business_address"):
            floor = random.randint(2, 10)
            building = random.choice(["Tropicana Tower", "City Center", "Trade Tower", "Plaza"])
            area = random.choice(self.DHAKA_AREAS)
            self.filled_data["business_address"] = f"Floor {floor}, {building}, {area}, Dhaka"
        
        # Business start year
        if not self.filled_data.get("business_start_year"):
            current_year = datetime.now().year
            self.filled_data["business_start_year"] = random.randint(current_year - 15, current_year - 3)
        
        # Number of employees
        if not self.filled_data.get("number_of_employees"):
            self.filled_data["number_of_employees"] = random.randint(5, 50)
    
    def _fill_travel_info(self):
        """Fill missing travel information"""
        
        # Travel purpose
        if not self.filled_data.get("travel_purpose"):
            self.filled_data["travel_purpose"] = "Tourism"
        
        # Duration
        if not self.filled_data.get("duration_days"):
            self.filled_data["duration_days"] = random.choice([7, 10, 14])
        
        # Departure date - 3-6 months from now
        if not self.filled_data.get("departure_date"):
            days_ahead = random.randint(90, 180)
            departure = datetime.now() + timedelta(days=days_ahead)
            self.filled_data["departure_date"] = departure.strftime("%Y-%m-%d")
        
        # Return date
        if not self.filled_data.get("return_date"):
            departure = datetime.strptime(self.filled_data.get("departure_date"), "%Y-%m-%d")
            duration = self.filled_data.get("duration_days", 14)
            return_date = departure + timedelta(days=duration)
            self.filled_data["return_date"] = return_date.strftime("%Y-%m-%d")
        
        # Previous travel
        if not self.filled_data.get("has_previous_travel"):
            self.filled_data["has_previous_travel"] = random.choice(["Yes", "No"])
        
        # Generate 1-3 previous travels if Yes
        if self.filled_data.get("has_previous_travel") == "Yes":
            if not self.filled_data.get("previous_travels"):
                num_travels = random.randint(1, 3)
                travels = []
                for _ in range(num_travels):
                    country_info = random.choice(self.TRAVEL_COUNTRIES)
                    year = random.randint(country_info["year_range"][0], country_info["year_range"][1])
                    duration = random.choice(country_info["days"])
                    travels.append({
                        "country": country_info["name"],
                        "year": year,
                        "duration_days": duration
                    })
                self.filled_data["previous_travels"] = travels
        
        # Air ticket
        if not self.filled_data.get("has_air_ticket"):
            self.filled_data["has_air_ticket"] = random.choice(["Yes", "No"])
        
        if self.filled_data.get("has_air_ticket") == "No":
            if not self.filled_data.get("airline_preference"):
                self.filled_data["airline_preference"] = random.choice(self.AIRLINES)
            if not self.filled_data.get("departure_airport"):
                self.filled_data["departure_airport"] = "Hazrat Shahjalal International Airport (DAC)"
        
        # Hotel booking
        if not self.filled_data.get("has_hotel_booking"):
            self.filled_data["has_hotel_booking"] = random.choice(["Yes", "No"])
        
        if self.filled_data.get("has_hotel_booking") == "No":
            # Auto-generate hotel
            hotel = random.choice(self.ICELAND_HOTELS)
            self.filled_data["hotel_name"] = hotel["name"]
            self.filled_data["hotel_address"] = hotel["address"]
            self.filled_data["room_type"] = random.choice(["Standard Double", "Deluxe Room", "Suite"])
        
        # Places to visit
        if not self.filled_data.get("places_to_visit"):
            self.filled_data["places_to_visit"] = "Reykjavik, Golden Circle, Blue Lagoon, Northern Lights, Geysir, Gullfoss Waterfall"
    
    def _fill_financial_info(self):
        """Fill missing financial information with realistic values"""
        
        # At least 1 bank account required
        if not self.filled_data.get("banks"):
            num_banks = random.randint(1, 2)
            banks = []
            for i in range(num_banks):
                bank_name = random.choice(self.BANKS)
                account_type = random.choice(self.ACCOUNT_TYPES)
                
                # Account number: XXX-XXX-XXXXXX format
                part1 = "".join([str(random.randint(0, 9)) for _ in range(3)])
                part2 = "".join([str(random.randint(0, 9)) for _ in range(3)])
                part3 = "".join([str(random.randint(0, 9)) for _ in range(6)])
                account_number = f"{part1}-{part2}-{part3}"
                
                # Balance based on travel budget
                if i == 0:  # Main account
                    balance = random.randint(600000, 1200000)  # 600K-1.2M BDT
                else:  # Secondary account
                    balance = random.randint(200000, 500000)  # 200K-500K BDT
                
                banks.append({
                    "bank_name": bank_name,
                    "account_type": account_type,
                    "account_number": account_number,
                    "balance": balance
                })
            self.filled_data["banks"] = banks
        
        # Monthly income
        if not self.filled_data.get("monthly_income"):
            # Based on balance (assume 6-10 months of income in bank)
            total_balance = sum(b.get("balance", 0) for b in self.filled_data.get("banks", []))
            monthly = total_balance // random.randint(6, 10)
            self.filled_data["monthly_income"] = monthly
        
        # Monthly expenses (70-80% of income)
        if not self.filled_data.get("monthly_expenses"):
            income = self.filled_data.get("monthly_income", 100000)
            self.filled_data["monthly_expenses"] = int(income * random.uniform(0.70, 0.80))
        
        # Income history (last 3 years)
        if not self.filled_data.get("income_sources"):
            monthly = self.filled_data.get("monthly_income", 100000)
            income_history = []
            for year in range(2021, 2024):
                annual = monthly * 12
                # Add 10-15% growth per year
                growth = random.uniform(1.10, 1.15) ** (2023 - year)
                annual_adjusted = int(annual * growth)
                tax_paid = int(annual_adjusted * random.uniform(0.02, 0.05))  # 2-5% tax
                income_history.append({
                    "year": year,
                    "income": annual_adjusted,
                    "tax_paid": tax_paid
                })
            self.filled_data["income_sources"] = income_history
        
        # Assets
        if not self.filled_data.get("has_assets"):
            self.filled_data["has_assets"] = "Yes"
        
        if self.filled_data.get("has_assets") == "Yes":
            if not self.filled_data.get("assets"):
                assets = []
                
                # Property (house/building)
                area = random.choice(self.DHAKA_AREAS)
                katha = round(random.uniform(3.0, 8.0), 2)
                sqft = int(katha * 720)  # 1 Katha ≈ 720 sq ft
                floors = random.randint(3, 6)
                # Property value: 4-8 million BDT per Katha in good areas
                property_value = int(katha * random.randint(4000000, 8000000))
                
                assets.append({
                    "asset_type": "Building/House",
                    "location": f"{area}, Dhaka",
                    "size": f"{katha} Katha ({sqft:,} sq ft)",
                    "estimated_value": property_value,
                    "description": f"{floors}-story building with {floors-1} residential units"
                })
                
                # Vehicle (optional)
                if random.random() > 0.4:  # 60% chance
                    car_models = ["Toyota Allion 2020", "Honda Civic 2019", "Toyota Corolla 2021", "Honda CR-V 2020"]
                    vehicle = random.choice(car_models)
                    vehicle_value = random.randint(2000000, 4000000)  # 2-4M BDT
                    assets.append({
                        "asset_type": "Vehicle",
                        "vehicle_type": vehicle,
                        "estimated_value": vehicle_value,
                        "description": "Personal car"
                    })
                
                self.filled_data["assets"] = assets
            
            # Rental income (if has building with multiple units)
            if not self.filled_data.get("rental_income"):
                building_asset = next((a for a in self.filled_data.get("assets", []) if "Building" in a.get("asset_type", "")), None)
                if building_asset:
                    # Assume 1-2% of property value per month as rental
                    property_val = building_asset.get("estimated_value", 10000000)
                    monthly_rental = int(property_val * random.uniform(0.01, 0.02))
                    self.filled_data["rental_income"] = monthly_rental
    
    def _fill_other_info(self):
        """Fill missing other information"""
        
        # TIN number
        if not self.filled_data.get("has_tin"):
            self.filled_data["has_tin"] = "Yes"
        
        if self.filled_data.get("has_tin") == "Yes":
            if not self.filled_data.get("tin_number"):
                # EXACTLY 12 digits in XXX-XXX-XXX-XXXX format
                part1 = "".join([str(random.randint(0, 9)) for _ in range(3)])
                part2 = "".join([str(random.randint(0, 9)) for _ in range(3)])
                part3 = "".join([str(random.randint(0, 9)) for _ in range(3)])
                part4 = "".join([str(random.randint(0, 9)) for _ in range(4)])
                self.filled_data["tin_number"] = f"{part1}-{part2}-{part3}-{part4}"
            
            if not self.filled_data.get("tin_circle"):
                zone = random.choice(["Dhaka", "Gulshan", "Motijheel", "Uttara", "Mirpur"])
                circle_num = random.randint(1, 5)
                self.filled_data["tin_circle"] = f"{zone} Taxes Circle-{circle_num}"
        
        # Tax certificates (last 3 years)
        if not self.filled_data.get("has_tax_certificates"):
            self.filled_data["has_tax_certificates"] = "Yes"
        
        if self.filled_data.get("has_tax_certificates") == "Yes":
            if not self.filled_data.get("tax_certificates"):
                certs = []
                for year in range(2021, 2024):
                    cert_num = random.randint(1000, 9999)
                    certs.append({
                        "year": f"{year}-{year+1}",
                        "certificate_number": f"TAX/{year}/NBR/{cert_num}"
                    })
                self.filled_data["tax_certificates"] = certs
        
        # Reasons to return
        if not self.filled_data.get("reasons_to_return"):
            reasons = []
            if self.filled_data.get("is_married") == "Yes":
                reasons.append("My wife and children depend on me")
            if self.filled_data.get("employment_status") == "Business Owner":
                reasons.append(f"I own and manage {self.filled_data.get('company_name', 'my business')}")
            if self.filled_data.get("assets"):
                reasons.append("I have significant property and assets in Bangladesh")
            if not reasons:
                reasons.append("My family, business, and all my assets are in Bangladesh")
            
            self.filled_data["reasons_to_return"] = ". ".join(reasons) + "."
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of what was auto-filled"""
        original_keys = set(self.base_data.keys())
        filled_keys = set(self.filled_data.keys())
        auto_filled_keys = filled_keys - original_keys
        
        return {
            "original_field_count": len(original_keys),
            "total_field_count": len(filled_keys),
            "auto_filled_count": len(auto_filled_keys),
            "auto_filled_fields": list(auto_filled_keys),
            "completion_percentage": 100 if filled_keys else 0
        }


def auto_fill_questionnaire(base_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Main function to auto-fill questionnaire
    
    Args:
        base_data: Existing questionnaire responses
        
    Returns:
        tuple: (filled_data, summary)
    """
    service = AutoFillService(base_data)
    filled_data = service.auto_fill_all()
    summary = service.get_summary()
    
    return filled_data, summary
