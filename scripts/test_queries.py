"""
Test queries that previously failed to verify they now work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.query_processor import preprocess_query
from backend.retrieval import get_retrieval_system
from backend.llm_service import get_llm_service
from backend.formatter import format_response
from config import SYSTEM_PROMPT, RETRIEVAL_CONFIG

# Test queries that previously failed
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the riskometer rating for SBI Multicap Fund?",
    "What is the benchmark for SBI Nifty Index Fund?",
]

def test_query(query: str, retrieval_system, llm_service):
    """Test a single query"""
    print(f"\n{'='*70}")
    print(f"TESTING QUERY: {query}")
    print('='*70)
    
    # Step 1: Preprocess query
    preprocessed = preprocess_query(query)
    print(f"\nPreprocessing:")
    print(f"  Classification: {preprocessed['classification']}")
    print(f"  Scheme Name: {preprocessed.get('scheme_name')}")
    print(f"  Factual Intent: {preprocessed.get('factual_intent')}")
    
    if preprocessed.get('precomputed_response'):
        print(f"\n[BLOCKED] Query blocked - will not proceed with retrieval")
        return False
    
    # Step 2: Retrieve chunks
    print(f"\nRetrieving chunks...")
    chunks = retrieval_system.retrieve(
        query=preprocessed['expanded_query'],
        top_k=RETRIEVAL_CONFIG.get("top_k", 3),
        scheme_name=preprocessed.get('scheme_name'),
        include_metadata=True
    )
    
    print(f"  Retrieved {len(chunks)} chunks")
    
    if not chunks:
        print(f"\n[FAILED] No chunks retrieved")
        return False
    
    # Show top chunk info
    if chunks:
        top_chunk = chunks[0]
        print(f"  Top chunk:")
        print(f"    Scheme: {top_chunk.get('scheme_name', 'Unknown')}")
        print(f"    Source: {top_chunk.get('source_url', 'Unknown')}")
        print(f"    Score: {top_chunk.get('reranked_score', top_chunk.get('score', 0)):.4f}")
        print(f"    Text preview: {top_chunk.get('text', '')[:150]}...")
    
    # Step 3: Prepare context
    context_dict = retrieval_system.prepare_context(
        chunks,
        max_chunks=RETRIEVAL_CONFIG.get("top_k", 3),
        max_context_tokens=RETRIEVAL_CONFIG.get("max_context_tokens", 800)
    )
    
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    primary_source_url = source_urls[0] if source_urls else None
    
    print(f"\nContext preparation:")
    print(f"  Chunks used: {context_dict['num_chunks']}")
    print(f"  Source URLs: {len(source_urls)}")
    print(f"  Context length: {len(context)} characters")
    
    # Step 4: Generate response
    print(f"\nGenerating response...")
    user_prompt = llm_service.format_user_prompt(context, query)
    
    validated_response, validation_result = llm_service.generate_validated_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        query=query,
        source_url=primary_source_url,
        scheme_name=preprocessed.get('scheme_name'),
        max_retries=3,
        use_fallback=True
    )
    
    # Step 5: Format response
    formatted_response = format_response(
        answer=validated_response,
        source_url=primary_source_url,
        validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
        query=query,
        scheme_name=preprocessed.get('scheme_name')
    )
    
    print(f"\nResponse:")
    print(f"  Answer: {formatted_response.get('answer', 'No answer')}")
    print(f"  Source URL: {formatted_response.get('source_url', 'No source')}")
    
    # Check if response is meaningful (not just fallback)
    answer = formatted_response.get('answer', '').lower()
    is_fallback = 'unable to generate' in answer or 'apologize' in answer or 'visit the official' in answer
    
    if is_fallback:
        print(f"\n[FAILED] Response appears to be a fallback")
        return False
    else:
        print(f"\n[SUCCESS] Query generated a response")
        return True

def main():
    print("="*70)
    print("TESTING QUERIES THAT PREVIOUSLY FAILED")
    print("="*70)
    
    # Initialize services
    print("\nInitializing services...")
    retrieval_system = get_retrieval_system()
    llm_service = get_llm_service()
    print("Services initialized successfully")
    
    # Test each query
    results = []
    for query in test_queries:
        success = test_query(query, retrieval_system, llm_service)
        results.append((query, success))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for query, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {query}")
    
    print(f"\nTotal: {passed}/{total} queries passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n[SUCCESS] All queries now work!")
    else:
        print(f"\n[WARNING] {total - passed} queries still need attention")

if __name__ == "__main__":
    main()

