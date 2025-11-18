"""
Upload processed document chunks to Pinecone vector database
Generates embeddings and uploads with metadata
"""

import json
import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion
from sentence_transformers import SentenceTransformer
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 32
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "mutual-fund-faq")


def initialize_pinecone() -> Pinecone:
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


def create_index_if_not_exists(pc: Pinecone, index_name: str, dimension: int = EMBEDDING_DIMENSION):
    """
    Create Pinecone index if it doesn't exist
    
    Args:
        pc: Pinecone client
        index_name: Name of the index
        dimension: Embedding dimension
    """
    existing_indexes = [index.name for index in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        logger.info(f"Creating index: {index_name} with dimension {dimension}")
        region = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        # Map region string to AwsRegion enum if needed
        aws_region = AwsRegion.US_EAST_1  # Default
        if "us-west" in region.lower():
            aws_region = AwsRegion.US_WEST_2
        elif "eu-west" in region.lower():
            aws_region = AwsRegion.EU_WEST_1
        
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=CloudProvider.AWS,
                region=aws_region
            )
        )
        logger.info(f"Index {index_name} created successfully")
        # Wait for index to be ready
        import time
        time.sleep(5)
    else:
        logger.info(f"Index {index_name} already exists")


def load_embedding_model() -> SentenceTransformer:
    """
    Load sentence transformer model for embeddings
    
    Returns:
        SentenceTransformer model
    """
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info("Embedding model loaded successfully")
    return model


def generate_embeddings_batch(model: SentenceTransformer, texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts
    
    Args:
        model: SentenceTransformer model
        texts: List of text strings
        
    Returns:
        List of embedding vectors
    """
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def prepare_pinecone_vectors(chunks: List[Dict], embeddings: List[List[float]]) -> List[Dict]:
    """
    Prepare vectors for Pinecone upsert
    
    Args:
        chunks: List of chunk dictionaries
        embeddings: List of embedding vectors
        
    Returns:
        List of Pinecone vector dictionaries
    """
    vectors = []
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Create unique ID
        vector_id = f"chunk_{chunk.get('source_url', 'unknown').replace('https://', '').replace('http://', '').replace('/', '_')}_{chunk.get('chunk_index', i)}"
        # Clean vector_id (Pinecone doesn't like certain characters)
        vector_id = "".join(c if c.isalnum() or c in ['_', '-'] else '_' for c in vector_id)
        
        # Prepare metadata (Pinecone metadata must be string, number, or boolean)
        metadata = {
            'text': chunk.get('text', '')[:5000],  # Limit text length for metadata
            'source_url': chunk.get('source_url', ''),
            'title': chunk.get('title', '')[:500],  # Limit title length
            'chunk_index': chunk.get('chunk_index', 0),
            'total_chunks': chunk.get('total_chunks', 0),
            'processed_date': chunk.get('processed_date', '')
        }
        
        # Add optional fields if they exist
        if chunk.get('scheme_name'):
            metadata['scheme_name'] = chunk.get('scheme_name')[:200]
        if chunk.get('document_type'):
            metadata['document_type'] = chunk.get('document_type')[:100]
        
        # Add factual data as JSON string (if available)
        if chunk.get('factual_data'):
            factual_str = json.dumps(chunk.get('factual_data'), ensure_ascii=False)
            metadata['factual_data'] = factual_str[:2000]  # Limit length
        
        vector = {
            'id': vector_id,
            'values': embedding,
            'metadata': metadata
        }
        vectors.append(vector)
    
    return vectors


def upload_to_pinecone(pc: Pinecone, index_name: str, chunks: List[Dict], 
                       model: SentenceTransformer, batch_size: int = BATCH_SIZE):
    """
    Upload chunks to Pinecone with embeddings
    
    Args:
        pc: Pinecone client
        index_name: Name of Pinecone index
        chunks: List of chunk dictionaries
        model: SentenceTransformer model
        batch_size: Batch size for processing
        
    Returns:
        Dictionary with upload statistics
    """
    index = pc.Index(index_name)
    
    total_chunks = len(chunks)
    uploaded = 0
    failed = 0
    
    logger.info(f"Starting upload of {total_chunks} chunks to Pinecone index: {index_name}")
    
    # Process in batches
    for i in range(0, total_chunks, batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_texts = [chunk.get('text', '') for chunk in batch_chunks]
        
        try:
            # Generate embeddings for batch
            logger.info(f"Generating embeddings for batch {i//batch_size + 1} ({len(batch_texts)} chunks)...")
            embeddings = generate_embeddings_batch(model, batch_texts)
            
            # Prepare vectors
            vectors = prepare_pinecone_vectors(batch_chunks, embeddings)
            
            # Upsert to Pinecone
            logger.info(f"Uploading batch {i//batch_size + 1} to Pinecone...")
            # Convert vectors to format expected by Pinecone
            pinecone_vectors = [
                {
                    'id': v['id'],
                    'values': v['values'],
                    'metadata': v['metadata']
                }
                for v in vectors
            ]
            index.upsert(vectors=pinecone_vectors)
            
            uploaded += len(batch_chunks)
            logger.info(f"Uploaded {uploaded}/{total_chunks} chunks")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error uploading batch {i//batch_size + 1}: {e}")
            failed += len(batch_chunks)
    
    stats = {
        'total_chunks': total_chunks,
        'uploaded': uploaded,
        'failed': failed
    }
    
    return stats


def main():
    """
    Main function to process chunks and upload to Pinecone
    """
    input_file = "data/processed/chunks.json"
    
    # Check if chunks file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Processed chunks file not found: {input_file}. Run process_documents.py first.")
    
    # Load processed chunks
    logger.info(f"Loading chunks from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} chunks")
    
    # Initialize Pinecone
    logger.info("Initializing Pinecone...")
    pc = initialize_pinecone()
    
    # Create index if needed
    create_index_if_not_exists(pc, INDEX_NAME, EMBEDDING_DIMENSION)
    
    # Load embedding model
    model = load_embedding_model()
    
    # Upload to Pinecone
    stats = upload_to_pinecone(pc, INDEX_NAME, chunks, model, BATCH_SIZE)
    
    # Print summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Successfully uploaded: {stats['uploaded']}")
    print(f"Failed: {stats['failed']}")
    print(f"Index: {INDEX_NAME}")
    print("="*70)


if __name__ == "__main__":
    main()

