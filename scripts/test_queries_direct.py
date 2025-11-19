"""
Test 5 factual queries directly using backend components (no Streamlit)
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.query_processor import preprocess_query
from backend.retrieval import get_retrieval_system
from backend.llm_service import get_llm_service
from backend.formatter import format_response, format_fallback_response
from config import SYSTEM_PROMPT, RETRIEVAL_CONFIG

# 5 factual queries to test
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the riskometer rating for SBI Multicap Fund?",
    "What is the benchmark for SBI Nifty Index Fund?",
]

def process_query_direct(query: str, llm_service, retrieval_system):
    """Process query directly without Streamlit"""
    from backend.validators import ValidationResult
    
    logger = logging.getLogger(__name__)
    logger.info(f"[QUERY] Processing: '{query}'")
    
    # Step 1: Preprocess query
    preprocessed = preprocess_query(query)
    classification = preprocessed['classification']
    scheme_name = preprocessed.get('scheme_name')
    precomputed_response = preprocessed.get('precomputed_response')
    
    logger.info(f"[QUERY] Classification: {classification}, Scheme: {scheme_name}")
    
    # Step 2: Check for precomputed response
    if precomputed_response:
        logger.info(f"[QUERY] Using precomputed response")
        return format_response(
            answer=precomputed_response.get('answer', ''),
            source_url=precomputed_response.get('source_url', ''),
            query=query,
            scheme_name=scheme_name
        )
    
    # Step 3: Retrieve chunks
    if classification != 'factual':
        logger.warning(f"[QUERY] Non-factual classification - using fallback")
        return format_fallback_response(query, scheme_name)
    
    logger.info(f"[QUERY] Retrieving chunks...")
    chunks = retrieval_system.retrieve(
        query=preprocessed['expanded_query'],
        top_k=RETRIEVAL_CONFIG.get("top_k", 3),
        scheme_name=scheme_name,
        include_metadata=True
    )
    logger.info(f"[QUERY] Retrieved {len(chunks)} chunks")
    
    if not chunks:
        logger.warning("[QUERY] No chunks retrieved - using fallback")
        return format_fallback_response(query, scheme_name)
    
    # Step 4: Prepare context
    max_chunks = RETRIEVAL_CONFIG.get("top_k", 3)
    max_context_tokens = RETRIEVAL_CONFIG.get("max_context_tokens", 800)
    logger.info(f"[QUERY] Preparing context...")
    context_dict = retrieval_system.prepare_context(
        chunks, 
        max_chunks=max_chunks,
        max_context_tokens=max_context_tokens
    )
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    primary_source_url = source_urls[0] if source_urls else None
    logger.info(f"[QUERY] Context prepared: {len(context)} chars, {len(source_urls)} source URLs")
    
    # Step 5: Format user prompt
    user_prompt = llm_service.format_user_prompt(context, query)
    
    # Step 6: Generate validated response
    logger.info(f"[QUERY] Generating response...")
    validated_response, validation_result = llm_service.generate_validated_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        query=query,
        source_url=primary_source_url,
        scheme_name=scheme_name,
        max_retries=3,
        use_fallback=True
    )
    logger.info(f"[QUERY] Response generated: {len(validated_response) if validated_response else 0} chars")
    
    # Step 7: Format response
    formatted_response = format_response(
        answer=validated_response,
        source_url=primary_source_url,
        validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
        query=query,
        scheme_name=scheme_name
    )
    
    return formatted_response

def test_query(query: str, query_num: int):
    """Test a single query and show response"""
    import sys
    sys.stdout.flush()
    print(f"\n{'='*80}")
    print(f"QUERY {query_num}: {query}")
    print('='*80)
    sys.stdout.flush()
    
    try:
        # Initialize services
        print("Initializing services...")
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        print("Services initialized.\n")
        
        # Process query
        print("Processing query...")
        response = process_query_direct(query, llm_service, retrieval_system)
        
        # Display response
        print(f"\n{'─'*80}")
        print("RESPONSE:")
        print(f"{'─'*80}")
        answer = response.get('answer', 'NO ANSWER')
        print(f"Answer: {answer}")
        print(f"\nSource URL: {response.get('source_url', 'NO SOURCE URL')}")
        print(f"Valid: {response.get('is_valid', 'UNKNOWN')}")
        
        if response.get('warnings'):
            print(f"Warnings: {response.get('warnings')}")
        if response.get('fixes_applied'):
            print(f"Fixes Applied: {response.get('fixes_applied')}")
        
        # Check if it's a fallback
        answer_lower = answer.lower()
        is_fallback = 'unable to generate' in answer_lower or 'apologize' in answer_lower or 'visit the official' in answer_lower
        
        if is_fallback:
            print(f"\n⚠️  STATUS: Fallback response (query may have failed)")
            return False
        elif not answer or answer == 'NO ANSWER':
            print(f"\n❌ STATUS: No answer generated")
            return False
        else:
            print(f"\n✅ STATUS: Success - Response generated")
            return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Also write to file
    output_file = "test_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        def print_both(*args, **kwargs):
            print(*args, **kwargs)
            print(*args, **kwargs, file=f)
        
        print_both("="*80)
        print_both("TESTING 5 FACTUAL QUERIES")
        print_both("="*80)
        
        results = []
        for i, query in enumerate(test_queries, 1):
            success = test_query(query, i)
            results.append((query, success))
        
        # Summary
        print_both("\n" + "="*80)
        print_both("SUMMARY")
        print_both("="*80)
        
        successful = sum(1 for _, success in results if success)
        for query, success in results:
            status = "✅" if success else "❌"
            print_both(f"{status} {query}")
        
        print_both(f"\nTotal: {successful}/{len(results)} queries generated successful responses ({successful/len(results)*100:.1f}%)")
        print_both(f"\nFull results saved to: {output_file}")

if __name__ == "__main__":
    main()

