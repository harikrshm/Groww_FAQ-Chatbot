"""
Test script for 4 factual questions with gemini-1.5-flash
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

def test_factual_query(query: str, query_number: int):
    """
    Test a single factual query through the full pipeline
    
    Args:
        query: Query string to test
        query_number: Query number for display
    """
    print(f"\n{'='*80}")
    print(f"Factual Query {query_number}:")
    print(f"Query: {query}")
    print(f"{'='*80}")
    
    try:
        # Initialize services
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        
        # Verify model name
        print(f"\nModel being used: {llm_service.model_name}")
        
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
        
        # Check if it's a fallback response
        answer = response.get('answer', '')
        if 'unable to generate a response' in answer.lower() or 'apologize' in answer.lower():
            print(f"\n⚠️  Note: This appears to be a fallback response (LLM generation may have failed)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("="*80)
    print("Testing 4 Factual Questions with gemini-1.5-flash")
    print("="*80)
    
    # Test queries - 4 different factual questions
    factual_queries = [
        "What is the expense ratio of SBI Large Cap Fund?",
        "What is the minimum SIP for SBI Small Cap Fund?",
        "What is the exit load for SBI Equity Hybrid Fund?",
        "What is the riskometer rating for SBI Multicap Fund?",
    ]
    
    results = []
    for idx, query in enumerate(factual_queries, 1):
        success = test_factual_query(query, idx)
        results.append((query, success))
        if idx < len(factual_queries):
            print("\n" + "-"*80)
            print("Waiting 2 seconds before next query to avoid rate limits...")
            import time
            time.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for idx, (query, success) in enumerate(results, 1):
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - Query {idx}: {query}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")

if __name__ == "__main__":
    main()

