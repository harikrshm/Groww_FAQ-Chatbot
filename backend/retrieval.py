"""
Retrieval system for querying Pinecone vector database
Handles query embedding, semantic search, and metadata filtering
"""

import os
import sys
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import logging

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMBEDDING_CONFIG, RETRIEVAL_CONFIG

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RetrievalSystem:
    """
    Retrieval system for querying Pinecone vector database
    """
    
    def __init__(self):
        """Initialize Pinecone client and embedding model"""
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "mutual-fund-faq")
        self.embedding_model_name = EMBEDDING_CONFIG["model_name"]
        self.dimension = EMBEDDING_CONFIG["dimension"]
        self.top_k = RETRIEVAL_CONFIG["top_k"]
        self.include_metadata = RETRIEVAL_CONFIG["include_metadata"]
        
        # Initialize Pinecone client
        self.pc = self._initialize_pinecone()
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
        
        # Load embedding model
        self.embedding_model = self._load_embedding_model()
        
        logger.info(f"Retrieval system initialized with index: {self.index_name}")
    
    def _initialize_pinecone(self) -> Pinecone:
        """
        Initialize Pinecone client
        
        Returns:
            Pinecone client instance
        """
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        
        pc = Pinecone(api_key=api_key)
        return pc
    
    def _load_embedding_model(self) -> SentenceTransformer:
        """
        Load sentence transformer model for embeddings
        
        Returns:
            SentenceTransformer model
        """
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        model = SentenceTransformer(self.embedding_model_name)
        logger.info("Embedding model loaded successfully")
        return model
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query
        
        Args:
            query: Query string
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.embedding_model.encode(query, show_progress_bar=False, convert_to_numpy=True)
        return embedding.tolist()
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        scheme_name: Optional[str] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Retrieve relevant chunks from Pinecone
        
        Args:
            query: Query string
            top_k: Number of top results to retrieve
            scheme_name: Optional scheme name for metadata filtering
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of retrieved chunks with scores and metadata
        """
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        # Prepare filter for metadata if scheme_name provided
        filter_dict = None
        if scheme_name:
            filter_dict = {"scheme_name": {"$eq": scheme_name}}
        
        # Query Pinecone
        try:
            if filter_dict:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=include_metadata,
                    filter=filter_dict
                )
            else:
                results = self.index.query(
                    vector=query_embedding,
                    top_k=top_k,
                    include_metadata=include_metadata
                )
            
            # Format results
            retrieved_chunks = []
            for match in results.matches:
                chunk = {
                    'id': match.id,
                    'score': match.score,
                    'text': match.metadata.get('text', '') if match.metadata else '',
                    'source_url': match.metadata.get('source_url', '') if match.metadata else '',
                    'scheme_name': match.metadata.get('scheme_name', '') if match.metadata else '',
                    'document_type': match.metadata.get('document_type', '') if match.metadata else '',
                    'chunk_index': match.metadata.get('chunk_index', 0) if match.metadata else 0,
                    'factual_data': match.metadata.get('factual_data', '') if match.metadata else '',
                }
                retrieved_chunks.append(chunk)
            
            logger.info(f"[RETRIEVAL] Retrieved {len(retrieved_chunks)} chunks for query: '{query[:100]}...'")
            
            # Log chunk details
            for i, chunk in enumerate(retrieved_chunks[:3], 1):
                logger.debug(f"[RETRIEVAL] Chunk {i}: score={chunk.get('score', 0):.4f}, scheme={chunk.get('scheme_name', 'Unknown')}, has_source_url={bool(chunk.get('source_url'))}")
            
            # Re-rank chunks if enabled
            if len(retrieved_chunks) > 0:
                logger.debug("[RETRIEVAL] Re-ranking chunks...")
                retrieved_chunks = self._rerank_chunks(retrieved_chunks, query)
                logger.debug(f"[RETRIEVAL] Re-ranking complete. Top score: {retrieved_chunks[0].get('reranked_score', 0):.4f}")
            
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving from Pinecone: {e}")
            return []
    
    def _rerank_chunks(self, chunks: List[Dict], query: str) -> List[Dict]:
        """
        Re-rank chunks by semantic similarity, keyword match, and document type priority
        
        Args:
            chunks: List of retrieved chunks
            query: Original query string
            
        Returns:
            Re-ranked list of chunks
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Document type priority (higher is better)
        doc_type_priority = {
            'scheme_details': 1.0,  # Official scheme details page - highest priority
            'groww_listing': 0.8,   # Groww listing - lower priority
            None: 0.5               # Unknown type - lowest priority
        }
        
        # Calculate re-ranking scores
        reranked_chunks = []
        for chunk in chunks:
            # Base score from Pinecone (semantic similarity)
            base_score = chunk.get('score', 0.0)
            
            # Keyword match bonus
            chunk_text = chunk.get('text', '').lower()
            chunk_words = set(re.findall(r'\b\w+\b', chunk_text))
            
            # Calculate keyword overlap
            keyword_overlap = len(query_words.intersection(chunk_words))
            keyword_bonus = min(keyword_overlap * 0.05, 0.2)  # Max 0.2 bonus
            
            # Document type priority bonus
            doc_type = chunk.get('document_type')
            type_priority = doc_type_priority.get(doc_type, 0.5)
            type_bonus = (type_priority - 0.5) * 0.1  # Max 0.05 bonus
            
            # Scheme name match bonus (if query mentions scheme and chunk matches)
            scheme_name = chunk.get('scheme_name', '').lower()
            if scheme_name and any(word in scheme_name for word in query_words if len(word) > 3):
                scheme_bonus = 0.1
            else:
                scheme_bonus = 0.0
            
            # Calculate final re-ranked score
            reranked_score = base_score + keyword_bonus + type_bonus + scheme_bonus
            
            chunk['reranked_score'] = reranked_score
            chunk['original_score'] = base_score
            reranked_chunks.append(chunk)
        
        # Sort by re-ranked score (descending)
        reranked_chunks.sort(key=lambda x: x['reranked_score'], reverse=True)
        
        logger.info(f"Re-ranked {len(reranked_chunks)} chunks")
        return reranked_chunks
    
    def prepare_context(self, chunks: List[Dict], max_chunks: int = 3, max_context_tokens: int = 800) -> Dict:
        """
        Prepare context from retrieved chunks for LLM (optimized for token efficiency)
        
        Args:
            chunks: List of retrieved chunks
            max_chunks: Maximum number of chunks to include (default: 3)
            max_context_tokens: Maximum tokens for context (approx 4 chars per token, default: 800)
            
        Returns:
            Dictionary with combined context and source URLs
        """
        # Limit to top chunks
        top_chunks = chunks[:max_chunks]
        
        # Combine chunk texts with truncation
        context_parts = []
        source_urls = []
        current_length = 0
        max_length = max_context_tokens * 4  # Approx 4 chars per token
        
        for i, chunk in enumerate(top_chunks, 1):
            chunk_text = chunk.get('text', '').strip()
            source_url = chunk.get('source_url', '').strip() if chunk.get('source_url') else ''
            
            # Collect source URL first (even if chunk text is empty or will be truncated)
            # This ensures we capture source URLs even from chunks that don't make it into context
            if source_url and source_url not in source_urls:
                source_urls.append(source_url)
            
            if chunk_text:
                # Estimate chunk length (including formatting)
                chunk_with_format = f"[Chunk {i}]\n{chunk_text}"
                chunk_length = len(chunk_with_format)
                
                # Truncate chunk if needed to stay within token limit
                if current_length + chunk_length > max_length:
                    remaining_space = max_length - current_length - len(f"[Chunk {i}]\n") - 50  # Reserve space
                    if remaining_space > 100:  # Only add if meaningful space remains
                        truncated_text = chunk_text[:remaining_space] + "..."
                        chunk_with_format = f"[Chunk {i}]\n{truncated_text}"
                        context_parts.append(chunk_with_format)
                        current_length += len(chunk_with_format)
                    break  # Stop adding chunks if we've reached the limit
                else:
                    context_parts.append(chunk_with_format)
                    current_length += chunk_length
        
        # Combine all chunks into context
        combined_context = "\n\n".join(context_parts)
        
        # Prepare result
        context_dict = {
            'context': combined_context,
            'source_urls': source_urls,
            'num_chunks': len(context_parts),  # Actual chunks used (may be less if truncated)
            'chunks': top_chunks[:len(context_parts)]  # Include only used chunks
        }
        
        logger.info(f"[RETRIEVAL] Prepared context from {len(context_parts)} chunks ({len(combined_context)} chars, ~{len(combined_context)//4} tokens) with {len(source_urls)} unique source URLs")
        if source_urls:
            logger.debug(f"[RETRIEVAL] Source URLs: {', '.join(source_urls[:3])}{'...' if len(source_urls) > 3 else ''}")
        else:
            logger.warning("[RETRIEVAL] No source URLs found in chunks!")
        return context_dict


# Global instance (singleton pattern)
_retrieval_system = None


def get_retrieval_system() -> RetrievalSystem:
    """
    Get or create retrieval system instance (singleton)
    
    Returns:
        RetrievalSystem instance
    """
    global _retrieval_system
    if _retrieval_system is None:
        _retrieval_system = RetrievalSystem()
    return _retrieval_system


if __name__ == "__main__":
    # Test retrieval system
    print("Testing Retrieval System:")
    print("="*70)
    
    retrieval = get_retrieval_system()
    
    # Test query
    test_query = "What is the expense ratio of SBI Large Cap Fund?"
    print(f"\nQuery: {test_query}")
    
    # Retrieve chunks
    results = retrieval.retrieve(test_query, top_k=3)
    
    print(f"\nRetrieved {len(results)} chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"\n{i}. Score: {chunk.get('reranked_score', chunk['score']):.4f}")
        print(f"   Scheme: {chunk['scheme_name']}")
        # Replace Unicode characters for display
        text_display = chunk['text'][:200].replace('₹', 'Rs.').replace('✓', '[OK]').replace('✗', '[X]')
        print(f"   Text: {text_display}...")
        print(f"   Source: {chunk['source_url']}")
    
    # Test context preparation
    print("\n" + "="*70)
    print("Testing Context Preparation:")
    print("="*70)
    context = retrieval.prepare_context(results, max_chunks=3)
    print(f"\nContext prepared from {context['num_chunks']} chunks")
    print(f"Source URLs: {len(context['source_urls'])}")
    for url in context['source_urls']:
        print(f"  - {url}")
    print(f"\nContext length: {len(context['context'])} characters")
    print(f"Context preview: {context['context'][:300]}...")

