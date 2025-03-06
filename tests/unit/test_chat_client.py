"""Tests for the OpenAI chat client."""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path if needed
src_dir = Path(__file__).parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

from src.llm_chat.chat.client import ChatClient


def test_client_initialization_without_api_key():
    """Test client initialization without an API key."""
    # Act
    with patch.dict('os.environ', {}, clear=True):
        client = ChatClient()
    
    # Assert
    assert client.api_key is None
    assert client.client is None
    assert client.is_available() is False


# Fix: Patch the correct import path in your module
@patch('src.llm_chat.chat.client.OpenAI')
def test_client_initialization(mock_openai):
    """Test client initialization with an API key."""
    # Arrange & Act
    client = ChatClient(api_key="test_key")
    
    # Assert
    assert client.api_key == "test_key"
    mock_openai.assert_called_once()


@patch('src.llm_chat.chat.client.OpenAI')
def test_get_completion(mock_openai):
    """Test getting a completion from the API."""
    # Arrange
    mock_instance = MagicMock()
    mock_openai.return_value = mock_instance
    
    # Mock the response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    
    # Set up the chain of mocks
    mock_instance.chat.completions.create.return_value = mock_response
    
    # Create the client with the mocked OpenAI
    client = ChatClient(api_key="test_key")
    
    # Act
    response = client.get_completion(
        [{"role": "user", "content": "Hello"}],
        model="gpt-3.5-turbo"
    )
    
    # Assert
    assert response == "Test response"
    mock_instance.chat.completions.create.assert_called_once()


def test_get_completion_no_client():
    """Test getting a completion without an initialized client."""
    # Arrange
    client = ChatClient(api_key=None)
    
    # Act
    response = client.get_completion([{"role": "user", "content": "Hello"}])
    
    # Assert
    assert isinstance(response, str)
    assert len(response) > 0  # Ensure we get some response
    # You could also check for specific fallback behavior if desired
