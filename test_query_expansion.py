"""
Test query expansion functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.query_processor import preprocess_query

# Test queries with different factual intents
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the exit load for SBI Small Cap Fund?",
    "What is the minimum SIP for SBI Multicap Fund?",
    "What is the lock-in period for SBI Equity Hybrid Fund?",
    "What is the riskometer of SBI Nifty Index Fund?",
]

print("="*80)
print("QUERY EXPANSION TEST")
print("="*80)

for query in test_queries:
    result = preprocess_query(query)
    
    print(f"\nOriginal Query: {query}")
    print(f"Normalized Query: {result['normalized_query']}")
    print(f"Expanded Query: {result['expanded_query']}")
    print(f"Factual Intent: {result['factual_intent']}")
    print(f"Scheme: {result['scheme_name']}")
    print("-"*80)

