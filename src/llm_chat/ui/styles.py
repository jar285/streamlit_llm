"""CSS styles for the Streamlit UI."""
import streamlit as st


def apply_base_styles():
    """Apply base CSS styles to the Streamlit app."""
    st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.8rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #2196F3;
    }
    .chat-message.assistant {
        background-color: #f0f2f6;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .message-content {
        margin-top: 0;
    }
    .chat-message .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.8rem;
        color: #666;
    }
    .chat-message .message-header .timestamp {
        font-style: italic;
    }
    .chat-message .message-header .role {
        font-weight: bold;
    }
    .user-avatar {
        font-size: 1.5rem;
        min-width: 2.5rem;
        color: white;
        background-color: #2196F3;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        height: 2.5rem;
    }
    .assistant-avatar {
        font-size: 1.5rem;
        min-width: 2.5rem;
        color: white;
        background-color: #4CAF50;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        height: 2.5rem;
    }
    .stChatInputContainer {
        padding-top: 1rem;
        border-top: 1px solid #ddd;
    }
    .main-header {
        text-align: center;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #eee;
    }
    .version-tag {
        opacity: 0.8;
        font-size: 0.8rem;
    }
    /* Custom styling for the chat input */
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    /* Sidebar styling */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    /* Conversation list styling */
    .conversation-item {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .conversation-item:hover {
        background-color: rgba(0,0,0,0.05);
    }
    .conversation-item.active {
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 3px solid #2196F3;
    }
    .conversation-item .title {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .conversation-item .meta {
        font-size: 0.8rem;
        color: #666;
    }
    /* Action buttons */
    .action-button {
        padding: 0.5rem;
        border-radius: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: background-color 0.3s;
        margin-bottom: 0.5rem;
    }
    .action-button:hover {
        background-color: rgba(0,0,0,0.05);
    }
    .action-button.primary {
        background-color: #2196F3;
        color: white;
    }
    .action-button.danger {
        background-color: #f44336;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_dark_theme():
    """Apply dark theme CSS overrides."""
    st.markdown("""
    <style>
    .chat-message.user {
        background-color: #2d3748;
        border-left: 5px solid #4299e1;
        color: #e2e8f0;
    }
    .chat-message.assistant {
        background-color: #1a202c;
        border-left: 5px solid #48bb78;
        color: #e2e8f0;
    }
    .chat-message .message-header {
        color: #a0aec0;
    }
    .conversation-item:hover {
        background-color: rgba(255,255,255,0.05);
    }
    .conversation-item.active {
        background-color: rgba(66, 153, 225, 0.2);
    }
    .conversation-item .meta {
        color: #a0aec0;
    }
    .main-header {
        border-bottom: 1px solid #2d3748;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_code_highlighting():
    """Apply syntax highlighting for code blocks."""
    st.markdown("""
    <style>
    code {
        padding: 0.2em 0.4em;
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 3px;
        font-family: monospace;
    }
    pre {
        padding: 1em;
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 5px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    .language-python, .language-javascript, .language-html, .language-css {
        color: #333;
    }
    .dark-mode .language-python, .dark-mode .language-javascript, .dark-mode .language-html, .dark-mode .language-css {
        color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_theme(theme: str = "light"):
    """Apply a complete theme to the app.
    
    Args:
        theme: Theme name ("light" or "dark")
    """
    # Always apply base styles
    apply_base_styles()
    
    # Apply code highlighting
    apply_code_highlighting()
    
    # Apply theme-specific overrides
    if theme.lower() == "dark":
        apply_dark_theme()
        # Add a class to the body for JavaScript-based styling
        st.markdown("""
        <script>
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
        </script>
        """, unsafe_allow_html=True)
    else:
        # Add light mode class and remove dark mode
        st.markdown("""
        <script>
            document.body.classList.add('light-mode');
            document.body.classList.remove('dark-mode');
        </script>
        """, unsafe_allow_html=True)