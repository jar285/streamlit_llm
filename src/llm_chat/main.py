"""Streamlit application module."""
import streamlit as st
import pandas as pd
import numpy as np
import logging
import importlib.metadata
from pathlib import Path

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


def generate_sample_data() -> pd.DataFrame:
    """Generate sample data for demonstration.
    
    Returns:
        pd.DataFrame: Sample dataframe with random data
    """
    logger.info("Generating sample data")
    np.random.seed(42)  # For reproducible results
    date_range = pd.date_range(start="2023-01-01", periods=20, freq="D")
    
    data = {
        "date": date_range,
        "value_a": np.random.randn(20).cumsum(),
        "value_b": np.random.randn(20).cumsum(),
        "category": np.random.choice(["A", "B", "C"], size=20)
    }
    
    return pd.DataFrame(data)


def create_sidebar() -> dict:
    """Create and process sidebar elements.
    
    Returns:
        dict: Dictionary of sidebar settings
    """
    st.sidebar.header("Settings")
    
    settings = {
        "chart_type": st.sidebar.selectbox(
            "Chart Type",
            options=["Line", "Bar", "Area"],
            index=0
        ),
        "show_raw_data": st.sidebar.checkbox("Show raw data", value=False),
        "smooth_factor": st.sidebar.slider("Smoothing factor", 0, 10, 0),
    }
    
    st.sidebar.header("About")
    st.sidebar.markdown(f"**llm_chat** v{__version__}")
    st.sidebar.markdown("Created with Streamlit")
    
    return settings


def display_chart(data: pd.DataFrame, settings: dict) -> None:
    """Display chart based on settings.
    
    Args:
        data: DataFrame containing the data
        settings: Dictionary of chart settings
    """
    # Apply smoothing if requested
    if settings["smooth_factor"] > 0:
        data = data.copy()
        for col in ["value_a", "value_b"]:
            data[col] = data[col].rolling(
                window=settings["smooth_factor"], 
                min_periods=1
            ).mean()
    
    # Display the appropriate chart type
    if settings["chart_type"] == "Line":
        st.line_chart(data.set_index("date")[["value_a", "value_b"]])
    elif settings["chart_type"] == "Bar":
        st.bar_chart(data.set_index("date")[["value_a", "value_b"]])
    else:  # Area chart
        st.area_chart(data.set_index("date")[["value_a", "value_b"]])
    
    # Show raw data if requested
    if settings["show_raw_data"]:
        st.subheader("Raw Data")
        st.dataframe(data)


def main() -> None:
    """Main Streamlit application."""
    logger.info(f"Starting Streamlit app v{__version__}")
    
    st.set_page_config(
        page_title="llm_chat",
        page_icon="✨",
        layout="wide",
    )
    
    st.title("llm_chat")
    st.caption(f"v{__version__}")
    
    # Create sidebar and get settings
    settings = create_sidebar()
    
    # Main content area
    st.header("Data Visualization")
    
    # Generate sample data
    data = generate_sample_data()
    
    # Display visualizations
    display_chart(data, settings)
    
    # Additional information
    with st.expander("About this application"):
        st.markdown("""
        This is a sample Streamlit application that demonstrates:
        
        - Data visualization with different chart types
        - Interactive controls in the sidebar
        - Expandable sections
        - Responsive layout
        
        Feel free to modify this template for your own needs.
        """)


if __name__ == "__main__":
    main()
