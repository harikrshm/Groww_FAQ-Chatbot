"""
Script to list available Gemini models using google.genai.Client
Checks if gemini-1.5-flash is available for the API key
"""

import os
import sys
from dotenv import load_dotenv

# Set up UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Try different import methods
try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_SDK = False
    except ImportError:
        print("Error: Neither google.genai nor google.generativeai is available")
        print("Please install: pip install google-generativeai")
        exit(1)

# Load environment variables
load_dotenv()

# Get API key from environment or use provided key
api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBU4vZNprqzTVvWOKnnWYFavgK53LpoWk4")

print("="*80)
print("Listing Available Gemini Models")
print("="*80)
print(f"Using API Key: {api_key[:20]}...{api_key[-10:]}")
print("="*80)
print()

try:
    if USE_NEW_SDK:
        # New SDK: google.genai
        client = genai.Client(api_key=api_key)
        models_generator = client.models.list_models()
        models_list = list(models_generator)
    else:
        # Old SDK: google.generativeai
        genai.configure(api_key=api_key)
        models_generator = genai.list_models()
        models_list = list(models_generator)
    
    print(f"Found {len(models_list)} models\n")
    
    # Track if gemini-1.5-flash is found
    gemini_15_flash_found = False
    gemini_models = []
    
    for m in models_list:
        # Get model name/ID - handle both object and dict-like structures
        try:
            if hasattr(m, "name"):
                model_name = m.name
            elif isinstance(m, dict):
                model_name = m.get("name", "<no-name>")
            else:
                model_name = str(m)
        except:
            model_name = str(m)
        
        # Extract just the model ID (remove "models/" prefix if present)
        model_id = model_name.replace("models/", "") if model_name and model_name.startswith("models/") else model_name
        
        # Check if it's a gemini model
        if "gemini" in model_id.lower():
            gemini_models.append(model_id)
            
            # Check specifically for gemini-1.5-flash
            if "gemini-1.5-flash" in model_id.lower():
                gemini_15_flash_found = True
                print("[OK] FOUND: gemini-1.5-flash variant!")
        
        print("MODEL ID:", model_id)
        print("Full Name:", model_name)
        
        # Print supported methods if available
        if hasattr(m, "supported_generation_methods"):
            print("Supported Methods:", m.supported_generation_methods)
        elif hasattr(m, "support"):
            print("Support:", m.support)
        
        # Print metadata if available
        if hasattr(m, "metadata"):
            print("Metadata:", m.metadata)
        
        print("-" * 60)
        print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total models found: {len(models_list)}")
    print(f"Gemini models found: {len(gemini_models)}")
    print()
    
    if gemini_models:
        print("All Gemini models:")
        for model in gemini_models:
            print(f"  - {model}")
        print()
    
    if gemini_15_flash_found:
        print("[OK] gemini-1.5-flash IS AVAILABLE for your API key!")
        print("   You can use: gemini-1.5-flash")
    else:
        print("[X] gemini-1.5-flash NOT FOUND in available models")
        print("   Available Gemini models:")
        for model in gemini_models:
            print(f"     - {model}")
        print()
        print("   You may need to use one of the available models above.")
    
    print("="*80)
    
except Exception as e:
    print(f"[ERROR] Error listing models: {e}")
    import traceback
    traceback.print_exc()

