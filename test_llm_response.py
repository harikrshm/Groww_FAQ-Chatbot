"""
Test LLM response generation with sample queries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query
from config import SYSTEM_PROMPT

# Test queries
test_queries = [
    "What is the expense ratio of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI Small Cap Fund?",
    "What is the exit load for SBI Equity Hybrid Fund?",
]

print("="*80)
print("LLM RESPONSE GENERATION TEST")
print("="*80)

# Initialize services
print("\nInitializing services...")
llm_service = get_llm_service()
retrieval = get_retrieval_system()

print("\n" + "="*80)

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
    
    if preprocessed['precomputed_response']:
        print(f"\n[BLOCKED] Query blocked - will not proceed with generation")
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
    
    print(f"  Retrieved {len(chunks)} chunks")
    
    # Prepare context
    context_dict = retrieval.prepare_context(chunks, max_chunks=5)
    context = context_dict['context']
    source_urls = context_dict['source_urls']
    
    print(f"  Context prepared from {context_dict['num_chunks']} chunks")
    print(f"  Source URLs: {len(source_urls)}")
    
    # Format user prompt
    user_prompt = llm_service.format_user_prompt(context, query)
    
    print(f"\nGenerating response with LLM...")
    
    # Generate response
    response = llm_service.generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
    
    if response:
        print(f"\n[SUCCESS] Response Generated:")
        print("-"*80)
        print(response)
        print("-"*80)
        print(f"\nResponse length: {len(response)} characters")
        print(f"Source URLs: {source_urls[0] if source_urls else 'None'}")
    else:
        print(f"\n[FAILED] Could not generate response")
        print("  Please check:")
        print("    1. GEMINI_API_KEY is set in .env file")
        print("    2. API key is valid (get from https://aistudio.google.com/app/apikey)")
        print("    3. google-generativeai package is installed (pip install google-generativeai)")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

