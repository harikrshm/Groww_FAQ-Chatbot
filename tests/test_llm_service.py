"""
Comprehensive test suite for LLM service
Tests Gemini integration, response generation, validation, and fallback handling
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from typing import Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_service import (
    LLMService,
    get_llm_service,
    _llm_service
)
from backend.validators import ValidationResult


class TestLLMServiceInitialization:
    """Test LLMService initialization"""
    
    @patch('backend.llm_service.genai')
    def test_initialization_success(self, mock_genai):
        """Test successful initialization"""
        # Mock genai module
        mock_genai.configure = MagicMock()
        
        # Mock API key validation
        mock_test_model = MagicMock()
        mock_test_response = MagicMock()
        mock_test_response.text = "test"
        mock_test_model.generate_content.return_value = mock_test_response
        mock_genai.GenerativeModel.return_value = mock_test_model
        
        # Patch module-level variables
        import backend.llm_service
        original_key = backend.llm_service.GEMINI_API_KEY
        original_model = backend.llm_service.GEMINI_MODEL
        
        try:
            backend.llm_service.GEMINI_API_KEY = 'test-api-key'
            backend.llm_service.GEMINI_MODEL = 'gemini-2.5-flash'
            
            # Initialize
            service = LLMService()
            
            # Verify initialization
            assert service.api_key == 'test-api-key'
            assert service.model_name == 'models/gemini-2.5-flash'
            assert service.model == mock_test_model
            mock_genai.configure.assert_called_once_with(api_key='test-api-key')
        finally:
            # Restore original values
            backend.llm_service.GEMINI_API_KEY = original_key
            backend.llm_service.GEMINI_MODEL = original_model
    
    @patch('backend.llm_service.genai', MagicMock())
    def test_initialization_missing_api_key(self):
        """Test initialization fails without API key"""
        # Patch module-level variable to None
        import backend.llm_service
        original_key = backend.llm_service.GEMINI_API_KEY
        
        try:
            backend.llm_service.GEMINI_API_KEY = None
            
            with pytest.raises(ValueError, match="GEMINI_API_KEY not found"):
                LLMService()
        finally:
            # Restore original value
            backend.llm_service.GEMINI_API_KEY = original_key
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
    def test_initialization_missing_genai_package(self):
        """Test initialization fails when genai package not installed"""
        with patch('backend.llm_service.genai', None):
            with pytest.raises(ImportError, match="google-generativeai package not installed"):
                LLMService()
    
    @patch.dict(os.environ, {
        'GEMINI_API_KEY': 'test-key',
        'GEMINI_MODEL': 'gemini-1.5-flash'
    })
    @patch('backend.llm_service.genai')
    def test_initialization_default_model(self, mock_genai):
        """Test default model when not provided"""
        mock_genai.configure = MagicMock()
        mock_model = MagicMock()
        mock_test_model = MagicMock()
        mock_test_response = MagicMock()
        mock_test_response.text = "test"
        mock_test_model.generate_content.return_value = mock_test_response
        mock_genai.GenerativeModel.return_value = mock_test_model
        
        # Remove GEMINI_MODEL from env
        if 'GEMINI_MODEL' in os.environ:
            del os.environ['GEMINI_MODEL']
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}, clear=False):
            service = LLMService()
            # Should use default from code
            assert service.model_name is not None


class TestCheckGeminiConnection:
    """Test Gemini API connection checking"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service"""
        with patch('backend.llm_service.genai') as mock_genai:
            mock_genai.configure = MagicMock()
            mock_test_model = MagicMock()
            mock_test_response = MagicMock()
            mock_test_response.text = "test"
            mock_test_model.generate_content.return_value = mock_test_response
            mock_genai.GenerativeModel.return_value = mock_test_model
            
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                service = LLMService()
                yield service, mock_genai
    
    def test_check_connection_success(self, mock_service):
        """Test successful connection check"""
        service, mock_genai = mock_service
        result = service._check_gemini_connection()
        assert result is True
    
    def test_check_connection_failure(self, mock_service):
        """Test connection check failure"""
        service, mock_genai = mock_service
        # Mock generate_content to raise exception
        mock_test_model = mock_genai.GenerativeModel.return_value
        mock_test_model.generate_content.side_effect = Exception("API error")
        
        result = service._check_gemini_connection()
        assert result is False


class TestGenerateResponse:
    """Test response generation"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service"""
        with patch('backend.llm_service.genai') as mock_genai:
            mock_genai.configure = MagicMock()
            mock_model = MagicMock()
            mock_test_model = MagicMock()
            mock_test_response = MagicMock()
            mock_test_response.text = "test"
            mock_test_model.generate_content.return_value = mock_test_response
            mock_genai.GenerativeModel.return_value = mock_test_model
            
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                service = LLMService()
                service.model = mock_model
                yield service, mock_model
    
    def test_generate_response_success(self, mock_service):
        """Test successful response generation"""
        service, mock_model = mock_service
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "The expense ratio is 1.5%."
        mock_model.generate_content.return_value = mock_response
        
        response = service.generate_response(
            system_prompt="You are a factual assistant.",
            user_prompt="What is the expense ratio?"
        )
        
        assert response == "The expense ratio is 1.5%."
        mock_model.generate_content.assert_called_once()
    
    def test_generate_response_none_on_failure(self, mock_service):
        """Test response generation returns None on failure"""
        service, mock_model = mock_service
        
        # Mock exception
        mock_model.generate_content.side_effect = Exception("API error")
        
        response = service.generate_response(
            system_prompt="You are a factual assistant.",
            user_prompt="What is the expense ratio?"
        )
        
        assert response is None
    
    def test_generate_response_safety_block(self, mock_service):
        """Test response generation handles safety blocks"""
        service, mock_model = mock_service
        
        # Mock safety block response
        mock_response = MagicMock()
        # Simulate ValueError when accessing .text (safety block)
        type(mock_response).text = PropertyMock(side_effect=ValueError("finish_reason: 2"))
        
        # Mock candidate with finish_reason
        mock_candidate = MagicMock()
        mock_candidate.finish_reason = 2  # SAFETY
        mock_candidate.content = None
        mock_candidate.safety_ratings = None
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        response = service.generate_response(
            system_prompt="You are a factual assistant.",
            user_prompt="What is the expense ratio?"
        )
        
        assert response is None
    
    def test_generate_response_custom_params(self, mock_service):
        """Test response generation with custom parameters"""
        service, mock_model = mock_service
        
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        
        response = service.generate_response(
            system_prompt="System",
            user_prompt="User",
            temperature=0.5,
            top_p=0.8,
            max_output_tokens=200
        )
        
        assert response == "Response"
        call_args = mock_model.generate_content.call_args
        gen_config = call_args.kwargs['generation_config']
        assert gen_config['temperature'] == 0.5
        assert gen_config['top_p'] == 0.8
        assert gen_config['max_output_tokens'] == 200


class TestFormatUserPrompt:
    """Test user prompt formatting"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service"""
        with patch('backend.llm_service.genai'):
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                service = LLMService()
                yield service
    
    def test_format_user_prompt_basic(self, mock_service):
        """Test basic user prompt formatting"""
        context = "The expense ratio is 1.5%."
        query = "What is the expense ratio?"
        
        prompt = mock_service.format_user_prompt(context, query)
        
        assert "Context:" in prompt
        assert context in prompt
        assert "User Query:" in prompt
        assert query in prompt
        assert "Based on the context" in prompt


class TestGenerateValidatedResponse:
    """Test validated response generation"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service"""
        with patch('backend.llm_service.genai') as mock_genai:
            mock_genai.configure = MagicMock()
            mock_model = MagicMock()
            mock_test_model = MagicMock()
            mock_test_response = MagicMock()
            mock_test_response.text = "test"
            mock_test_model.generate_content.return_value = mock_test_response
            mock_genai.GenerativeModel.return_value = mock_test_model
            
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                service = LLMService()
                service.model = mock_model
                yield service, mock_model
    
    @patch('backend.llm_service.validate_and_fix_response')
    def test_generate_validated_response_success(self, mock_validate, mock_service):
        """Test successful validated response generation"""
        service, mock_model = mock_service
        
        # Mock successful generation
        mock_response = MagicMock()
        mock_response.text = "The expense ratio is 1.5%. Last updated from sources."
        mock_model.generate_content.return_value = mock_response
        
        # Mock validation success
        validation_result = ValidationResult()
        validation_result.is_valid = True
        mock_validate.return_value = ("The expense ratio is 1.5%. Last updated from sources.", validation_result)
        
        response, result = service.generate_validated_response(
            system_prompt="System",
            user_prompt="User",
            query="What is the expense ratio?"
        )
        
        assert response == "The expense ratio is 1.5%. Last updated from sources."
        assert result.is_valid is True
        mock_validate.assert_called_once()
    
    @patch('backend.llm_service.validate_and_fix_response')
    def test_generate_validated_response_retry(self, mock_validate, mock_service):
        """Test validated response generation with retry"""
        service, mock_model = mock_service
        
        # Mock first attempt failure, second success
        mock_response1 = MagicMock()
        mock_response1.text = "Response without citation"
        mock_response2 = MagicMock()
        mock_response2.text = "Response with citation. Last updated from sources."
        mock_model.generate_content.side_effect = [mock_response1, mock_response2]
        
        # Mock validation: first fails, second succeeds
        result1 = ValidationResult()
        result1.is_valid = False
        result1.add_error("Response missing source citation")
        
        result2 = ValidationResult()
        result2.is_valid = True
        
        mock_validate.side_effect = [
            ("Response without citation", result1),
            ("Response with citation. Last updated from sources.", result2)
        ]
        
        response, result = service.generate_validated_response(
            system_prompt="System",
            user_prompt="User",
            query="What is the expense ratio?",
            max_retries=2
        )
        
        assert result.is_valid is True
        assert mock_validate.call_count == 2
    
    @patch('backend.llm_service.validate_and_fix_response')
    def test_generate_validated_response_fallback(self, mock_validate, mock_service):
        """Test validated response generation uses fallback when all retries fail"""
        service, mock_model = mock_service
        
        # Mock generation failure
        mock_model.generate_content.return_value = None
        
        response, result = service.generate_validated_response(
            system_prompt="System",
            user_prompt="User",
            query="What is the expense ratio?",
            max_retries=2,
            use_fallback=True
        )
        
        assert "I apologize" in response
        assert "Last updated from sources" in response
        assert len(result.warnings) > 0
        assert any("fallback" in warning.lower() for warning in result.warnings)
    
    @patch('backend.llm_service.validate_and_fix_response')
    def test_generate_validated_response_no_fallback(self, mock_validate, mock_service):
        """Test validated response generation without fallback"""
        service, mock_model = mock_service
        
        # Mock generation failure
        mock_model.generate_content.return_value = None
        
        response, result = service.generate_validated_response(
            system_prompt="System",
            user_prompt="User",
            query="What is the expense ratio?",
            max_retries=1,
            use_fallback=False
        )
        
        assert response == ""
        assert len(result.errors) > 0


class TestGenerateFallbackResponse:
    """Test fallback response generation"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service"""
        with patch('backend.llm_service.genai'):
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                service = LLMService()
                yield service
    
    def test_generate_fallback_with_scheme(self, mock_service):
        """Test fallback response with scheme name"""
        response = mock_service.generate_fallback_response(
            query="What is the expense ratio?",
            scheme_name="SBI Large Cap Fund"
        )
        
        assert "SBI Large Cap Fund" in response
        assert "I apologize" in response
        assert "Last updated from sources" in response
    
    def test_generate_fallback_without_scheme(self, mock_service):
        """Test fallback response without scheme name"""
        response = mock_service.generate_fallback_response(
            query="What is the expense ratio?"
        )
        
        assert "I apologize" in response
        assert "Last updated from sources" in response
        assert "SBI Mutual Fund" in response
    
    def test_generate_fallback_with_source_url(self, mock_service):
        """Test fallback response with source URL"""
        response = mock_service.generate_fallback_response(
            query="What is the expense ratio?",
            source_url="https://example.com/scheme"
        )
        
        assert "Last updated from sources" in response


class TestSingletonPattern:
    """Test singleton pattern for LLM service"""
    
    def test_get_llm_service_singleton(self):
        """Test get_llm_service returns same instance"""
        # Reset global instance
        import backend.llm_service
        backend.llm_service._llm_service = None
        
        with patch('backend.llm_service.genai'):
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                instance1 = get_llm_service()
                instance2 = get_llm_service()
                
                # Should be the same instance
                assert instance1 is instance2
    
    def test_get_llm_service_creates_on_first_call(self):
        """Test get_llm_service creates instance on first call"""
        # Reset global instance
        import backend.llm_service
        backend.llm_service._llm_service = None
        
        with patch('backend.llm_service.genai'):
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test-key',
                'GEMINI_MODEL': 'gemini-2.5-flash'
            }):
                instance = get_llm_service()
                
                assert instance is not None
                assert isinstance(instance, LLMService)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

