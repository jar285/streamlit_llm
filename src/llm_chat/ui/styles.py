"""CSS styles for the Streamlit UI."""
import streamlit as st


def apply_base_styles():
    """Apply base CSS styles to the Streamlit app."""
    st.markdown("""
    <style>
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1.25rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message:hover {
        box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
    }
    
    .chat-message.user {
        background-color: #e3f2fd;
        margin-left: 2rem;
        position: relative;
    }
    
    .chat-message.assistant {
        background-color: #f5f5f5;
        margin-right: 2rem;
        position: relative;
    }
    
    .chat-message.system {
        background-color: #f3e5f5;
        border-left: 3px solid #9C27B0;
        margin: 0 1rem;
    }
    
    .chat-message .message-content {
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    
    .chat-message .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        color: #555;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        padding-bottom: 0.5rem;
    }
    
    .chat-message .message-header .timestamp {
        font-style: italic;
        opacity: 0.8;
    }
    
    .chat-message .message-header .role {
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    
    /* Message avatar styling */
    .message-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 8px;
        font-size: 0.9rem;
    }
    
    .user .message-avatar {
        background-color: #2196F3;
        color: white;
    }
    
    .assistant .message-avatar {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Bubble tails for more natural chat look */
    .chat-message.user:after {
        content: '';
        position: absolute;
        right: -10px;
        top: 15px;
        border: 10px solid transparent;
        border-left-color: #e3f2fd;
        border-right: 0;
    }
    
    .chat-message.assistant:after {
        content: '';
        position: absolute;
        left: -10px;
        top: 15px;
        border: 10px solid transparent;
        border-right-color: #f5f5f5;
        border-left: 0;
    }
    
    /* Message assistant type badge */
    .message-assistant-type {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.5rem;
        border-radius: 1rem;
        background-color: rgba(33, 150, 243, 0.1);
        font-size: 0.75rem;
        margin-left: 8px;
        color: #0277bd;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_code_highlighting():
    """Apply enhanced syntax highlighting for code blocks."""
    st.markdown("""
    <style>
    /* Inline code */
    code {
        padding: 0.2em 0.4em;
        background-color: rgba(0, 0, 0, 0.05);
        border-radius: 3px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.85em;
        color: #333;
    }
    
    /* Code blocks */
    pre {
        padding: 1em;
        background-color: #f6f8fa;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid rgba(0, 0, 0, 0.1);
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        margin: 1em 0;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        font-size: 0.9em;
        color: #333;
        display: block;
        line-height: 1.5;
    }
    
    /* Add language identifier on top */
    pre[data-language]:before {
        content: attr(data-language);
        display: block;
        background: rgba(0, 0, 0, 0.05);
        padding: 0.25em 0.6em;
        border-radius: 3px;
        font-size: 0.7em;
        color: #666;
        margin-bottom: 1em;
        width: fit-content;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_header_and_input_styles():
    st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 0.8rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
        color: #333;
    }
    
    .version-tag {
        background-color: rgba(0,0,0,0.1);
        padding: 0.15rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.7rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    /* Chat input styling */
    .stChatInput {
        padding: 0.8rem;
        border-radius: 1.5rem !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stChatInput:focus-within {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Add a fixed chat input container at the bottom */
    .chat-input-container {
        position: sticky;
        bottom: 1rem;
        background-color: white;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        margin-top: 1rem;
        z-index: 100;
    }
    
    /* Typing indicator animation */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
    }
    
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background: #666;
        border-radius: 50%;
        display: block;
        margin: 0 2px;
        opacity: 0.4;
    }
    
    .typing-indicator span:nth-child(1) {
        animation: pulse 1s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation: pulse 1s infinite 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation: pulse 1s infinite 0.4s;
    }
    
    @keyframes pulse {
        0% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.4; transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)

def apply_sidebar_styles():
    st.markdown("""
    <style>
    /* Sidebar enhancements */
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(0,0,0,0.1);
        color: #333;
    }
    
    /* Conversation list styling */
    .conversation-card {
        background-color: white;
        border-radius: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: all 0.2s ease;
        cursor: pointer;
        border-left: 3px solid transparent;
    }
    
    .conversation-card:hover {
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
        transform: translateY(-2px);
    }
    
    .conversation-card.active {
        border-left-color: #2196F3;
        background-color: #e3f2fd;
    }
    
    .conversation-title {
        font-weight: 500;
        margin-bottom: 0.25rem;
        color: #333;
    }
    
    .conversation-meta {
        font-size: 0.8rem;
        color: #666;
        display: flex;
        justify-content: space-between;
    }
    
    /* Assistant selector cards */
    .assistant-card {
        background-color: white;
        border-radius: 0.75rem;
        padding: 0.75rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    
    .assistant-card:hover {
        box-shadow: 0 3px 6px rgba(0,0,0,0.16);
    }
    
    .assistant-card.selected {
        border-left-color: #2196F3;
        background-color: #e3f2fd;
    }
    
    .assistant-icon {
        font-size: 1.75rem;
        margin-right: 0.75rem;
        display: inline-block;
    }
    
    .assistant-name {
        font-weight: 500;
        margin-bottom: 0.25rem;
        color: #333;
    }
    
    .assistant-description {
        font-size: 0.85rem;
        color: #666;
        line-height: 1.4;
    }
    
    /* Material buttons */
    .material-button {
        display: inline-block;
        background-color: #f1f3f4;
        color: #333;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s ease;
        margin: 0.25rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .material-button:hover {
        background-color: #e5e7e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    
    .material-button.primary {
        background-color: #2196F3;
        color: white;
    }
    
    .material-button.primary:hover {
        background-color: #1e88e5;
    }
    
    .material-button.danger {
        background-color: #f44336;
        color: white;
    }
    
    .material-button.danger:hover {
        background-color: #e53935;
    }
    
    /* Button groups */
    .button-group {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_animations():
    st.markdown("""
    <style>
    /* General transitions */
    * {
        transition: background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }
    
    /* Button click effect */
    button:active {
        transform: scale(0.97);
    }
    
    /* Page transition effect */
    @keyframes pageTransition {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .main-content {
        animation: pageTransition 0.4s ease-out;
    }
    
    /* Hover effects for interactive elements */
    .hoverable {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .hoverable:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Ripple effect for buttons (simplified) */
    .ripple {
        position: relative;
        overflow: hidden;
    }
    
    .ripple:after {
        content: "";
        display: block;
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        background-image: radial-gradient(circle, #fff 10%, transparent 10.01%);
        background-repeat: no-repeat;
        background-position: 50%;
        transform: scale(10, 10);
        opacity: 0;
        transition: transform .5s, opacity 1s;
    }
    
    .ripple:active:after {
        transform: scale(0, 0);
        opacity: .3;
        transition: 0s;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_layout_fixes():
    """Apply fixes for common layout issues."""
    st.markdown("""
    <style>
    /* Fix for the overlapping bar issue */
    .main .block-container {
        padding-bottom: 80px;
    }
    
    /* Ensure the main content area stays visible */
    .main .block-container {
        overflow: visible !important;
    }
    
    /* Better spacing for messages */
    .element-container {
        margin-bottom: 10px !important;
    }
    
    /* Fix for the stickiness of the chat input */
    .stChatInputContainer {
        position: sticky !important;
        bottom: 0 !important;
        background-color: white !important;
        padding: 1rem !important;
        z-index: 999 !important;
        margin-top: 1rem !important;
        border-top: 1px solid #f0f0f0 !important;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_theme():
    """Apply the light theme to the app."""
    # Apply base styles
    apply_base_styles()

    # Apply header and input styles
    apply_header_and_input_styles()

    # Apply sidebar and styles
    apply_sidebar_styles
    
    # Apply code highlighting
    apply_code_highlighting()

    # Apply animations
    apply_animations

    apply_layout_fixes()