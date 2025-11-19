"""
Test the new system prompt to verify it doesn't trigger safety filters
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


def test_new_prompt():
    """Test the new system prompt"""
    log.info("="*80)
    log.info("TESTING NEW SYSTEM PROMPT")
    log.info("="*80)
    
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        log.info(f"System prompt length: {len(SYSTEM_PROMPT)} chars")
        log.info(f"\nSystem prompt preview:\n{SYSTEM_PROMPT[:300]}...")
        
        # Test context and query
        test_context = "SBI Large Cap Fund has an expense ratio of 1.48% for regular plans and 0.81% for direct plans."
        test_query = "What is the expense ratio of SBI Large Cap Fund?"
        
        user_prompt = f"""Context:
{test_context}

User Query: {test_query}

Based on the context above, provide a factual answer to the user's query. Follow all the rules in the system prompt."""
        
        combined_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        
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
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 150,
        }
        
        log.info("\nCalling generate_content with new system prompt...")
        response = model.generate_content(
            contents=combined_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        log.info(f"Response received: {type(response)}")
        
        # Try to get text
        try:
            text = response.text
            log.info(f"\n✓ SUCCESS - Response generated:")
            log.info(f"{'='*80}")
            log.info(text)
            log.info(f"{'='*80}")
            log.info(f"Response length: {len(text)} characters")
            return True
        except ValueError as e:
            log.error(f"\n❌ FAILED - response.text raised ValueError: {e}")
        
        # Check candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                finish_reason_value = int(finish_reason) if hasattr(finish_reason, '__int__') else finish_reason
                log.error(f"\nFinish reason: {finish_reason} (value: {finish_reason_value})")
                
                if finish_reason_value == 2:
                    log.error("❌ BLOCKED BY SAFETY FILTER (finish_reason: 2 = SAFETY)")
                elif finish_reason_value == 3:
                    log.warning("⚠️  BLOCKED BY RECITATION (finish_reason: 3 = RECITATION)")
            
            # Try to extract text from candidate
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            log.info(f"Text from candidate: {part.text}")
                            return True
            
            # Safety ratings
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                log.info("\nSafety ratings:")
                for rating in candidate.safety_ratings:
                    category = getattr(rating, 'category', 'Unknown')
                    probability = getattr(rating, 'probability', 'N/A')
                    severity = getattr(rating, 'severity', 'N/A')
                    log.info(f"  - {category}: probability={probability}, severity={severity}")
        
        return False
        
    except Exception as e:
        log.exception("Test failed with exception")
        return False


if __name__ == "__main__":
    success = test_new_prompt()
    log.info("\n" + "="*80)
    if success:
        log.info("✓ NEW SYSTEM PROMPT WORKS!")
    else:
        log.info("❌ NEW SYSTEM PROMPT STILL BLOCKED")
    log.info("="*80)
