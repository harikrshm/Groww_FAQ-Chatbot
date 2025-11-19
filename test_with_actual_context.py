"""
Test with actual retrieved context to see what's triggering the block
"""

import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SYSTEM_PROMPT
from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Suppress verbose logging
logging.getLogger('backend.llm_service').setLevel(logging.WARNING)
logging.getLogger('backend.retrieval').setLevel(logging.WARNING)


def test_with_actual_retrieval():
    """Test with actual retrieved context"""
    log.info("="*80)
    log.info("TESTING WITH ACTUAL RETRIEVED CONTEXT")
    log.info("="*80)
    
    query = "What is the expense ratio of SBI Large Cap Fund?"
    
    # Preprocess query
    preprocessed = preprocess_query(query)
    log.info(f"Query: {query}")
    log.info(f"Classification: {preprocessed['classification']}")
    log.info(f"Scheme: {preprocessed['scheme_name']}")
    
    if preprocessed['precomputed_response']:
        log.info("Query would be blocked by preprocessor")
        return
    
    # Retrieve chunks
    retrieval = get_retrieval_system()
    chunks = retrieval.retrieve(
        query=preprocessed['expanded_query'],
        top_k=3,  # Use fewer chunks for testing
        scheme_name=preprocessed['scheme_name'],
        include_metadata=True
    )
    
    log.info(f"\nRetrieved {len(chunks)} chunks")
    
    # Prepare context
    context_dict = retrieval.prepare_context(chunks, max_chunks=3)
    context = context_dict['context']
    
    log.info(f"\nContext length: {len(context)} characters")
    log.info(f"\nContext preview (first 500 chars):\n{context[:500]}...")
    
    # Check for potential trigger words in context
    trigger_words = ['buy', 'sell', 'invest', 'recommend', 'performance', 'best', 'top', 'should', 'advice']
    found_triggers = []
    context_lower = context.lower()
    for word in trigger_words:
        if word in context_lower:
            found_triggers.append(word)
    
    if found_triggers:
        log.warning(f"\n⚠️  Found potential trigger words in context: {found_triggers}")
    else:
        log.info(f"\n✓ No obvious trigger words found in context")
    
    # Test with LLM service
    llm_service = get_llm_service()
    user_prompt = llm_service.format_user_prompt(context, query)
    
    log.info(f"\nUser prompt length: {len(user_prompt)} characters")
    log.info(f"\nUser prompt preview (first 300 chars):\n{user_prompt[:300]}...")
    
    log.info(f"\nCalling LLM service...")
    response = llm_service.generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )
    
    if response:
        log.info(f"\n✓ SUCCESS - Response generated:")
        log.info(f"{response}")
    else:
        log.error(f"\n❌ FAILED - No response generated")


if __name__ == "__main__":
    test_with_actual_retrieval()

