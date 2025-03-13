"""Application settings and configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv
import importlib.metadata
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def get_version() -> str:
    """Get the application version.
    
    Returns:
        Version string
    """
    try:
        # First try direct import if package is installed
        from llm_chat.__version__ import __version__
        return __version__
    except ImportError:
        try:
            # Try to get version from metadata if installed
            return importlib.metadata.version("llm_chat")
        except importlib.metadata.PackageNotFoundError:
            # Fallback version
            return "0.1.0"


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment.
    
    Returns:
        API key or None if not found
    """
    return os.getenv("OPENAI_API_KEY")


def get_default_settings() -> Dict[str, Any]:
    """Get default application settings.
    
    Returns:
        Dictionary of default settings
    """
    return {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1024,
        "assistant_type": "general"
    }


def get_app_config() -> Dict[str, Any]:
    """Get application configuration.
    
    Returns:
        Dictionary of configuration values
    """
    return {
        "version": get_version(),
        "api_key": get_openai_api_key(),
        "default_settings": get_default_settings(),
        "app_name": "AI Chat",
        "app_icon": "💬",
    }


def save_user_settings(settings: Dict[str, Any]) -> None:
    """Save user settings to disk.
    
    Args:
        settings: Settings to save
    """
    # Create settings directory if needed
    home_dir = Path.home()
    settings_dir = home_dir / ".llm_chat" / "settings"
    os.makedirs(settings_dir, exist_ok=True)
    
    # TODO: Implement settings save logic
    logger.info("User settings saved")


def load_user_settings() -> Dict[str, Any]:
    """Load user settings from disk.
    
    Returns:
        Dictionary of user settings
    """
    # Default to app defaults
    settings = get_default_settings()
    
    # TODO: Implement settings load logic
    
    return settings