"""
Streamlit Main Application
============================
Image Steganography Web Application.
Main entry point - orchestrates all UI components.
"""

import streamlit as st
from pathlib import Path
import sys

# Configure base path
BASE_PATH = Path(__file__).parent.absolute()
sys.path.append(str(BASE_PATH))

# Import modules
from src.db_utils import (
    initialize_database,
    add_user,
    verify_user,
    log_operation,
    log_activity
)
from src.analytics import (
    create_timeline_chart,
    create_method_pie_chart,
    create_encode_decode_chart,
    create_method_comparison_chart,
    create_encryption_chart,
    get_activity_dataframe,
    get_statistics_summary
)
from src.ui_components import (
    show_encode_section,
    show_decode_section,
    show_comparison_section,
    show_statistics_section,
    show_auth_section
)
from src.styles import apply_dark_theme

# ============================================================================
#                           PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ITR Steganography",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
#                           APPLY STYLING
# ============================================================================

apply_dark_theme()

# ============================================================================
#                           MAIN APPLICATION
# ============================================================================

def main():
    """
    Main Application Function
    ==========================
    Orchestrates the main application flow:
    - Displays header
    - Initializes database
    - Handles login/registration
    - Routes to appropriate UI section
    """
    st.markdown("""
        <div class="main-header">
            <h1>🕵️ Image Steganography</h1>
            <p>Secure Message Hiding using LSB and Hybrid DCT Methods</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    if not initialize_database():
        st.stop()
    
    # ===== AUTHENTICATION SECTION =====
    if not st.session_state.get("logged_in", False):
        show_auth_section()
    
    # ===== MAIN APPLICATION (AFTER LOGIN) =====
    else:
        # User info and logout
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.write(f"👤 Welcome, **{st.session_state.username}**!")
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
        
        st.divider()
        
        # Menu navigation
        menu = st.radio(
            "📋 Menu",
            ["Encode", "Decode", "Comparison", "Statistics"],
            horizontal=True
        )
        
        # Route to appropriate section
        if menu == "Encode":
            show_encode_section()
        elif menu == "Decode":
            show_decode_section()
        elif menu == "Comparison":
            show_comparison_section()
        elif menu == "Statistics":
            show_statistics_section()


# ============================================================================
#                           SESSION STATE INITIALIZATION
# ============================================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ============================================================================
#                           ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()