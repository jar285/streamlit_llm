"""Chat interface components for Streamlit UI."""
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..chat.message import Message, Conversation
from ..chat.system_prompts import AssistantType


def render_message(message: Message, assistant_type: Optional[AssistantType] = None) -> None:
    """Render a single chat message.
    
    Args:
        message: Message object to render
        assistant_type: Current assistant type (optional)
    """
    role = message.role
    content = message.content
    timestamp = message.timestamp
    
    if role == "user":
        avatar = "👤"
        role_display = "You"
        message_class = "user"
    elif role == "system":
        avatar = "⚙️"
        role_display = "System"
        message_class = "system"
    else:
        avatar = assistant_type.icon if assistant_type else "🤖"
        role_display = assistant_type.name if assistant_type else "AI Assistant"
        message_class = "assistant"
    
    # Add assistant type badge for assistant messages
    assistant_badge = ""
    if role == "assistant" and assistant_type:
        assistant_badge = f"""
        <span class="message-assistant-type">
            {assistant_type.icon} {assistant_type.name}
        </span>
        """
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-header">
            <span class="role">{role_display} {assistant_badge}</span>
            <span class="timestamp">{timestamp}</span>
        </div>
        <div class="message-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_conversation(conversation: Conversation, assistant_type: Optional[AssistantType] = None) -> None:
    """Render a complete conversation.
    
    Args:
        conversation: Conversation object to render
        assistant_type: Current assistant type (optional)
    """
    for message in conversation.messages:
        render_message(message, assistant_type)


def render_header(title: str, version: str) -> None:
    """Render the application header.
    
    Args:
        title: Application title
        version: Application version
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <div class="version-tag">v{version}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_input() -> str:
    """Render the chat input box and return user input if any.
    
    Returns:
        User input text or empty string
    """
    return st.chat_input("Type your message here...") or ""


def format_date(date_str: str) -> str:
    """Format ISO date string to human-readable format.
    
    Args:
        date_str: ISO format date string
        
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%b %d, %Y %H:%M")
    except:
        return date_str