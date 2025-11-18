"""
Document preprocessing script
Cleans, chunks, and prepares documents for embedding and vector storage
"""

import json
import re
import os
from typing import List, Dict
from datetime import datetime

# Chunking configuration
CHUNK_SIZE = 1000  # tokens (approximate)
CHUNK_OVERLAP = 200  # tokens (approximate)


def clean_text(text: str) -> str:
    """
    Clean text by removing HTML tags, normalizing whitespace, etc.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML tags (basic cleanup - BeautifulSoup should have done most)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might interfere (but keep punctuation)
    # Keep: letters, numbers, punctuation, common symbols
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\%\₹\$\-\(\)]', '', text)
    
    # Normalize whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    return cleaned_text.strip()


def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens in text (rough approximation)
    Uses average of 4 characters per token
    
    Args:
        text: Text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, 
               chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens
        chunk_overlap: Overlap size in tokens
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Estimate tokens
    estimated_tokens = estimate_tokens(text)
    
    # If text is smaller than chunk_size, return as single chunk
    if estimated_tokens <= chunk_size:
        return [text]
    
    chunks = []
    
    # Convert token sizes to character approximations
    char_chunk_size = chunk_size * 4
    char_overlap = chunk_overlap * 4
    
    start = 0
    while start < len(text):
        # Calculate end position
        end = start + char_chunk_size
        
        # If this is not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within last 20% of chunk
            search_start = max(start, end - int(char_chunk_size * 0.2))
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end > start:
                end = sentence_end + 1
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position (with overlap)
        start = end - char_overlap
        if start >= len(text):
            break
    
    return chunks


def process_document(doc: Dict) -> List[Dict]:
    """
    Process a single document: clean and chunk
    
    Args:
        doc: Document dictionary with 'content', 'url', etc.
        
    Returns:
        List of chunk dictionaries with metadata
    """
    url = doc.get('url', '')
    title = doc.get('title', '')
    content = doc.get('content', '')
    scheme_name = doc.get('scheme_name', None)
    document_type = doc.get('document_type', None)
    factual_data = doc.get('factual_data', {})
    
    # Clean text
    cleaned_content = clean_text(content)
    
    if not cleaned_content:
        return []
    
    # Chunk text
    chunks = chunk_text(cleaned_content, CHUNK_SIZE, CHUNK_OVERLAP)
    
    # Create chunk documents with metadata
    processed_chunks = []
    for idx, chunk_content in enumerate(chunks):
        chunk_doc = {
            'text': chunk_content,
            'source_url': url,
            'title': title,
            'scheme_name': scheme_name,
            'document_type': document_type,
            'chunk_index': idx,
            'total_chunks': len(chunks),
            'factual_data': factual_data,  # Include factual data in each chunk
            'processed_date': datetime.now().isoformat()
        }
        processed_chunks.append(chunk_doc)
    
    return processed_chunks


def process_scraped_data(input_file: str = "data/raw/scraped_data.json",
                         output_file: str = "data/processed/chunks.json") -> Dict:
    """
    Process all scraped documents: clean, chunk, and save
    
    Args:
        input_file: Path to scraped data JSON file
        output_file: Path to output processed chunks JSON file
        
    Returns:
        Dictionary with processing statistics
    """
    # Load scraped data
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        scraped_docs = json.load(f)
    
    print(f"Processing {len(scraped_docs)} documents from {input_file}...")
    
    # Process all documents
    all_chunks = []
    stats = {
        'total_documents': len(scraped_docs),
        'total_chunks': 0,
        'documents_processed': 0,
        'documents_failed': 0
    }
    
    for doc in scraped_docs:
        try:
            chunks = process_document(doc)
            all_chunks.extend(chunks)
            stats['total_chunks'] += len(chunks)
            stats['documents_processed'] += 1
            
            print(f"  Processed: {doc.get('title', 'Unknown')} -> {len(chunks)} chunks")
        except Exception as e:
            print(f"  Error processing {doc.get('url', 'Unknown')}: {e}")
            stats['documents_failed'] += 1
    
    # Save processed chunks
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessing complete!")
    print(f"  Documents processed: {stats['documents_processed']}/{stats['total_documents']}")
    print(f"  Total chunks created: {stats['total_chunks']}")
    print(f"  Output saved to: {output_file}")
    
    return stats


if __name__ == "__main__":
    # Process scraped data
    stats = process_scraped_data()
    print(f"\nStatistics: {stats}")

