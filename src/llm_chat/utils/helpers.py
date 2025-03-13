"""Utility functions for the application."""
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import os
import json

logger = logging.getLogger(__name__)


def format_timestamp(timestamp: Optional[str] = None) -> str:
    """Format timestamp for display.
    
    Args:
        timestamp: ISO format timestamp string or None for current time
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        dt = datetime.now()
    else:
        try:
            dt = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            # Invalid timestamp, use current time
            dt = datetime.now()
    
    return dt.strftime("%H:%M:%S")


def format_date_for_display(date_str: str) -> str:
    """Format ISO date string to human-readable format.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%b %d, %Y %H:%M")
    except (ValueError, TypeError):
        return date_str


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string, returning default on error.
    
    Args:
        json_str: JSON string to parse
        default: Default value to return on error
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default or {}


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if text and len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def sanitize_html_content(content: str) -> str:
    """Sanitize content to ensure it's not treated as HTML.
    
    Args:
        content: Text content to sanitize
        
    Returns:
        Sanitized content
    """
    import html
    return html.escape(content)


def get_conversation_title_from_messages(messages: List[Dict[str, Any]]) -> str:
    """Generate a title from the first few messages.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Generated title
    """
    # Try to extract a meaningful title from the first user message
    first_user_msg = next((m for m in messages if m.get("role") == "user"), None)
    
    if first_user_msg and first_user_msg.get("content"):
        content = first_user_msg["content"]
        title = " ".join(content.split()[:5])
        if len(content.split()) > 5:
            title += "..."
        return title
    
    # If no suitable message, generate a timestamp-based title
    return f"Conversation {datetime.now().strftime('%b %d, %H:%M')}"