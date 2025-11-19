"""
Debug script for LLM service to diagnose Gemini API safety filter issues
Tests both new and legacy SDK patterns to identify the root cause
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Changed to valid model name

if not API_KEY:
    log.error("GEMINI_API_KEY not found in environment variables")
    log.error("Please set it in .env file or export it")
    sys.exit(1)

log.info(f"Using API Key: {API_KEY[:10]}...{API_KEY[-4:] if len(API_KEY) > 14 else '***'}")
log.info(f"Using Model: {MODEL}")


def debug_with_new_sdk():
    """Try using the new google.genai SDK pattern"""
    log.info("\n" + "="*80)
    log.info("TESTING WITH NEW SDK PATTERN (google.genai)")
    log.info("="*80)
    
    try:
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=API_KEY)
        
        # Build permissive safety settings for debugging
        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ]
        
        config = types.GenerateContentConfig(safety_settings=safety_settings)
        
        log.info("Calling generate_content with new SDK...")
        response = client.models.generate_content(
            model=MODEL,
            contents=["Hello — this is a small debug prompt. Please respond with OK."],
            config=config
        )
        
        # Inspect response
        log.info(f"Response received: {type(response)}")
        
        for candidate in response.candidates:
            log.info(f"Candidate finish reason: {candidate.finish_reason}")
            
            # Try to get text
            try:
                if hasattr(candidate, 'output') and candidate.output:
                    text = candidate.output[0].content if candidate.output else "<no output>"
                    log.info(f"Candidate text: {text}")
                elif hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        text = candidate.content.parts[0].text if candidate.content.parts[0].text else "<no text>"
                        log.info(f"Candidate text: {text}")
                    else:
                        log.info(f"Candidate content: {candidate.content}")
                else:
                    log.info("No text found in candidate")
            except Exception as e:
                log.warning(f"Error extracting text: {e}")
            
            # Safety ratings diagnostic
            if hasattr(candidate, "safety_ratings"):
                log.info("Safety ratings:")
                for rating in candidate.safety_ratings:
                    log.info(f"  - {rating.category}: probability={getattr(rating, 'probability', 'N/A')} "
                           f"severity={getattr(rating, 'severity', 'N/A')}")
            else:
                log.info("No safety_ratings attribute on candidate")
        
        # Prompt feedback
        if hasattr(response, "prompt_feedback") and response.prompt_feedback:
            log.info(f"Prompt feedback: {response.prompt_feedback}")
        
        log.info("✓ New SDK test completed successfully")
        return True
        
    except ImportError:
        log.warning("New SDK (google.genai) not available, skipping this test")
        return False
    except Exception as e:
        log.exception("New SDK test raised an exception")
        return False


def debug_with_legacy_sdk():
    """Use the legacy google.generativeai SDK pattern (what we currently use)"""
    log.info("\n" + "="*80)
    log.info("TESTING WITH LEGACY SDK PATTERN (google.generativeai)")
    log.info("="*80)
    
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        # Configure API key
        genai.configure(api_key=API_KEY)
        
        # Ensure model name has correct format
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        log.info(f"Using model name: {model_name}")
        
        # Build permissive safety settings
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
        
        # Initialize model
        model = genai.GenerativeModel(model_name=model_name)
        
        # Generation config
        generation_config = {
            "temperature": 0.1,
            "max_output_tokens": 50,
        }
        
        log.info("Calling generate_content with legacy SDK...")
        response = model.generate_content(
            contents="Hello — this is a small debug prompt. Please respond with OK.",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        log.info(f"Response received: {type(response)}")
        
        # Try to get text first
        try:
            text = response.text
            log.info(f"✓ Response text (via response.text): {text}")
        except ValueError as e:
            log.warning(f"response.text raised ValueError: {e}")
            log.info("Checking candidates directly...")
        
        # Inspect candidates
        if hasattr(response, 'candidates') and response.candidates:
            for idx, candidate in enumerate(response.candidates):
                log.info(f"\nCandidate {idx}:")
                log.info(f"  Type: {type(candidate)}")
                
                # Check finish_reason
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    finish_reason_value = int(finish_reason) if hasattr(finish_reason, '__int__') else finish_reason
                    log.info(f"  Finish reason: {finish_reason} (value: {finish_reason_value})")
                    
                    if finish_reason_value == 2:
                        log.error("  ❌ BLOCKED BY SAFETY FILTER (finish_reason: 2 = SAFETY)")
                    elif finish_reason_value == 3:
                        log.warning("  ⚠️  BLOCKED BY RECITATION (finish_reason: 3 = RECITATION)")
                    elif finish_reason_value == 1:
                        log.info("  ✓ STOPPED (finish_reason: 1 = STOP - normal completion)")
                
                # Try to extract text from candidate
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        for part_idx, part in enumerate(candidate.content.parts):
                            if hasattr(part, 'text') and part.text:
                                log.info(f"  Text from part {part_idx}: {part.text}")
                            else:
                                log.info(f"  Part {part_idx}: {part} (no text attribute)")
                    else:
                        log.info(f"  Content: {candidate.content} (no parts)")
                else:
                    log.info("  No content attribute")
                
                # Safety ratings
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    log.info("  Safety ratings:")
                    for rating in candidate.safety_ratings:
                        category = getattr(rating, 'category', 'Unknown')
                        probability = getattr(rating, 'probability', 'N/A')
                        severity = getattr(rating, 'severity', 'N/A')
                        log.info(f"    - {category}: probability={probability}, severity={severity}")
                else:
                    log.info("  No safety_ratings attribute")
        else:
            log.warning("No candidates in response")
        
        # Prompt feedback
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            log.info(f"\nPrompt feedback: {response.prompt_feedback}")
            if hasattr(response.prompt_feedback, 'block_reason'):
                log.warning(f"  Block reason: {response.prompt_feedback.block_reason}")
        
        log.info("\n✓ Legacy SDK test completed")
        return True
        
    except ImportError:
        log.error("Legacy SDK (google.generativeai) not available!")
        log.error("Please install: pip install google-generativeai")
        return False
    except Exception as e:
        log.exception("Legacy SDK test raised an exception")
        return False


def debug_with_simple_prompt():
    """Test with the simplest possible prompt"""
    log.info("\n" + "="*80)
    log.info("TESTING WITH SIMPLEST PROMPT (no safety settings)")
    log.info("="*80)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=API_KEY)
        model_name = MODEL if MODEL.startswith("models/") else f"models/{MODEL}"
        model = genai.GenerativeModel(model_name=model_name)
        
        log.info("Calling with minimal prompt and no safety settings override...")
        response = model.generate_content("Say OK")
        
        try:
            text = response.text
            log.info(f"✓ Response: {text}")
        except ValueError as e:
            log.error(f"❌ Failed: {e}")
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    log.error(f"Finish reason: {candidate.finish_reason}")
        
        return True
    except Exception as e:
        log.exception("Simple prompt test failed")
        return False


def main():
    """Run all debug tests"""
    log.info("="*80)
    log.info("GEMINI LLM SERVICE DEBUG SCRIPT")
    log.info("="*80)
    log.info(f"Model: {MODEL}")
    log.info(f"API Key: {'Set' if API_KEY else 'NOT SET'}")
    
    # Test 1: Try new SDK
    debug_with_new_sdk()
    
    # Test 2: Try legacy SDK (what we use)
    debug_with_legacy_sdk()
    
    # Test 3: Simplest possible test
    debug_with_simple_prompt()
    
    log.info("\n" + "="*80)
    log.info("DEBUG SCRIPT COMPLETE")
    log.info("="*80)
    log.info("\nNext steps:")
    log.info("1. Check finish_reason values (2 = SAFETY block, 3 = RECITATION)")
    log.info("2. Review safety_ratings to see which category is blocking")
    log.info("3. Verify model name is correct (try gemini-1.5-flash if gemini-2.5-flash fails)")
    log.info("4. Check Google Cloud Console for account-level safety restrictions")


if __name__ == "__main__":
    main()

