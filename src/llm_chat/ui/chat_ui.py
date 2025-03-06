"""Chat interface components for Streamlit UI."""
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any

from ..chat.message import Message, Conversation


def render_message(message: Message) -> None:
    """Render a single chat message.
    
    Args:
        message: Message object to render
    """
    role = message.role
    content = message.content
    timestamp = message.timestamp
    
    if role == "user":
        avatar = "👤"
        role_display = "You"
        message_class = "user"
    else:
        avatar = "🤖"
        role_display = "AI Assistant"
        message_class = "assistant"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message-header">
            <span class="role">{role_display}</span>
            <span class="timestamp">{timestamp}</span>
        </div>
        <div class="message-content">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_conversation(conversation: Conversation) -> None:
    """Render a complete conversation.
    
    Args:
        conversation: Conversation object to render
    """
    for message in conversation.messages:
        render_message(message)


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


def render_conversation_list(conversations: List[Dict[str, Any]], 
                            current_id: str = None,
                            on_load=None,
                            on_rename=None,
                            on_delete=None) -> None:
    """Render the list of saved conversations.
    
    Args:
        conversations: List of conversation metadata
        current_id: ID of the currently active conversation
        on_load: Callback for loading a conversation
        on_rename: Callback for renaming a conversation
        on_delete: Callback for deleting a conversation
    """
    if not conversations:
        st.sidebar.info("No saved conversations yet.")
        return
    
    for conv in conversations:
        # Determine if this is the active conversation
        is_active = current_id == conv["id"]
        
        # Create a container for each conversation
        with st.sidebar.container():
            # Display conversation info
            st.markdown(
                f"""
                <div class="conversation-item {'active' if is_active else ''}">
                    <div class="title">{conv["title"]}</div>
                    <div class="meta">
                        {format_date(conv["updated"])} · {conv["message_count"]} messages
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Buttons for this conversation
            col1, col2, col3 = st.columns([1, 1, 1])
            
            # Load button
            if col1.button("Load", key=f"load_{conv['id']}", use_container_width=True) and not is_active:
                if on_load:
                    on_load(conv["id"])
            
            # Rename button
            if col2.button("Rename", key=f"rename_{conv['id']}", use_container_width=True):
                if on_rename:
                    on_rename(conv["id"], conv["title"])
            
            # Delete button
            if col3.button("Delete", key=f"delete_{conv['id']}", use_container_width=True):
                if on_delete:
                    on_delete(conv["id"])


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