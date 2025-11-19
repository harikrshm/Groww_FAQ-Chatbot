"""
Test if the query itself is triggering safety filters
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


def test_query(prompt, query, description):
    """Test a prompt+query combination"""
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
        
        full_prompt = f"{prompt}\n\nUser Query: {query}\n\nProvide a factual answer."
        
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
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            log.warning(f"⚠️  {description}: Rate limit - waiting 60 seconds...")
            time.sleep(60)
            return test_query(prompt, query, description)  # Retry
        else:
            log.error(f"❌ {description}: Exception - {error_str[:100]}")
            return False


def main():
    log.info("="*80)
    log.info("TESTING IF QUERY IS TRIGGERING SAFETY FILTERS")
    log.info("="*80)
    log.info("Waiting 60 seconds to avoid rate limits...")
    time.sleep(60)
    
    base_prompt = "You are a factual FAQ assistant. Provide only factual information."
    
    test_queries = [
        ("Hello", "Simple greeting"),
        ("What is 2+2?", "Math question"),
        ("What is the weather?", "General question"),
        ("What is the expense ratio?", "Generic expense ratio question"),
        ("What is the expense ratio of SBI Large Cap Fund?", "Specific fund question"),
        ("Tell me about mutual funds", "General mutual fund question"),
    ]
    
    results = []
    for query, desc in test_queries:
        full_desc = f"{desc} - '{query[:30]}...'"
        result = test_query(base_prompt, query, full_desc)
        results.append((full_desc, result))
        log.info("")
        time.sleep(2)  # Small delay between requests
    
    log.info("="*80)
    log.info("RESULTS SUMMARY")
    log.info("="*80)
    for desc, result in results:
        status = "✓ PASS" if result else "❌ BLOCKED"
        log.info(f"{status}: {desc}")


if __name__ == "__main__":
    main()

