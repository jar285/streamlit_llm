# tests/test_chat_history.py
import pytest
import tempfile
import os
import json
from datetime import datetime
from pathlib import Path

from src.llm_chat.chat.history import ChatHistoryManager


@pytest.fixture
def temp_history_dir():
    """Create a temporary directory for chat history files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_init_creates_directory(temp_history_dir):
    """Test that initializing creates the storage directory."""
    # Arrange
    storage_dir = os.path.join(temp_history_dir, "test_history")
    
    # Act
    manager = ChatHistoryManager(storage_dir=storage_dir)
    
    # Assert
    assert os.path.exists(storage_dir)


def test_save_and_load_conversation(temp_history_dir):
    """Test that conversations can be saved and loaded."""
    # Arrange
    manager = ChatHistoryManager(storage_dir=temp_history_dir)
    
    test_messages = [
        {"role": "user", "content": "Hello", "timestamp": "12:00"},
        {"role": "assistant", "content": "Hi there!", "timestamp": "12:01"}
    ]
    
    # Act
    conv_id = manager.save_conversation(messages=test_messages, title="Test Conversation")
    loaded_conv = manager.load_conversation(conv_id)
    
    # Assert
    assert loaded_conv["title"] == "Test Conversation"
    assert len(loaded_conv["messages"]) == 2
    assert loaded_conv["messages"][0]["content"] == "Hello"
    assert loaded_conv["messages"][1]["content"] == "Hi there!"


def test_list_conversations(temp_history_dir):
    """Test listing conversations."""
    # Arrange
    manager = ChatHistoryManager(storage_dir=temp_history_dir)
    
    # Create a few test conversations with unique IDs
    test_messages = [{"role": "user", "content": "Hello"}]
    conv_id1 = manager.save_conversation(
        messages=test_messages, 
        title="Conversation 1",
        conversation_id="test_conv_1"  # Explicitly set ID
    )
    
    test_messages2 = [{"role": "user", "content": "Another test"}]
    conv_id2 = manager.save_conversation(
        messages=test_messages2, 
        title="Conversation 2",
        conversation_id="test_conv_2"  # Explicitly set ID
    )
    
    # Act
    conversations = manager.list_conversations()
    
    # Assert
    assert len(conversations) == 2
    # Or if the behavior is to only keep the newest:
    # assert len(conversations) == 1
    # assert conversations[0]["title"] == "Conversation 2"
    
    # Check that conversations are sorted by date (newest first)
    assert conversations[0]["id"] == conv_id2
    assert conversations[1]["id"] == conv_id1
    
    # Check metadata
    assert conversations[0]["title"] == "Conversation 2"
    assert conversations[1]["title"] == "Conversation 1"
    assert conversations[0]["message_count"] == 1
    assert conversations[1]["message_count"] == 1


def test_delete_conversation(temp_history_dir):
    """Test deleting a conversation."""
    # Arrange
    manager = ChatHistoryManager(storage_dir=temp_history_dir)
    
    test_messages = [{"role": "user", "content": "Hello"}]
    conv_id = manager.save_conversation(messages=test_messages, title="Test Conversation")
    
    # Act & Assert - Should return True for successful deletion
    assert manager.delete_conversation(conv_id) is True
    
    # Verify the conversation is gone
    with pytest.raises(FileNotFoundError):
        manager.load_conversation(conv_id)
    
    # Act & Assert - Should return False for nonexistent conversation
    assert manager.delete_conversation("nonexistent-id") is False


def test_rename_conversation(temp_history_dir):
    """Test renaming a conversation."""
    # Arrange
    manager = ChatHistoryManager(storage_dir=temp_history_dir)
    
    test_messages = [{"role": "user", "content": "Hello"}]
    conv_id = manager.save_conversation(messages=test_messages, title="Old Title")
    
    # Act
    result = manager.rename_conversation(conv_id, "New Title")
    loaded_conv = manager.load_conversation(conv_id)
    
    # Assert
    assert result is True
    assert loaded_conv["title"] == "New Title"


def test_auto_generate_title(temp_history_dir):
    """Test automatic title generation from messages."""
    # Arrange
    manager = ChatHistoryManager(storage_dir=temp_history_dir)
    
    test_messages = [
        {"role": "user", "content": "This should be the title of my conversation"}
    ]
    
    # Act
    conv_id = manager.save_conversation(messages=test_messages)
    loaded_conv = manager.load_conversation(conv_id)
    
    # Assert
    assert "This should be the title" in loaded_conv["title"]