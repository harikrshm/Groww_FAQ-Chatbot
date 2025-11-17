"""
Response template formatter for different query types
Ensures consistent formatting: ≤3 sentences, citation link, footer
"""

import sys
import os
from typing import Dict

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NON_MF_RESPONSE, ADVICE_RESPONSE, JAILBREAK_RESPONSE


def format_response(response_dict: Dict, query_type: str) -> Dict:
    """
    Format response according to requirements:
    - ≤3 sentences
    - Include citation link
    - Add "Last updated from sources." footer
    
    Args:
        response_dict: Response dictionary from config
        query_type: Type of query ('non_mf', 'advice', 'jailbreak')
        
    Returns:
        Formatted response dictionary
    """
    answer = response_dict.get("answer", "")
    source_url = response_dict.get("source_url", "")
    
    # Ensure answer is ≤3 sentences
    sentences = [s.strip() for s in answer.split('.') if s.strip()]
    if len(sentences) > 3:
        answer = '. '.join(sentences[:3]) + '.'
    
    # Add footer
    footer = " Last updated from sources."
    if not answer.endswith(footer):
        answer += footer
    
    # Ensure source URL is present
    if not source_url:
        if query_type == 'non_mf':
            source_url = "https://www.amfiindia.com"
        else:
            source_url = "https://www.sebi.gov.in/sebiweb/home/HomePage.jsp?siteLanguage=en"
    
    return {
        "answer": answer,
        "source_url": source_url,
        "query_type": query_type
    }


def get_non_mf_response() -> Dict:
    """Get formatted non-MF query response"""
    return format_response(NON_MF_RESPONSE, 'non_mf')


def get_advice_response() -> Dict:
    """Get formatted advice query response"""
    return format_response(ADVICE_RESPONSE, 'advice')


def get_jailbreak_response() -> Dict:
    """Get formatted jailbreak query response"""
    return format_response(JAILBREAK_RESPONSE, 'jailbreak')


def get_response_by_type(query_type: str) -> Dict:
    """
    Get appropriate response based on query type
    
    Args:
        query_type: 'non_mf', 'advice', or 'jailbreak'
        
    Returns:
        Formatted response dictionary
    """
    if query_type == 'non_mf':
        return get_non_mf_response()
    elif query_type == 'advice':
        return get_advice_response()
    elif query_type == 'jailbreak':
        return get_jailbreak_response()
    else:
        # Default fallback
        return get_advice_response()


if __name__ == "__main__":
    # Test response templates
    print("Testing Response Templates:")
    print("="*70)
    
    print("\n1. Non-MF Response:")
    print("-"*70)
    response = get_non_mf_response()
    print(f"Answer: {response['answer']}")
    print(f"Source URL: {response['source_url']}")
    
    print("\n2. Advice Response:")
    print("-"*70)
    response = get_advice_response()
    print(f"Answer: {response['answer']}")
    print(f"Source URL: {response['source_url']}")
    
    print("\n3. Jailbreak Response:")
    print("-"*70)
    response = get_jailbreak_response()
    print(f"Answer: {response['answer']}")
    print(f"Source URL: {response['source_url']}")

