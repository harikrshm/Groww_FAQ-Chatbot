"""
Test all factual terms from the system prompt to ensure they work
"""

import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SYSTEM_PROMPT, FACTUAL_INTENTS
from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Test queries for each factual intent
test_queries = {
    "expense_ratio": "What is the expense ratio of SBI Large Cap Fund?",
    "exit_load": "What is the exit load for SBI Equity Hybrid Fund?",
    "minimum_sip": "What is the minimum SIP for SBI Small Cap Fund?",
    "lock_in": "What is the lock-in period for SBI Equity Hybrid Fund?",
    "riskometer": "What is the riskometer rating of SBI Small Cap Fund?",
    "benchmark": "What is the benchmark for SBI Large Cap Fund?",
    "statement": "How to download statement for SBI Large Cap Fund?",
    "nav": "What is the NAV of SBI Multicap Fund?",
    "aum": "What is the AUM of SBI Large Cap Fund?",
    "fund_manager": "Who is the fund manager of SBI Large Cap Fund?",
    "investment_objective": "What is the investment objective of SBI Small Cap Fund?",
    "scheme_details": "What are the scheme details of SBI Multicap Fund?",
}

print("="*80)
print("TESTING ALL FACTUAL TERMS WITH NEW SYSTEM PROMPT")
print("="*80)
print(f"\nSystem prompt includes {len(FACTUAL_INTENTS)} factual intent types")
print(f"Total test queries: {len(test_queries)}")
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

results = {
    "success": [],
    "failed": [],
    "blocked": []
}

for intent_type, query in test_queries.items():
    print(f"\n{'='*80}")
    print(f"TEST: {intent_type.upper()}")
    print(f"Query: {query}")
    print("="*80)
    
    try:
        # Preprocess query
        preprocessed = preprocess_query(query)
        print(f"Classification: {preprocessed['classification']}")
        print(f"Factual Intent: {preprocessed.get('factual_intent', 'None')}")
        
        if preprocessed['precomputed_response']:
            print(f"[WARNING] Query blocked at preprocessing stage")
            results["blocked"].append((intent_type, query, "preprocessing"))
            continue
        
        # Retrieve chunks
        chunks = retrieval.retrieve(
            query=preprocessed['expanded_query'],
            top_k=5,
            scheme_name=preprocessed['scheme_name'],
            include_metadata=True
        )
        
        print(f"Retrieved {len(chunks)} chunks")
        
        if not chunks:
            print("[WARNING] No chunks retrieved")
            results["failed"].append((intent_type, query, "no_chunks"))
            continue
        
        # Prepare context
        context_dict = retrieval.prepare_context(chunks, max_chunks=5)
        context = context_dict['context']
        
        print(f"Context prepared: {len(context)} characters")
        
        # Format user prompt
        user_prompt = llm_service.format_user_prompt(context, query)
        
        # Generate response
        print("Generating response...")
        response = llm_service.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        
        if response:
            print(f"[SUCCESS]")
            print(f"Response: {response[:150]}...")
            results["success"].append((intent_type, query))
        else:
            print(f"[FAILED] No response generated")
            results["failed"].append((intent_type, query, "no_response"))
            
    except Exception as e:
        print(f"[ERROR]: {e}")
        results["failed"].append((intent_type, query, str(e)[:50]))

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"\nTotal tests: {len(test_queries)}")
print(f"[OK] Successful: {len(results['success'])}")
print(f"[FAILED] Failed: {len(results['failed'])}")
print(f"[BLOCKED] Blocked: {len(results['blocked'])}")

if results['success']:
    print("\n[SUCCESSFUL TESTS]:")
    for intent_type, query in results['success']:
        print(f"  - {intent_type}: {query}")

if results['failed']:
    print("\n[FAILED TESTS]:")
    for intent_type, query, reason in results['failed']:
        print(f"  - {intent_type}: {query} (Reason: {reason})")

if results['blocked']:
    print("\n[BLOCKED TESTS]:")
    for intent_type, query, reason in results['blocked']:
        print(f"  - {intent_type}: {query} (Reason: {reason})")

print("\n" + "="*80)
success_rate = (len(results['success']) / len(test_queries)) * 100
print(f"Success Rate: {success_rate:.1f}%")
print("="*80)

