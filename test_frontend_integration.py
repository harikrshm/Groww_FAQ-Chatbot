"""
Test frontend integration with sample queries
Tests the complete flow: backend integration → response display
"""

import os
import sys
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Sample queries from user
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


def process_query_test(query: str, llm_service, retrieval_system):
    """
    Test version of process_query function (same logic as app.py)
    """
    from backend.query_processor import preprocess_query
    from backend.formatter import format_response, format_fallback_response
    from config import SYSTEM_PROMPT
    
    # Step 1: Preprocess query
    preprocessed = preprocess_query(query)
    classification = preprocessed['classification']
    scheme_name = preprocessed.get('scheme_name')
    precomputed_response = preprocessed.get('precomputed_response')
    
    # Step 2: Check for precomputed response
    if precomputed_response:
        return format_response(
            answer=precomputed_response.get('answer', ''),
            source_url=precomputed_response.get('source_url', ''),
            query=query,
            scheme_name=scheme_name
        )
    
    # Step 3: Retrieve chunks (only for factual queries)
    if classification != 'factual':
        return format_fallback_response(query, scheme_name)
    
    chunks = retrieval_system.retrieve(
        query=preprocessed['expanded_query'],
        top_k=5,
        scheme_name=scheme_name,
        include_metadata=True
    )
    
    if not chunks:
        return format_fallback_response(query, scheme_name)
    
    # Step 4: Prepare context
    context_dict = retrieval_system.prepare_context(chunks, max_chunks=5)
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    primary_source_url = source_urls[0] if source_urls else None
    
    # Step 5: Format user prompt
    user_prompt = llm_service.format_user_prompt(context, query)
    
    # Step 6: Generate validated response
    validated_response, validation_result = llm_service.generate_validated_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        query=query,
        source_url=primary_source_url,
        scheme_name=scheme_name,
        max_retries=3,
        use_fallback=True
    )
    
    # Step 7: Format response
    formatted_response = format_response(
        answer=validated_response,
        source_url=primary_source_url,
        validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
        query=query,
        scheme_name=scheme_name
    )
    
    return formatted_response


def initialize_backend_services_test():
    """Test version of initialize_backend_services"""
    try:
        from backend.llm_service import get_llm_service
        from backend.retrieval import get_retrieval_system
        
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        
        return llm_service, retrieval_system
    except Exception as e:
        print(f"Failed to initialize backend services: {e}")
        return None, None


print("="*80)
print("FRONTEND INTEGRATION TEST")
print("="*80)
print(f"\nTesting {len(test_queries)} queries through app.py process_query() function")
print("\n" + "="*80)

# Initialize backend services
print("\nInitializing backend services...")
try:
    llm_service, retrieval_system = initialize_backend_services_test()
    if llm_service and retrieval_system:
        print("[OK] Backend services initialized successfully\n")
    else:
        print("[ERROR] Failed to initialize backend services")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to initialize: {e}")
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
        # Process query
        formatted_response = process_query_test(query, llm_service, retrieval_system)
        
        # Extract response details
        answer = formatted_response.get('answer', '')
        source_url = formatted_response.get('source_url', '')
        is_valid = formatted_response.get('is_valid', False)
        warnings = formatted_response.get('warnings', [])
        fixes_applied = formatted_response.get('fixes_applied', [])
        
        # Check if it's a precomputed response
        is_precomputed = any(keyword in answer.lower() for keyword in [
            "i can only provide factual information",
            "i don't have information",
            "cannot provide"
        ])
        
        print(f"\n[RESULT]")
        print(f"  Answer: {answer[:200]}...")
        print(f"  Source URL: {source_url}")
        print(f"  Valid: {is_valid}")
        
        if is_precomputed:
            status = "BLOCKED_AS_EXPECTED" if expected_type == "advice" else "BLOCKED"
            print(f"  Status: {status} (Precomputed response)")
        else:
            status = "SUCCESS"
            print(f"  Status: {status} (Generated response)")
        
        if warnings:
            print(f"  Warnings: {warnings}")
        if fixes_applied:
            print(f"  Fixes Applied: {fixes_applied}")
        
        results.append({
            "test": i,
            "query": query,
            "status": status,
            "answer": answer,
            "source_url": source_url,
            "is_valid": is_valid
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
print("UI COMPONENT VERIFICATION")
print("="*80)

# Test welcome component
try:
    from frontend.components.welcome import render_welcome, get_example_question, EXAMPLE_QUESTIONS
    print(f"\n[OK] Welcome component: Available")
    print(f"  Example questions: {len(EXAMPLE_QUESTIONS)}")
except Exception as e:
    print(f"\n[ERROR] Welcome component: {e}")

# Test chat UI component
try:
    from frontend.components.chat_ui import (
        render_message_bubble, render_chat_history, render_input_area,
        render_loading_indicator, add_message_to_history
    )
    print(f"[OK] Chat UI component: Available")
except Exception as e:
    print(f"[ERROR] Chat UI component: {e}")

# Test footer component
try:
    from frontend.components.footer import render_footer
    print(f"[OK] Footer component: Available")
except Exception as e:
    print(f"[ERROR] Footer component: {e}")

# Test CSS file
try:
    with open('frontend/styles.css', 'r') as f:
        css_content = f.read()
        print(f"[OK] CSS file: Found ({len(css_content)} chars)")
except Exception as e:
    print(f"[ERROR] CSS file: {e}")

print("\n" + "="*80)
print("FRONTEND INTEGRATION TEST COMPLETE")
print("="*80)
