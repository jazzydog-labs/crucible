import sys
import types
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from crucible.ai import AIModel


def test_query_uses_openai():
    # Mock the OpenAI client and response
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        # Create mock response structure with usage data
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="pong"))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5)
        
        # Configure mock client
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test the query
        model = AIModel(api_key="test-key")
        result = model.query("ping")
        
        assert result == "pong"
        assert model.total_input_tokens == 10
        assert model.total_output_tokens == 5
        assert model.total_requests == 1
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
        mock_response.usage = Mock(prompt_tokens=20, completion_tokens=10)
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        model = AIModel(api_key="test-key")
        model.query("test prompt", max_tokens=150)
        
        # Check that create was called with max_tokens
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['max_tokens'] == 150


def test_usage_tracking():
    # Test usage tracking functionality
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        # Create mock responses with different token counts
        mock_response1 = Mock()
        mock_response1.choices = [Mock(message=Mock(content="response1"))]
        mock_response1.usage = Mock(prompt_tokens=100, completion_tokens=50)
        
        mock_response2 = Mock()
        mock_response2.choices = [Mock(message=Mock(content="response2"))]
        mock_response2.usage = Mock(prompt_tokens=200, completion_tokens=100)
        
        # Configure mock client
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        mock_openai.return_value = mock_client
        
        # Test the queries
        model = AIModel(api_key="test-key")
        model.query("prompt1")
        model.query("prompt2")
        
        # Check usage stats
        stats = model.get_usage_stats()
        assert stats['total_requests'] == 2
        assert stats['total_input_tokens'] == 300
        assert stats['total_output_tokens'] == 150
        assert stats['total_tokens'] == 450
        assert stats['model'] == 'gpt-4o-mini'
        
        # Check cost calculation (300/1M * 0.15 + 150/1M * 0.60)
        assert stats['input_cost'] == round(300 / 1_000_000 * 0.15, 6)
        assert stats['output_cost'] == round(150 / 1_000_000 * 0.60, 6)
        assert stats['total_cost'] == round(stats['input_cost'] + stats['output_cost'], 6)


def test_reset_usage_stats():
    # Test resetting usage statistics
    with patch('crucible.ai.openai.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="response"))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50)
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        model = AIModel(api_key="test-key")
        model.query("test")
        
        # Verify stats are tracked
        assert model.total_requests == 1
        assert model.total_input_tokens == 100
        assert model.total_output_tokens == 50
        
        # Reset stats
        model.reset_usage_stats()
        
        # Verify stats are reset
        assert model.total_requests == 0
        assert model.total_input_tokens == 0
        assert model.total_output_tokens == 0