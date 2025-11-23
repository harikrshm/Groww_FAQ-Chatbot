"""
Diagnostic script to check Pinecone vector database
Verifies NAV data uploaded and retrievable
"""

import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def diagnose_pinecone():
    """
    Check Pinecone database for NAV data and overall health
    """
    from pinecone import Pinecone
    from sentence_transformers import SentenceTransformer
    import json
    
    print("="*80)
    print("PINECONE DATABASE DIAGNOSTIC")
    print("="*80)
    
    # Initialize Pinecone
    print("\n[1] Initializing Pinecone...")
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ragchatbot")
    
    if not api_key:
        print("❌ ERROR: PINECONE_API_KEY not found in environment")
        return
    
    print(f"  Index name: {index_name}")
    
    try:
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        print("  ✓ Connected to Pinecone")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return
    
    # Get index stats
    print("\n[2] Checking index statistics...")
    try:
        stats = index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"  Total vectors: {total_vectors}")
        print(f"  Dimensions: {stats.get('dimension', 'Unknown')}")
        
        if total_vectors == 0:
            print("  ❌ ERROR: No vectors in index! Data not uploaded.")
            return
        elif total_vectors < 1900:
            print(f"  ⚠️  WARNING: Expected ~1942 vectors, found {total_vectors}")
        else:
            print(f"  ✓ Vector count looks good")
    except Exception as e:
        print(f"  ❌ Failed to get stats: {e}")
        return
    
    # Load embedding model
    print("\n[3] Loading embedding model...")
    try:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("  ✓ Model loaded")
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        return
    
    # Test NAV queries
    print("\n[4] Testing NAV queries...")
    test_queries = [
        "What is the NAV of SBI Large Cap Fund?",
        "Current NAV",
        "Net Asset Value",
        "NAV price"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        try:
            # Generate embedding
            query_embedding = model.encode(query).tolist()
            
            # Search Pinecone
            results = index.query(
                vector=query_embedding,
                top_k=5,
                include_metadata=True
            )
            
            print(f"    Results: {len(results.get('matches', []))} matches")
            
            if len(results.get('matches', [])) == 0:
                print("    ❌ NO RESULTS FOUND!")
                continue
            
            # Analyze top results
            for i, match in enumerate(results['matches'][:3]):
                score = match.get('score', 0)
                metadata = match.get('metadata', {})
                
                print(f"\n    Match {i+1}:")
                print(f"      Score: {score:.4f}")
                print(f"      Scheme: {metadata.get('scheme_name', 'N/A')}")
                print(f"      Source: {metadata.get('source_url', 'N/A')[:60]}...")
                
                # Check for NAV in text
                text = metadata.get('text', '')
                if 'nav' in text.lower():
                    print(f"      ✓ Contains 'NAV' in text")
                    # Extract NAV snippet
                    nav_idx = text.lower().find('nav')
                    snippet = text[max(0, nav_idx-30):min(len(text), nav_idx+100)]
                    print(f"      Snippet: ...{snippet}...")
                else:
                    print(f"      ⚠️  Does NOT contain 'NAV'")
                
                # Check factual_data
                factual_data = metadata.get('factual_data', {})
                if factual_data:
                    print(f"      Factual data keys: {list(factual_data.keys())}")
                
        except Exception as e:
            print(f"    ❌ Query failed: {e}")
    
    # Search for specific NAV data in metadata
    print("\n[5] Searching for vectors with NAV in metadata...")
    try:
        # Try to fetch a few random vectors to inspect
        query_embedding = model.encode("SBI Large Cap Fund NAV").tolist()
        results = index.query(
            vector=query_embedding,
            top_k=10,
            include_metadata=True,
            filter={"scheme_name": "SBI Large Cap Fund"}
        )
        
        print(f"  Found {len(results.get('matches', []))} vectors for 'SBI Large Cap Fund'")
        
        nav_found = 0
        for match in results.get('matches', []):
            metadata = match.get('metadata', {})
            text = metadata.get('text', '').lower()
            
            # Look for NAV patterns
            if any(pattern in text for pattern in ['nav as on', 'nav:', '₹', 'net asset value']):
                nav_found += 1
                print(f"\n  ✓ Vector ID: {match.get('id', 'unknown')}")
                print(f"    Contains NAV data")
                # Extract snippet with NAV
                for pattern in ['nav as on', 'nav:', '₹']:
                    if pattern in text:
                        idx = text.find(pattern)
                        snippet = text[max(0, idx-20):min(len(text), idx+150)]
                        print(f"    Snippet: ...{snippet}...")
                        break
        
        print(f"\n  Total vectors with NAV data: {nav_found}/{len(results.get('matches', []))}")
        
        if nav_found == 0:
            print("  ❌ ERROR: No NAV data found in vectors!")
            print("  This indicates a scraping or processing issue.")
        else:
            print(f"  ✓ NAV data present in database")
            
    except Exception as e:
        print(f"  ❌ Search failed: {e}")
    
    # Compare with local chunks.json
    print("\n[6] Comparing with local chunks.json...")
    chunks_file = "data/processed/chunks.json"
    if os.path.exists(chunks_file):
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            print(f"  Local chunks: {len(chunks)}")
            print(f"  Pinecone vectors: {total_vectors}")
            
            if len(chunks) != total_vectors:
                print(f"  ⚠️  WARNING: Mismatch! Expected {len(chunks)}, found {total_vectors}")
                print(f"  Some chunks may not have been uploaded.")
            else:
                print(f"  ✓ Counts match")
            
            # Check if NAV in chunks
            nav_chunks = 0
            for chunk in chunks[:100]:  # Sample first 100
                if 'nav' in chunk.get('text', '').lower():
                    nav_chunks += 1
            
            print(f"  NAV mentions in first 100 chunks: {nav_chunks}")
            
        except Exception as e:
            print(f"  ⚠️  Could not read chunks.json: {e}")
    else:
        print(f"  ⚠️  chunks.json not found at {chunks_file}")
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)


if __name__ == "__main__":
    diagnose_pinecone()

