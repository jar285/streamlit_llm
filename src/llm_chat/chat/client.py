"""OpenAI client module for managing API interactions."""
import logging
import os
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

# Set up logging
logger = logging.getLogger(__name__)

# Monkey patch to fix proxies issue
def apply_openai_patches():
    """Apply monkey patches to OpenAI client to fix known issues."""
    # Fix for proxies parameter issue
    original_init = openai._base_client.SyncHttpxClientWrapper.__init__
    
    def patched_init(self, *args, **kwargs):
        # Remove the proxies parameter if it exists
        if 'proxies' in kwargs:
            del kwargs['proxies']
        original_init(self, *args, **kwargs)
    
    # Apply the patch
    openai._base_client.SyncHttpxClientWrapper.__init__ = patched_init
    logger.info("Applied OpenAI client patches")


class ChatClient:
    """Client for interacting with OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        # Apply patches for OpenAI client
        apply_openai_patches()
        
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Initialized OpenAI client")
    
    def get_completion(self, 
                      messages: List[Dict[str, str]], 
                      model: str = "gpt-3.5-turbo",
                      temperature: float = 0.7,
                      max_tokens: int = 1024) -> Optional[str]:
        """Get a completion from the OpenAI API.
        
        Args:
            messages: List of message dictionaries
            model: OpenAI model to use
            temperature: Temperature parameter (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            The response text or None if error
        """
        if not self.client:
            logger.error("Cannot get completion: OpenAI client not initialized")
            return "Error: OpenAI API client not initialized. Please check your API key."
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if the client is available and properly initialized."""
        return self.client is not None