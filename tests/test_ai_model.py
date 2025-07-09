import sys
import types
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from crucible.ai import AIModel


def test_query_uses_openai():
    # Mock the OpenAI client and response
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        # Create mock response structure
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="pong"))]
        
        # Configure mock client
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test the query
        model = AIModel(api_key="test-key", model="test")
        result = model.query("ping")
        
        assert result == "pong"
        mock_client.chat.completions.create.assert_called_once()


def test_missing_api_key():
    # Test that AIModel works with missing API key
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        # Mock client creation to not fail
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Should work with None API key (will use env or file)
        model = AIModel(api_key=None)
        assert hasattr(model, 'client')
        
        # The OpenAI client should have been created
        mock_openai.assert_called_once()


def test_query_with_max_tokens():
    # Test that max_tokens is properly set
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="test response"))]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        model = AIModel(api_key="test-key")
        model.query("test prompt")
        
        # Check that create was called with max_tokens
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['max_tokens'] == 200  # Limited for demo