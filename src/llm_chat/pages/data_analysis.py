"""Data analysis with AI for Streamlit multi-page app."""
import streamlit as st
import pandas as pd
import numpy as np
import os
import logging
import openai
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Monkey patch the OpenAI client to bypass the proxies issue
# (Only apply if not already patched in main.py)
if not hasattr(openai, "_patched_for_proxies"):
    original_init = openai._base_client.SyncHttpxClientWrapper.__init__

    def patched_init(self, *args, **kwargs):
        # Remove the proxies parameter if it exists
        if 'proxies' in kwargs:
            del kwargs['proxies']
        original_init(self, *args, **kwargs)

    # Apply the monkey patch
    openai._base_client.SyncHttpxClientWrapper.__init__ = patched_init
    openai._patched_for_proxies = True

# Initialize OpenAI API client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.set_page_config(page_title="AI Data Analysis", page_icon="📊")

st.title("AI Data Analysis")
st.markdown("Upload data and get AI-powered insights.")

# Check if API key is available
if not api_key:
    st.error("OpenAI API Key is missing. Please add it to your .env file.")
    st.stop()

# Generate some sample data if needed
@st.cache_data
def get_sample_data() -> pd.DataFrame:
    """Generate sample data with caching.
    
    Returns:
        pd.DataFrame: Sample dataframe
    """
    logger.info("Generating cached sample data")
    np.random.seed(42)
    data = {
        "category": np.random.choice(["A", "B", "C", "D"], size=100),
        "value1": np.random.randn(100),
        "value2": np.random.randn(100) * 2 + 1,
        "date": pd.date_range(start="2023-01-01", periods=100)
    }
    return pd.DataFrame(data)

# Allow file upload for real data
uploaded_file = st.file_uploader("Upload your CSV data for analysis", type=["csv"])

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        st.success(f"Successfully loaded data with {len(data)} rows and {len(data.columns)} columns")
        logger.info(f"User uploaded file: {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        logger.error(f"File upload error: {e}")
        st.info("Loading sample data instead...")
        data = get_sample_data()
else:
    st.info("No file uploaded. Using sample data for demonstration.")
    data = get_sample_data()

# Display data overview
st.subheader("Data Overview")
st.dataframe(data.head())

# Basic data statistics
col1, col2 = st.columns(2)
with col1:
    st.subheader("Summary Statistics")
    st.dataframe(data.describe())

with col2:
    if "category" in data.columns:
        st.subheader("Category Distribution")
        cat_counts = data["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        st.bar_chart(cat_counts.set_index("Category"))

# AI Analysis section
st.subheader("AI-Powered Data Analysis")

# Initialize chat history for this page
if "data_analysis_messages" not in st.session_state:
    st.session_state.data_analysis_messages = []

# Create a default system message about data analysis
default_system_message = {
    "role": "system", 
    "content": f"You are a helpful data analysis assistant. The user has uploaded a dataset with {len(data)} rows and the following columns: {', '.join(data.columns)}. Help them analyze and understand their data."
}

# Chat input for data analysis questions
analysis_prompt = st.text_area("Ask a question about your data:", 
                              placeholder="Example: What are the key trends in this data? or Can you suggest visualizations for this dataset?",
                              height=100)

if st.button("Analyze"):
    if analysis_prompt:
        # Show spinner while processing
        with st.spinner("Analyzing data..."):
            # Create messages for this specific query
            messages = [default_system_message]
            
            # Add data description to provide context
            data_description = f"""
            Dataset Summary:
            - Shape: {data.shape}
            - Columns: {', '.join(data.columns)}
            - Data Types: {dict(data.dtypes.astype(str))}
            - Sample data (first 5 rows): {data.head().to_dict()}
            - Summary statistics: {data.describe().to_dict()}
            """
            
            messages.append({"role": "user", "content": f"{data_description}\n\nQuestion: {analysis_prompt}"})
            
            try:
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                
                analysis_result = response.choices[0].message.content
                
                # Display the result
                st.markdown("### Analysis Results")
                st.markdown(analysis_result)
                
                # Store in session state
                st.session_state.data_analysis_messages.append({"role": "user", "content": analysis_prompt})
                st.session_state.data_analysis_messages.append({"role": "assistant", "content": analysis_result})
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                logger.error(f"OpenAI API error: {e}")
    else:
        st.warning("Please enter a question about your data.")

# Show previous analysis history
if st.session_state.data_analysis_messages:
    with st.expander("Previous Analysis", expanded=False):
        for msg in st.session_state.data_analysis_messages:
            st.markdown(f"**{msg['role'].title()}**: {msg['content']}")

# Advanced options
with st.expander("Advanced Options"):
    st.subheader("Custom Visualization")
    
    numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()
    
    if len(numeric_cols) >= 2:
        chart_type = st.selectbox(
            "Chart Type",
            options=["Line", "Bar", "Scatter", "Histogram"],
            index=0
        )
        
        selected_cols = st.multiselect(
            "Select columns to visualize",
            options=data.columns.tolist(),
            default=numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols
        )
        
        if selected_cols:
            if chart_type == "Line":
                st.line_chart(data[selected_cols])
            elif chart_type == "Bar":
                st.bar_chart(data[selected_cols])
            elif chart_type == "Scatter" and len(selected_cols) >= 2:
                x_col = st.selectbox("X axis", options=selected_cols, index=0)
                y_col = st.selectbox("Y axis", options=selected_cols, index=min(1, len(selected_cols)-1))
                
                scatter_data = pd.DataFrame({
                    "x": data[x_col],
                    "y": data[y_col]
                })
                st.scatter_chart(scatter_data)
            elif chart_type == "Histogram" and selected_cols:
                for col in selected_cols:
                    st.subheader(f"Histogram of {col}")
                    hist_values = np.histogram(data[col].dropna(), bins=30)[0]
                    st.bar_chart(hist_values)