"""Sidebar components for Streamlit UI."""
import streamlit as st
from typing import Dict, Any, List, Callable, Optional
import os

from ..chat.history import ChatHistoryManager
from ..chat.system_prompts import system_prompt_manager
from .chat_ui import format_date


def render_settings_sidebar(version: str) -> Dict[str, Any]:
    """Render the settings sidebar and return the selected settings."""
    st.sidebar.markdown("<div class='sidebar-header'>Settings</div>", unsafe_allow_html=True)
    
    # Get all assistant types
    assistant_types = system_prompt_manager.get_all_assistant_types()
    assistant_type_options = [f"{at.icon} {at.name}" for at in assistant_types]
    assistant_type_ids = [at.id for at in assistant_types]
    
    # Get current assistant type from session state (default to general)
    current_assistant_type = st.session_state.get("assistant_type", "general")
    
    # Find the index of the current assistant type
    try:
        current_index = assistant_type_ids.index(current_assistant_type)
    except ValueError:
        current_index = 0  # Default to first option if not found
    
    settings = {
        "model": st.sidebar.selectbox(
            "Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=2
        ),
        "temperature": st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1),
        "max_tokens": st.sidebar.slider("Max Tokens", 256, 4096, 1024, 128),
    }
    
    # Add custom CSS for assistant type cards
    st.markdown("""
    <style>
    .assistant-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 3px solid transparent;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .assistant-card:hover {
        background-color: #f0f1f2;
    }
    .assistant-card.selected {
        border-left-color: #2196F3;
        background-color: #e6f7ff;
    }
    .assistant-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .assistant-name {
        font-weight: 600;
        margin-bottom: 4px;
    }
    .assistant-description {
        font-size: 0.85rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add assistant type selector header
    st.sidebar.markdown("### Assistant Type")
    
    # Use select box for selecting assistant type
    selected_assistant_index = st.sidebar.selectbox(
        "Select an assistant type:",
        options=range(len(assistant_type_options)),
        format_func=lambda i: assistant_type_options[i],
        index=current_index,
        key="assistant_type_selector"
    )
    
    selected_assistant_id = assistant_type_ids[selected_assistant_index]
    settings["assistant_type"] = selected_assistant_id
    
    # Show selected assistant type details
    selected_assistant = assistant_types[selected_assistant_index]
    st.sidebar.markdown(f"""
    <div class="assistant-card selected">
        <div class="assistant-icon">{selected_assistant.icon}</div>
        <div class="assistant-name">{selected_assistant.name}</div>
        <div class="assistant-description">{selected_assistant.description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    return settings


def render_about_sidebar(version: str, api_key: Optional[str] = None) -> None:
    """Render the about sidebar.
    
    Args:
        version: Application version string
        api_key: OpenAI API key (to show status)
    """
    st.sidebar.markdown("<div class='sidebar-header'>About</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**llm_chat** v{version}")
    st.sidebar.markdown("Created with Streamlit & OpenAI")
    
    # Display API key status
    if api_key:
        st.sidebar.success("OpenAI API Key: Connected")
    else:
        st.sidebar.error("OpenAI API Key: Missing")
        st.sidebar.markdown("""
        Please add your OpenAI API key to a `.env` file in the project root:
        ```
        OPENAI_API_KEY=your_api_key_here
        ```
        """)


def handle_rename_start(conversation_id: str, current_title: str) -> None:
    """Handle the start of a conversation rename process."""
    st.session_state.show_rename_ui = True
    st.session_state.new_title = current_title
    st.session_state.conversation_id_to_rename = conversation_id
    st.rerun()


def render_conversation_sidebar(
    history_manager: ChatHistoryManager,
    current_conversation_id: Optional[str] = None,
    on_new_conversation: Optional[Callable] = None,
    on_load_conversation: Optional[Callable[[str], None]] = None,
    on_rename_conversation: Optional[Callable[[str, str], None]] = None,
    on_delete_conversation: Optional[Callable[[str], None]] = None
) -> None:
    """Render improved conversation sidebar for managing chat history."""
    st.sidebar.markdown("<div class='sidebar-header'>Conversations</div>", unsafe_allow_html=True)
    
    # New conversation button 
    if st.sidebar.button("➕ New Conversation", key="new_conversation_btn", use_container_width=True):
        if on_new_conversation:
            on_new_conversation()
    
    # Show rename UI if active
    if "show_rename_ui" in st.session_state and st.session_state.show_rename_ui:
        with st.sidebar.container():
            st.markdown("""
            <div style="background-color: white; padding: 15px; border-radius: 8px; 
                        margin: 15px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0; margin-bottom: 10px; color: #333;">Rename Conversation</h4>
            </div>
            """, unsafe_allow_html=True)
            
            new_title = st.text_input(
                "New title", 
                value=st.session_state.get("new_title", ""),
                key="rename_input",
                placeholder="Enter new title..."
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Save", key="save_rename", use_container_width=True):
                    if on_rename_conversation and "conversation_id_to_rename" in st.session_state:
                        on_rename_conversation(st.session_state.conversation_id_to_rename, new_title)
                    st.session_state.show_rename_ui = False
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", key="cancel_rename", use_container_width=True):
                    st.session_state.show_rename_ui = False
                    st.rerun()
    
    # Divider
    st.sidebar.markdown("---")
    
    # List of saved conversations
    conversations = history_manager.list_conversations()
    
    if not conversations:
        st.sidebar.info("No saved conversations yet.")
        return
    
    # Display conversations with material design cards
    for conv in conversations:
        # Determine if this is the active conversation
        is_active = current_conversation_id == conv["id"]
        
        # Create a container for each conversation item
        with st.sidebar.container():
            # Display conversation info with styling
            st.markdown(
                f"""
                <div class="conversation-card {"active" if is_active else ""}">
                    <div class="conversation-title">{conv["title"]}</div>
                    <div class="conversation-meta">
                        <span>{format_date(conv["updated"])}</span>
                        <span>{conv["message_count"]} messages</span>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Standard buttons without visibility tricks
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Load", key=f"load_{conv['id']}", use_container_width=True):
                    if on_load_conversation and not is_active:
                        on_load_conversation(conv["id"])
            
            with col2:
                if st.button("Rename", key=f"rename_{conv['id']}", use_container_width=True):
                    if on_rename_conversation:
                        handle_rename_start(conv["id"], conv["title"])
            
            with col3:
                if st.button("Delete", key=f"delete_{conv['id']}", use_container_width=True):
                    if on_delete_conversation:
                        on_delete_conversation(conv["id"])