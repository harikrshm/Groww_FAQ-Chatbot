"""
Test LLM service with actual system prompt and user prompt format
to identify if the prompt content is triggering safety filters
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Set up logging
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


def test_with_real_prompts():
    """Test with actual system prompt and user prompt format"""
    log.info("="*80)
    log.info("TESTING WITH ACTUAL SYSTEM PROMPT AND USER PROMPT FORMAT")
    log.info("="*80)
    
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        # Use actual system prompt
        system_prompt = SYSTEM_PROMPT
        
        # Simulate actual user prompt format
        test_context = "SBI Large Cap Fund has an expense ratio of 1.48% for regular plans and 0.81% for direct plans."
        test_query = "What is the expense ratio of SBI Large Cap Fund?"
        
        user_prompt = f"""Context:
{test_context}

User Query: {test_query}

Based on the context above, provide a factual answer to the user's query. Follow all the rules in the system prompt."""
        
        # Combine as done in llm_service.py
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        log.info(f"System prompt length: {len(system_prompt)} chars")
        log.info(f"User prompt length: {len(user_prompt)} chars")
        log.info(f"Combined prompt length: {len(combined_prompt)} chars")
        log.info(f"\nFirst 500 chars of combined prompt:\n{combined_prompt[:500]}...")
        
        # Safety settings
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
        
        log.info("\nCalling generate_content with real prompts...")
        response = model.generate_content(
            contents=combined_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        log.info(f"Response received: {type(response)}")
        
        # Try to get text
        try:
            text = response.text
            log.info(f"✓ SUCCESS - Response text: {text}")
            log.info(f"Response length: {len(text)} characters")
        except ValueError as e:
            log.error(f"❌ FAILED - response.text raised ValueError: {e}")
        
        # Check candidates
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'finish_reason'):
                finish_reason = candidate.finish_reason
                finish_reason_value = int(finish_reason) if hasattr(finish_reason, '__int__') else finish_reason
                log.info(f"\nFinish reason: {finish_reason} (value: {finish_reason_value})")
                
                if finish_reason_value == 2:
                    log.error("❌ BLOCKED BY SAFETY FILTER (finish_reason: 2 = SAFETY)")
                elif finish_reason_value == 3:
                    log.warning("⚠️  BLOCKED BY RECITATION (finish_reason: 3 = RECITATION)")
                elif finish_reason_value == 1:
                    log.info("✓ STOPPED (finish_reason: 1 = STOP - normal completion)")
            
            # Try to extract text from candidate
            if hasattr(candidate, 'content') and candidate.content:
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            log.info(f"Text from candidate: {part.text}")
            
            # Safety ratings
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                log.info("\nSafety ratings:")
                for rating in candidate.safety_ratings:
                    category = getattr(rating, 'category', 'Unknown')
                    probability = getattr(rating, 'probability', 'N/A')
                    severity = getattr(rating, 'severity', 'N/A')
                    log.info(f"  - {category}: probability={probability}, severity={severity}")
        
        # Prompt feedback
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            log.info(f"\nPrompt feedback: {response.prompt_feedback}")
            if hasattr(response.prompt_feedback, 'block_reason'):
                log.warning(f"Block reason: {response.prompt_feedback.block_reason}")
        
        return True
        
    except Exception as e:
        log.exception("Test failed with exception")
        return False


def test_with_simplified_system_prompt():
    """Test with a simplified system prompt to see if specific words trigger filters"""
    log.info("\n" + "="*80)
    log.info("TESTING WITH SIMPLIFIED SYSTEM PROMPT")
    log.info("="*80)
    
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        # Simplified system prompt (removing potentially triggering words)
        simplified_prompt = """You are a factual FAQ assistant. Provide only factual information from the provided context.
Keep responses to 3 sentences or less. End with 'Last updated from sources.'"""
        
        test_context = "SBI Large Cap Fund has an expense ratio of 1.48% for regular plans."
        test_query = "What is the expense ratio of SBI Large Cap Fund?"
        
        user_prompt = f"""Context:
{test_context}

User Query: {test_query}

Based on the context above, provide a factual answer."""
        
        combined_prompt = f"{simplified_prompt}\n\n{user_prompt}"
        
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
        
        log.info("Calling with simplified prompt...")
        response = model.generate_content(
            contents=combined_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        try:
            text = response.text
            log.info(f"✓ SUCCESS - Response: {text}")
        except ValueError as e:
            log.error(f"❌ FAILED: {e}")
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    log.error(f"Finish reason: {candidate.finish_reason}")
        
        return True
        
    except Exception as e:
        log.exception("Simplified prompt test failed")
        return False


if __name__ == "__main__":
    test_with_real_prompts()
    test_with_simplified_system_prompt()
    
    log.info("\n" + "="*80)
    log.info("TESTING COMPLETE")
    log.info("="*80)

