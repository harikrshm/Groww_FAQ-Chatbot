"""Simple test to verify queries work"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.retrieval import get_retrieval_system
from backend.query_processor import preprocess_query

print("Testing query retrieval...")
print("="*70)

query = "What is the expense ratio of SBI Large Cap Fund?"
print(f"\nQuery: {query}")

# Preprocess
preprocessed = preprocess_query(query)
print(f"Scheme: {preprocessed.get('scheme_name')}")

# Retrieve
retrieval = get_retrieval_system()
chunks = retrieval.retrieve(
    query=preprocessed['expanded_query'],
    top_k=3,
    scheme_name=preprocessed.get('scheme_name')
)

print(f"\nRetrieved {len(chunks)} chunks")
if chunks:
    print(f"Top chunk:")
    print(f"  Scheme: {chunks[0].get('scheme_name')}")
    print(f"  Source: {chunks[0].get('source_url', '')[:80]}...")
    print(f"  Score: {chunks[0].get('reranked_score', chunks[0].get('score', 0)):.4f}")
    print(f"  Text: {chunks[0].get('text', '')[:200]}...")
else:
    print("No chunks retrieved!")

