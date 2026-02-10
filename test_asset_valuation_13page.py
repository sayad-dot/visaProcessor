"""
Test the 13-page Asset Valuation template generation
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.template_renderer import TemplateRenderer

def test_13page_asset_valuation():
    """Test generating the comprehensive 13-page asset valuation"""
    
    renderer = TemplateRenderer()
    
    # Sample data matching the real template structure
    test_data = {
        'owner_name': 'MD SWAPON SHEIKH',
        'father_name': 'MD BABUL SHEIKH',
        'owner_father_relation': 'S/0 – MD BABUL SHEIKH',
        'owner_address': 'SHILON DIA, WARD NO - 14, CHANDPUR SADAR MODEL, BABURHAT -3602, CHANDPUR',
        
        # Asset values
        'flat_value_1': '13623000',
        'flat_value_2': '14500000',
        'flat_value_3': '12000000',
        'car_value': '3500000',
        'business_value': '10250000',
        
        # Property details
        'property_location_1': 'House – 38, Level 07, Road – 01, Sector – 02, Block – F, Aftabnagar, Badda, Gulshan – 1212, Dhaka, Bangladesh.',
        'property_size_1': '1,434',
        'property_size_1_decimal': '0.72116',
        
        'property_location_2': '"Priyanka Runway City" Flat Size -2,220 sqft Flat A: 5 (North aild Level/Floor 2d',
        'property_size_2': '2,220',
        
        'property_location_3': '"Basundhara Riverview" 1.4428 Decimal 3 Flat Size 1,625x3= 4,875 sqft Mouza at Badda, Khatian – 4253, P.S: Keraniganj, Deed No. 6240 Dated 20.05.2023.',
        'property_size_3': '4,875',
        'property_size_3_decimal': '1.4428',
        
        # Vehicle details
        'vehicle_type': 'Car Saloon',
        'vehicle_reg': 'Dhaka Metro Ga 26-2489',
        'vehicle_chassis': 'BL5FP-107239',
        'vehicle_engine': 'ZY-748906',
        'vehicle_manufacturer': 'MAZDA',
        
        # Business details
        'business_name': 'SHEIKH ONLINE SERVICE',
        'business_type': 'Proprietor',
        'business_ownership': '100',
        'business_location': '706, Moddo Naya Nagar, Vatara, Dhaka-1212 Bangladesh',
        
        # Deed details
        'deed_a_number': '6334',
        'deed_a_dist': 'DHAKA',
        'deed_a_ps': 'Tejgaon',
        'deed_a_sro': 'BADDA',
        'deed_a_mouza': 'North Meradia - 23',
        'deed_a_khatian': '4874',
        'deed_a_dag': '609',
        
        'deed_c_number': '6240',
        'deed_c_dist': 'DHAKA',
        'deed_c_ps': 'KERANIGANJ',
        'deed_c_sro': 'KUNDA',
        'deed_c_mouza': 'BEYARA - 94',
        'deed_c_khatian': '4253',
        'deed_c_dag': '1116/1122',
        
        # Area info
        'area_thana_1': 'Badda',
        'area_thana_3': 'Keraniganj',
        'flat_floor_1': '8th Floor Aftab Nagar, Badda, Gulshan – 1212, Dhaka',
    }
    
    output_path = 'generated/test_asset_valuation_13page.pdf'
    
    # Create generated directory if it doesn't exist
    os.makedirs('generated', exist_ok=True)
    
    print("=" * 80)
    print("Testing 13-Page Asset Valuation Generation")
    print("=" * 80)
    
    try:
        result = renderer.render_asset_valuation(test_data, output_path)
        file_size = os.path.getsize(result)
        
        print(f"✅ SUCCESS: 13-page Asset Valuation generated at {result}")
        print(f"File size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("13-Page Asset Valuation: ✅ PASSED")
        print("\n🎉 Test completed! The comprehensive template is working correctly.")
        print(f"\n📄 Open the file to review: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to generate Asset Valuation")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_13page_asset_valuation()
    sys.exit(0 if success else 1)
