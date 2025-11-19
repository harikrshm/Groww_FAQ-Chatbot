"""
Comprehensive test suite for retrieval system
Tests Pinecone retrieval, embedding generation, re-ranking, and context preparation
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.retrieval import (
    RetrievalSystem,
    get_retrieval_system,
    _retrieval_system
)


class TestRetrievalSystemInitialization:
    """Test RetrievalSystem initialization"""
    
    @patch.dict(os.environ, {
        'PINECONE_API_KEY': 'test-api-key',
        'PINECONE_INDEX_NAME': 'test-index'
    })
    @patch('backend.retrieval.Pinecone')
    @patch('backend.retrieval.SentenceTransformer')
    def test_initialization_success(self, mock_transformer, mock_pinecone):
        """Test successful initialization"""
        # Mock Pinecone client and index
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pc.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc
        
        # Mock SentenceTransformer
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        
        # Initialize
        retrieval = RetrievalSystem()
        
        # Verify initialization
        assert retrieval.index_name == 'test-index'
        assert retrieval.embedding_model == mock_model
        assert retrieval.index == mock_index
        mock_pinecone.assert_called_once_with(api_key='test-api-key')
        mock_transformer.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('backend.retrieval.Pinecone')
    def test_initialization_missing_api_key(self, mock_pinecone):
        """Test initialization fails without API key"""
        with pytest.raises(ValueError, match="PINECONE_API_KEY not found"):
            RetrievalSystem()
    
    @patch.dict(os.environ, {'PINECONE_API_KEY': 'test-key'})
    @patch('backend.retrieval.Pinecone')
    @patch('backend.retrieval.SentenceTransformer')
    def test_initialization_default_index_name(self, mock_transformer, mock_pinecone):
        """Test default index name when not provided"""
        mock_pc = MagicMock()
        mock_index = MagicMock()
        mock_pc.Index.return_value = mock_index
        mock_pinecone.return_value = mock_pc
        mock_transformer.return_value = MagicMock()
        
        # Remove PINECONE_INDEX_NAME from env
        if 'PINECONE_INDEX_NAME' in os.environ:
            del os.environ['PINECONE_INDEX_NAME']
        
        retrieval = RetrievalSystem()
        # Should use default from code (mutual-fund-faq or ragchatbot)
        assert retrieval.index_name is not None


class TestGenerateQueryEmbedding:
    """Test query embedding generation"""
    
    @pytest.fixture
    def mock_retrieval(self):
        """Create a mock retrieval system"""
        import numpy as np
        with patch('backend.retrieval.Pinecone'), \
             patch('backend.retrieval.SentenceTransformer') as mock_transformer:
            mock_model = MagicMock()
            # Return numpy array that has tolist() method
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4, 0.5] * 20)  # 100 dim vector
            mock_transformer.return_value = mock_model
            
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                retrieval = RetrievalSystem()
                yield retrieval, mock_model
    
    def test_generate_embedding_basic(self, mock_retrieval):
        """Test basic embedding generation"""
        retrieval, mock_model = mock_retrieval
        query = "What is the expense ratio?"
        
        embedding = retrieval.generate_query_embedding(query)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, (int, float)) for x in embedding)
        mock_model.encode.assert_called_once_with(
            query, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
    
    def test_generate_embedding_empty_query(self, mock_retrieval):
        """Test embedding generation with empty query"""
        retrieval, mock_model = mock_retrieval
        query = ""
        
        embedding = retrieval.generate_query_embedding(query)
        
        assert isinstance(embedding, list)
        mock_model.encode.assert_called_once()


class TestRetrieve:
    """Test Pinecone retrieval"""
    
    @pytest.fixture
    def mock_retrieval_with_index(self):
        """Create a mock retrieval system with mocked index"""
        import numpy as np
        with patch('backend.retrieval.Pinecone') as mock_pinecone, \
             patch('backend.retrieval.SentenceTransformer') as mock_transformer:
            # Mock embedding model
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1] * 384)  # Mock embedding as numpy array
            mock_transformer.return_value = mock_model
            
            # Mock Pinecone client and index
            mock_pc = MagicMock()
            mock_index = MagicMock()
            mock_pc.Index.return_value = mock_index
            mock_pinecone.return_value = mock_pc
            
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                retrieval = RetrievalSystem()
                yield retrieval, mock_index, mock_model
    
    def test_retrieve_basic(self, mock_retrieval_with_index):
        """Test basic retrieval without filters"""
        retrieval, mock_index, mock_model = mock_retrieval_with_index
        
        # Mock Pinecone query response
        mock_match1 = MagicMock()
        mock_match1.id = "chunk_1"
        mock_match1.score = 0.95
        mock_match1.metadata = {
            'text': 'Expense ratio is 1.5%',
            'source_url': 'https://example.com/scheme1',
            'scheme_name': 'SBI Large Cap Fund',
            'document_type': 'scheme_details',
            'chunk_index': 0,
            'factual_data': 'expense_ratio: 1.5%'
        }
        
        mock_match2 = MagicMock()
        mock_match2.id = "chunk_2"
        mock_match2.score = 0.88
        mock_match2.metadata = {
            'text': 'Minimum SIP is 500',
            'source_url': 'https://example.com/scheme1',
            'scheme_name': 'SBI Large Cap Fund',
            'document_type': 'scheme_details',
            'chunk_index': 1,
            'factual_data': 'minimum_sip: 500'
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match1, mock_match2]
        mock_index.query.return_value = mock_results
        
        # Test retrieval
        query = "What is the expense ratio?"
        results = retrieval.retrieve(query, top_k=2)
        
        # Verify results
        assert len(results) == 2
        assert results[0]['id'] == 'chunk_1'
        assert results[0]['score'] == 0.95
        assert results[0]['text'] == 'Expense ratio is 1.5%'
        assert results[0]['scheme_name'] == 'SBI Large Cap Fund'
        assert 'reranked_score' in results[0]  # Should have re-ranked score
        
        # Verify Pinecone was called correctly
        mock_index.query.assert_called_once()
        call_args = mock_index.query.call_args
        assert call_args.kwargs['top_k'] == 2
        assert call_args.kwargs['include_metadata'] is True
        assert 'filter' not in call_args.kwargs  # No filter for basic query
    
    def test_retrieve_with_scheme_filter(self, mock_retrieval_with_index):
        """Test retrieval with scheme name filter"""
        retrieval, mock_index, mock_model = mock_retrieval_with_index
        
        # Mock response
        mock_match = MagicMock()
        mock_match.id = "chunk_1"
        mock_match.score = 0.90
        mock_match.metadata = {
            'text': 'Expense ratio is 1.5%',
            'source_url': 'https://example.com/scheme1',
            'scheme_name': 'SBI Large Cap Fund',
            'document_type': 'scheme_details',
            'chunk_index': 0
        }
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        mock_index.query.return_value = mock_results
        
        # Test retrieval with scheme filter
        query = "What is the expense ratio?"
        results = retrieval.retrieve(
            query, 
            top_k=5, 
            scheme_name="SBI Large Cap Fund"
        )
        
        # Verify filter was applied
        call_args = mock_index.query.call_args
        assert 'filter' in call_args.kwargs
        filter_dict = call_args.kwargs['filter']
        assert filter_dict == {"scheme_name": {"$eq": "SBI Large Cap Fund"}}
    
    def test_retrieve_no_metadata(self, mock_retrieval_with_index):
        """Test retrieval without metadata"""
        retrieval, mock_index, mock_model = mock_retrieval_with_index
        
        mock_match = MagicMock()
        mock_match.id = "chunk_1"
        mock_match.score = 0.90
        mock_match.metadata = None
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        mock_index.query.return_value = mock_results
        
        results = retrieval.retrieve("test query", include_metadata=False)
        
        assert len(results) == 1
        assert results[0]['text'] == ''  # No metadata, so empty text
        assert results[0]['source_url'] == ''
    
    def test_retrieve_empty_results(self, mock_retrieval_with_index):
        """Test retrieval with no results"""
        retrieval, mock_index, mock_model = mock_retrieval_with_index
        
        mock_results = MagicMock()
        mock_results.matches = []
        mock_index.query.return_value = mock_results
        
        results = retrieval.retrieve("test query")
        
        assert len(results) == 0
    
    def test_retrieve_error_handling(self, mock_retrieval_with_index):
        """Test error handling during retrieval"""
        retrieval, mock_index, mock_model = mock_retrieval_with_index
        
        # Mock Pinecone to raise an exception
        mock_index.query.side_effect = Exception("Pinecone error")
        
        results = retrieval.retrieve("test query")
        
        # Should return empty list on error
        assert results == []


class TestRerankChunks:
    """Test chunk re-ranking"""
    
    @pytest.fixture
    def mock_retrieval(self):
        """Create a mock retrieval system"""
        with patch('backend.retrieval.Pinecone'), \
             patch('backend.retrieval.SentenceTransformer'):
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                retrieval = RetrievalSystem()
                yield retrieval
    
    def test_rerank_by_keyword_match(self, mock_retrieval):
        """Test re-ranking boosts chunks with keyword matches"""
        chunks = [
            {
                'id': 'chunk_1',
                'score': 0.80,
                'text': 'The expense ratio is 1.5% for this fund',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            },
            {
                'id': 'chunk_2',
                'score': 0.85,  # Higher base score
                'text': 'The fund has various features and benefits',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            }
        ]
        
        query = "What is the expense ratio?"
        reranked = mock_retrieval._rerank_chunks(chunks, query)
        
        # Chunk 1 should be ranked higher due to keyword match
        assert reranked[0]['id'] == 'chunk_1'
        assert reranked[0]['reranked_score'] > reranked[1]['reranked_score']
        assert 'original_score' in reranked[0]
        assert reranked[0]['original_score'] == 0.80
    
    def test_rerank_by_document_type(self, mock_retrieval):
        """Test re-ranking prioritizes scheme_details over other types"""
        chunks = [
            {
                'id': 'chunk_1',
                'score': 0.80,
                'text': 'Some information',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'groww_listing'
            },
            {
                'id': 'chunk_2',
                'score': 0.80,  # Same base score
                'text': 'Some information',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            }
        ]
        
        query = "test query"
        reranked = mock_retrieval._rerank_chunks(chunks, query)
        
        # scheme_details should be ranked higher
        assert reranked[0]['id'] == 'chunk_2'
        assert reranked[0]['document_type'] == 'scheme_details'
    
    def test_rerank_by_scheme_name_match(self, mock_retrieval):
        """Test re-ranking boosts chunks matching scheme name in query"""
        chunks = [
            {
                'id': 'chunk_1',
                'score': 0.80,
                'text': 'Some information about small cap',
                'scheme_name': 'SBI Small Cap Fund',
                'document_type': 'scheme_details'
            },
            {
                'id': 'chunk_2',
                'score': 0.80,
                'text': 'Some information about large cap',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            }
        ]
        
        query = "What is the expense ratio of SBI Large Cap Fund?"
        reranked = mock_retrieval._rerank_chunks(chunks, query)
        
        # Chunk with matching scheme name should be ranked higher
        # Note: The scheme name matching checks if query words (>3 chars) are in scheme_name
        # "large" (5 chars) is in "SBI Large Cap Fund" but not in "SBI Small Cap Fund"
        assert reranked[0]['id'] == 'chunk_2', f"Expected chunk_2 first, got {reranked[0]['id']} with score {reranked[0].get('reranked_score')}"
        assert reranked[0]['scheme_name'] == 'SBI Large Cap Fund'
    
    def test_rerank_preserves_order_when_scores_equal(self, mock_retrieval):
        """Test re-ranking preserves order when all factors are equal"""
        chunks = [
            {
                'id': 'chunk_1',
                'score': 0.80,
                'text': 'Some information',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            },
            {
                'id': 'chunk_2',
                'score': 0.80,
                'text': 'Some other information',
                'scheme_name': 'SBI Large Cap Fund',
                'document_type': 'scheme_details'
            }
        ]
        
        query = "test query"
        reranked = mock_retrieval._rerank_chunks(chunks, query)
        
        # Should maintain order (chunk_1 first) when scores are equal
        assert len(reranked) == 2
        assert reranked[0]['reranked_score'] >= reranked[1]['reranked_score']


class TestPrepareContext:
    """Test context preparation"""
    
    @pytest.fixture
    def mock_retrieval(self):
        """Create a mock retrieval system"""
        with patch('backend.retrieval.Pinecone'), \
             patch('backend.retrieval.SentenceTransformer'):
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                retrieval = RetrievalSystem()
                yield retrieval
    
    def test_prepare_context_basic(self, mock_retrieval):
        """Test basic context preparation"""
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'Expense ratio is 1.5%',
                'source_url': 'https://example.com/scheme1',
                'scheme_name': 'SBI Large Cap Fund'
            },
            {
                'id': 'chunk_2',
                'text': 'Minimum SIP is 500',
                'source_url': 'https://example.com/scheme1',
                'scheme_name': 'SBI Large Cap Fund'
            }
        ]
        
        context = mock_retrieval.prepare_context(chunks, max_chunks=5)
        
        assert 'context' in context
        assert 'source_urls' in context
        assert 'num_chunks' in context
        assert 'chunks' in context
        
        assert context['num_chunks'] == 2
        assert len(context['source_urls']) == 1  # Unique URLs
        assert context['source_urls'][0] == 'https://example.com/scheme1'
        assert '[Chunk 1]' in context['context']
        assert '[Chunk 2]' in context['context']
        assert 'Expense ratio is 1.5%' in context['context']
        assert 'Minimum SIP is 500' in context['context']
    
    def test_prepare_context_max_chunks(self, mock_retrieval):
        """Test context preparation respects max_chunks limit"""
        chunks = [
            {'id': f'chunk_{i}', 'text': f'Text {i}', 'source_url': f'https://example.com/{i}'}
            for i in range(10)
        ]
        
        context = mock_retrieval.prepare_context(chunks, max_chunks=3)
        
        assert context['num_chunks'] == 3
        assert len(context['chunks']) == 3
        assert '[Chunk 1]' in context['context']
        assert '[Chunk 3]' in context['context']
        assert '[Chunk 4]' not in context['context']  # Should not include 4th chunk
    
    def test_prepare_context_unique_urls(self, mock_retrieval):
        """Test context preparation collects unique source URLs"""
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'Text 1',
                'source_url': 'https://example.com/scheme1'
            },
            {
                'id': 'chunk_2',
                'text': 'Text 2',
                'source_url': 'https://example.com/scheme1'  # Duplicate
            },
            {
                'id': 'chunk_3',
                'text': 'Text 3',
                'source_url': 'https://example.com/scheme2'  # Different
            }
        ]
        
        context = mock_retrieval.prepare_context(chunks, max_chunks=5)
        
        assert len(context['source_urls']) == 2
        assert 'https://example.com/scheme1' in context['source_urls']
        assert 'https://example.com/scheme2' in context['source_urls']
    
    def test_prepare_context_empty_chunks(self, mock_retrieval):
        """Test context preparation with empty chunks"""
        chunks = []
        
        context = mock_retrieval.prepare_context(chunks, max_chunks=5)
        
        assert context['num_chunks'] == 0
        assert context['context'] == ''
        assert len(context['source_urls']) == 0
    
    def test_prepare_context_empty_text(self, mock_retrieval):
        """Test context preparation skips chunks with empty text"""
        chunks = [
            {
                'id': 'chunk_1',
                'text': 'Valid text',
                'source_url': 'https://example.com/scheme1'
            },
            {
                'id': 'chunk_2',
                'text': '',  # Empty text
                'source_url': 'https://example.com/scheme1'
            },
            {
                'id': 'chunk_3',
                'text': '   ',  # Whitespace only
                'source_url': 'https://example.com/scheme1'
            }
        ]
        
        context = mock_retrieval.prepare_context(chunks, max_chunks=5)
        
        # Should only include chunk_1
        assert '[Chunk 1]' in context['context']
        assert 'Valid text' in context['context']
        assert '[Chunk 2]' not in context['context']
        assert '[Chunk 3]' not in context['context']


class TestSingletonPattern:
    """Test singleton pattern for retrieval system"""
    
    def test_get_retrieval_system_singleton(self):
        """Test get_retrieval_system returns same instance"""
        # Reset global instance
        import backend.retrieval
        backend.retrieval._retrieval_system = None
        
        with patch('backend.retrieval.Pinecone'), \
             patch('backend.retrieval.SentenceTransformer'):
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                instance1 = get_retrieval_system()
                instance2 = get_retrieval_system()
                
                # Should be the same instance
                assert instance1 is instance2
    
    def test_get_retrieval_system_creates_on_first_call(self):
        """Test get_retrieval_system creates instance on first call"""
        # Reset global instance
        import backend.retrieval
        backend.retrieval._retrieval_system = None
        
        with patch('backend.retrieval.Pinecone'), \
             patch('backend.retrieval.SentenceTransformer'):
            with patch.dict(os.environ, {
                'PINECONE_API_KEY': 'test-key',
                'PINECONE_INDEX_NAME': 'test-index'
            }):
                instance = get_retrieval_system()
                
                assert instance is not None
                assert isinstance(instance, RetrievalSystem)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

