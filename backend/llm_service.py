"""
LLM service for response generation using Groq (Llama 3.1 8B Instant)
Handles Groq client initialization, prompt formatting, and response generation
"""

import os
import sys
import logging
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None
    logging.warning("groq package not installed. Please install: pip install groq")

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_CONFIG, SYSTEM_PROMPT
from backend.validators import validate_and_fix_response, ValidationResult

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Default model: llama-3.1-8b-instant (Llama 3.1 8B via Groq)
GROQ_MODEL = "llama-3.1-8b-instant"


class LLMService:
    """
    LLM service for generating responses using Groq (Llama 3.1 8B Instant)
    """
    
    def __init__(self):
        """Initialize Groq client"""
        if Groq is None:
            raise ImportError("groq package not installed. Install with: pip install groq")
        
        self.api_key = GROQ_API_KEY
        self.model_name = GROQ_MODEL
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file.")
        
        # Initialize Groq client
        try:
            self.client = Groq(api_key=self.api_key)
            logger.info(f"LLM Service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            raise
        
        # Get generation config from LLM_CONFIG (optimized for token efficiency)
        self.temperature = LLM_CONFIG.get("temperature", 0.1)
        self.top_p = LLM_CONFIG.get("top_p", 0.9)
        self.max_tokens = LLM_CONFIG.get("max_output_tokens", 100)  # Reduced from 150
        
        # Verify API key is valid
        self._check_groq_connection()
    
    def _check_groq_connection(self) -> bool:
        """
        Check if Groq API key is valid
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Try a simple API call to verify the key
            test_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": "test"}
                ],
                temperature=0.1,
                max_tokens=10,
            )
            logger.info("Groq API key validated successfully")
            return True
        except Exception as e:
            logger.error(f"Groq API key validation failed: {e}")
            logger.error("Please check your GROQ_API_KEY in .env file")
            logger.error("Get API key from: https://console.groq.com/keys")
            return False
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Generate response using Groq API (Llama 3.1 8B Instant)
        
        Args:
            system_prompt: System prompt with instructions
            user_prompt: User prompt with context and query
            temperature: Temperature for generation (optional, uses default if not provided)
            top_p: Top-p for generation (optional, uses default if not provided)
            max_output_tokens: Max tokens to generate (optional, uses default if not provided)
            
        Returns:
            Generated response text, or None if generation fails
        """
        try:
            # Groq uses chat completion format with separate system and user messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Prepare generation parameters
            generation_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "top_p": top_p if top_p is not None else self.top_p,
                "max_tokens": max_output_tokens if max_output_tokens is not None else self.max_tokens,
            }
            
            logger.info(f"Generating response with Groq model: {self.model_name}")
            
            # Generate response using Groq API
            response = self.client.chat.completions.create(**generation_params)
            
            # Extract text from response
            if response and response.choices and len(response.choices) > 0:
                generated_text = response.choices[0].message.content
                if generated_text:
                    generated_text = generated_text.strip()
                    logger.info(f"Response generated successfully ({len(generated_text)} characters)")
                    return generated_text
            
            logger.warning("Groq returned empty response with no content")
            return None
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            # Check for specific error types
            error_str = str(e).lower()
            if "api_key" in error_str or "authentication" in error_str or "unauthorized" in error_str:
                logger.error("Invalid or missing Groq API key")
            elif "quota" in error_str or "rate limit" in error_str or "429" in str(e):
                logger.error("Groq API quota exceeded or rate limit reached")
            elif "model" in error_str and "not found" in error_str:
                logger.error(f"Model {self.model_name} not found. Please check the model name.")
            return None
    
    
    def format_user_prompt(self, context: str, query: str) -> str:
        """
        Format user prompt with context and query (optimized for token efficiency)
        
        Args:
            context: Retrieved context chunks
            query: User query
            
        Returns:
            Formatted user prompt (concise)
        """
        # Concise prompt format to save tokens
        prompt = f"""Context:
{context}

Query: {query}

Answer from context only."""
        
        return prompt
    
    def generate_validated_response(
        self,
        system_prompt: str,
        user_prompt: str,
        query: str,
        source_url: Optional[str] = None,
        scheme_name: Optional[str] = None,
        max_retries: int = 3,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        use_fallback: bool = True
    ) -> Tuple[str, ValidationResult]:
        """
        Generate response with validation and retry logic
        
        Args:
            system_prompt: System prompt with instructions
            user_prompt: User prompt with context and query
            query: Original user query (for fallback)
            source_url: Optional source URL for citation validation
            scheme_name: Optional scheme name (for fallback)
            max_retries: Maximum number of retry attempts (default: 3)
            temperature: Temperature for generation (optional)
            top_p: Top-p for generation (optional)
            max_output_tokens: Max tokens to generate (optional)
            use_fallback: Whether to use fallback response if all retries fail (default: True)
            
        Returns:
            Tuple of (validated_response, validation_result)
            - validated_response: Generated and validated response text, or fallback response if all retries fail
            - validation_result: ValidationResult object with validation details
        """
        last_validation_result = None
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Generating validated response (attempt {attempt}/{max_retries})")
            
            # Generate response
            raw_response = self.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens
            )
            
            # If generation failed, return None
            if raw_response is None:
                logger.warning(f"Response generation failed on attempt {attempt}")
                
                # Retry with same prompt if not last attempt
                if attempt < max_retries:
                    logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                    continue
                else:
                    # All retries exhausted - use fallback
                    if use_fallback:
                        logger.warning("All retries exhausted, using fallback response")
                        fallback = self.generate_fallback_response(query, scheme_name, source_url)
                        result = ValidationResult()
                        result.add_warning("Used fallback response after all retries failed")
                        return fallback, result
                    else:
                        # Create validation result for failed generation
                        result = ValidationResult()
                        result.add_error("Response generation failed after all retries")
                        return "", result
            
            # Validate and fix response
            validated_response, validation_result = validate_and_fix_response(
                response=raw_response,
                source_url=source_url,
                max_sentences=3,
                remove_advice=True,
                max_fix_attempts=1
            )
            
            last_validation_result = validation_result
            
            # Log validation results
            if validation_result.is_valid:
                if validation_result.fixes_applied:
                    logger.info(f"Response validated with fixes applied: {validation_result.fixes_applied}")
                else:
                    logger.info("Response validated successfully (no fixes needed)")
                return validated_response, validation_result
            else:
                # Check if errors are fixable
                fixable_errors = [
                    "Response missing source citation",
                    "Response too long",
                    "Response contains advice/opinion words"
                ]
                
                has_fixable_errors = any(
                    any(fixable in error for fixable in fixable_errors)
                    for error in validation_result.errors
                )
                
                if has_fixable_errors and validation_result.fixes_applied:
                    # Errors were fixed, but validation still failed - might need another pass
                    logger.warning(f"Response had fixable errors, but validation still failed. Errors: {validation_result.errors}")
                    if attempt < max_retries:
                        logger.info(f"Retrying with fixed response... (attempt {attempt + 1}/{max_retries})")
                        # Use the fixed response as input for next attempt
                        user_prompt = f"{user_prompt}\n\nPrevious response that needs improvement: {validated_response}"
                        continue
                
                # Non-fixable errors or all retries exhausted
                if attempt < max_retries:
                    logger.warning(f"Validation failed: {validation_result.errors}. Retrying... (attempt {attempt + 1}/{max_retries})")
                else:
                    logger.error(f"Validation failed after {max_retries} attempts. Errors: {validation_result.errors}")
                    # Return the fixed response even if validation failed (better than nothing)
                    if validated_response and validated_response != raw_response:
                        logger.info("Returning fixed response despite validation failures")
                        return validated_response, validation_result
        
        # All retries exhausted
        if last_validation_result is None:
            if use_fallback:
                logger.warning("All retries exhausted, using fallback response")
                fallback = self.generate_fallback_response(query, scheme_name, source_url)
                result = ValidationResult()
                result.add_warning("Used fallback response after all retries failed")
                return fallback, result
            else:
                result = ValidationResult()
                result.add_error("Response generation and validation failed after all retries")
                return "", result
        
        # If we have a validated response (even if validation failed), return it
        if validated_response:
            return validated_response, last_validation_result
        
        # Last resort: use fallback
        if use_fallback:
            logger.warning("Using fallback response as last resort")
            fallback = self.generate_fallback_response(query, scheme_name, source_url)
            last_validation_result.add_warning("Used fallback response as last resort")
            return fallback, last_validation_result
        
        return "", last_validation_result
    
    def generate_fallback_response(
        self,
        query: str,
        scheme_name: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> str:
        """
        Generate fallback response when LLM fails or validation fails
        
        Args:
            query: User query
            scheme_name: Optional scheme name if detected
            source_url: Optional source URL from retrieval
            
        Returns:
            Fallback response text
        """
        from config import DEFAULT_FALLBACK_URL, SBI_MF_LINK
        
        # Use provided source URL or default
        fallback_url = source_url if source_url else DEFAULT_FALLBACK_URL
        
        if scheme_name:
            fallback_response = (
                f"I apologize, but I'm unable to generate a response for your query about {scheme_name}. "
                f"Please visit the official SBI Mutual Fund website for detailed information about this scheme. "
                f"Last updated from sources."
            )
        else:
            fallback_response = (
                f"I apologize, but I'm unable to generate a response for your query. "
                f"Please visit the official SBI Mutual Fund website for more information. "
                f"Last updated from sources."
            )
        
        logger.info("Generated fallback response")
        return fallback_response


# Global instance (singleton pattern)
_llm_service = None


def get_llm_service() -> LLMService:
    """
    Get or create LLM service instance (singleton)
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


if __name__ == "__main__":
    # Test LLM service
    print("Testing LLM Service (Groq - Llama 3.1 8B Instant):")
    print("="*70)
    
    try:
        llm_service = get_llm_service()
        
        # Test system prompt
        system_prompt = SYSTEM_PROMPT
        
        # Test user prompt
        test_context = "SBI Large Cap Fund has an expense ratio of 1.48% for regular plans and 0.81% for direct plans."
        test_query = "What is the expense ratio of SBI Large Cap Fund?"
        
        user_prompt = llm_service.format_user_prompt(test_context, test_query)
        
        print(f"\nSystem Prompt (first 300 chars):")
        print(f"{system_prompt[:300]}...")
        
        print(f"\nUser Prompt:")
        print(user_prompt)
        
        # Generate response
        print(f"\nGenerating response...")
        response = llm_service.generate_response(system_prompt, user_prompt)
        
        if response:
            print(f"\nGenerated Response:")
            print(response)
        else:
            print("\nFailed to generate response. Please check Groq API key is set correctly.")
    except ImportError as e:
        print(f"\nError: {e}")
        print("Please install groq: pip install groq")
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please set GROQ_API_KEY in .env file")
        print("Get API key from: https://console.groq.com/keys")
    except Exception as e:
        print(f"\nError: {e}")
