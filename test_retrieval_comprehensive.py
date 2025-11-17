"""
Comprehensive test for retrieval system
Tests retrieval, re-ranking, and context preparation with source URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

# Test queries
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the exit load for SBI Multicap Fund?",
    "What is the benchmark of SBI Equity Hybrid Fund?",
]

print("="*80)
print("COMPREHENSIVE RETRIEVAL TEST")
print("="*80)

retrieval = get_retrieval_system()

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {query}")
    print("="*80)
    
    # Preprocess query
    preprocessed = preprocess_query(query)
    print(f"\nPreprocessing:")
    print(f"  Scheme: {preprocessed['scheme_name']}")
    print(f"  Intent: {preprocessed['factual_intent']}")
    
    # Retrieve chunks
    chunks = retrieval.retrieve(
        query=preprocessed['expanded_query'],
        top_k=5,
        scheme_name=preprocessed['scheme_name'],
        include_metadata=True
    )
    
    print(f"\nRetrieved {len(chunks)} chunks")
    
    # Prepare context
    context = retrieval.prepare_context(chunks, max_chunks=5)
    
    print(f"\nContext Preparation:")
    print(f"  Chunks used: {context['num_chunks']}")
    print(f"  Unique source URLs: {len(context['source_urls'])}")
    print(f"  Context length: {len(context['context'])} characters")
    
    print(f"\nSource URLs:")
    for j, url in enumerate(context['source_urls'], 1):
        print(f"  {j}. {url}")
    
    # Verify source URLs are preserved
    print(f"\nVerification:")
    all_urls_preserved = True
    for chunk in chunks[:context['num_chunks']]:
        chunk_url = chunk.get('source_url', '')
        if chunk_url and chunk_url not in context['source_urls']:
            print(f"  [ERROR] URL missing: {chunk_url}")
            all_urls_preserved = False
    
    if all_urls_preserved:
        print(f"  [OK] All source URLs preserved correctly")
    else:
        print(f"  [ERROR] Some source URLs missing")

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print("All retrieval tests completed. Source URLs verified.")
print("="*80)

