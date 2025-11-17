"""
Test retrieval system with user-provided queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

# User-provided test queries
test_queries = [
    "What is the minimum lump-sum investment amount for SBI Magnum Ultra Short Duration Fund?",
    "What does the riskometer of SBI Small Cap Fund currently indicate according to the AMC?",
    "Does SBI Nifty 50 Index Fund have any exit load as per the scheme details page?",
    "How can I download my capital gains statement from SBI Mutual Fund?",
    "Which benchmark does the SBI Large Cap Fund follow according to its scheme details?",
]

print("="*80)
print("RETRIEVAL TEST - USER QUERIES")
print("="*80)

retrieval = get_retrieval_system()

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"QUERY {i}: {query}")
    print("="*80)
    
    # Preprocess query
    preprocessed = preprocess_query(query)
    print(f"\nQuery Preprocessing:")
    print(f"  Classification: {preprocessed['classification']}")
    print(f"  Scheme Name: {preprocessed['scheme_name']}")
    print(f"  Factual Intent: {preprocessed['factual_intent']}")
    print(f"  Expanded Query: {preprocessed['expanded_query']}")
    
    if preprocessed['precomputed_response']:
        print(f"\n[BLOCKED] Query blocked - will not proceed with retrieval")
        print(f"  Response: {preprocessed['precomputed_response']['answer'][:150]}...")
        continue
    
    # Retrieve chunks
    print(f"\nRetrieving chunks...")
    chunks = retrieval.retrieve(
        query=preprocessed['expanded_query'],
        top_k=5,
        scheme_name=preprocessed['scheme_name'],
        include_metadata=True
    )
    
    print(f"\nRetrieved {len(chunks)} chunks:")
    print("-"*80)
    
    for j, chunk in enumerate(chunks, 1):
        reranked_score = chunk.get('reranked_score', chunk.get('score', 0))
        original_score = chunk.get('original_score', chunk.get('score', 0))
        
        print(f"\nChunk {j}:")
        print(f"  Re-ranked Score: {reranked_score:.4f} (Original: {original_score:.4f})")
        print(f"  Scheme Name: {chunk['scheme_name']}")
        print(f"  Document Type: {chunk['document_type']}")
        print(f"  Source URL: {chunk['source_url']}")
        
        # Show text preview (handle Unicode)
        text_preview = chunk['text'][:200].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
        print(f"  Text Preview: {text_preview}...")
        
        # Show factual data if available
        if chunk.get('factual_data'):
            factual_str = str(chunk['factual_data'])
            factual_preview = factual_str[:150].replace('₹', 'Rs.')
            print(f"  Factual Data: {factual_preview}...")
    
    # Prepare context
    print(f"\n{'='*80}")
    print("Context Preparation:")
    print("="*80)
    context = retrieval.prepare_context(chunks, max_chunks=5)
    
    print(f"  Chunks used: {context['num_chunks']}")
    print(f"  Unique source URLs: {len(context['source_urls'])}")
    print(f"  Context length: {len(context['context'])} characters")
    
    print(f"\n  Source URLs:")
    for j, url in enumerate(context['source_urls'], 1):
        print(f"    {j}. {url}")
    
    # Verify source URLs
    print(f"\n  Verification:")
    all_urls_preserved = True
    for chunk in chunks[:context['num_chunks']]:
        chunk_url = chunk.get('source_url', '')
        if chunk_url and chunk_url not in context['source_urls']:
            print(f"    [ERROR] URL missing: {chunk_url}")
            all_urls_preserved = False
    
    if all_urls_preserved:
        print(f"    [OK] All source URLs preserved correctly")
    
    # Show context preview
    print(f"\n  Context Preview (first 500 chars):")
    context_preview = context['context'][:500].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
    print(f"    {context_preview}...")

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total queries tested: {len(test_queries)}")
print("="*80)

