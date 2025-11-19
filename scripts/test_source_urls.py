"""
Test script to verify source URL extraction and flow through the pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query
from backend.formatter import format_response

print("="*70)
print("TESTING SOURCE URL EXTRACTION AND FLOW")
print("="*70)

# Test query
query = "What is the expense ratio of SBI Large Cap Fund?"
print(f"\nQuery: {query}")

# Step 1: Preprocess
preprocessed = preprocess_query(query)
print(f"\n1. Preprocessing:")
print(f"   Scheme: {preprocessed.get('scheme_name')}")

# Step 2: Retrieve chunks
retrieval = get_retrieval_system()
chunks = retrieval.retrieve(
    query=preprocessed['expanded_query'],
    top_k=3,
    scheme_name=preprocessed.get('scheme_name')
)

print(f"\n2. Retrieval:")
print(f"   Retrieved {len(chunks)} chunks")
if chunks:
    print(f"   First chunk source_url: {chunks[0].get('source_url', 'MISSING')}")
    print(f"   First chunk has source_url: {bool(chunks[0].get('source_url'))}")

# Step 3: Prepare context
context_dict = retrieval.prepare_context(chunks, max_chunks=3)
source_urls = context_dict.get('source_urls', [])

print(f"\n3. Context Preparation:")
print(f"   Source URLs extracted: {len(source_urls)}")
for i, url in enumerate(source_urls, 1):
    print(f"   {i}. {url}")

primary_source_url = source_urls[0] if source_urls else None
print(f"   Primary source URL: {primary_source_url}")

# Step 4: Format response
formatted = format_response(
    answer="The expense ratio is 1.48%. Last updated from sources.",
    source_url=primary_source_url,
    query=query,
    scheme_name=preprocessed.get('scheme_name')
)

print(f"\n4. Formatted Response:")
print(f"   Answer: {formatted.get('answer', '')[:100]}...")
print(f"   Source URL in response: {formatted.get('source_url', 'MISSING')}")
print(f"   Has source_url: {bool(formatted.get('source_url'))}")

# Step 5: Check if source URL would be displayed
print(f"\n5. Display Check:")
if formatted.get('source_url'):
    print(f"   ✓ Source URL would be displayed in chat UI")
    print(f"   URL: {formatted.get('source_url')}")
else:
    print(f"   ✗ Source URL is missing - would NOT be displayed")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

