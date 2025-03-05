"""Streamlit application entry point."""
import sys
import os
from pathlib import Path

# Add src directory to Python path to ensure proper imports
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run the main function
import streamlit as st
from llm_chat.main import main

if __name__ == "__main__":
    main()
