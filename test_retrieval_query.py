"""
Test retrieval system with specific user query
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

# User query
query = "What is the current expense ratio and benchmark of SBI Equity Hybrid Fund"

print("="*80)
print("RETRIEVAL TEST - USER QUERY")
print("="*80)
print(f"\nQuery: {query}")

# Preprocess query
preprocessed = preprocess_query(query)
print(f"\nQuery Preprocessing:")
print(f"  Classification: {preprocessed['classification']}")
print(f"  Scheme Name: {preprocessed['scheme_name']}")
print(f"  Factual Intent: {preprocessed['factual_intent']}")
print(f"  Expanded Query: {preprocessed['expanded_query']}")

# Initialize retrieval system
retrieval = get_retrieval_system()

# Test 1: Retrieve without filtering
print("\n" + "="*80)
print("TEST 1: Retrieval WITHOUT scheme filtering")
print("="*80)
results_no_filter = retrieval.retrieve(
    query=preprocessed['expanded_query'],
    top_k=5,
    scheme_name=None,
    include_metadata=True
)

print(f"\nRetrieved {len(results_no_filter)} chunks:")
for i, chunk in enumerate(results_no_filter, 1):
    print(f"\n{'='*80}")
    print(f"Chunk {i}:")
    print(f"  Score: {chunk['score']:.4f}")
    print(f"  Scheme Name: {chunk['scheme_name']}")
    print(f"  Document Type: {chunk['document_type']}")
    print(f"  Chunk Index: {chunk['chunk_index']}")
    print(f"  Source URL: {chunk['source_url']}")
    # Replace Unicode characters for display
    text_display = chunk['text'][:300].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
    print(f"  Text Preview: {text_display}...")
    if chunk.get('factual_data'):
        factual_display = str(chunk['factual_data'])[:200].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
        print(f"  Factual Data: {factual_display}...")

# Test 2: Retrieve WITH scheme filtering
if preprocessed['scheme_name']:
    print("\n" + "="*80)
    print(f"TEST 2: Retrieval WITH scheme filtering ({preprocessed['scheme_name']})")
    print("="*80)
    results_with_filter = retrieval.retrieve(
        query=preprocessed['expanded_query'],
        top_k=5,
        scheme_name=preprocessed['scheme_name'],
        include_metadata=True
    )
    
    print(f"\nRetrieved {len(results_with_filter)} chunks:")
    for i, chunk in enumerate(results_with_filter, 1):
        print(f"\n{'='*80}")
        print(f"Chunk {i}:")
        print(f"  Score: {chunk['score']:.4f}")
        print(f"  Scheme Name: {chunk['scheme_name']}")
        print(f"  Document Type: {chunk['document_type']}")
        print(f"  Chunk Index: {chunk['chunk_index']}")
        print(f"  Source URL: {chunk['source_url']}")
        # Replace Unicode characters for display
        text_display = chunk['text'][:300].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
        print(f"  Text Preview: {text_display}...")
        if chunk.get('factual_data'):
            factual_display = str(chunk['factual_data'])[:200].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
            print(f"  Factual Data: {factual_display}...")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total chunks retrieved (no filter): {len(results_no_filter)}")
if preprocessed['scheme_name']:
    print(f"Total chunks retrieved (with filter): {len(results_with_filter)}")
print("="*80)

