"""Chat history management for storing and retrieving conversation threads."""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """Manages saving, loading, and organizing chat histories."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize the chat history manager.
        
        Args:
            storage_dir: Directory to store chat histories. Defaults to ~/.llm_chat/history
        """
        if storage_dir is None:
            # Default to user's home directory
            home_dir = Path.home()
            storage_dir = home_dir / ".llm_chat" / "history"
        
        self.storage_dir = Path(storage_dir)
        self._ensure_storage_dir()
        
        # Cache for conversation metadata
        self._conversations_cache = None
    
    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)
        
    def get_conversation_path(self, conversation_id: str) -> Path:
        """Get the file path for a conversation."""
        return self.storage_dir / f"{conversation_id}.json"
    
    def save_conversation(self, 
                          messages: List[Dict[str, Any]], 
                          conversation_id: Optional[str] = None,
                          title: Optional[str] = None) -> str:
        """Save a conversation to disk.
        
        Args:
            messages: List of message dictionaries
            conversation_id: ID of the conversation to update, or None to create new
            title: Title of the conversation (optional)
            
        Returns:
            str: The conversation ID
        """
        # If no ID provided, create a new one based on timestamp
        if not conversation_id:
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # If no title provided, generate one from the first few messages
        if not title and messages:
            # Try to extract a meaningful title from the first user message
            first_user_msg = next((m for m in messages if m["role"] == "user"), None)
            if first_user_msg:
                # Take first few words of first user message
                content = first_user_msg["content"]
                title = " ".join(content.split()[:5])
                if len(content.split()) > 5:
                    title += "..."
            else:
                title = f"Conversation {conversation_id}"
        
        # Add metadata
        conversation_data = {
            "id": conversation_id,
            "title": title,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "messages": messages
        }
        
        # Save to file
        file_path = self.get_conversation_path(conversation_id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        # Invalidate cache
        self._conversations_cache = None
        
        logger.info(f"Saved conversation {conversation_id} with {len(messages)} messages")
        return conversation_id
    
    def load_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Load a conversation from disk.
        
        Args:
            conversation_id: ID of the conversation to load
            
        Returns:
            Dict: The conversation data
            
        Raises:
            FileNotFoundError: If the conversation doesn't exist
        """
        file_path = self.get_conversation_path(conversation_id)
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        
        logger.info(f"Loaded conversation {conversation_id} with {len(conversation_data['messages'])} messages")
        return conversation_data
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        file_path = self.get_conversation_path(conversation_id)
        if not file_path.exists():
            return False
        
        os.remove(file_path)
        # Invalidate cache
        self._conversations_cache = None
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True
    
    def list_conversations(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """List all saved conversations with metadata.
        
        Args:
            force_refresh: Force refresh the cache
            
        Returns:
            List of conversation metadata
        """
        # Use cached list unless refresh is forced
        if self._conversations_cache is not None and not force_refresh:
            return self._conversations_cache
        
        conversations = []
        
        # Find all JSON files in the storage directory
        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract metadata, excluding full messages
                conversation_meta = {
                    "id": data.get("id", file_path.stem),
                    "title": data.get("title", "Unnamed Conversation"),
                    "created": data.get("created", ""),
                    "updated": data.get("updated", ""),
                    "message_count": len(data.get("messages", [])),
                }
                conversations.append(conversation_meta)
            except Exception as e:
                logger.error(f"Error loading conversation from {file_path}: {e}")
        
        # Sort by creation date, newest first
        conversations.sort(key=lambda x: x["created"], reverse=True)
        
        # Update cache
        self._conversations_cache = conversations
        
        return conversations
    
    def rename_conversation(self, conversation_id: str, new_title: str) -> bool:
        """Rename a conversation.
        
        Args:
            conversation_id: ID of the conversation to rename
            new_title: New title for the conversation
            
        Returns:
            bool: True if renamed, False if not found
        """
        try:
            conversation = self.load_conversation(conversation_id)
            conversation["title"] = new_title
            conversation["updated"] = datetime.now().isoformat()
            
            file_path = self.get_conversation_path(conversation_id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            
            # Invalidate cache
            self._conversations_cache = None
            
            logger.info(f"Renamed conversation {conversation_id} to '{new_title}'")
            return True
        except FileNotFoundError:
            return False