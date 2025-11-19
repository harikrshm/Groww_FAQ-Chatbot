"""
Test if it's the query or the prompt causing the block
"""

import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SYSTEM_PROMPT

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


def test_combination(system_prompt, query, context, description):
    """Test a specific combination"""
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        user_prompt = f"""Context:
{context}

User Query: {query}

Based on the context above, provide a factual answer to the user's query. Follow all the rules in the system prompt."""
        
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
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
            "max_output_tokens": 150,
        }
        
        response = model.generate_content(
            contents=combined_prompt,
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
                        log.info(f"✓ {description}: SUCCESS - {text[:80]}...")
                        return True
                    except:
                        log.warning(f"⚠️  {description}: finish_reason=1 but no text")
                        return True
        
        return False
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            log.warning(f"⚠️  {description}: Rate limit hit")
            return None
        else:
            log.error(f"❌ {description}: Exception - {error_str[:100]}")
            return False


def main():
    log.info("="*80)
    log.info("TESTING QUERY VS PROMPT")
    log.info("="*80)
    
    system_prompt = SYSTEM_PROMPT
    
    # Test different combinations
    tests = [
        (
            "You are a helpful assistant.",
            "What is 2+2?",
            "Math context: 2+2 equals 4.",
            "Simple math (baseline)"
        ),
        (
            system_prompt,
            "What is an expense ratio?",
            "An expense ratio is the annual fee charged by a fund.",
            "New prompt + generic question"
        ),
        (
            system_prompt,
            "What is the expense ratio?",
            "The expense ratio is 1.5%.",
            "New prompt + expense ratio question (no fund name)"
        ),
        (
            system_prompt,
            "What is the expense ratio of SBI Large Cap Fund?",
            "SBI Large Cap Fund has an expense ratio of 1.48%.",
            "New prompt + specific fund question"
        ),
    ]
    
    results = []
    for sys_p, query, context, desc in tests:
        result = test_combination(sys_p, query, context, desc)
        results.append((desc, result))
        log.info("")
        import time
        time.sleep(3)  # Small delay
    
    log.info("="*80)
    log.info("RESULTS SUMMARY")
    log.info("="*80)
    for desc, result in results:
        if result is None:
            status = "⚠️  RATE LIMIT"
        elif result:
            status = "✓ PASS"
        else:
            status = "❌ BLOCKED"
        log.info(f"{status}: {desc}")


if __name__ == "__main__":
    main()

