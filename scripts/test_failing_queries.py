"""
Test the specific failing queries to see what happens with detailed logging
"""

import sys
import os
import logging

# Set up logging to see all details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.query_processor import preprocess_query
from backend.retrieval import get_retrieval_system
from backend.llm_service import get_llm_service
from backend.formatter import format_response, format_fallback_response
from config import SYSTEM_PROMPT, RETRIEVAL_CONFIG

# Test queries that previously failed
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?",
]

def test_query(query: str):
    """Test a single query with full logging"""
    print("\n" + "="*80)
    print(f"TESTING: {query}")
    print("="*80)
    
    # Initialize services
    retrieval_system = get_retrieval_system()
    llm_service = get_llm_service()
    
    # Import process_query from app
    from app import process_query
    
    # Process query (this will use all the logging we added)
    try:
        response = process_query(query, llm_service, retrieval_system)
        
        print(f"\n{'='*80}")
        print("RESULT:")
        print(f"{'='*80}")
        print(f"Answer: {response.get('answer', 'NO ANSWER')}")
        print(f"Source URL: {response.get('source_url', 'NO SOURCE URL')}")
        print(f"Is Valid: {response.get('is_valid', 'UNKNOWN')}")
        
        if response.get('warnings'):
            print(f"Warnings: {response.get('warnings')}")
        if response.get('fixes_applied'):
            print(f"Fixes Applied: {response.get('fixes_applied')}")
        
        # Check if it's a fallback
        answer = response.get('answer', '').lower()
        is_fallback = 'unable to generate' in answer or 'apologize' in answer or 'visit the official' in answer
        
        if is_fallback:
            print(f"\n❌ FAILED: Response is a fallback")
            return False
        else:
            print(f"\n✅ SUCCESS: Query generated a response")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("TESTING FAILING QUERIES WITH DETAILED LOGGING")
    print("="*80)
    
    results = []
    for query in test_queries:
        success = test_query(query)
        results.append((query, success))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {query}")
    
    print(f"\nTotal: {passed}/{total} queries passed ({passed/total*100:.1f}%)")

if __name__ == "__main__":
    main()

