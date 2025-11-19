"""
Test 5 factual queries and show responses
"""

import sys
import os
import logging

# Set up logging to INFO level (less verbose)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import process_query
from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system

# 5 factual queries to test
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the riskometer rating for SBI Multicap Fund?",
    "What is the benchmark for SBI Nifty Index Fund?",
]

def test_query(query: str, query_num: int):
    """Test a single query and show response"""
    print(f"\n{'='*80}")
    print(f"QUERY {query_num}: {query}")
    print('='*80)
    
    try:
        # Initialize services
        print("Initializing services...")
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        print("Services initialized.\n")
        
        # Process query
        print("Processing query...")
        response = process_query(query, llm_service, retrieval_system)
        
        # Display response
        print(f"\n{'─'*80}")
        print("RESPONSE:")
        print(f"{'─'*80}")
        print(f"Answer: {response.get('answer', 'NO ANSWER')}")
        print(f"\nSource URL: {response.get('source_url', 'NO SOURCE URL')}")
        print(f"Valid: {response.get('is_valid', 'UNKNOWN')}")
        
        if response.get('warnings'):
            print(f"Warnings: {response.get('warnings')}")
        if response.get('fixes_applied'):
            print(f"Fixes Applied: {response.get('fixes_applied')}")
        
        # Check if it's a fallback
        answer = response.get('answer', '').lower()
        is_fallback = 'unable to generate' in answer or 'apologize' in answer or 'visit the official' in answer
        
        if is_fallback:
            print(f"\n⚠️  STATUS: Fallback response (query may have failed)")
        elif not response.get('answer'):
            print(f"\n❌ STATUS: No answer generated")
        else:
            print(f"\n✅ STATUS: Success - Response generated")
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*80)
    print("TESTING 5 FACTUAL QUERIES")
    print("="*80)
    
    results = []
    for i, query in enumerate(test_queries, 1):
        response = test_query(query, i)
        results.append((query, response))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    successful = 0
    for query, response in results:
        if response:
            answer = response.get('answer', '').lower()
            is_fallback = 'unable to generate' in answer or 'apologize' in answer or 'visit the official' in answer
            if response.get('answer') and not is_fallback:
                successful += 1
                status = "✅"
            else:
                status = "⚠️"
        else:
            status = "❌"
        
        print(f"{status} {query}")
    
    print(f"\nTotal: {successful}/{len(results)} queries generated successful responses")

if __name__ == "__main__":
    main()

