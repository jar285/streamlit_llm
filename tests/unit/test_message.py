# tests/test_message.py
import pytest
from datetime import datetime

from src.llm_chat.chat.message import Message, Conversation


def test_message_creation():
    """Test creating a message."""
    # Arrange & Act
    message = Message("user", "Hello, world!")
    
    # Assert
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert message.timestamp is not None


def test_message_to_dict():
    """Test converting a message to dictionary."""
    # Arrange
    message = Message("assistant", "Test content", timestamp="12:34")
    
    # Act
    result = message.to_dict()
    
    # Assert
    assert result["role"] == "assistant"
    assert result["content"] == "Test content"
    assert result["timestamp"] == "12:34"


def test_message_from_dict():
    """Test creating a message from dictionary."""
    # Arrange
    data = {
        "role": "system",
        "content": "System message",
        "timestamp": "10:00",
        "extra_field": "value"
    }
    
    # Act
    message = Message.from_dict(data)
    
    # Assert
    assert message.role == "system"
    assert message.content == "System message"
    assert message.timestamp == "10:00"
    assert message.metadata.get("extra_field") == "value"


def test_conversation_creation():
    """Test creating a conversation."""
    # Act
    conversation = Conversation(id="test-id", title="Test Title")
    
    # Assert
    assert conversation.id == "test-id"
    assert conversation.title == "Test Title"
    assert len(conversation.messages) == 0


def test_conversation_add_message():
    """Test adding messages to a conversation."""
    # Arrange
    conversation = Conversation(id="test-id")
    message = Message.user_message("Test message")
    
    # Act
    conversation.add_message(message)
    
    # Assert
    assert len(conversation.messages) == 1
    assert conversation.messages[0].content == "Test message"


def test_conversation_to_dict():
    """Test converting a conversation to dictionary."""
    # Arrange
    conversation = Conversation(id="test-id", title="Test Title")
    conversation.add_message(Message.user_message("Hello"))
    conversation.add_message(Message.assistant_message("Hi there"))
    
    # Act
    result = conversation.to_dict()
    
    # Assert
    assert result["id"] == "test-id"
    assert result["title"] == "Test Title"
    assert len(result["messages"]) == 2
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][1]["role"] == "assistant"


def test_conversation_api_messages():
    """Test getting API-formatted messages."""
    # Arrange
    conversation = Conversation()
    conversation.add_message(Message.user_message("Hello"))
    conversation.add_message(Message.system_message("System message"))
    
    # Act
    api_messages = conversation.get_api_messages()
    
    # Assert
    assert len(api_messages) == 2
    assert "timestamp" not in api_messages[0]
    assert api_messages[0]["role"] == "user"
    assert api_messages[0]["content"] == "Hello"