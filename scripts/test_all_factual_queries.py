"""
Test all factual query types to ensure they work correctly
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import process_query
from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system

# Test queries covering all factual query types
test_queries = [
    # Expense ratio queries
    ("What is the expense ratio of SBI Large Cap Fund?", "expense_ratio"),
    ("What is the expense ratio for SBI Small Cap Fund?", "expense_ratio"),
    ("What is the expense ratio of SBI Multicap Fund?", "expense_ratio"),
    
    # Exit load queries
    ("What is the exit load for SBI Equity Hybrid Fund?", "exit_load"),
    ("What is the exit load of SBI Large Cap Fund?", "exit_load"),
    
    # Minimum SIP queries
    ("What is the minimum SIP for SBI Small Cap Fund?", "minimum_sip"),
    ("What is the minimum SIP amount for SBI Large Cap Fund?", "minimum_sip"),
    
    # Riskometer queries
    ("What is the riskometer rating for SBI Multicap Fund?", "riskometer"),
    ("What is the riskometer for SBI Small Cap Fund?", "riskometer"),
    
    # Benchmark queries
    ("What is the benchmark for SBI Nifty Index Fund?", "benchmark"),
    ("What is the benchmark of SBI Large Cap Fund?", "benchmark"),
    
    # Lock-in period queries
    ("What is the lock-in period for SBI Equity Hybrid Fund?", "lock_in_period"),
    
    # Minimum investment queries
    ("What is the minimum investment for SBI Small Cap Fund?", "minimum_investment"),
]

def test_query(query: str, query_type: str):
    """Test a single query"""
    print(f"\n{'='*70}")
    print(f"Testing: {query_type.upper()}")
    print(f"Query: {query}")
    print('='*70)
    
    try:
        # Initialize services
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        
        # Process query
        response = process_query(query, llm_service, retrieval_system)
        
        answer = response.get('answer', '')
        source_url = response.get('source_url', '')
        is_valid = response.get('is_valid', True)
        
        # Check if it's a fallback
        answer_lower = answer.lower()
        is_fallback = 'unable to generate' in answer_lower or 'apologize' in answer_lower or 'visit the official' in answer_lower
        
        if is_fallback:
            print(f"❌ FAILED: Fallback response")
            print(f"   Answer: {answer[:150]}...")
            return False
        elif not answer:
            print(f"❌ FAILED: No answer generated")
            return False
        else:
            print(f"✅ SUCCESS: Response generated")
            print(f"   Answer: {answer[:200]}...")
            print(f"   Source URL: {source_url if source_url else 'None'}")
            print(f"   Valid: {is_valid}")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("TESTING ALL FACTUAL QUERY TYPES")
    print("="*70)
    
    results = []
    by_type = {}
    
    for query, query_type in test_queries:
        success = test_query(query, query_type)
        results.append((query, query_type, success))
        
        if query_type not in by_type:
            by_type[query_type] = {'passed': 0, 'failed': 0}
        
        if success:
            by_type[query_type]['passed'] += 1
        else:
            by_type[query_type]['failed'] += 1
    
    # Summary by query type
    print("\n" + "="*70)
    print("SUMMARY BY QUERY TYPE")
    print("="*70)
    
    for query_type, counts in sorted(by_type.items()):
        total = counts['passed'] + counts['failed']
        passed = counts['passed']
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️"
        print(f"{status} {query_type}: {passed}/{total} passed ({percentage:.1f}%)")
    
    # Overall summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, _, success in results if success)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total queries tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {percentage:.1f}%")
    
    if passed == total:
        print("\n🎉 All queries passed!")
    else:
        print(f"\n⚠️ {total - passed} queries failed. Check logs for details.")

if __name__ == "__main__":
    main()

