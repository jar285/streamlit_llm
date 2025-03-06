"""Sidebar components for Streamlit UI."""
import streamlit as st
from typing import Dict, Any, List, Callable, Optional
import os

from ..chat.history import ChatHistoryManager
from .chat_ui import format_date


def render_settings_sidebar(version: str) -> Dict[str, Any]:
    """Render the settings sidebar and return the selected settings."""
    st.sidebar.markdown("<div class='sidebar-header'>Settings</div>", unsafe_allow_html=True)
    
    # Get current theme from session state (default to light)
    current_theme = st.session_state.get("theme", "light")
    
    settings = {
        "model": st.sidebar.selectbox(
            "Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=2
        ),
        "temperature": st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1),
        "max_tokens": st.sidebar.slider("Max Tokens", 256, 4096, 1024, 128),
    }
    
    # Theme selection with immediate effect
    theme_options = ["Light", "Dark"]
    theme_index = 1 if current_theme == "dark" else 0
    
    new_theme_index = st.sidebar.radio(
        "Theme", 
        options=range(len(theme_options)),
        format_func=lambda x: theme_options[x],
        index=theme_index,
        horizontal=True,
        key="theme_selector"
    )
    
    # Set the theme based on selection
    selected_theme = "dark" if new_theme_index == 1 else "light"
    
    # Check if theme changed
    if selected_theme != current_theme:
        st.session_state["theme"] = selected_theme
        # Force a rerun to apply the theme immediately
        st.rerun()
    
    settings["theme"] = selected_theme
    
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


def render_conversation_list_with_dropdown(
    conversations: List[Dict[str, Any]], 
    current_id: str = None,
    on_load=None,
    on_rename=None,
    on_delete=None
) -> None:
    """Render the list of saved conversations with dropdown menus."""
    if not conversations:
        st.sidebar.info("No saved conversations yet.")
        return
    
    # Add custom CSS for dropdown menu
    st.markdown("""
    <style>
    .conversation-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 3px solid transparent;
        position: relative;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .conversation-card:hover {
        background-color: #f0f1f2;
    }
    .conversation-card.active {
        border-left-color: #2196F3;
        background-color: #e6f7ff;
    }
    .conversation-title {
        font-weight: 600;
        margin-bottom: 4px;
        font-size: 0.95rem;
        padding-right: 30px;
    }
    .conversation-meta {
        font-size: 0.75rem;
        color: #666;
        margin-bottom: 0;
    }
    .actions-menu {
        position: absolute;
        top: 8px;
        right: 8px;
    }
    .menu-dots {
        cursor: pointer;
        font-size: 1.2rem;
        color: #777;
        background: transparent;
        border: none;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }
    .menu-dots:hover {
        background: rgba(0,0,0,0.05);
    }
    .dropdown-menu {
        display: none;
        position: absolute;
        right: 0;
        top: 100%;
        background-color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-radius: 4px;
        z-index: 1000;
        min-width: 120px;
        overflow: hidden;
    }
    .dropdown-menu.show {
        display: block;
    }
    .dropdown-item {
        padding: 8px 12px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background 0.2s;
        color: #333;
        display: flex;
        align-items: center;
    }
    .dropdown-item:hover {
        background-color: #f5f5f5;
    }
    .dropdown-item i {
        margin-right: 8px;
        width: 16px;
        text-align: center;
        color: #555;
    }
    
    /* Dark mode styles */
    .dark-mode .conversation-card {
        background-color: #2d3748;
        color: #e2e8f0;
    }
    .dark-mode .conversation-card:hover {
        background-color: #3a4a63;
    }
    .dark-mode .conversation-card.active {
        background-color: #374151;
        border-left-color: #4299e1;
    }
    .dark-mode .conversation-meta {
        color: #a0aec0;
    }
    .dark-mode .menu-dots {
        color: #a0aec0;
    }
    .dark-mode .menu-dots:hover {
        background: rgba(255,255,255,0.1);
    }
    .dark-mode .dropdown-menu {
        background-color: #1a202c;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .dark-mode .dropdown-item {
        color: #e2e8f0;
    }
    .dark-mode .dropdown-item:hover {
        background-color: #2d3748;
    }
    .dark-mode .dropdown-item i {
        color: #a0aec0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript for dropdown functionality
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Close all dropdowns when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.menu-dots')) {
                document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                    menu.classList.remove('show');
                });
            }
        });
        
        // Function to toggle dropdown visibility
        window.toggleMenu = function(id) {
            // Close all other menus first
            document.querySelectorAll('.dropdown-menu').forEach(function(menu) {
                if (menu.id !== 'menu-' + id) {
                    menu.classList.remove('show');
                }
            });
            
            // Toggle the selected menu
            const menu = document.getElementById('menu-' + id);
            menu.classList.toggle('show');
            event.stopPropagation();
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    for i, conv in enumerate(conversations):
        # Determine if this is the active conversation
        is_active = current_id == conv["id"]
        
        # Create container for the conversation card
        st.sidebar.markdown(
            f"""
            <div class="conversation-card {'active' if is_active else ''}" 
                 onclick="document.getElementById('btn-load-{i}').click();">
                <div class="conversation-title">{conv["title"]}</div>
                <div class="conversation-meta">
                    {format_date(conv["updated"])} · {conv["message_count"]} messages
                </div>
                <div class="actions-menu">
                    <button class="menu-dots" onclick="toggleMenu('{i}'); event.stopPropagation();">⋮</button>
                    <div id="menu-{i}" class="dropdown-menu">
                        <div class="dropdown-item" onclick="document.getElementById('btn-load-{i}').click();">
                            <i>📂</i> Load
                        </div>
                        <div class="dropdown-item" onclick="document.getElementById('btn-rename-{i}').click();">
                            <i>✏️</i> Rename
                        </div>
                        <div class="dropdown-item" onclick="document.getElementById('btn-delete-{i}').click();">
                            <i>🗑️</i> Delete
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Hidden buttons for actions (now without label_visibility)
        col1, col2, col3 = st.sidebar.columns(3)
        with col1:
            if st.button("Load", key=f"btn-load-{i}", help="Load conversation", 
                       use_container_width=True):
                if on_load and not is_active:
                    on_load(conv["id"])
        
        with col2:
            if st.button("Rename", key=f"btn-rename-{i}", help="Rename conversation", 
                       use_container_width=True):
                if on_rename:
                    on_rename(conv["id"], conv["title"])
        
        with col3:
            if st.button("Delete", key=f"btn-delete-{i}", help="Delete conversation", 
                       use_container_width=True):
                if on_delete:
                    on_delete(conv["id"])


def render_conversation_sidebar(
    history_manager: ChatHistoryManager,
    current_conversation_id: Optional[str] = None,
    on_new_conversation: Optional[Callable] = None,
    on_load_conversation: Optional[Callable[[str], None]] = None,
    on_rename_conversation: Optional[Callable[[str, str], None]] = None,
    on_delete_conversation: Optional[Callable[[str], None]] = None
) -> None:
    """Render the conversation sidebar for managing chat history."""
    st.sidebar.markdown("<div class='sidebar-header'>Conversations</div>", unsafe_allow_html=True)
    
    # New conversation button
    if st.sidebar.button("New Conversation", use_container_width=True):
        if on_new_conversation:
            on_new_conversation()
    
    # Show rename UI if active
    if "show_rename_ui" in st.session_state and st.session_state.show_rename_ui:
        with st.sidebar.container():
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #2196F3;">
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
    
    # List of saved conversations with dropdown menu
    conversations = history_manager.list_conversations()
    render_conversation_list_with_dropdown(
        conversations, 
        current_conversation_id,
        on_load=on_load_conversation,
        on_rename=lambda conv_id, title: handle_rename_start(conv_id, title),
        on_delete=on_delete_conversation
    )