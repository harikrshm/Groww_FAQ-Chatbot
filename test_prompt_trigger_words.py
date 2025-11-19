"""
Test which specific words/phrases in the system prompt trigger safety filters
"""

import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not API_KEY:
    log.error("GEMINI_API_KEY not found")
    sys.exit(1)


def test_prompt(prompt_text, description):
    """Test a prompt and return whether it was blocked"""
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        safety_settings = [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ]
        
        generation_config = {
            "temperature": 0.1,
            "max_output_tokens": 50,
        }
        
        user_query = "What is the expense ratio of SBI Large Cap Fund?"
        full_prompt = f"{prompt_text}\n\nUser Query: {user_query}\n\nProvide a factual answer."
        
        response = model.generate_content(
            contents=full_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = int(candidate.finish_reason) if hasattr(candidate.finish_reason, '__int__') else candidate.finish_reason
                if finish_reason == 2:
                    log.error(f"❌ {description}: BLOCKED (finish_reason: 2)")
                    return False
                elif finish_reason == 1:
                    try:
                        text = response.text
                        log.info(f"✓ {description}: SUCCESS - {text[:50]}...")
                        return True
                    except:
                        log.warning(f"⚠️  {description}: finish_reason=1 but no text")
                        return True
        
        return False
        
    except Exception as e:
        log.error(f"❌ {description}: Exception - {e}")
        return False


def main():
    log.info("="*80)
    log.info("TESTING PROMPT TRIGGER WORDS")
    log.info("="*80)
    
    # Test different versions of the system prompt
    tests = [
        ("You are a factual FAQ assistant.", "Base prompt"),
        ("You are a factual FAQ assistant. Provide only factual information.", "With 'factual information'"),
        ("You are a factual FAQ assistant. Do NOT provide opinions or recommendations.", "With 'recommendations'"),
        ("You are a factual FAQ assistant. Never suggest which fund to buy or sell.", "With 'buy or sell'"),
        ("You are a factual FAQ assistant. Never suggest which fund to invest in.", "With 'invest in'"),
        ("You are a factual FAQ assistant. Never provide investment advice.", "With 'investment advice'"),
        ("You are a factual FAQ assistant. Never make claims about fund performance.", "With 'performance'"),
        ("You are a factual FAQ assistant. Never provide recommendations, opinions, or predictions.", "With 'recommendations, opinions, predictions'"),
        ("You are a factual FAQ assistant for SBI Mutual Fund schemes. Your role is to provide ONLY factual information from the provided context.", "Full first sentence"),
        ("You are a factual FAQ assistant. Never suggest which fund to buy, sell, or invest in.", "With 'buy, sell, or invest'"),
    ]
    
    results = []
    for prompt, desc in tests:
        result = test_prompt(prompt, desc)
        results.append((desc, result))
        log.info("")
    
    log.info("="*80)
    log.info("RESULTS SUMMARY")
    log.info("="*80)
    for desc, result in results:
        status = "✓ PASS" if result else "❌ BLOCKED"
        log.info(f"{status}: {desc}")


if __name__ == "__main__":
    main()

