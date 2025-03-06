"""Streamlit application configuration and state management."""
import streamlit as st
import logging
from datetime import datetime
import os
from typing import Dict, Any, List, Optional

# Import from your modules
from .chat.client import ChatClient
from .chat.history import ChatHistoryManager
from .chat.message import Message, Conversation
from .config.settings import get_app_config, get_default_settings
from .ui.styles import apply_theme
from .ui.chat_ui import render_message, render_header, render_chat_input
from .ui.sidebar import render_settings_sidebar, render_about_sidebar, render_conversation_sidebar

# Set up logging
logger = logging.getLogger(__name__)


def setup_page_config():
    """Configure the Streamlit page."""
    config = get_app_config()
    
    st.set_page_config(
        page_title=config["app_name"],
        page_icon=config["app_icon"],
        layout="wide",
    )


def init_session_state():
    """Initialize session state variables."""
    # Initialize conversation if not exists
    if "conversation" not in st.session_state:
        st.session_state.conversation = Conversation()
        # Add a welcome message
        welcome_msg = Message.assistant_message(
            "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?"
        )
        st.session_state.conversation.add_message(welcome_msg)
    
    # Initialize history manager if not exists
    if "history_manager" not in st.session_state:
        st.session_state.history_manager = ChatHistoryManager()
    
    # Initialize settings if not exists
    if "settings" not in st.session_state:
        st.session_state.settings = get_default_settings()
    
    # UI state
    if "show_rename_ui" not in st.session_state:
        st.session_state.show_rename_ui = False
    
    if "new_title" not in st.session_state:
        st.session_state.new_title = ""
    
    # Initialize API client
    if "api_client" not in st.session_state:
        config = get_app_config()
        st.session_state.api_client = ChatClient(api_key=config["api_key"])


def create_new_conversation():
    """Create a new conversation."""
    st.session_state.conversation = Conversation()
    welcome_msg = Message.assistant_message(
        "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?"
    )
    st.session_state.conversation.add_message(welcome_msg)
    st.rerun()


def load_conversation(conversation_id: str):
    """Load a conversation from history.
    
    Args:
        conversation_id: ID of the conversation to load
    """
    try:
        history_manager = st.session_state.history_manager
        conversation_data = history_manager.load_conversation(conversation_id)
        st.session_state.conversation = Conversation.from_dict(conversation_data)
        st.rerun()
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")


def rename_conversation(conversation_id: str, new_title: str):
    """Rename a conversation in history."""
    if not new_title.strip():
        st.error("Title cannot be empty")
        return
        
    history_manager = st.session_state.history_manager
    success = history_manager.rename_conversation(conversation_id, new_title)
    
    if success:
        st.toast(f"Renamed conversation to '{new_title}'")
    else:
        st.error("Failed to rename conversation")
        
    # Clear rename UI state
    st.session_state.show_rename_ui = False
    
    # Rerun to update UI
    st.rerun()



def delete_conversation(conversation_id: str):
    """Delete a conversation from history.
    
    Args:
        conversation_id: ID of the conversation to delete
    """
    history_manager = st.session_state.history_manager
    # Check if deleting current conversation
    current_id = getattr(st.session_state.conversation, "id", None)
    
    if history_manager.delete_conversation(conversation_id):
        # If deleting current conversation, create new one
        if conversation_id == current_id:
            create_new_conversation()
        else:
            st.rerun()


def save_current_conversation():
    """Save the current conversation to history."""
    history_manager = st.session_state.history_manager
    conversation = st.session_state.conversation
    
    # Convert to dict for saving
    conversation_dict = conversation.to_dict()
    
    # Save conversation
    conversation_id = history_manager.save_conversation(
        messages=conversation_dict["messages"],
        conversation_id=conversation.id,
        title=conversation.title
    )
    
    # Update conversation ID
    conversation.id = conversation_id


def process_user_input(user_input: str):
    """Process user input and generate a response.
    
    Args:
        user_input: User's message text
    """
    if not user_input.strip():
        return
    
    # Get current conversation
    conversation = st.session_state.conversation
    
    # Add user message
    user_message = Message.user_message(user_input)
    conversation.add_message(user_message)
    
    # Display the message
    render_message(user_message)
    
    # Get API client and settings
    api_client = st.session_state.api_client
    settings = st.session_state.settings
    
    # Get AI response
    with st.spinner("Thinking..."):
        # Format messages for API
        api_messages = conversation.get_api_messages()
        
        response_text = api_client.get_completion(
            messages=api_messages,
            model=settings["model"],
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"]
        )
        
        # Create assistant message
        assistant_message = Message.assistant_message(response_text)
        conversation.add_message(assistant_message)
        
        # Save the conversation automatically
        save_current_conversation()
    
    # Display assistant message
    render_message(assistant_message)
    
    # Rerun to update UI
    st.rerun()


def run_app():
    """Run the Streamlit application."""
    logger.info("Starting application")
    
    # Initialize session state before anything else
    init_session_state()
    
    # Set up page config
    setup_page_config()
    
    # Get app configuration
    config = get_app_config()
    
    # Apply theme from session state (not settings yet, as they haven't been updated)
    current_theme = st.session_state.get("theme", "light")
    apply_theme(current_theme)
    
    # Render the app header
    render_header(config["app_name"], config["version"])
    
    # Render sidebar components (which may update the theme)
    settings = render_settings_sidebar(config["version"])
    st.session_state.settings = settings  # Update settings
    
    # Show conversation management sidebar
    render_conversation_sidebar(
        st.session_state.history_manager,
        getattr(st.session_state.conversation, "id", None),
        on_new_conversation=create_new_conversation,
        on_load_conversation=load_conversation,
        on_rename_conversation=rename_conversation,
        on_delete_conversation=delete_conversation
    )
    
    # Render about section
    render_about_sidebar(config["version"], config["api_key"])
    
    # Display current conversation
    for message in st.session_state.conversation.messages:
        render_message(message)
    
    # Chat input
    user_input = render_chat_input()
    if user_input:
        process_user_input(user_input)
    
    # Action buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Save Chat", use_container_width=True):
            save_current_conversation()
            st.success("Conversation saved!")
    
    # Additional information
    with st.expander("About this application"):
        st.markdown("""
        This is a Streamlit-based chat application that uses OpenAI's API to generate responses.
        
        Features:
        - Chat with various OpenAI models
        - Adjust model parameters like temperature and max tokens
        - Save and load conversations
        - Create multiple conversation threads
        - Dark/Light theme options
        
        To use this application, make sure you have an OpenAI API key in your .env file.
        """)