"""
Test script for Phase 2.5 Safety Filter Implementation
Tests 2 example questions and 2 factual questions
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from app import process_query

# Set up UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_query(query: str, query_type: str):
    """
    Test a single query through the full pipeline
    
    Args:
        query: Query string to test
        query_type: Type of query (e.g., "Example Question" or "Factual Query")
    """
    print(f"\n{'='*80}")
    print(f"Testing {query_type}:")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    try:
        # Initialize services
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        
        # Process query
        print("\nProcessing query through full pipeline...")
        response = process_query(query, llm_service, retrieval_system)
        
        # Display results
        print(f"\n✅ Response Generated:")
        print(f"Answer: {response.get('answer', 'N/A')}")
        print(f"Source URL: {response.get('source_url', 'N/A')}")
        
        # Check for warnings/errors
        validation_result = response.get('validation_result')
        if validation_result:
            warnings = validation_result.get('warnings', [])
            errors = validation_result.get('errors', [])
            if warnings:
                print(f"\n⚠️  Warnings: {warnings}")
            if errors:
                print(f"\n❌ Errors: {errors}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("="*80)
    print("Phase 2.5 Safety Filter Implementation Test")
    print("="*80)
    
    # Test queries
    test_queries = [
        # Example Questions (2)
        ("What is the expense ratio of SBI Large Cap Fund?", "Example Question 1"),
        ("What is the minimum SIP for SBI Small Cap Fund?", "Example Question 2"),
        
        # Factual Questions (2)
        ("What is the exit load for SBI Equity Hybrid Fund?", "Factual Query 1"),
        ("What is the riskometer rating for SBI Multicap Fund?", "Factual Query 2"),
    ]
    
    results = []
    for query, query_type in test_queries:
        success = test_query(query, query_type)
        results.append((query, query_type, success))
        print("\n" + "-"*80)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for query, query_type, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {query_type}: {query}")
    
    total = len(results)
    passed = sum(1 for _, _, success in results if success)
    print(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")

if __name__ == "__main__":
    main()

