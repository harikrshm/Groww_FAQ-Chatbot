"""
Response formatter for consistent response structure
Formats LLM responses into standardized structure for frontend display
"""

import sys
import os
from typing import Dict, Optional, List
from urllib.parse import urlparse

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEFAULT_FALLBACK_URL, SBI_MF_LINK

# Set up logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_response(
    answer: str,
    source_url: Optional[str] = None,
    validation_result: Optional[Dict] = None,
    query: Optional[str] = None,
    scheme_name: Optional[str] = None
) -> Dict:
    """
    Format response into standardized structure
    
    Args:
        answer: Response text/answer
        source_url: Source URL for citation
        validation_result: Optional validation result dictionary
        query: Original user query
        scheme_name: Optional scheme name
        
    Returns:
        Formatted response dictionary with structure:
        {
            "answer": str,
            "source_url": str,
            "is_valid": bool,
            "warnings": List[str],
            "fixes_applied": List[str]
        }
    """
    # Ensure answer is not None
    if answer is None:
        answer = ""
    
    # Clean up answer
    answer = answer.strip()
    
    # Determine source URL
    if not source_url:
        source_url = DEFAULT_FALLBACK_URL
    
    # Validate URL format
    try:
        parsed = urlparse(source_url)
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"Invalid source URL format: {source_url}, using default")
            source_url = DEFAULT_FALLBACK_URL
    except Exception as e:
        logger.warning(f"Error parsing source URL: {e}, using default")
        source_url = DEFAULT_FALLBACK_URL
    
    # Extract validation info if provided
    is_valid = True
    warnings = []
    fixes_applied = []
    
    if validation_result:
        is_valid = validation_result.get("is_valid", True)
        warnings = validation_result.get("warnings", [])
        fixes_applied = validation_result.get("fixes_applied", [])
    
    # Build response structure
    formatted_response = {
        "answer": answer,
        "source_url": source_url,
        "is_valid": is_valid,
        "warnings": warnings,
        "fixes_applied": fixes_applied
    }
    
    # Add optional metadata
    if query:
        formatted_response["query"] = query
    if scheme_name:
        formatted_response["scheme_name"] = scheme_name
    
    return formatted_response


def format_error_response(
    error_message: str,
    query: Optional[str] = None,
    scheme_name: Optional[str] = None
) -> Dict:
    """
    Format error response
    
    Args:
        error_message: Error message to display
        query: Original user query
        scheme_name: Optional scheme name
        
    Returns:
        Formatted error response dictionary
    """
    return format_response(
        answer=error_message,
        source_url=DEFAULT_FALLBACK_URL,
        validation_result={
            "is_valid": False,
            "errors": [error_message],
            "warnings": [],
            "fixes_applied": []
        },
        query=query,
        scheme_name=scheme_name
    )


def format_fallback_response(
    query: Optional[str] = None,
    scheme_name: Optional[str] = None,
    source_url: Optional[str] = None
) -> Dict:
    """
    Format fallback response when LLM fails
    
    Args:
        query: Original user query
        scheme_name: Optional scheme name
        source_url: Optional source URL
        
    Returns:
        Formatted fallback response dictionary
    """
    if scheme_name:
        answer = (
            f"I apologize, but I'm unable to generate a response for your query about {scheme_name}. "
            f"Please visit the official SBI Mutual Fund website for detailed information about this scheme. "
            f"Last updated from sources."
        )
    else:
        answer = (
            f"I apologize, but I'm unable to generate a response for your query. "
            f"Please visit the official SBI Mutual Fund website for more information. "
            f"Last updated from sources."
        )
    
    return format_response(
        answer=answer,
        source_url=source_url or DEFAULT_FALLBACK_URL,
        validation_result={
            "is_valid": True,
            "errors": [],
            "warnings": ["Fallback response used"],
            "fixes_applied": []
        },
        query=query,
        scheme_name=scheme_name
    )


def extract_source_urls_from_response(response: str) -> List[str]:
    """
    Extract URLs from response text
    
    Args:
        response: Response text
        
    Returns:
        List of URLs found in response
    """
    import re
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
    urls = re.findall(url_pattern, response)
    
    return urls


def clean_response_text(text: str) -> str:
    """
    Clean response text (remove extra whitespace, normalize)
    
    Args:
        text: Raw response text
        
    Returns:
        Cleaned response text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Ensure proper sentence endings
    text = text.strip()
    if text and not text[-1] in ".!?":
        text += "."
    
    return text


if __name__ == "__main__":
    # Test formatter
    print("="*80)
    print("TESTING RESPONSE FORMATTER")
    print("="*80)
    
    # Test 1: Normal response
    response1 = format_response(
        answer="The expense ratio is 1.48%. Last updated from sources.",
        source_url="https://www.sbimf.com/scheme-details",
        validation_result={
            "is_valid": True,
            "warnings": [],
            "fixes_applied": []
        },
        query="What is the expense ratio?",
        scheme_name="SBI Large Cap Fund"
    )
    print("\nTest 1: Normal response")
    print(f"Answer: {response1['answer']}")
    print(f"Source URL: {response1['source_url']}")
    print(f"Valid: {response1['is_valid']}")
    
    # Test 2: Response with fixes
    response2 = format_response(
        answer="The minimum SIP is Rs. 500. Last updated from sources.",
        source_url="https://www.sbimf.com/scheme-details",
        validation_result={
            "is_valid": True,
            "warnings": [],
            "fixes_applied": ["Added source citation", "Truncated from 5 to 3 sentences"]
        },
        query="What is the minimum SIP?",
        scheme_name="SBI Small Cap Fund"
    )
    print("\nTest 2: Response with fixes")
    print(f"Answer: {response2['answer']}")
    print(f"Fixes applied: {response2['fixes_applied']}")
    
    # Test 3: Fallback response
    response3 = format_fallback_response(
        query="What is the expense ratio?",
        scheme_name="SBI Large Cap Fund"
    )
    print("\nTest 3: Fallback response")
    print(f"Answer: {response3['answer']}")
    print(f"Warnings: {response3['warnings']}")
    
    # Test 4: Error response
    response4 = format_error_response(
        error_message="Unable to retrieve information",
        query="What is the expense ratio?",
        scheme_name="SBI Large Cap Fund"
    )
    print("\nTest 4: Error response")
    print(f"Answer: {response4['answer']}")
    print(f"Valid: {response4['is_valid']}")
    
    print("\n" + "="*80)
    print("FORMATTER TESTS COMPLETE")
    print("="*80)

