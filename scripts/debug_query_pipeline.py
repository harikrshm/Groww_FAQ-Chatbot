"""
Diagnostic script to debug query pipeline
Logs every step to identify where factual queries fail
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'debug_pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

def test_query_pipeline(query: str):
    """
    Test a query through the complete pipeline with detailed logging
    """
    logger.info("="*80)
    logger.info(f"TESTING QUERY: '{query}'")
    logger.info("="*80)
    
    try:
        # Import backend modules
        from backend.query_processor import (
            normalize_query, extract_scheme_name, detect_factual_intent,
            classify_query, expand_query_with_synonyms, preprocess_query,
            detect_jailbreak, detect_advice_query, detect_non_mf_query
        )
        from backend.retrieval import get_retrieval_system
        from backend.llm_service import get_llm_service
        from config import RETRIEVAL_CONFIG, FACTUAL_INTENTS
        
        # Step 1: Normalize Query
        logger.info("\n[STEP 1] NORMALIZING QUERY")
        normalized = normalize_query(query)
        logger.info(f"  Original: '{query}'")
        logger.info(f"  Normalized: '{normalized}'")
        
        # Step 2: Extract Scheme Name
        logger.info("\n[STEP 2] EXTRACTING SCHEME NAME")
        scheme_name = extract_scheme_name(query)
        logger.info(f"  Scheme Name: {scheme_name if scheme_name else 'None'}")
        
        # Step 3: Test Classification Components Individually
        logger.info("\n[STEP 3] TESTING CLASSIFICATION COMPONENTS")
        
        is_jailbreak = detect_jailbreak(normalized)
        logger.info(f"  Jailbreak Detection: {is_jailbreak}")
        
        is_advice = detect_advice_query(normalized)
        logger.info(f"  Advice Detection: {is_advice}")
        
        is_non_mf = detect_non_mf_query(normalized)
        logger.info(f"  Non-MF Detection: {is_non_mf}")
        
        # Step 4: Detect Factual Intent
        logger.info("\n[STEP 4] DETECTING FACTUAL INTENT")
        factual_intent = detect_factual_intent(normalized)
        logger.info(f"  Factual Intent: {factual_intent if factual_intent else 'None detected'}")
        
        if factual_intent:
            logger.info(f"  Matched patterns from FACTUAL_INTENTS['{factual_intent}']:")
            for pattern in FACTUAL_INTENTS[factual_intent]:
                if pattern.lower() in normalized.lower():
                    logger.info(f"    [MATCH] '{pattern}'")
        else:
            logger.warning("  [WARNING] NO FACTUAL INTENT DETECTED - Query may be blocked!")
        
        # Step 5: Full Classification
        logger.info("\n[STEP 5] FULL CLASSIFICATION")
        classification, precomputed_response = classify_query(query)
        logger.info(f"  Classification: {classification}")
        logger.info(f"  Precomputed Response: {bool(precomputed_response)}")
        
        if precomputed_response:
            logger.warning(f"  [BLOCKED] QUERY BLOCKED - Returning precomputed response")
            logger.warning(f"  Response: {precomputed_response.get('answer', '')[:100]}...")
            return {
                'status': 'BLOCKED',
                'classification': classification,
                'reason': 'Precomputed response returned'
            }
        
        # Step 6: Preprocess Query (Full Pipeline)
        logger.info("\n[STEP 6] PREPROCESSING QUERY (FULL PIPELINE)")
        preprocessed = preprocess_query(query)
        logger.info(f"  Original Query: {preprocessed['original_query']}")
        logger.info(f"  Normalized Query: {preprocessed['normalized_query']}")
        logger.info(f"  Expanded Query: {preprocessed['expanded_query']}")
        logger.info(f"  Scheme Name: {preprocessed.get('scheme_name')}")
        logger.info(f"  Factual Intent: {preprocessed.get('factual_intent')}")
        logger.info(f"  Classification: {preprocessed['classification']}")
        
        if preprocessed.get('precomputed_response'):
            logger.warning(f"  [BLOCKED] PRECOMPUTED RESPONSE PRESENT - Query stopped here")
            return {
                'status': 'BLOCKED',
                'classification': preprocessed['classification'],
                'reason': 'Precomputed response in preprocessing'
            }
        
        # Step 7: Retrieve Chunks
        logger.info("\n[STEP 7] RETRIEVING CHUNKS FROM PINECONE")
        try:
            retrieval_system = get_retrieval_system()
            logger.info(f"  Using expanded query: '{preprocessed['expanded_query']}'")
            logger.info(f"  top_k: {RETRIEVAL_CONFIG['top_k']}")
            logger.info(f"  Scheme filter: {preprocessed.get('scheme_name')}")
            
            chunks = retrieval_system.retrieve(
                query=preprocessed['expanded_query'],
                top_k=RETRIEVAL_CONFIG['top_k'],
                scheme_name=preprocessed.get('scheme_name'),
                include_metadata=True
            )
            
            logger.info(f"  Retrieved {len(chunks)} chunks")
            
            if len(chunks) == 0:
                logger.error("  [ERROR] NO CHUNKS RETRIEVED - Cannot generate answer!")
                return {
                    'status': 'FAILED',
                    'step': 'RETRIEVAL',
                    'reason': 'No chunks retrieved from Pinecone'
                }
            
            # Log chunk details
            for i, chunk in enumerate(chunks):
                logger.info(f"\n  Chunk {i+1}:")
                logger.info(f"    Score: {chunk.get('score', 'N/A')}")
                logger.info(f"    Source: {chunk.get('source_url', 'N/A')}")
                logger.info(f"    Scheme: {chunk.get('scheme_name', 'N/A')}")
                logger.info(f"    Text preview: {chunk.get('text', '')[:150]}...")
                
                # Check if chunk contains NAV
                if 'nav' in chunk.get('text', '').lower():
                    logger.info(f"    [OK] Contains 'NAV'")
                
        except Exception as e:
            logger.error(f"  [ERROR] RETRIEVAL ERROR: {e}")
            return {
                'status': 'FAILED',
                'step': 'RETRIEVAL',
                'reason': str(e)
            }
        
        # Step 8: Generate LLM Response
        logger.info("\n[STEP 8] GENERATING LLM RESPONSE")
        try:
            llm_service = get_llm_service()
            
            # Prepare context
            context_parts = []
            source_urls = []
            for chunk in chunks:
                context_parts.append(chunk.get('text', ''))
                if chunk.get('source_url'):
                    source_urls.append(chunk['source_url'])
            
            context = "\n\n".join(context_parts)
            logger.info(f"  Context length: {len(context)} characters")
            logger.info(f"  Source URLs: {len(source_urls)}")
            
            # Format user prompt
            user_prompt = llm_service.format_user_prompt(context, query)
            logger.info(f"  User prompt length: {len(user_prompt)} characters")
            
            # Get primary source URL
            primary_source_url = source_urls[0] if source_urls else None
            
            # Generate validated response
            from config import SYSTEM_PROMPT
            response, validation_result = llm_service.generate_validated_response(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                query=query,
                source_url=primary_source_url,
                scheme_name=preprocessed.get('scheme_name'),
                max_retries=3,
                use_fallback=True
            )
            
            logger.info(f"  Generated response: {response[:200]}...")
            logger.info(f"  Validation valid: {validation_result.is_valid}")
            logger.info(f"  Validation errors: {validation_result.errors}")
            logger.info(f"  Validation warnings: {validation_result.warnings}")
            
            if not validation_result.is_valid:
                logger.warning("  [WARNING] VALIDATION FAILED - Response may be blocked")
            
            # Format the final response (as done in app.py)
            from backend.formatter import format_response
            formatted = format_response(
                answer=response,
                source_url=source_urls[0] if source_urls else None,
                validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
                query=query,
                scheme_name=preprocessed.get('scheme_name')
            )
            
            logger.info(f"\n[STEP 9] FINAL FORMATTED RESPONSE")
            logger.info(f"  Answer: {formatted.get('answer', '')[:150]}...")
            logger.info(f"  Source URL (FINAL): {formatted.get('source_url', 'None')}")
            logger.info(f"  Is Valid: {formatted.get('is_valid', False)}")
            
            return {
                'status': 'SUCCESS',
                'response': response,
                'formatted_response': formatted,
                'source_url_displayed': formatted.get('source_url'),
                'validation': validation_result.to_dict(),
                'chunks_retrieved': len(chunks)
            }
            
        except Exception as e:
            logger.error(f"  [ERROR] LLM GENERATION ERROR: {e}")
            return {
                'status': 'FAILED',
                'step': 'LLM_GENERATION',
                'reason': str(e)
            }
        
    except Exception as e:
        logger.error(f"[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'status': 'FAILED',
            'step': 'UNKNOWN',
            'reason': str(e)
        }


if __name__ == "__main__":
    # Test queries - NAV and other factual questions
    test_queries = [
        # NAV queries (likely failing)
        "What is the NAV of SBI Large Cap Fund?",
        "Current NAV",
        "What is NAV?",
        "NAV of SBI Large Cap",
        "Latest NAV",
        
        # Other factual queries
        "What is the expense ratio?",
        "Exit load of SBI Large Cap Fund",
        "Minimum SIP amount",
    ]
    
    # Allow user to provide custom query
    if len(sys.argv) > 1:
        test_queries = [" ".join(sys.argv[1:])]
    
    print("\n" + "="*80)
    print("QUERY PIPELINE DIAGNOSTIC TOOL")
    print("="*80)
    print(f"\nTesting {len(test_queries)} queries...\n")
    
    results = []
    for query in test_queries:
        result = test_query_pipeline(query)
        results.append((query, result))
        print("\n" + "-"*80 + "\n")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for query, result in results:
        status_symbol = "[OK]" if result['status'] == 'SUCCESS' else "[FAIL]"
        print(f"{status_symbol} {query[:60]:60s} | Status: {result['status']}")
        if result['status'] != 'SUCCESS':
            print(f"   Reason: {result.get('reason', 'Unknown')}")
    
    print("\n" + "="*80)
    print(f"Check log file for detailed output: debug_pipeline_{datetime.now().strftime('%Y%m%d')}_*.log")
    print("="*80)

