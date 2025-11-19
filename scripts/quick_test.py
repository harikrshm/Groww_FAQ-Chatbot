"""Quick test of one query"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.query_processor import preprocess_query
from backend.retrieval import get_retrieval_system
from backend.llm_service import get_llm_service
from backend.formatter import format_response, format_fallback_response
from config import SYSTEM_PROMPT, RETRIEVAL_CONFIG

query = "What is the expense ratio of SBI Large Cap Fund?"

print("="*70)
print(f"Testing: {query}")
print("="*70)

# Preprocess
print("\n1. Preprocessing...")
preprocessed = preprocess_query(query)
print(f"   Classification: {preprocessed['classification']}")
print(f"   Scheme: {preprocessed.get('scheme_name')}")

# Retrieve
print("\n2. Retrieving chunks...")
retrieval = get_retrieval_system()
chunks = retrieval.retrieve(
    query=preprocessed['expanded_query'],
    top_k=3,
    scheme_name=preprocessed.get('scheme_name')
)
print(f"   Retrieved {len(chunks)} chunks")

if chunks:
    print(f"   Top chunk: {chunks[0].get('scheme_name')}, score: {chunks[0].get('score', 0):.4f}")

# Prepare context
print("\n3. Preparing context...")
context_dict = retrieval.prepare_context(chunks, max_chunks=3)
print(f"   Context length: {len(context_dict['context'])} chars")
print(f"   Source URLs: {len(context_dict['source_urls'])}")

# Generate response
print("\n4. Generating response...")
llm = get_llm_service()
user_prompt = llm.format_user_prompt(context_dict['context'], query)
response, validation = llm.generate_validated_response(
    system_prompt=SYSTEM_PROMPT,
    user_prompt=user_prompt,
    query=query,
    source_url=context_dict['source_urls'][0] if context_dict['source_urls'] else None,
    scheme_name=preprocessed.get('scheme_name'),
    max_retries=3,
    use_fallback=True
)

# Format
formatted = format_response(
    answer=response,
    source_url=context_dict['source_urls'][0] if context_dict['source_urls'] else None,
    query=query,
    scheme_name=preprocessed.get('scheme_name')
)

print("\n" + "="*70)
print("RESPONSE:")
print("="*70)
print(f"Answer: {formatted.get('answer')}")
print(f"Source URL: {formatted.get('source_url')}")
print("="*70)

