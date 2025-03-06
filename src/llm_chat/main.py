"""Streamlit chat application with OpenAI."""
import streamlit as st
import os
import logging
from dotenv import load_dotenv
import importlib.metadata
from pathlib import Path
import openai
from openai import OpenAI
import time
from datetime import datetime
import json
import uuid
import sys

# Set up explicit path to the utils directory
try:
    # Get the directory of the current script
    current_file = Path(__file__).resolve()
    parent_dir = current_file.parent
    utils_dir = parent_dir / "utils"
    
    # Add the utils directory to the Python path
    if str(utils_dir) not in sys.path:
        sys.path.append(str(utils_dir))
        
    # Also add the parent directory to handle package imports
    if str(parent_dir) not in sys.path:
        sys.path.append(str(parent_dir))
        
    # Now try to import the chat history manager
    from llm_chat.utils.chat_history import ChatHistoryManager
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to direct import
    try:
        from llm_chat.utils.chat_history import ChatHistoryManager
    except ImportError:
        # Define a fallback version
        class ChatHistoryManager:
            def __init__(self, *args, **kwargs):
                self.available = False
                print("Using fallback ChatHistoryManager - saving/loading unavailable")
                
            def save_conversation(self, *args, **kwargs):
                return None
                
            def list_conversations(self, *args, **kwargs):
                return []
                
            def load_conversation(self, *args, **kwargs):
                return {"messages": []}
                
            def delete_conversation(self, *args, **kwargs):
                return False

# Load environment variables from .env file
load_dotenv()

# Get version in a way that works with Streamlit
try:
    # First try direct import if package is installed
    from llm_chat.__version__ import __version__
except ImportError:
    try:
        # Try to get version from metadata if installed
        __version__ = importlib.metadata.version("llm_chat")
    except importlib.metadata.PackageNotFoundError:
        # Fallback version if not installed
        __version__ = "0.1.0"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Monkey patch the OpenAI client to bypass the proxies issue
original_init = openai._base_client.SyncHttpxClientWrapper.__init__

def patched_init(self, *args, **kwargs):
    # Remove the proxies parameter if it exists
    if 'proxies' in kwargs:
        del kwargs['proxies']
    original_init(self, *args, **kwargs)

# Apply the monkey patch
openai._base_client.SyncHttpxClientWrapper.__init__ = patched_init

# Initialize OpenAI API client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Custom CSS for improved UI
def apply_custom_css():
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

# Custom message container
def message_container(message, timestamp=None):
    role = message["role"]
    content = message["content"]
    
    if timestamp is None:
        timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))
    
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

def create_sidebar() -> dict:
    """Create and process sidebar elements."""
    st.sidebar.markdown("<div class='sidebar-header'>Settings</div>", unsafe_allow_html=True)
    
    settings = {
        "model": st.sidebar.selectbox(
            "Model",
            options=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=2
        ),
        "temperature": st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1),
        "max_tokens": st.sidebar.slider("Max Tokens", 256, 4096, 1024, 128),
    }
    
    # Custom themes
    theme = st.sidebar.radio("Theme", ["Light", "Dark"], horizontal=True)
    if theme == "Dark":
        # Apply dark theme CSS
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
        </style>
        """, unsafe_allow_html=True)
    
    return settings


def get_chat_response(messages, settings):
    """Get a response from the OpenAI API."""
    if not api_key:
        return "Error: OpenAI API key not found. Please check your .env file."
        
    try:
        response = client.chat.completions.create(
            model=settings["model"],
            messages=messages,
            temperature=settings["temperature"],
            max_tokens=settings["max_tokens"]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return f"Error: {str(e)}"


def format_date(date_str):
    """Format ISO date string to human-readable format."""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%b %d, %Y %H:%M")
    except:
        return date_str


def init_session_state():
    """Initialize session state variables."""
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?",
            "timestamp": datetime.now().strftime("%H:%M")
        })
    
    if "history_manager" not in st.session_state:
        # Initialize the chat history manager
        st.session_state.history_manager = ChatHistoryManager()
    
    if "show_rename_ui" not in st.session_state:
        st.session_state.show_rename_ui = False
    
    if "new_title" not in st.session_state:
        st.session_state.new_title = ""


def save_current_conversation():
    """Save the current conversation to disk."""
    if not st.session_state.messages:
        return
    
    history_manager = st.session_state.history_manager
    messages = st.session_state.messages
    
    # Save or update the conversation
    conversation_id = history_manager.save_conversation(
        messages=messages,
        conversation_id=st.session_state.current_conversation_id
    )
    
    # Update the current conversation ID
    st.session_state.current_conversation_id = conversation_id


def load_conversation(conversation_id):
    """Load a conversation from disk."""
    history_manager = st.session_state.history_manager
    
    try:
        conversation = history_manager.load_conversation(conversation_id)
        st.session_state.messages = conversation.get("messages", [])
        st.session_state.current_conversation_id = conversation_id
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")


def conversation_sidebar():
    """Create a sidebar for managing conversations."""
    history_manager = st.session_state.history_manager
    
    st.sidebar.markdown("<div class='sidebar-header'>Conversations</div>", unsafe_allow_html=True)
    
    # New conversation button
    if st.sidebar.button("New Conversation", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
        st.session_state.current_conversation_id = None
        st.rerun()
    
    # List of saved conversations
    conversations = history_manager.list_conversations()
    
    # Show rename UI if active
    if st.session_state.show_rename_ui and st.session_state.current_conversation_id:
        with st.sidebar.expander("Rename Conversation", expanded=True):
            st.text_input(
                "New title", 
                value=st.session_state.new_title,
                key="rename_input",
                on_change=lambda: setattr(st.session_state, "new_title", st.session_state.rename_input)
            )
            
            col1, col2 = st.columns(2)
            if col1.button("Save", use_container_width=True):
                history_manager.rename_conversation(
                    st.session_state.current_conversation_id,
                    st.session_state.new_title
                )
                st.session_state.show_rename_ui = False
                st.rerun()
            
            if col2.button("Cancel", use_container_width=True):
                st.session_state.show_rename_ui = False
                st.rerun()
    
    # Divider
    st.sidebar.markdown("---")
    
    # Display the list of conversations
    if not conversations:
        st.sidebar.info("No saved conversations yet.")
    else:
        for conv in conversations:
            # Determine if this is the active conversation
            is_active = st.session_state.current_conversation_id == conv["id"]
            
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
                    load_conversation(conv["id"])
                    st.rerun()
                
                # Rename button
                if col2.button("Rename", key=f"rename_{conv['id']}", use_container_width=True):
                    st.session_state.show_rename_ui = True
                    st.session_state.new_title = conv["title"]
                    st.session_state.current_conversation_id = conv["id"]
                    st.rerun()
                
                # Delete button
                if col3.button("Delete", key=f"delete_{conv['id']}", use_container_width=True):
                    if history_manager.delete_conversation(conv["id"]):
                        # If deleting the active conversation, reset
                        if is_active:
                            st.session_state.messages = [{
                                "role": "assistant", 
                                "content": "Hello! I'm an AI assistant powered by OpenAI. How can I help you today?",
                                "timestamp": datetime.now().strftime("%H:%M")
                            }]
                            st.session_state.current_conversation_id = None
                        st.rerun()
    
    # Display about section below conversations
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div class='sidebar-header'>About</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"**llm_chat** v{__version__}")
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


def main() -> None:
    """Main Streamlit application."""
    logger.info(f"Starting Streamlit chat app v{__version__}")
    
    st.set_page_config(
        page_title="AI Chat",
        page_icon="💬",
        layout="wide",
    )
    
    # Initialize session state
    init_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>AI Chat</h1>
        <div class="version-tag">v{__version__}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get model settings
    settings = create_sidebar()
    
    # Show conversation sidebar
    conversation_sidebar()
    
    # Display chat messages
    for message in st.session_state.messages:
        timestamp = message.get("timestamp", None)
        message_container(message, timestamp)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        user_message = {
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        message_container(user_message)
        
        # Get AI response
        with st.spinner("Thinking..."):
            # Format messages for API (without timestamp)
            api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            response = get_chat_response(api_messages, settings)
            
            # Create assistant message
            response_message = {
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            
            # Add to chat history
            st.session_state.messages.append(response_message)
            
            # Save the conversation automatically
            save_current_conversation()
        
        # Display assistant message
        message_container(response_message)
        
        # Rerun to update UI
        st.rerun()
    
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


if __name__ == "__main__":
    main()