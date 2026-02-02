"""
Test script for template-based document generation
Run this to verify visiting card and asset valuation templates work
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.template_renderer import TemplateRenderer
from datetime import datetime

def test_visiting_card():
    """Test visiting card generation"""
    print("=" * 60)
    print("Testing Visiting Card Generation")
    print("=" * 60)
    
    renderer = TemplateRenderer()
    
    # Test data
    test_data = {
        'full_name': 'MD SWAPON SHEIKH',
        'designation': 'CEO & Managing Director',
        'phone': '+880 1777-265211',
        'email': 'swapon@company.com',
        'website': 'www.swcompany.com',
        'address': 'Chandpur Sadar, Chandpur, Bangladesh'
    }
    
    output_path = 'generated/test_visiting_card.pdf'
    os.makedirs('generated', exist_ok=True)
    
    try:
        renderer.render_visiting_card(test_data, output_path)
        print(f"✅ SUCCESS: Visiting card generated at {output_path}")
        print(f"   File size: {os.path.getsize(output_path)} bytes")
        return True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_asset_valuation():
    """Test asset valuation generation"""
    print("\n" + "=" * 60)
    print("Testing Asset Valuation Generation")
    print("=" * 60)
    
    renderer = TemplateRenderer()
    
    # Test data
    test_data = {
        'owner_name': 'MD SWAPON SHEIKH',
        'owner_father_relation': 'S/O - MD BABUL SHEIKH',
        'owner_address': 'SHILON DIA, WARD NO - 14, CHANDPUR SADAR, CHANDPUR',
        'flat_value_1': '13623000',
        'flat_value_2': '14500000',
        'flat_value_3': '12000000',
        'car_value': '3500000',
        'business_value': '10250000',
        'business_name': 'SHEIKH ONLINE SERVICE',
        'business_type': 'Proprietor (100% Ownership)',
    }
    
    output_path = 'generated/test_asset_valuation.pdf'
    
    try:
        renderer.render_asset_valuation(test_data, output_path)
        print(f"✅ SUCCESS: Asset valuation generated at {output_path}")
        print(f"   File size: {os.path.getsize(output_path)} bytes")
        return True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Template Generation Tests\n")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {os.getcwd()}\n")
    
    # Run tests
    visiting_card_ok = test_visiting_card()
    asset_valuation_ok = test_asset_valuation()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Visiting Card: {'✅ PASSED' if visiting_card_ok else '❌ FAILED'}")
    print(f"Asset Valuation: {'✅ PASSED' if asset_valuation_ok else '❌ FAILED'}")
    
    if visiting_card_ok and asset_valuation_ok:
        print("\n🎉 All tests passed! Templates are working correctly.")
        print("\nGenerated files:")
        print("  - generated/test_visiting_card.pdf")
        print("  - generated/test_asset_valuation.pdf")
        print("\nYou can now use these templates in your visa application system!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 60)
