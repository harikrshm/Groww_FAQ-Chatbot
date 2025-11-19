"""
Script to list available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available Gemini models...")
print("="*80)

try:
    models = genai.list_models()
    print("\nAvailable models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            print(f"    Display Name: {model.display_name}")
            print(f"    Description: {model.description}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")

