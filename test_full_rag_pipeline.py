"""
Test script for full RAG pipeline with Groq (Llama 3.1 8B Instant)
Tests various factual queries through the complete pipeline
"""

import sys
import os
import time
import logging

# Set up UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from app import process_query

# Configure logging for the test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Factual queries to test - covering different types of factual information
# Reduced to 5 queries to avoid rate limits
FACTUAL_QUERIES = [
    # Expense ratio queries
    "What is the expense ratio of SBI Large Cap Fund?",
    
    # Exit load queries
    "What is the exit load for SBI Equity Hybrid Fund?",
    
    # Minimum SIP queries
    "What is the minimum SIP for SBI Small Cap Fund?",
    
    # Riskometer queries
    "What is the riskometer rating for SBI Multicap Fund?",
    
    # Lock-in period queries
    "What is the lock-in period for SBI Equity Hybrid Fund?",
]

def run_test():
    print("="*80)
    print("Testing Full RAG Pipeline with Groq (Llama 3.1 8B Instant)")
    print("="*80)
    print()

    # Initialize services
    print("Initializing services...")
    try:
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        print(f"✅ LLM Service initialized: {llm_service.model_name}")
        print(f"✅ Retrieval System initialized")
        print()
    except Exception as e:
        print(f"❌ Error initializing services: {e}")
        return

    test_results = []
    successful_tests = 0
    failed_tests = 0

    for i, query in enumerate(FACTUAL_QUERIES, 1):
        print(f"{'='*80}")
        print(f"Test {i}/{len(FACTUAL_QUERIES)}")
        print(f"{'='*80}")
        print(f"Query: {query}")
        print(f"{'-'*80}")
        print()

        try:
            # Process query through full RAG pipeline
            start_time = time.time()
            formatted_response = process_query(
                query,
                llm_service,
                retrieval_system
            )
            end_time = time.time()
            processing_time = end_time - start_time

            # Extract response details
            answer = formatted_response.get('answer', 'No answer generated.')
            source_url = formatted_response.get('source_url', 'No source URL.')
            validation_result = formatted_response.get('validation_result', {})
            validation_warnings = validation_result.get('warnings', [])
            validation_errors = validation_result.get('errors', [])

            # Display results
            print(f"✅ Response Generated (in {processing_time:.2f}s)")
            print(f"\nAnswer:")
            print(f"  {answer}")
            print(f"\nSource URL: {source_url}")
            
            if validation_warnings:
                print(f"\n⚠️  Validation Warnings:")
                for warning in validation_warnings:
                    print(f"   - {warning}")
            
            if validation_errors:
                print(f"\n❌ Validation Errors:")
                for error in validation_errors:
                    print(f"   - {error}")
            
            # Check if response is valid
            is_valid = (
                answer and 
                answer != 'No answer generated.' and
                len(answer) > 10 and
                not any('fallback' in w.lower() for w in validation_warnings)
            )
            
            if is_valid:
                successful_tests += 1
                test_results.append((query, True, processing_time, None))
                print(f"\n✅ TEST PASSED")
            else:
                failed_tests += 1
                test_results.append((query, False, processing_time, "Invalid or fallback response"))
                print(f"\n❌ TEST FAILED: Invalid or fallback response")

        except Exception as e:
            failed_tests += 1
            test_results.append((query, False, 0, str(e)))
            print(f"❌ Error during processing: {e}")
            import traceback
            traceback.print_exc()

        print()
        
        # Add delay between queries to avoid rate limits (Groq free tier: 6000 TPM)
        if i < len(FACTUAL_QUERIES):
            wait_time = 3  # Wait 3 seconds between queries
            print(f"Waiting {wait_time} seconds before next query to avoid rate limits...")
            time.sleep(wait_time)
            print()

    # Print summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(FACTUAL_QUERIES)}")
    print(f"✅ Passed: {successful_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/len(FACTUAL_QUERIES)*100):.1f}%")
    print()
    
    if test_results:
        avg_time = sum(t[2] for t in test_results if t[2] > 0) / len([t for t in test_results if t[2] > 0])
        print(f"Average Processing Time: {avg_time:.2f}s")
        print()
    
    print("Detailed Results:")
    print("-"*80)
    for query, passed, proc_time, error in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        time_str = f"({proc_time:.2f}s)" if proc_time > 0 else ""
        print(f"{status} {time_str} - {query}")
        if error:
            print(f"   Error: {error}")
    print("="*80)

if __name__ == "__main__":
    run_test()

