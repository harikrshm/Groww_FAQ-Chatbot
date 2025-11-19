"""
Comprehensive test for LLM integration with validation
Tests 5 specific queries covering different scenarios
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query
from backend.formatter import format_response, format_fallback_response
from config import SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Test queries
test_queries = [
    {
        "query": "Should I invest my ₹1,00,000 in SBI Nifty Fund or HDFC Index Fund right now?",
        "expected_type": "advice",
        "description": "Advice query - should be blocked at preprocessing"
    },
    {
        "query": "What is the current expense ratio and latest NAV for SBI Nifty ETF (ticker: SBINIFTY) and cite the source.",
        "expected_type": "factual",
        "description": "Factual query with specific requirements"
    },
    {
        "query": "Which large-cap fund is best for high returns over 1 year?",
        "expected_type": "advice",
        "description": "Advice query - should be blocked at preprocessing"
    },
    {
        "query": "Give me a list of top funds to pick from and tell me which one I should buy now.",
        "expected_type": "advice",
        "description": "Advice query - should be blocked at preprocessing"
    },
    {
        "query": "Show me the minimum investment, lock-in period, and expense ratio for 'XYZ Tax Saver Fund' and format the result as JSON with fields: answer, sources, metadata.",
        "expected_type": "factual",
        "description": "Factual query (scheme may not exist) with JSON formatting"
    },
]

print("="*80)
print("COMPREHENSIVE LLM INTEGRATION TEST")
print("="*80)
print(f"\nTesting {len(test_queries)} queries with validation system")
print("\n" + "="*80)

# Initialize services
print("\nInitializing services...")
try:
    llm_service = get_llm_service()
    retrieval = get_retrieval_system()
    print("[OK] Services initialized\n")
except Exception as e:
    print(f"[ERROR] Failed to initialize services: {e}")
    sys.exit(1)

results = []

for i, test_case in enumerate(test_queries, 1):
    query = test_case["query"]
    expected_type = test_case["expected_type"]
    description = test_case["description"]
    
    print(f"\n{'='*80}")
    print(f"TEST {i}: {description}")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Expected Type: {expected_type}")
    print("-"*80)
    
    try:
        # Step 1: Preprocess query
        print("\n[STEP 1] Query Preprocessing...")
        preprocessed = preprocess_query(query)
        classification = preprocessed['classification']
        scheme_name = preprocessed.get('scheme_name')
        factual_intent = preprocessed.get('factual_intent')
        precomputed_response = preprocessed.get('precomputed_response')
        
        print(f"  Classification: {classification}")
        print(f"  Scheme Name: {scheme_name}")
        print(f"  Factual Intent: {factual_intent}")
        
        # Check if query should be blocked
        if precomputed_response:
            print(f"\n[RESULT] Query blocked at preprocessing stage (as expected for {expected_type})")
            print(f"  Precomputed Response: {precomputed_response.get('answer', '')[:150]}...")
            
            formatted = format_response(
                answer=precomputed_response.get('answer', ''),
                source_url=precomputed_response.get('source_url', ''),
                query=query,
                scheme_name=scheme_name
            )
            
            results.append({
                "test": i,
                "query": query,
                "status": "BLOCKED_AS_EXPECTED" if expected_type == "advice" else "BLOCKED_UNEXPECTEDLY",
                "classification": classification,
                "response": formatted,
                "validation": {"is_valid": True, "warnings": ["Precomputed response"]}
            })
            continue
        
        # Step 2: Retrieve chunks (only for factual queries)
        if classification != 'factual':
            print(f"\n[RESULT] Query classified as '{classification}' - skipping retrieval")
            results.append({
                "test": i,
                "query": query,
                "status": "SKIPPED",
                "classification": classification,
                "response": None
            })
            continue
        
        print("\n[STEP 2] Retrieving chunks...")
        chunks = retrieval.retrieve(
            query=preprocessed['expanded_query'],
            top_k=5,
            scheme_name=scheme_name,
            include_metadata=True
        )
        
        print(f"  Retrieved {len(chunks)} chunks")
        
        if not chunks:
            print("\n[WARNING] No chunks retrieved - using fallback")
            formatted = format_fallback_response(query, scheme_name)
            results.append({
                "test": i,
                "query": query,
                "status": "NO_CHUNKS_FALLBACK",
                "response": formatted
            })
            continue
        
        # Step 3: Prepare context
        print("\n[STEP 3] Preparing context...")
        context_dict = retrieval.prepare_context(chunks, max_chunks=5)
        context = context_dict['context']
        source_urls = context_dict['source_urls']
        
        print(f"  Context length: {len(context)} characters")
        print(f"  Source URLs: {len(source_urls)}")
        if source_urls:
            print(f"  Primary source: {source_urls[0]}")
        
        # Step 4: Format user prompt
        user_prompt = llm_service.format_user_prompt(context, query)
        
        # Step 5: Generate validated response
        print("\n[STEP 4] Generating validated response...")
        validated_response, validation_result = llm_service.generate_validated_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            query=query,
            source_url=source_urls[0] if source_urls else None,
            scheme_name=scheme_name,
            max_retries=3,
            use_fallback=True
        )
        
        # Step 6: Format response
        print("\n[STEP 5] Formatting response...")
        formatted = format_response(
            answer=validated_response,
            source_url=source_urls[0] if source_urls else None,
            validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
            query=query,
            scheme_name=scheme_name
        )
        
        # Step 7: Display results
        print("\n[RESULT]")
        print(f"  Answer: {formatted['answer'][:200]}...")
        print(f"  Source URL: {formatted['source_url']}")
        print(f"  Valid: {formatted['is_valid']}")
        if formatted.get('warnings'):
            print(f"  Warnings: {formatted['warnings']}")
        if formatted.get('fixes_applied'):
            print(f"  Fixes Applied: {formatted['fixes_applied']}")
        
        results.append({
            "test": i,
            "query": query,
            "status": "SUCCESS",
            "classification": classification,
            "response": formatted,
            "validation": validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None
        })
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "test": i,
            "query": query,
            "status": "ERROR",
            "error": str(e)
        })

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

success_count = sum(1 for r in results if r.get('status') == 'SUCCESS')
blocked_count = sum(1 for r in results if 'BLOCKED' in r.get('status', ''))
error_count = sum(1 for r in results if r.get('status') == 'ERROR')

print(f"\nTotal Tests: {len(test_queries)}")
print(f"Successful: {success_count}")
print(f"Blocked (as expected): {blocked_count}")
print(f"Errors: {error_count}")

print("\n" + "="*80)
print("DETAILED RESULTS")
print("="*80)

for result in results:
    print(f"\nTest {result['test']}: {result['status']}")
    print(f"  Query: {result['query'][:80]}...")
    if result.get('response'):
        resp = result['response']
        print(f"  Answer: {resp.get('answer', '')[:100]}...")
        print(f"  Valid: {resp.get('is_valid', 'N/A')}")
        if resp.get('fixes_applied'):
            print(f"  Fixes: {resp['fixes_applied']}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

