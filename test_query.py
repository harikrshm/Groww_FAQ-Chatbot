"""
Test query processor with specific queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.query_processor import preprocess_query

# Test queries
test_queries = [
    "should I invest in high cap or mid cap",
    "What is the expense ratio of SBI Large Cap Fund?",
    "Should I buy SBI Small Cap Fund?",
    "What is the minimum SIP for SBI Multicap Fund?",
    "What is the price of Reliance stock?",
]

print("="*70)
print("QUERY PROCESSOR TEST")
print("="*70)

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 70)
    
    result = preprocess_query(query)
    
    print(f"Classification: {result['classification']}")
    print(f"Scheme Name: {result['scheme_name']}")
    print(f"Factual Intent: {result['factual_intent']}")
    
    if result['precomputed_response']:
        print(f"\nResponse:")
        print(f"  {result['precomputed_response']['answer']}")
        print(f"\nSource URL: {result['precomputed_response']['source_url']}")
    else:
        print("\nResponse: Will proceed with RAG retrieval (factual query)")
    
    print("="*70)

