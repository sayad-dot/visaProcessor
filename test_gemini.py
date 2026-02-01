import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment")
    exit(1)

try:
    genai.configure(api_key=api_key)
    
    # Try to list models
    print("🔍 Testing API connection...")
    models = genai.list_models()
    
    print(f"✅ Connected successfully!")
    print(f"📊 Found {len(list(models))} models")
    
    # Test a simple generation with gemini-1.5-flash
    print("\n🤖 Testing model 'gemini-1.5-flash'...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"✅ Model test successful: {response.text[:50]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")