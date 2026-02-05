"""
StegoTool: Advanced Image Steganography System
==============================================
Main Streamlit Application Entry Point
Run with: streamlit run app.py
"""

import sys
from pathlib import Path
import streamlit as st

# Configure base path for imports
BASE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_PATH))

# Initialize database on startup
from src.db.db_utils import initialize_database
initialize_database()

# Import UI components
from src.db.db_utils import (
    initialize_database,
    add_user,
    verify_user,
    log_operation,
    log_activity
)
from src.analytics.stats import (
    create_timeline_chart,
    create_method_pie_chart,
    create_encode_decode_chart,
    create_method_comparison_chart,
    create_encryption_chart,
    get_activity_dataframe,
    get_statistics_summary
)
from src.ui.ui_components import (
    show_encode_section,
    show_decode_section,
    show_comparison_section,
    show_statistics_section,
    show_auth_section,
    show_batch_processing_section,
    show_pixel_selector_section,
    show_steg_detector_section,
    show_redundancy_section,
    show_watermarking_section
)
from src.ui.styles import apply_dark_theme

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
#                           SESSION STATE INITIALIZATION
# ============================================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Initialize current page in session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "🔐 Encode"

# ============================================================================
#                           NAVIGATION HELPER
# ============================================================================

def set_page(page_name):
    """Set the current page in session state."""
    st.session_state.current_page = page_name

# ============================================================================
#                           MAIN APPLICATION
# ============================================================================

def main():
    """Main application logic."""
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1>🕵️ Image Steganography</h1>
            <p style='font-size: 18px; color: #8B949E;'>
                Secure Message Hiding using LSB and Hybrid DCT/DWT Methods
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Check authentication
    if not st.session_state.logged_in:
        # Show authentication interface
        show_auth_section()
    else:
        # Show main application
        st.sidebar.title(f"👤 {st.session_state.username}")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()
        
        st.sidebar.divider()
        
        # Navigation label
        st.sidebar.markdown("### Navigation")
        
        # Define navigation items
        nav_items = [
            ("🔐 Encode", "encode"),
            ("🔍 Decode", "decode"),
            ("📊 Compare Methods", "compare"),
            ("📈 Statistics", "stats"),
            ("🎯 Pixel Selector", "pixel"),
            ("🔍 Detect Stego", "detect"),
            ("🛡️ Error Correction", "ecc"),
            ("💧 Watermarking", "watermark"),
            ("⚙️ Batch Processing", "batch")
        ]
        
        # Create navigation buttons
        for label, key in nav_items:
            # Highlight the active button
            button_type = "primary" if st.session_state.current_page == label else "secondary"
            if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True, type=button_type):
                set_page(label)
                st.rerun()
        
        st.sidebar.divider()
        
        # Display selected section based on current_page
        page = st.session_state.current_page
        
        if page == "🔐 Encode":
            show_encode_section()
        elif page == "🔍 Decode":
            show_decode_section()
        elif page == "📊 Compare Methods":
            show_comparison_section()
        elif page == "📈 Statistics":
            show_statistics_section()
        elif page == "🎯 Pixel Selector":
            show_pixel_selector_section()
        elif page == "🔍 Detect Stego":
            show_steg_detector_section()
        elif page == "🛡️ Error Correction":
            show_redundancy_section()
        elif page == "💧 Watermarking":
            show_watermarking_section()
        else:  # Batch Processing
            show_batch_processing_section()
        
        # Footer
        st.divider()
        st.markdown("""
            <div style='text-align: center; padding: 20px; color: #8B949E; font-size: 12px;'>
                <p><strong>Image Steganography Application v2.0</strong></p>
                <p>Advanced secure message hiding using LSB, DCT, and DWT steganography techniques</p>
                <p>Powered by StegoTool Framework</p>
            </div>
        """, unsafe_allow_html=True)


# ============================================================================
#                           ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please check the logs for more details.")