import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found!")
    exit(1)

try:
    print("🔍 Configuring Gemini AI...")
    genai.configure(api_key=api_key)
    
    print("📊 Listing ALL available models that support generateContent:")
    models = list(genai.list_models())
    
    working_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✓ {model.name}")
            working_models.append(model.name)
    
    print(f"\n✅ Found {len(working_models)} models that support generateContent")
    
    # Try each model
    for model_name in working_models:
        print(f"\n🤖 Testing '{model_name}'...")
        try:
            # Use a very simple test
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            if response and hasattr(response, 'text'):
                print(f"✅ WORKS: {model_name}")
                print(f"   Response: {response.text[:100]}")
                break  # Found a working model
            else:
                print(f"❌ No response from {model_name}")
        except Exception as e:
            print(f"❌ Error with {model_name}: {str(e)[:100]}")
    
    print("\n✨ RECOMMENDED MODELS TO USE:")
    for model_name in working_models:
        if 'flash' in model_name.lower():
            print(f"  - {model_name} (fast)")
        elif 'pro' in model_name.lower():
            print(f"  - {model_name} (powerful)")
            
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()