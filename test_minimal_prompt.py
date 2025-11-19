"""
Test with increasingly minimal prompts to find the trigger
"""

import os
import sys
import logging
from dotenv import load_dotenv
import time

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


def test_prompt(system_prompt, user_prompt, description):
    """Test a prompt combination"""
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
            "max_output_tokens": 100,
        }
        
        combined = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(
            contents=combined,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                finish_reason = int(candidate.finish_reason) if hasattr(candidate.finish_reason, '__int__') else candidate.finish_reason
                if finish_reason == 2:
                    log.error(f"❌ {description}: BLOCKED")
                    return False
                elif finish_reason == 1:
                    try:
                        text = response.text
                        log.info(f"✓ {description}: SUCCESS - {text[:60]}...")
                        return True
                    except:
                        log.warning(f"⚠️  {description}: finish_reason=1 but no text")
                        return True
        
        return False
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            log.warning(f"⚠️  {description}: Rate limit")
            return None
        else:
            log.error(f"❌ {description}: {error_str[:80]}")
            return False


def main():
    log.info("="*80)
    log.info("TESTING MINIMAL PROMPTS")
    log.info("="*80)
    log.info("Waiting 60 seconds to avoid rate limits...")
    time.sleep(60)
    
    test_context = "SBI Large Cap Fund has an expense ratio of 1.48% for regular plans."
    test_query = "What is the expense ratio of SBI Large Cap Fund?"
    
    tests = [
        # Test 1: Minimal system prompt, simple user prompt
        (
            "You are an FAQ assistant. Answer questions using the provided context.",
            f"Context: {test_context}\n\nQuestion: {test_query}\n\nAnswer:",
            "Minimal FAQ assistant"
        ),
        # Test 2: No system prompt, just user prompt
        (
            "",
            f"Context: {test_context}\n\nQuestion: {test_query}\n\nAnswer based on context:",
            "No system prompt"
        ),
        # Test 3: Very simple system prompt
        (
            "Answer questions using the provided context.",
            f"Context: {test_context}\n\nQuestion: {test_query}",
            "Simple answer instruction"
        ),
        # Test 4: With "mutual fund" in system prompt
        (
            "You are an FAQ assistant for fund information. Answer questions using the provided context.",
            f"Context: {test_context}\n\nQuestion: {test_query}",
            "FAQ assistant for fund information"
        ),
    ]
    
    results = []
    for sys_prompt, user_prompt, desc in tests:
        result = test_prompt(sys_prompt, user_prompt, desc)
        results.append((desc, result))
        log.info("")
        if result is None:  # Rate limit
            log.info("Waiting 60 seconds...")
            time.sleep(60)
        else:
            time.sleep(2)
    
    log.info("="*80)
    log.info("RESULTS")
    log.info("="*80)
    for desc, result in results:
        if result is None:
            status = "⚠️  RATE LIMITED"
        elif result:
            status = "✓ PASS"
        else:
            status = "❌ BLOCKED"
        log.info(f"{status}: {desc}")


if __name__ == "__main__":
    main()

