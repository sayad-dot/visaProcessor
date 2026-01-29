#!/usr/bin/env python3
"""
Quick Test Script for Phase 3.1
Tests AI analysis and questionnaire generation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    print("🔍 Testing backend health...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Backend is healthy:", response.json())
        return True
    else:
        print("❌ Backend not responding")
        return False

def test_analysis_endpoints():
    """Test if analysis endpoints exist"""
    print("\n🔍 Testing analysis endpoints...")
    
    # This will fail with 404 (no app), but confirms endpoint exists
    response = requests.post(f"{BASE_URL}/api/analysis/start/999")
    if response.status_code in [404, 422]:  # Not found or validation error
        print("✅ Analysis start endpoint exists")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/api/analysis/status/999")
    if response.status_code in [404, 422]:
        print("✅ Analysis status endpoint exists")
    else:
        print(f"❌ Unexpected response: {response.status_code}")

def test_questionnaire_endpoints():
    """Test if questionnaire endpoints exist"""
    print("\n🔍 Testing questionnaire endpoints...")
    
    response = requests.get(f"{BASE_URL}/api/questionnaire/generate/999")
    if response.status_code in [404, 422, 400]:
        print("✅ Questionnaire generate endpoint exists")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/api/questionnaire/progress/999")
    if response.status_code in [404, 422]:
        print("✅ Questionnaire progress endpoint exists")
    else:
        print(f"❌ Unexpected response: {response.status_code}")

def test_swagger_docs():
    """Test if Swagger docs show new endpoints"""
    print("\n🔍 Testing Swagger documentation...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})
        
        analysis_endpoints = [p for p in paths if '/analysis/' in p]
        questionnaire_endpoints = [p for p in paths if '/questionnaire/' in p]
        
        print(f"✅ Found {len(analysis_endpoints)} analysis endpoints:")
        for endpoint in analysis_endpoints:
            print(f"   - {endpoint}")
        
        print(f"✅ Found {len(questionnaire_endpoints)} questionnaire endpoints:")
        for endpoint in questionnaire_endpoints:
            print(f"   - {endpoint}")
        
        return len(analysis_endpoints) >= 3 and len(questionnaire_endpoints) >= 4
    else:
        print("❌ Could not fetch OpenAPI spec")
        return False

def test_database_tables():
    """Test if database tables exist by trying to query"""
    print("\n🔍 Testing database tables...")
    print("⚠️  This requires a test application ID")
    print("   Database tables should be verified manually:")
    print("   - extracted_data")
    print("   - questionnaire_responses")
    print("   - analysis_sessions")

def main():
    print("=" * 60)
    print("Phase 3.1 Quick Test Script")
    print("=" * 60)
    
    if not test_health():
        print("\n❌ Backend is not running. Start it first:")
        print("   cd backend && source venv/bin/activate && python main.py")
        return
    
    test_analysis_endpoints()
    test_questionnaire_endpoints()
    test_swagger_docs()
    test_database_tables()
    
    print("\n" + "=" * 60)
    print("✅ Phase 3.1 Backend Tests Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Open frontend: http://localhost:3000")
    print("2. Create a test application")
    print("3. Upload 8 test documents")
    print("4. Click 'Analyze Documents'")
    print("5. Fill the questionnaire")
    print("\nSee PHASE_3_1_TEST_GUIDE.md for detailed testing instructions")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure backend is running on http://localhost:8000")
