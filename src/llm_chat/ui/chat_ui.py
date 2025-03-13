"""Chat interface components for Streamlit UI."""
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..chat.message import Message, Conversation
from ..chat.system_prompts import AssistantType


# Update the render_message function in src/llm_chat/ui/chat_ui.py
def render_message(message: Message, assistant_type: Optional[AssistantType] = None) -> None:
    """Render a single chat message using Streamlit native components."""
    role = message.role
    content = message.content
    timestamp = message.timestamp
    
    # Define styles based on the role
    if role == "user":
        box_color = "#e3f2fd"
        avatar = "👤"
        name = "You"
    elif role == "system":
        box_color = "#f3e5f5"
        avatar = "⚙️"
        name = "System"
    else:
        box_color = "#f5f5f5"
        avatar = assistant_type.icon if assistant_type else "🤖"
        name = assistant_type.name if assistant_type else "AI Assistant"
    
    # Create a container with custom CSS
    message_container = st.container()
    
    with message_container:
        # Use columns for layout
        col1, col2 = st.columns([1, 20])
        
        with col1:
            st.markdown(f"<div style='font-size:1.5rem; text-align:center;'>{avatar}</div>", unsafe_allow_html=True)
        
        with col2:
            # Message header with name and timestamp
            st.markdown(f"<div style='display:flex; justify-content:space-between;'><strong>{name}</strong><span style='color:#666; font-size:0.8rem;'>{timestamp}</span></div>", unsafe_allow_html=True)
            
            # Message content in a colored box
            st.markdown(f"""
            <div style='background-color:{box_color}; padding:10px; border-radius:10px; margin-top:5px; margin-bottom:15px;'>
                {content}
            </div>
            """, unsafe_allow_html=True)
        
        # Add some space after each message
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)


def render_conversation(conversation: Conversation, assistant_type: Optional[AssistantType] = None) -> None:
    """Render a complete conversation.
    
    Args:
        conversation: Conversation object to render
        assistant_type: Current assistant type (optional)
    """
    for message in conversation.messages:
        render_message(message, assistant_type)


def render_header(title: str, version: str) -> None:
    """Render an improved application header."""
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <div class="version-tag">v{version}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chat_input() -> str:
    """Render the chat input box and return user input if any."""
    # Add some vertical space before the input
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Add a fixed position container for the chat input
    st.markdown("""
    <style>
    .chat-input-fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: white;
        z-index: 1000;
        border-top: 1px solid #f0f0f0;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Return the Streamlit chat input
    return st.chat_input("Send a message...")




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