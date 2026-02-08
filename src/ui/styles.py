"""
UI Styles Module
================
Contains all custom CSS styling for dark mode theme.
Professional SaaS-style layout with animations.
"""

import streamlit as st


def apply_dark_theme():
    """
    Apply dark theme styling to the entire application.
    
    Features:
    - Dark background (#0E1117)
    - Green accent color (#238636)
    - Custom card-style containers
    - Rounded corners and subtle shadows
    - Professional SaaS-style layout
    - Smooth animations
    """
    st.markdown("""
<style>
    /* ================================================================
       MAIN CONTAINER & BACKGROUND
       ================================================================ */
    .main { background-color: #0E1117; }
    .stApp { background-color: #0E1117; }
    
    /* ================================================================
       TYPOGRAPHY
       ================================================================ */
    h1, h2, h3, h4, h5, h6 { 
        color: #C9D1D9 !important; 
        font-weight: 700; 
    }
    
    p, span, label { color: #8B949E; }
    
    /* ================================================================
       MAIN HEADER
       ================================================================ */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #238636 0%, #1f6feb 100%);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInDown 0.6s ease-out;
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
    
    /* ================================================================
       CARD CONTAINERS
       ================================================================ */
    .card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #30363D;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
    }
    
    .card:hover {
        border-color: #238636;
        box-shadow: 0 8px 24px rgba(35, 134, 54, 0.15);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #C9D1D9;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #30363D;
    }
    
    .card-success {
        border-left: 4px solid #238636;
    }
    
    .card-warning {
        border-left: 4px solid #D29922;
    }
    
    .card-error {
        border-left: 4px solid #F85149;
    }
    
    .card-info {
        border-left: 4px solid #1F6FEB;
    }
    
    /* ================================================================
       FEATURE CARDS (Grid Layout)
       ================================================================ */
    .feature-card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #30363D;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        border-color: #238636;
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: #C9D1D9;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #8B949E;
        font-size: 0.9rem;
    }
    
    /* ================================================================
       METRIC CARDS
       ================================================================ */
    .metric-card {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #30363D;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card:hover {
        border-color: #238636;
        box-shadow: 0 8px 24px rgba(35, 134, 54, 0.2);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #238636;
        margin: 8px 0;
    }
    
    .metric-label {
        color: #8B949E;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ================================================================
       STATUS BADGES
       ================================================================ */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-success {
        background-color: rgba(35, 134, 54, 0.2);
        color: #238636;
        border: 1px solid #238636;
    }
    
    .badge-warning {
        background-color: rgba(210, 153, 34, 0.2);
        color: #D29922;
        border: 1px solid #D29922;
    }
    
    .badge-error {
        background-color: rgba(248, 81, 73, 0.2);
        color: #F85149;
        border: 1px solid #F85149;
    }
    
    .badge-info {
        background-color: rgba(31, 111, 235, 0.2);
        color: #1F6FEB;
        border: 1px solid #1F6FEB;
    }
    
    /* ================================================================
       BUTTONS
       ================================================================ */
    .stButton > button {
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%) !important;
        color: white !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2EA043 0%, #3FB950 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(35, 134, 54, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: #238636 !important;
        color: #238636 !important;
        background: rgba(35, 134, 54, 0.1) !important;
    }
    
    /* ================================================================
       TABS
       ================================================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #161B22;
        border-radius: 10px;
        padding: 6px;
        border: 1px solid #30363D;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        color: #8B949E !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #C9D1D9 !important;
        background-color: rgba(35, 134, 54, 0.1) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%) !important;
        color: white !important;
    }
    
    /* ================================================================
       FORM INPUTS
       ================================================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #238636 !important;
        box-shadow: 0 0 0 3px rgba(35, 134, 54, 0.15) !important;
    }
    
    /* ================================================================
       EXPANDERS
       ================================================================ */
    .streamlit-expanderHeader {
        background-color: #161B22 !important;
        border-radius: 8px !important;
        border: 1px solid #30363D !important;
        color: #C9D1D9 !important;
        transition: all 0.2s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #238636 !important;
    }
    
    .streamlit-expanderContent {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* ================================================================
       ALERTS / MESSAGES
       ================================================================ */
    .stSuccess {
        background-color: rgba(35, 134, 54, 0.1) !important;
        border: 1px solid rgba(35, 134, 54, 0.3) !important;
        border-left: 4px solid #238636 !important;
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        color: #3FB950 !important;
        animation: fadeIn 0.3s ease-out;
    }
    
    .stError {
        background-color: rgba(248, 81, 73, 0.1) !important;
        border: 1px solid rgba(248, 81, 73, 0.3) !important;
        border-left: 4px solid #F85149 !important;
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        color: #F85149 !important;
        animation: fadeIn 0.3s ease-out;
    }
    
    .stWarning {
        background-color: rgba(210, 153, 34, 0.1) !important;
        border: 1px solid rgba(210, 153, 34, 0.3) !important;
        border-left: 4px solid #D29922 !important;
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        color: #E3B341 !important;
        animation: fadeIn 0.3s ease-out;
    }
    
    .stInfo {
        background-color: rgba(31, 111, 235, 0.1) !important;
        border: 1px solid rgba(31, 111, 235, 0.3) !important;
        border-left: 4px solid #1F6FEB !important;
        border-radius: 8px !important;
        padding: 1rem 1.25rem !important;
        color: #79C0FF !important;
        animation: fadeIn 0.3s ease-out;
    }
    
    /* ================================================================
       PROGRESS BAR
       ================================================================ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #238636 0%, #3FB950 100%) !important;
        border-radius: 4px !important;
    }
    
    /* ================================================================
       FILE UPLOADER
       ================================================================ */
    .stFileUploader > div > div > div {
        background-color: #161B22 !important;
        border: 2px dashed #30363D !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }
    
    .stFileUploader > div > div > div:hover {
        border-color: #238636 !important;
        background-color: rgba(35, 134, 54, 0.05) !important;
    }
    
    /* ================================================================
       DATAFRAME / TABLES
       ================================================================ */
    .dataframe {
        background-color: #161B22 !important;
        border-radius: 8px !important;
        border: 1px solid #30363D !important;
    }
    
    /* ================================================================
       SLIDER
       ================================================================ */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #238636 0%, #3FB950 100%) !important;
    }
    
    /* ================================================================
       DIVIDER
       ================================================================ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #30363D, transparent) !important;
        margin: 1.5rem 0 !important;
    }
    
    /* ================================================================
       SIDEBAR
       ================================================================ */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363D !important;
    }
    
    /* ================================================================
       ANIMATIONS
       ================================================================ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Animation classes */
    .animate-fade-in { animation: fadeIn 0.4s ease-out; }
    .animate-fade-in-down { animation: fadeInDown 0.4s ease-out; }
    .animate-fade-in-up { animation: fadeInUp 0.4s ease-out; }
    .animate-slide-in-left { animation: slideInLeft 0.4s ease-out; }
    .animate-scale-in { animation: scaleIn 0.3s ease-out; }
    .animate-pulse { animation: pulse 2s infinite; }
    
    /* Staggered animations */
    .stagger-1 { animation-delay: 0.1s; }
    .stagger-2 { animation-delay: 0.2s; }
    .stagger-3 { animation-delay: 0.3s; }
    .stagger-4 { animation-delay: 0.4s; }
    
    /* ================================================================
       LOTTIE ANIMATION CONTAINER
       ================================================================ */
    .lottie-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem;
    }
    
    /* ================================================================
       RESULT CONTAINER
       ================================================================ */
    .result-container {
        background: linear-gradient(145deg, #161B22 0%, #0D1117 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #238636;
        box-shadow: 0 4px 20px rgba(35, 134, 54, 0.15);
        animation: scaleIn 0.3s ease-out;
    }
    
    /* ================================================================
       IMAGE COMPARISON CONTAINER
       ================================================================ */
    .image-compare-container {
        background: #161B22;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #30363D;
    }
    
    .image-label {
        text-align: center;
        color: #8B949E;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
    }
    
    /* ================================================================
       STEP INDICATOR
       ================================================================ */
    .step-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 0.75rem;
    }
    
    .step-title {
        color: #C9D1D9;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
    """, unsafe_allow_html=True)


# ============================================================================
#                    REUSABLE HTML COMPONENTS
# ============================================================================

def render_card(content, card_type="default", header=None):
    """
    Render a card container with optional header.
    
    Args:
        content: HTML content inside the card
        card_type: 'default', 'success', 'warning', 'error', 'info'
        header: Optional header text
    """
    card_class = f"card card-{card_type}" if card_type != "default" else "card"
    header_html = f'<div class="card-header">{header}</div>' if header else ""
    
    st.markdown(f"""
        <div class="{card_class}">
            {header_html}
            {content}
        </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, icon=""):
    """Render a metric card."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{icon} {label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def render_feature_card(icon, title, description):
    """Render a feature card."""
    st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{description}</div>
        </div>
    """, unsafe_allow_html=True)


def render_badge(text, badge_type="info"):
    """Render a status badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def render_step_header(step_number, title):
    """Render a step indicator with number and title."""
    st.markdown(f"""
        <div class="step-indicator animate-fade-in">
            <div class="step-number">{step_number}</div>
            <div class="step-title">{title}</div>
        </div>
    """, unsafe_allow_html=True)


def render_result_container(content):
    """Render a result container for successful operations."""
    st.markdown(f"""
        <div class="result-container">
            {content}
        </div>
    """, unsafe_allow_html=True)
