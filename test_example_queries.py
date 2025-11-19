"""
Test the three example queries from welcome page and generate answers
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Example queries from welcome page
EXAMPLE_QUERIES = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?"
]

def test_example_queries():
    print("="*80)
    print("TESTING EXAMPLE QUERIES FROM WELCOME PAGE")
    print("="*80)
    print()
    
    # Initialize services
    print("Initializing services...")
    llm_service = get_llm_service()
    retrieval_system = get_retrieval_system()
    print("✅ Services initialized\n")
    
    results = []
    
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        print("="*80)
        print(f"Query {i}/3: {query}")
        print("="*80)
        print()
        
        try:
            # Process query through full pipeline
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
            
            print(f"✅ Response Generated (in {processing_time:.2f}s)")
            print(f"\nAnswer:")
            print(f"  {answer}")
            print(f"\nSource URL:")
            print(f"  {source_url}")
            
            # Store result
            results.append({
                'query': query,
                'answer': answer,
                'source_url': source_url,
                'processing_time': processing_time,
                'success': True
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'query': query,
                'answer': None,
                'source_url': None,
                'processing_time': 0,
                'success': False,
                'error': str(e)
            })
        
        print()
        
        # Add delay between queries
        if i < len(EXAMPLE_QUERIES):
            print("Waiting 2 seconds before next query...\n")
            time.sleep(2)
    
    # Print summary
    print("="*80)
    print("SUMMARY - EXAMPLE QUERY ANSWERS")
    print("="*80)
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Query: {result['query']}")
        if result['success']:
            print(f"   Answer: {result['answer']}")
            print(f"   Source: {result['source_url']}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        print()
    
    # Generate formatted output for frontend
    print("="*80)
    print("FORMATTED ANSWERS FOR FRONTEND")
    print("="*80)
    print()
    print("# Example Questions with Pre-computed Answers")
    print("EXAMPLE_QUESTIONS_WITH_ANSWERS = [")
    for result in results:
        if result['success']:
            print(f"    {{")
            print(f"        'query': \"{result['query']}\",")
            print(f"        'answer': \"{result['answer']}\",")
            print(f"        'source_url': \"{result['source_url']}\"")
            print(f"    }},")
        else:
            print(f"    # Query: {result['query']} - FAILED")
    print("]")
    print()
    
    return results

if __name__ == "__main__":
    test_example_queries()

