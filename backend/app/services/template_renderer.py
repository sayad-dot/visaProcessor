"""
Template-based PDF generation using HTML templates
Renders professional documents using Jinja2 templates and WeasyPrint
"""
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from typing import Dict, Any
import random


class TemplateRenderer:
    """Renders HTML templates to PDF using WeasyPrint"""
    
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def _format_currency(self, value: str) -> str:
        """Format number as currency with commas"""
        try:
            # Remove any existing formatting
            clean_value = str(value).replace(',', '').replace('BDT', '').replace('Tk', '').strip()
            if not clean_value or clean_value == 'N/A':
                return '0'
            num = int(float(clean_value))
            return f"{num:,}"
        except:
            return '0'
    
    def _generate_random_bangladesh_data(self) -> Dict[str, str]:
        """Generate realistic random data for missing fields"""
        locations = [
            "House-15, Road-7, Block-C, Banani, Dhaka-1213",
            "Flat-4B, Level-6, Gulshan Avenue, Gulshan-1, Dhaka-1212",
            "Plot-22, Sector-10, Uttara Model Town, Dhaka-1230",
            "House-88, Road-3, Dhanmondi R/A, Dhaka-1205",
            "Flat-3A, Bashundhara R/A, Block-D, Dhaka-1229"
        ]
        
        business_names = [
            "TRADE INTERNATIONAL",
            "GLOBAL ENTERPRISE",
            "BUSINESS SOLUTIONS BD",
            "COMMERCIAL VENTURES",
            "EXPORT IMPORT TRADERS"
        ]
        
        vehicles = [
            ("Car Saloon", "Dhaka Metro GA", "TOYOTA"),
            ("Car Saloon", "Dhaka Metro KA", "HONDA"),
            ("SUV", "Dhaka Metro GHA", "MAZDA"),
            ("Car Saloon", "Dhaka Metro BA", "NISSAN")
        ]
        
        return {
            'location': random.choice(locations),
            'business_name': random.choice(business_names),
            'vehicle': random.choice(vehicles)
        }
    
    def render_visiting_card(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Render visiting card from HTML template
        
        Args:
            data: Dictionary with user information
            output_path: Path where PDF will be saved
            
        Returns:
            Path to generated PDF
        """
        template = self.env.get_template('visiting_card_template.html')
        
        # Prepare template data with defaults
        template_data = {
            'full_name': data.get('full_name', 'Business Owner'),
            'designation': data.get('designation', 'Managing Director'),
            'phone': data.get('phone', '+880 1XXX-XXXXXX'),
            'email': data.get('email', 'contact@company.com'),
            'website': data.get('website', 'www.company.com'),
            'address': data.get('address', 'Dhaka, Bangladesh')
        }
        
        # Render HTML
        html_content = template.render(**template_data)
        
        # Generate PDF using WeasyPrint
        try:
            HTML(string=html_content).write_pdf(output_path)
        except Exception as e:
            # Enhanced error message
            import traceback
            error_details = traceback.format_exc()
            raise Exception(f"WeasyPrint rendering failed: {str(e)}\n\nFull traceback:\n{error_details}")
        
        return output_path
    
    def render_asset_valuation(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Render comprehensive 13-page asset valuation certificate from HTML template
        
        Args:
            data: Dictionary with property and asset information
            output_path: Path where PDF will be saved
            
        Returns:
            Path to generated PDF
        """
        template = self.env.get_template('asset_valuation_template_13page.html')
        
        # Get random data for missing fields
        random_data = self._generate_random_bangladesh_data()
        
        # Calculate values
        flat_1 = self._format_currency(data.get('flat_value_1', data.get('property_value', '13623000')))
        flat_2 = self._format_currency(data.get('flat_value_2', '14500000'))
        flat_3 = self._format_currency(data.get('flat_value_3', '12000000'))
        car_val = self._format_currency(data.get('car_value', data.get('vehicle_value', '3500000')))
        business_val = self._format_currency(data.get('business_value', '10250000'))
        
        # Calculate totals and rates
        try:
            total = (int(flat_1.replace(',', '')) + 
                    int(flat_2.replace(',', '')) + 
                    int(flat_3.replace(',', '')) + 
                    int(car_val.replace(',', '')) + 
                    int(business_val.replace(',', '')))
            total_formatted = f"{total:,}"
            exchange_rate = 160.57
            total_pounds = f"{total / exchange_rate:,.2f}"
            
            # Calculate per sqft rates
            size_1 = int(data.get('property_size_1', '1434').replace(',', ''))
            size_2 = int(data.get('property_size_2', '2220').replace(',', ''))
            size_3 = int(data.get('property_size_3', '4875').replace(',', ''))
            
            rate_1 = f"{int(flat_1.replace(',', '')) / size_1:,.2f}"
            rate_2 = f"{int(flat_2.replace(',', '')) / size_2:,.2f}"
            rate_3 = f"{int(flat_3.replace(',', '')) / size_3:,.2f}"
        except:
            total_formatted = "53,873,000"
            total_pounds = "335,569.75"
            rate_1, rate_2, rate_3 = "9,500.00", "6,531.53", "2,461.53"
        
        # Father name processing
        father_name = data.get('father_name', 'FATHER NAME')
        owner_father_relation = data.get('owner_father_relation', f"S/O - {father_name}")
        owner_father_short = data.get('owner_father_relation', f"S/O - {father_name}").replace("S/O - ", "S/O – ")
        
        # Generate vehicle details
        vehicle_data = random_data['vehicle']
        chassis_num = f"BL5FP-{random.randint(100000, 999999)}"
        engine_num = f"ZY-{random.randint(700000, 999999)}"
        
        # Dates
        now = datetime.now()
        report_date = now.strftime('%d %B - %Y')
        report_date_short = now.strftime('%d/%m/%Y')
        
        # Prepare comprehensive template data for 13 pages
        template_data = {
            # PAGE 1: Cover page
            'year': str(now.year),
            'owner_name': data.get('owner_name', data.get('full_name', 'MD PROPERTY OWNER')).upper(),
            'report_date_short': report_date_short,
            
            # PAGE 2: Title page
            'owner_father_relation': owner_father_relation,
            'owner_address': data.get('owner_address', data.get('address', 'Dhaka, Bangladesh')),
            'report_number': f"11/{now.year}",
            'report_date': now.strftime('%d %B - %Y'),
            'reference_number': f"2527/{now.year}",
            
            # PAGE 3: Synopsis - Asset values
            'flat_value_1': flat_1,
            'flat_value_2': flat_2,
            'flat_value_3': flat_3,
            'car_value': car_val,
            'business_value': business_val,
            'total_value': total_formatted,
            'exchange_rate': '160.57',
            'total_pounds': total_pounds,
            
            # PAGE 4-5: Location details
            'owner_father_relation_short': owner_father_short,
            'property_location_1': data.get('property_location_1', 
                'House – 38, Level 07, Road – 01, Sector – 02, Block – F, Aftabnagar, Badda, Gulshan – 1212, Dhaka, Bangladesh.'),
            'property_location_2': data.get('property_location_2', 
                '"Priyanka Runway City" Flat Size -2,220 sqft Flat A: 5 (North aild Level/Floor 2d'),
            'property_location_3': data.get('property_location_3', 
                '"Basundhara Riverview" 1.4428 Decimal 3 Flat Size 1,625x3= 4,875 sqft Mouza at Badda, Khatian – 4253, P.S: Keraniganj, Deed No. 6240 Dated 20.05.2023.'),
            'property_location_3_short': 'Mouza at Beyara, Khatian – 4253, P.S: Keraniganj',
            
            # Vehicle details
            'vehicle_type': data.get('vehicle_type', vehicle_data[0]),
            'vehicle_reg': data.get('vehicle_reg', 
                f"{vehicle_data[1]} {random.randint(10, 99)}-{random.randint(1000, 9999)}"),
            'vehicle_chassis': data.get('vehicle_chassis', chassis_num),
            'vehicle_engine': data.get('vehicle_engine', engine_num),
            'vehicle_manufacturer': data.get('vehicle_manufacturer', vehicle_data[2]),
            
            # Business details
            'business_name': data.get('business_name', random_data['business_name']).upper(),
            'business_type': data.get('business_type', 'Proprietor'),
            'business_ownership': data.get('business_ownership', '100'),
            'business_location': data.get('business_location', random_data['location']),
            
            # PAGE 6: Property deed details
            'property_size_1': data.get('property_size_1', '1,434'),
            'property_size_1_decimal': data.get('property_size_1_decimal', '0.72116'),
            'property_size_2': data.get('property_size_2', '2,220'),
            'property_size_3': data.get('property_size_3', '4,875'),
            'property_size_3_decimal': data.get('property_size_3_decimal', '1.4428'),
            
            # Deed details for Schedule A
            'deed_a_number': data.get('deed_a_number', '6334'),
            'deed_a_dist': data.get('deed_a_dist', 'DHAKA'),
            'deed_a_ps': data.get('deed_a_ps', 'Tejgaon'),
            'deed_a_sro': data.get('deed_a_sro', 'BADDA'),
            'deed_a_mouza': data.get('deed_a_mouza', 'North Meradia - 23'),
            'deed_a_khatian': data.get('deed_a_khatian', '4874'),
            'deed_a_dag': data.get('deed_a_dag', '609'),
            
            # Deed details for Schedule C
            'deed_c_number': data.get('deed_c_number', '6240'),
            'deed_c_dist': data.get('deed_c_dist', 'DHAKA'),
            'deed_c_ps': data.get('deed_c_ps', 'KERANIGANJ'),
            'deed_c_sro': data.get('deed_c_sro', 'KUNDA'),
            'deed_c_mouza': data.get('deed_c_mouza', 'BEYARA - 94'),
            'deed_c_khatian': data.get('deed_c_khatian', '4253'),
            'deed_c_dag': data.get('deed_c_dag', '1116/1122'),
            
            # PAGE 8: Importance of locality
            'area_thana_1': data.get('area_thana_1', 'Badda'),
            'area_thana_3': data.get('area_thana_3', 'Keraniganj'),
            'flat_floor_1': data.get('flat_floor_1', '8th Floor Aftab Nagar, Badda, Gulshan – 1212, Dhaka'),
            
            # PAGE 9-10: Valuation details
            'inspection_request_date': data.get('inspection_request_date', '18.10.2025'),
            'inspection_visit_date': data.get('inspection_visit_date', '28.10.2025'),
            
            # PAGE 10: Per sqft rates
            'rate_per_sqft_1': rate_1,
            'rate_per_sqft_2': rate_2,
            'rate_per_sqft_3': rate_3,
        }
        
        # Render HTML
        html_content = template.render(**template_data)
        
        # Generate PDF using WeasyPrint
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
    
    def render_asset_valuation_5page(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Render 5-page simplified asset valuation certificate (old version for compatibility)
        
        Args:
            data: Dictionary with property and asset information
            output_path: Path where PDF will be saved
            
        Returns:
            Path to generated PDF
        """
        template = self.env.get_template('asset_valuation_template.html')
        
        # Get random data for missing fields
        random_data = self._generate_random_bangladesh_data()
        
        # Calculate values
        flat_1 = self._format_currency(data.get('flat_value_1', data.get('property_value', '13623000')))
        flat_2 = self._format_currency(data.get('flat_value_2', '14500000'))
        flat_3 = self._format_currency(data.get('flat_value_3', '12000000'))
        car_val = self._format_currency(data.get('car_value', data.get('vehicle_value', '3500000')))
        business_val = self._format_currency(data.get('business_value', '10250000'))
        
        # Calculate total
        try:
            total = (int(flat_1.replace(',', '')) + 
                    int(flat_2.replace(',', '')) + 
                    int(flat_3.replace(',', '')) + 
                    int(car_val.replace(',', '')) + 
                    int(business_val.replace(',', '')))
            total_formatted = f"{total:,}"
            total_pounds = f"{total / 160.57:,.2f}"
        except:
            total_formatted = "53,873,000"
            total_pounds = "335,569.75"
        
        # Prepare template data
        template_data = {
            # Basic info
            'year': str(datetime.now().year),
            'owner_name': data.get('owner_name', data.get('full_name', 'PROPERTY OWNER')),
            'owner_father_relation': data.get('owner_father_relation', 
                f"S/O - {data.get('father_name', 'FATHER NAME')}"),
            'owner_address': data.get('owner_address', data.get('address', 'Dhaka, Bangladesh')),
            'report_date': datetime.now().strftime('%d %B, %Y'),
            'report_number': f"{datetime.now().strftime('%m/%Y')}",
            'reference_number': f"{datetime.now().strftime('2527/%Y')}",
            
            # Asset values
            'flat_value_1': flat_1,
            'flat_value_2': flat_2,
            'flat_value_3': flat_3,
            'car_value': car_val,
            'business_value': business_val,
            'total_value': total_formatted,
            'exchange_rate': '160.57',
            'total_pound': total_pounds,
            'total_pounds': total_pounds,
            
            # Property details
            'property_location_1': data.get('property_location_1', 
                'House-38, Level-07, Road-01, Sector-02, Block-F, Aftabnagar, Badda, Gulshan-1212, Dhaka'),
            'property_size_1': data.get('property_size_1', '1,434'),
            
            'property_location_2': data.get('property_location_2', 
                '"Priyanka Runway City" Flat A: 5, Level/Floor 2, Dhaka'),
            'property_size_2': data.get('property_size_2', '2,220'),
            
            'property_location_3': data.get('property_location_3', 
                '"Basundhara Riverview" Mouza at Badda, Khatian-4253, P.S: Keraniganj'),
            'property_size_3': data.get('property_size_3', '4,875'),
            
            # Vehicle details
            'vehicle_type': data.get('vehicle_type', random_data['vehicle'][0]),
            'vehicle_reg': data.get('vehicle_reg', 
                f"{random_data['vehicle'][1]} {random.randint(10, 99)}-{random.randint(1000, 9999)}"),
            'vehicle_manufacturer': data.get('vehicle_manufacturer', random_data['vehicle'][2]),
            
            # Business details
            'business_name': data.get('business_name', random_data['business_name']),
            'business_type': data.get('business_type', 'Proprietor (100% Ownership)'),
            'business_location': data.get('business_location', random_data['location']),
        }
        
        # Render HTML
        html_content = template.render(**template_data)
        
        # Generate PDF using WeasyPrint
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
