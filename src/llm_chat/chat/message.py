"""Message handling for chat interactions."""
from datetime import datetime
from typing import Dict, Any, List, Optional


class Message:
    """Represents a chat message with role, content and metadata."""
    
    def __init__(self, 
                 role: str, 
                 content: str, 
                 timestamp: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize a chat message.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Text content of the message
            timestamp: Timestamp of the message (defaults to now)
            metadata: Additional metadata for the message
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            **self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create a message from dictionary representation."""
        role = data.get("role", "")
        content = data.get("content", "")
        timestamp = data.get("timestamp", None)
        
        # Extract metadata (all fields except standard ones)
        standard_fields = {"role", "content", "timestamp"}
        metadata = {k: v for k, v in data.items() if k not in standard_fields}
        
        return cls(role, content, timestamp, metadata)
    
    @classmethod
    def user_message(cls, content: str) -> 'Message':
        """Create a user message."""
        # Ensure content is treated as plain text, not HTML
        return cls("user", content)

    @classmethod
    def assistant_message(cls, content: str) -> 'Message':
        """Create an assistant message."""
        # Ensure content is treated as plain text, not HTML
        return cls("assistant", content)
    
    @classmethod
    def system_message(cls, content: str) -> 'Message':
        """Create a system message."""
        return cls("system", content)


class Conversation:
    """Represents a chat conversation with multiple messages."""
    
    def __init__(self, 
                 messages: Optional[List[Message]] = None,
                 id: Optional[str] = None,
                 title: Optional[str] = None,
                 system_prompt: Optional[str] = None):
        """Initialize a conversation.
        
        Args:
            messages: List of messages in the conversation
            id: Unique identifier for the conversation
            title: Title of the conversation
            system_prompt: System prompt for the conversation
        """
        self.messages = messages or []
        self.id = id
        self.title = title
        self.system_prompt = system_prompt
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now().isoformat()
    
    def set_system_prompt(self, system_prompt: str) -> None:
        """Set the system prompt for this conversation.
        
        Args:
            system_prompt: The system prompt text
        """
        self.system_prompt = system_prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "system_prompt": self.system_prompt,
            "created": self.created_at,
            "updated": self.updated_at,
            "messages": [m.to_dict() for m in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create a conversation from dictionary representation."""
        id = data.get("id")
        title = data.get("title")
        system_prompt = data.get("system_prompt")
        
        # Create message objects
        message_dicts = data.get("messages", [])
        messages = [Message.from_dict(m) for m in message_dicts]
        
        # Create conversation
        conversation = cls(messages, id, title, system_prompt)
        
        # Set timestamps if available
        conversation.created_at = data.get("created", conversation.created_at)
        conversation.updated_at = data.get("updated", conversation.updated_at)
        
        return conversation
    
    def get_api_messages(self) -> List[Dict[str, str]]:
        """Get messages in format suitable for API calls (without metadata).
        
        This includes the system prompt as a system message if present.
        """
        # Start with system prompt if available
        api_messages = []
        if self.system_prompt:
            api_messages.append({"role": "system", "content": self.system_prompt})
        
        # Add conversation messages
        api_messages.extend([{"role": m.role, "content": m.content} for m in self.messages])
        
        return api_messages
    
    def get_last_user_message(self) -> Optional[Message]:
        """Get the most recent user message."""
        for message in reversed(self.messages):
            if message.role == "user":
                return message
        return None
    
    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)