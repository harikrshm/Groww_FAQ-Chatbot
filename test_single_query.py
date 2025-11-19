"""
Test single query with detailed logs and reasoning
Tests: "what is the expense ratio for sbi small cap fund?"
"""

import sys
import os
import logging
import traceback

# Set up UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from backend.llm_service import get_llm_service
from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query
from app import process_query

def test_query():
    query = "what is the expense ratio for sbi small cap fund?"
    
    print("="*80)
    print("TEST QUERY WITH DETAILED LOGS AND REASONING")
    print("="*80)
    print(f"\nQuery: {query}")
    print("="*80)
    
    try:
        # Step 1: Initialize services
        print("\n[STEP 1] Initializing Services...")
        print("-"*80)
        llm_service = get_llm_service()
        retrieval_system = get_retrieval_system()
        print(f"✅ LLM Service initialized: {llm_service.model_name}")
        print(f"✅ Retrieval System initialized")
        
        # Step 2: Preprocess query
        print("\n[STEP 2] Query Preprocessing...")
        print("-"*80)
        preprocessed = preprocess_query(query)
        print(f"Original Query: {query}")
        print(f"Classification: {preprocessed['classification']}")
        print(f"Scheme Name: {preprocessed.get('scheme_name', 'None')}")
        print(f"Factual Intent: {preprocessed.get('factual_intent', 'None')}")
        print(f"Expanded Query: {preprocessed.get('expanded_query', query)}")
        
        if preprocessed.get('precomputed_response'):
            print(f"⚠️  Precomputed Response: {preprocessed['precomputed_response']}")
            return
        
        # Step 3: Retrieve chunks
        print("\n[STEP 3] Retrieving Context Chunks...")
        print("-"*80)
        chunks = retrieval_system.retrieve(
            query=preprocessed['expanded_query'],
            top_k=3,  # Using optimized top_k
            scheme_name=preprocessed.get('scheme_name'),
            include_metadata=True
        )
        
        print(f"Retrieved {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i}:")
            print(f"  Scheme: {chunk.get('scheme_name', 'Unknown')}")
            print(f"  Score: {chunk.get('reranked_score', chunk.get('score', 0)):.4f}")
            print(f"  Source: {chunk.get('source_url', 'No URL')}")
            text_preview = chunk.get('text', '')[:150].replace('\n', ' ')
            print(f"  Preview: {text_preview}...")
        
        if not chunks:
            print("❌ No chunks retrieved - cannot proceed")
            return
        
        # Step 4: Prepare context
        print("\n[STEP 4] Preparing Context...")
        print("-"*80)
        context_dict = retrieval_system.prepare_context(
            chunks, 
            max_chunks=3,
            max_context_tokens=800
        )
        context = context_dict['context']
        source_urls = context_dict['source_urls']
        
        print(f"Context prepared from {context_dict['num_chunks']} chunks")
        print(f"Context length: {len(context)} characters (~{len(context)//4} tokens)")
        print(f"Source URLs: {len(source_urls)} unique URLs")
        for i, url in enumerate(source_urls, 1):
            print(f"  {i}. {url}")
        
        # Step 5: Format prompts
        print("\n[STEP 5] Formatting Prompts...")
        print("-"*80)
        user_prompt = llm_service.format_user_prompt(context, query)
        system_prompt = "Provide factual data from context. Keep responses to 3 sentences max. End with \"Last updated from sources.\" Use neutral language. No advice or opinions.\n\nIf context lacks info, say \"I don't have that information. Visit the official SBI Mutual Fund website.\"\n\nAnswer ONLY from context. No external knowledge."
        
        print(f"System Prompt Length: {len(system_prompt)} characters (~{len(system_prompt)//4} tokens)")
        print(f"User Prompt Length: {len(user_prompt)} characters (~{len(user_prompt)//4} tokens)")
        print(f"Total Input Tokens (approx): {(len(system_prompt) + len(user_prompt))//4}")
        
        # Step 6: Generate response
        print("\n[STEP 6] Generating LLM Response...")
        print("-"*80)
        print("Calling Groq API (Llama 3.1 8B Instant)...")
        
        response = llm_service.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            top_p=0.9,
            max_output_tokens=100
        )
        
        if response:
            print(f"✅ Response generated: {len(response)} characters")
            print(f"\nRaw Response:")
            print(f"  {response}")
        else:
            print("❌ Failed to generate response")
            return
        
        # Step 7: Validate response
        print("\n[STEP 7] Validating Response...")
        print("-"*80)
        from backend.validators import validate_and_fix_response
        validated_response, validation_result = validate_and_fix_response(
            response=response,
            source_url=source_urls[0] if source_urls else None
        )
        
        print(f"Validation Result:")
        print(f"  Valid: {validation_result.is_valid}")
        if validation_result.errors:
            print(f"  Errors: {validation_result.errors}")
        if validation_result.warnings:
            print(f"  Warnings: {validation_result.warnings}")
        if validation_result.fixes_applied:
            print(f"  Fixes Applied: {validation_result.fixes_applied}")
        
        print(f"\nValidated Response:")
        print(f"  {validated_response}")
        
        # Step 8: Final formatted response
        print("\n[STEP 8] Final Formatted Response...")
        print("-"*80)
        from backend.formatter import format_response
        formatted_response = format_response(
            answer=validated_response,
            source_url=source_urls[0] if source_urls else None,
            validation_result=validation_result.to_dict() if hasattr(validation_result, 'to_dict') else None,
            query=query,
            scheme_name=preprocessed.get('scheme_name')
        )
        
        print(f"\n{'='*80}")
        print("FINAL RESPONSE")
        print("="*80)
        print(f"\nAnswer:")
        print(f"  {formatted_response.get('answer', 'No answer')}")
        print(f"\nSource URL:")
        print(f"  {formatted_response.get('source_url', 'No source')}")
        print(f"\n{'='*80}")
        
        # Reasoning summary
        print("\n[REASONING SUMMARY]")
        print("-"*80)
        print("1. Query Classification: Factual query about expense ratio")
        print("2. Scheme Detection: SBI Small Cap Fund identified")
        print("3. Retrieval: Retrieved top 3 relevant chunks from Pinecone")
        print("4. Context Preparation: Combined chunks with token limit (800 tokens)")
        print("5. LLM Generation: Used Groq (Llama 3.1 8B Instant) with optimized prompts")
        print("6. Validation: Checked for source citation, length, and factual content")
        print("7. Formatting: Structured response with answer and source URL")
        print("\n✅ Query processed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nFull Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_query()

