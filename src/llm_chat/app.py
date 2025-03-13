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
from .chat.system_prompts import system_prompt_manager
from .config.settings import get_app_config, get_default_settings
from .ui.styles import apply_theme
from .ui.chat_ui import render_message, render_header, render_chat_input
from .ui.sidebar import render_settings_sidebar, render_about_sidebar, render_conversation_sidebar
from .utils.helpers import sanitize_html_content

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
    # Initialize settings if not exists
    if "settings" not in st.session_state:
        st.session_state.settings = get_default_settings()
    
    # Initialize assistant type if not exists
    if "assistant_type" not in st.session_state:
        st.session_state.assistant_type = "general"
    
    # Initialize conversation if not exists
    if "conversation" not in st.session_state:
        st.session_state.conversation = Conversation()
        
        # Get system prompt for the current assistant type
        system_prompt = system_prompt_manager.get_system_prompt(st.session_state.assistant_type)
        st.session_state.conversation.set_system_prompt(system_prompt)
        
        # Add a welcome message
        assistant_type = system_prompt_manager.get_assistant_type(st.session_state.assistant_type)
        welcome_text = f"Hello! I'm your {assistant_type.name if assistant_type else 'AI Assistant'}. How can I help you today?"
        welcome_msg = Message.assistant_message(welcome_text)
        st.session_state.conversation.add_message(welcome_msg)
        
        # Log the welcome message for debugging
        print(f"Welcome message content: {welcome_msg.content}")
    
    # Initialize history manager if not exists
    if "history_manager" not in st.session_state:
        st.session_state.history_manager = ChatHistoryManager()
    
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
    # Get the current assistant type
    current_assistant_type = st.session_state.get("assistant_type", "general")
    
    # Get the system prompt for this assistant type
    system_prompt = system_prompt_manager.get_system_prompt(current_assistant_type)
    
    # Create new conversation with the system prompt
    st.session_state.conversation = Conversation(system_prompt=system_prompt)
    
    # Get the selected assistant type info
    assistant_type = system_prompt_manager.get_assistant_type(current_assistant_type)
    
    # Add a welcome message
    welcome_msg = Message.assistant_message(
        f"Hello! I'm your {assistant_type.name if assistant_type else 'AI Assistant'}. How can I help you today?"
    )
    st.session_state.conversation.add_message(welcome_msg)
    st.rerun()


def update_assistant_type(new_type: str):
    """Update the assistant type and system prompt for the current conversation.
    
    Args:
        new_type: The new assistant type ID
    """
    # Update session state
    st.session_state.assistant_type = new_type
    
    # Get the system prompt for this assistant type
    system_prompt = system_prompt_manager.get_system_prompt(new_type)
    
    # Update the current conversation
    if "conversation" in st.session_state:
        st.session_state.conversation.set_system_prompt(system_prompt)
    
    # Get the selected assistant type info
    assistant_type = system_prompt_manager.get_assistant_type(new_type)

    # Add a message about the switch with sanitization
    if assistant_type:
        switch_msg = Message.assistant_message(sanitize_html_content(
            f"I'm now in {assistant_type.name} mode. How can I assist you?"
        ))
        st.session_state.conversation.add_message(switch_msg)


def load_conversation(conversation_id: str):
    """Load a conversation from history.
    
    Args:
        conversation_id: ID of the conversation to load
    """
    try:
        history_manager = st.session_state.history_manager
        conversation_data = history_manager.load_conversation(conversation_id)
        loaded_conversation = Conversation.from_dict(conversation_data)
        
        # Update the assistant type based on the loaded conversation
        if loaded_conversation.system_prompt:
            # Try to find an assistant type that matches this system prompt
            for assistant_type in system_prompt_manager.get_all_assistant_types():
                if assistant_type.system_prompt == loaded_conversation.system_prompt:
                    st.session_state.assistant_type = assistant_type.id
                    break
        
        st.session_state.conversation = loaded_conversation
        st.rerun()
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")
        logger.error(f"Error loading conversation {conversation_id}: {str(e)}")


def rename_conversation(conversation_id: str, new_title: str):
    """Rename a conversation in history."""
    if not new_title.strip():
        st.error("Title cannot be empty")
        return
        
    history_manager = st.session_state.history_manager
    success = history_manager.rename_conversation(conversation_id, new_title)
    
    if success:
        st.success(f"Renamed conversation to '{new_title}'")
        # If this is the current conversation, update its title
        if conversation_id == getattr(st.session_state.conversation, "id", None):
            st.session_state.conversation.title = new_title
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
    try:
        history_manager = st.session_state.history_manager
        # Check if deleting current conversation
        current_id = getattr(st.session_state.conversation, "id", None)
        
        success = history_manager.delete_conversation(conversation_id)
        
        if success:
            st.success("Conversation deleted")
            # If deleting current conversation, create new one
            if conversation_id == current_id:
                create_new_conversation()
            else:
                st.rerun()
        else:
            st.error("Failed to delete conversation")
    except Exception as e:
        st.error(f"Error deleting conversation: {str(e)}")
        logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")


def save_current_conversation():
    """Save the current conversation to history."""
    try:
        history_manager = st.session_state.history_manager
        conversation = st.session_state.conversation
        
        # Convert to dict for saving
        conversation_dict = conversation.to_dict()
        
        # Save conversation with system prompt
        conversation_id = history_manager.save_conversation(
            messages=conversation_dict["messages"],
            conversation_id=conversation.id,
            title=conversation.title,
            system_prompt=conversation.system_prompt
        )
        
        # Update conversation ID
        conversation.id = conversation_id
        
        st.success("Conversation saved successfully!")
        
        logger.info(f"Saved conversation {conversation_id} with system prompt")
        return True
    except Exception as e:
        st.error(f"Error saving conversation: {str(e)}")
        logger.error(f"Error saving conversation: {str(e)}")
        return False


def process_user_input(user_input: str):
    """Process user input and generate a response."""
    if not user_input.strip():
        return
    
    # Get current conversation
    conversation = st.session_state.conversation
    
    # Add user message - apply sanitization here
    user_message = Message.user_message(sanitize_html_content(user_input))
    conversation.add_message(user_message)
    
    # Display the message
    render_message(user_message)
    
    # Get API client and settings
    api_client = st.session_state.api_client
    settings = st.session_state.settings
    
    # Get AI response
    with st.spinner("Thinking..."):
        try:
            # Format messages for API
            api_messages = conversation.get_api_messages()
            
            response_text = api_client.get_completion(
                messages=api_messages,
                model=settings["model"],
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"]
            )
            
            # Create assistant message - apply sanitization here
            assistant_message = Message.assistant_message(sanitize_html_content(response_text))
            conversation.add_message(assistant_message)
            
            # Save the conversation automatically
            save_current_conversation()
            
            # Display assistant message
            render_message(assistant_message)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            logger.error(f"Error in process_user_input: {str(e)}")
    
    # Rerun to update UI
    st.rerun()


def run_app():
    """Run the Streamlit application."""
    logger.info("Starting application")
    
    # Set up page config
    setup_page_config()
    
    # Initialize session state
    init_session_state()
    
    # Get app configuration
    config = get_app_config()
    
    # Apply base styles
    apply_theme()
    
    # Render the app header
    render_header(config["app_name"], config["version"])
    
    # Get current assistant type info
    current_assistant_type = st.session_state.assistant_type
    assistant_type = system_prompt_manager.get_assistant_type(current_assistant_type)
    
    # Show current assistant type
    if assistant_type:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; 
                    padding: 1rem 1.5rem; background-color: white; 
                    border-radius: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);">
            <div style="font-size: 2.5rem; margin-right: 1rem;">{assistant_type.icon}</div>
            <div style="flex-grow: 1;">
                <div style="font-weight: 600; font-size: 1.25rem; margin-bottom: 0.25rem; color: #333;">{assistant_type.name}</div>
                <div style="font-size: 0.9rem; color: #666; line-height: 1.4;">{assistant_type.description}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Render sidebar components and get updated settings
    settings = render_settings_sidebar(config["version"])
    
    # Check if assistant type has changed
    if settings["assistant_type"] != st.session_state.assistant_type:
        update_assistant_type(settings["assistant_type"])
    
    # Update settings in session state
    st.session_state.settings = settings
    
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
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0;
            margin-top: 0;
        }
        
        /* Fix for overlapping bar */
        .main-content-container {
            overflow: visible !important;
        }
        
        /* Remove extra spacing between messages */
        .stMarkdown {
            margin-bottom: 0 !important;
        }
        
        /* Ensure chat container is properly spaced */
        .chat-container {
            margin-bottom: 80px; /* Space for input box */
        }
    </style>
    """, unsafe_allow_html=True)

    # Create a container for all chat messages
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        # Display current conversation
        for message in st.session_state.conversation.messages:
            render_message(message, assistant_type)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = render_chat_input()
    if user_input:
        process_user_input(user_input)
    
    
    # Additional information
    with st.expander("About this application"):
        st.markdown("""
        This is a Streamlit-based chat application that uses OpenAI's API to generate responses.
        
        Features:
        - Chat with various OpenAI models
        - Choose different assistant types with specialized expertise
        - Adjust model parameters like temperature and max tokens
        - Save and load conversations
        - Create multiple conversation threads
        
        To use this application, make sure you have an OpenAI API key in your .env file.
        """)