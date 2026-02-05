"""
UI Styles Module
================
Contains all custom CSS styling for dark mode theme.
"""

import streamlit as st


def apply_dark_theme():
    """
    Apply dark theme styling to the entire application.
    
    Features:
    - Dark background (#0E1117)
    - Green accent color (#238636)
    - Custom button styles
    - Message styling
    - Metric card styling
    """
    st.markdown("""
<style>
    /* Main container and background */
    .main { background-color: #0E1117; }
    .stApp { background-color: #0E1117; }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 { color: #C9D1D9 !important; font-weight: 700; }
    
    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #238636 0%, #1f6feb 100%);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        color: #FFFFFF !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: #E6EDF3 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #238636 !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #2EA043 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.4) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #161B22;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #30363D;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 6px !important;
        padding: 12px 20px !important;
        color: #8B949E !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #238636 !important;
        color: white !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #0D1117 !important;
        border-color: #30363D !important;
        color: #C9D1D9 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #238636 !important;
        box-shadow: 0 0 0 2px rgba(35, 134, 54, 0.2) !important;
    }
    
    /* Messages */
    .stSuccess {
        background-color: rgba(35, 134, 54, 0.15) !important;
        border-left: 4px solid #238636 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        color: #AECF97 !important;
    }
    
    .stError {
        background-color: rgba(248, 81, 73, 0.15) !important;
        border-left: 4px solid #F85149 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        color: #F85149 !important;
    }
    
    .stWarning {
        background-color: rgba(230, 171, 39, 0.15) !important;
        border-left: 4px solid #D29922 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        color: #E3B341 !important;
    }
    
    .stInfo {
        background-color: rgba(31, 111, 235, 0.15) !important;
        border-left: 4px solid #1F6FEB !important;
        border-radius: 6px !important;
        padding: 1rem !important;
        color: #79C0FF !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #161B22 0%, #0D1117 100%);
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #30363D;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card:hover {
        border-color: #238636;
        box-shadow: 0 4px 16px rgba(35, 134, 54, 0.2);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #238636;
        margin: 8px 0;
    }
    
    .metric-label {
        color: #8B949E;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Other elements */
    hr { border-color: #30363D !important; }
    .dataframe { background-color: #161B22 !important; }
    .stFileUploader > div > div > div { background-color: #161B22 !important; border-color: #30363D !important; border-radius: 8px !important; }
    .stProgress > div > div > div > div { background-color: #238636 !important; }
</style>
    """, unsafe_allow_html=True)
