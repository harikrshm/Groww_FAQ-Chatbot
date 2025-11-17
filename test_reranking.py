"""
Test re-ranking functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

# Test query
query = "What is the current expense ratio and benchmark of SBI Equity Hybrid Fund"

print("="*80)
print("RE-RANKING TEST")
print("="*80)
print(f"\nQuery: {query}")

# Preprocess query
preprocessed = preprocess_query(query)
print(f"Expanded Query: {preprocessed['expanded_query']}")

# Initialize retrieval system
retrieval = get_retrieval_system()

# Retrieve with re-ranking
results = retrieval.retrieve(
    query=preprocessed['expanded_query'],
    top_k=5,
    scheme_name=preprocessed['scheme_name'],
    include_metadata=True
)

print(f"\n{'='*80}")
print("RE-RANKED RESULTS")
print("="*80)

for i, chunk in enumerate(results, 1):
    print(f"\n{i}. Re-ranked Score: {chunk['reranked_score']:.4f} (Original: {chunk['original_score']:.4f})")
    print(f"   Scheme: {chunk['scheme_name']}")
    print(f"   Document Type: {chunk['document_type']}")
    print(f"   Source URL: {chunk['source_url']}")
    text_display = chunk['text'][:150].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
    print(f"   Text: {text_display}...")

print("\n" + "="*80)
print("RE-RANKING ANALYSIS")
print("="*80)
print("Re-ranking factors:")
print("  - Base score: Semantic similarity from Pinecone")
print("  - Keyword bonus: Up to 0.2 for matching query keywords")
print("  - Document type bonus: Up to 0.05 (scheme_details > groww_listing)")
print("  - Scheme match bonus: 0.1 if scheme name matches query")
print("="*80)

