"""Test one query quickly"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Initializing...")
from backend.query_processor import preprocess_query
from backend.retrieval import get_retrieval_system
from backend.llm_service import get_llm_service
from backend.formatter import format_response, format_fallback_response
from config import SYSTEM_PROMPT, RETRIEVAL_CONFIG

query = "What is the expense ratio of SBI Large Cap Fund?"

print(f"\nQuery: {query}\n")

# Preprocess
preprocessed = preprocess_query(query)
print(f"Classification: {preprocessed['classification']}, Scheme: {preprocessed.get('scheme_name')}")

# Retrieve
retrieval = get_retrieval_system()
chunks = retrieval.retrieve(preprocessed['expanded_query'], top_k=3, scheme_name=preprocessed.get('scheme_name'))
print(f"Retrieved {len(chunks)} chunks")

if not chunks:
    print("No chunks - using fallback")
    response = format_fallback_response(query, preprocessed.get('scheme_name'))
else:
    # Prepare context
    context_dict = retrieval.prepare_context(chunks, max_chunks=3)
    source_url = context_dict['source_urls'][0] if context_dict['source_urls'] else None
    
    # Generate
    llm = get_llm_service()
    user_prompt = llm.format_user_prompt(context_dict['context'], query)
    answer, validation = llm.generate_validated_response(
        SYSTEM_PROMPT, user_prompt, query, source_url, preprocessed.get('scheme_name'), max_retries=3, use_fallback=True
    )
    
    # Format
    response = format_response(answer, source_url, validation.to_dict() if hasattr(validation, 'to_dict') else None, query, preprocessed.get('scheme_name'))

print(f"\n{'='*70}")
print("RESPONSE:")
print(f"{'='*70}")
print(f"Answer: {response.get('answer')}")
print(f"Source URL: {response.get('source_url')}")
print(f"{'='*70}")

