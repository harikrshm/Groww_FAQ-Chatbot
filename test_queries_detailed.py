"""
Test query processor with user-provided queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.query_processor import preprocess_query

# User-provided test queries
test_queries = [
    "I have ₹5 lakh. Should I invest in SBI Small Cap Fund or SBI Large Cap Fund for the next 3 years?",
    "What percentage of my salary should I put into equity mutual funds every month?",
    "What is the current expense ratio and benchmark of SBI Equity Hybrid Fund?",
    "Can you help me choose a health insurance plan under ₹15,000?",
    "Is SBI Bluechip Fund good for long-term investment? Also give me its latest riskometer.",
]

print("="*80)
print("QUERY PROCESSOR TEST - USER QUERIES")
print("="*80)

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    # Replace rupee symbol for display
    query_display = query.replace('₹', 'Rs.')
    print(f"QUERY {i}: {query_display}")
    print("-"*80)
    
    result = preprocess_query(query)
    
    print(f"Classification: {result['classification']}")
    print(f"Scheme Name: {result['scheme_name']}")
    print(f"Factual Intent: {result['factual_intent']}")
    
    if result['precomputed_response']:
        print(f"\n[BLOCKED] Pre-computed Response:")
        print(f"Answer: {result['precomputed_response']['answer']}")
        print(f"Source URL: {result['precomputed_response']['source_url']}")
    else:
        print(f"\n[ALLOWED] Will proceed with RAG retrieval")
        print(f"Reason: Factual query - will search vector store and generate answer")
    
    print("="*80)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("Queries classified as:")
for i, query in enumerate(test_queries, 1):
    result = preprocess_query(query)
    print(f"  {i}. {result['classification'].upper()}")
print("="*80)

