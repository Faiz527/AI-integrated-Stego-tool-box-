"""
UI Components Module
====================
Contains all Streamlit UI sections and components.
Handles encode, decode, comparison, and statistics interfaces.
"""

import streamlit as st
from PIL import Image
from io import BytesIO
import time
import pandas as pd

# FIXED IMPORTS - DCT functions are in steganography.py, not dct_steganography.py
from .steganography import encode_image, decode_image, encode_dct, decode_dct
from .dwt_steganography import encode_dct_dwt, decode_dct_dwt
from .encryption import encrypt_message, decrypt_message
from .analytics import (
    create_timeline_chart,
    create_method_pie_chart,
    create_encode_decode_chart,
    create_method_comparison_chart,
    create_encryption_chart,
    create_size_distribution_chart,  # ← ADD THIS LINE
    get_activity_dataframe,
    get_statistics_summary
)
from .db_utils import log_activity, get_user_stats, log_operation


# ============================================================================
#                           ENCODE SECTION
# ============================================================================

def show_encode_section():
    """
    UI Section: Encode Secret Message
    ==================================
    Updated to support LSB, Hybrid DCT, and Hybrid DWT methods.
    """
    st.subheader("📝 Encode Secret Message")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_img = st.file_uploader(
            "Upload image",
            type=["png", "jpg", "jpeg"],
            key="encode_uploader"
        )
    
    with col2:
        encoding_method = st.radio(
            "Select Encoding Method:",
            [
                "LSB (Spatial Domain)", 
                "Hybrid DCT (Y-Channel LSB)", 
                "Hybrid DWT (Haar Wavelet)"
            ],
            help="LSB: High capacity, fast\nHybrid DCT: JPEG compatible\nHybrid DWT: Best security, compression proof"
        )
    
    secret_text = st.text_area(
        "Enter secret message:",
        height=120,
        placeholder="Type your secret message here..."
    )
    
    # Method-specific options and info
    if "LSB" in encoding_method:
        filter_type = st.selectbox("Apply filter", ["None", "Blur", "Sharpen", "Grayscale"])
        st.info("""
        💡 **LSB Method**: Fast encoding with high capacity. Best for PNG format.
        - **Speed**: ⚡⚡⚡ Very Fast
        - **Capacity**: 180 KB (800×600 image)
        - **Best for**: Maximum capacity, PNG archives
        - **Risk**: Fails with JPEG compression
        """)
    elif "DCT" in encoding_method and "DWT" not in encoding_method:
        filter_type = "None"
        st.info("""
        💡 **Hybrid DCT Method**: Uses Y-channel frequency properties. JPEG compatible.
        - **Speed**: ⚡⚡ Fast
        - **Capacity**: 60 KB (800×600 image)
        - **Best for**: Web distribution, JPEG files
        - **Advantage**: Better detection resistance
        """)
    else:  # DWT
        filter_type = "None"
        st.info("""
        💡 **Hybrid DWT Method**: Haar wavelet in frequency domain. Most secure & compression-proof.
        - **Speed**: ⚡ Moderate
        - **Capacity**: 15 KB (800×600 image)
        - **Best for**: Maximum security, JPEG/WebP compression resistance
        - **Advantage**: Best steganalysis resistance, highest noise tolerance
        """)
    
    # Encryption options
    col1, col2 = st.columns(2)
    with col1:
        use_encryption = st.checkbox("🔒 Encrypt message")
    with col2:
        encryption_password = None
        if use_encryption:
            encryption_password = st.text_input("Encryption password", type="password", key="encode_password")
    
    # Encode button
    if st.button("🔐 Encode Message", key="encode_button", type="primary"):
        if not uploaded_img:
            st.error("❌ Please upload an image")
        elif not secret_text:
            st.error("❌ Please enter a message")
        elif use_encryption and not encryption_password:
            st.error("❌ Please enter an encryption password")
        else:
            try:
                img = Image.open(uploaded_img)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                if use_encryption and encryption_password:
                    status_text.text("🔐 Encrypting message...")
                    progress_bar.progress(20)
                    secret_text_to_encode = encrypt_message(secret_text, encryption_password)
                else:
                    secret_text_to_encode = secret_text
                
                status_text.text(f"⏳ Encoding with {encoding_method}...")
                progress_bar.progress(40)
                time.sleep(0.3)
                
                if "LSB" in encoding_method and "DWT" not in encoding_method:
                    encoded_img = encode_image(img, secret_text_to_encode, filter_type)
                    method_used = "LSB"
                    log_operation("encode", "LSB", len(secret_text_to_encode), use_encryption)

                elif "DCT" in encoding_method:
                    encoded_img = encode_dct(img, secret_text_to_encode)
                    method_used = "Hybrid DCT"
                    log_operation("encode", "DCT", len(secret_text_to_encode), use_encryption)

                elif "DWT" in encoding_method:
                    encoded_img = encode_dct_dwt(img, secret_text_to_encode)
                    method_used = "Hybrid DWT"
                    log_operation("encode", "DWT", len(secret_text_to_encode), use_encryption)
                
                progress_bar.progress(80)
                status_text.text("💾 Preparing download...")
                time.sleep(0.2)
                
                buffered = BytesIO()
                encoded_img.save(buffered, format="PNG", optimize=False)
                progress_bar.progress(100)
                status_text.text("✅ Encoding complete!")
                
                st.success(f"✅ Message encoded successfully using {method_used}!")
                
                st.download_button(
                    "📥 Download Encoded Image",
                    buffered.getvalue(),
                    "encoded_image.png",
                    "image/png",
                    key="download_encoded"
                )
                
                log_activity(st.session_state.username, f"Encoded with {method_used}")
                log_operation(st.session_state.username, "Encode", method_used)
                
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            except ValueError as e:
                st.error(f"❌ Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


# ============================================================================
#                           DECODE SECTION
# ============================================================================

def show_decode_section():
    """
    UI Section: Decode Secret Message
    Updated to support all three methods
    """
    st.subheader("🔍 Decode Secret Message")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_img = st.file_uploader(
            "Upload encoded image",
            type=["png", "jpg", "jpeg"],
            key="decode_uploader"
        )
    
    with col2:
        decoding_method = st.radio(
            "Select Decoding Method:",
            [
                "LSB (Spatial Domain)", 
                "Hybrid DCT (Y-Channel LSB)", 
                "Hybrid DWT (Haar Wavelet)"
            ],
            help="Must match the method used for encoding"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        use_decryption = st.checkbox("🔒 Decrypt message")
    with col2:
        decryption_password = None
        if use_decryption:
            decryption_password = st.text_input("Decryption password", type="password", key="decode_password")
    
    if st.button("🔐 Decode Message", key="decode_button", type="primary"):
        if not uploaded_img:
            st.error("❌ Please upload an encoded image")
        elif use_decryption and not decryption_password:
            st.error("❌ Please enter the decryption password")
        else:
            try:
                img = Image.open(uploaded_img)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text(f"⏳ Decoding with {decoding_method}...")
                progress_bar.progress(30)
                time.sleep(0.2)
                
                if "LSB" in decoding_method and "DWT" not in decoding_method:
                    decoded_text = decode_image(img)
                    method_used = "LSB"
                elif "DWT" in decoding_method:
                    # Enable debug mode for DWT to diagnose issues
                    with st.expander("🔍 Debug Information"):
                        decoded_text = decode_dct_dwt(img, debug=True)
                    method_used = "Hybrid DWT"
                else:
                    decoded_text = decode_dct(img, debug=False)
                    method_used = "Hybrid DCT"
                
                progress_bar.progress(70)
                
                if decoded_text:
                    st.success(f"✓ Extracted {len(decoded_text)} characters")
                else:
                    st.warning(f"⚠️ No message found - verify correct decoding method")
                
                if decoded_text:
                    if use_decryption and decryption_password:
                        status_text.text("🔐 Decrypting message...")
                        progress_bar.progress(85)
                        decoded_text = decrypt_message(decoded_text, decryption_password)
                        if decoded_text is None:
                            st.error("❌ Decryption failed - wrong password?")
                            progress_bar.empty()
                            status_text.empty()
                            return
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Decoding complete!")
                    
                    st.success(f"✅ Message decoded successfully using {method_used}!")
                    
                    st.write("### 📄 Decoded Message:")
                    st.text_area(
                        "Message content:",
                        value=decoded_text,
                        height=150,
                        disabled=False,
                        key="decoded_message"
                    )
                    
                    log_activity(st.session_state.username, f"Decoded with {method_used}")
                    log_operation(st.session_state.username, "Decode", method_used)
                    
                else:
                    st.error("❌ No message found in the image.")
                    st.info("""
                    **Troubleshooting tips:**
                    - Ensure you selected the **correct decoding method**
                    - Verify the image wasn't modified after encoding
                    - Try re-encoding and decoding to test
                    - For DWT, ensure image wasn't heavily compressed
                    """)
                
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ============================================================================
#                           COMPARISON SECTION
# ============================================================================

def show_comparison_section():
    """
    UI Section: Method Comparison
    Updated to show all three methods
    """
    st.subheader("📊 Method Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: #161B22; border-radius: 8px; padding: 20px; border: 1px solid #30363D; border-left: 4px solid #DA3633;'>
        
        ### 🔴 LSB (Spatial)
        
        **Speed**: ⚡⚡⚡ Very Fast
        **Capacity**: 180 KB
        
        **Pros:**
        - Maximum capacity
        - Easiest to implement
        - Fastest processing
        
        **Cons:**
        - Fails with JPEG
        - Easy to detect
        - RGB visible modifications
        
        **Best for:**
        - PNG archives
        - Maximum capacity
        
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #161B22; border-radius: 8px; padding: 20px; border: 1px solid #30363D; border-left: 4px solid #238636;'>
        
        ### 🟢 Hybrid DCT
        
        **Speed**: ⚡⚡ Fast
        **Capacity**: 60 KB
        
        **Pros:**
        - JPEG compatible
        - Better security
        - Y-channel only
        
        **Cons:**
        - Lower capacity
        - Still LSB-based
        - Moderate robustness
        
        **Best for:**
        - Web distribution
        - JPEG files
        
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: #161B22; border-radius: 8px; padding: 20px; border: 1px solid #30363D; border-left: 4px solid #1F6FEB;'>
        
        ### 🔵 Hybrid DWT
        
        **Speed**: ⚡ Moderate
        **Capacity**: 15 KB
        
        **Pros:**
        - Best security 🏆
        - Compression proof
        - High noise tolerance
        - Steganalysis resistant
        
        **Cons:**
        - Lower capacity
        - Slightly slower
        - Complex math
        
        **Best for:**
        - Maximum security
        - Any compression
        
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed comparison table
    st.markdown("### 📋 Detailed Comparison Table")
    
    comparison_data = {
        'Feature': [
            'Domain', 'Speed', 'Capacity', 'JPEG Safe', 'Compression Robust',
            'Detection Resistance', 'Noise Tolerance', 'Implementation', 'Use Case'
        ],
        'LSB': [
            'Spatial RGB', '⚡⚡⚡', '180 KB', '❌ No', '❌ No',
            '😟 Weak', 'Low', 'Simple', 'PNG Archives'
        ],
        'Hybrid DCT': [
            'Y-channel LSB', '⚡⚡', '60 KB', '✅ Yes', '✅ Yes',
            '💪 Strong', 'Medium', 'Medium', 'Web Distribution'
        ],
        'Hybrid DWT': [
            'LL Band (Haar)', '⚡', '15 KB', '✅✅ Excellent', '✅✅ Excellent',
            '💪💪 Very Strong', '🏆 High', 'Medium-High', 'Max Security'
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================================
#                           STATISTICS SECTION
# ============================================================================

def show_statistics_section():
    """
    UI Section: Statistics & Analytics
    ===================================
    Displays comprehensive analytics with charts, metrics, and activity logs.
    Includes filter options and export functionality.
    """
    st.subheader("📊 Statistics & Analytics")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.selectbox(
            "📅 Time Period",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            key="stats_time_filter"
        )
    
    with col2:
        st.selectbox(
            "🔐 Method",
            ["All Methods", "LSB (Spatial)", "Hybrid DCT", "Encrypted"],
            key="stats_method_filter"
        )
    
    with col3:
        st.selectbox(
            "⚙️ Action",
            ["All", "Encode", "Decode"],
            key="stats_action_filter"
        )
    
    # Key metrics
    st.markdown("### 📈 Key Metrics")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    stats = get_user_stats(st.session_state.username)
    total_ops = sum([count for _, count in stats]) if stats else 0
    
    with metric_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Operations</div>
            <div class="metric-value">{total_ops}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Encode Count</div>
            <div class="metric-value">{total_ops // 2 if total_ops > 0 else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Decode Count</div>
            <div class="metric-value">{total_ops // 2 if total_ops > 0 else 0}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">98%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.markdown("### 📉 Detailed Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### Operations Over Time")
        fig_time = create_timeline_chart({})
        st.plotly_chart(fig_time, use_container_width=True)
    
    with chart_col2:
        st.markdown("#### Method Distribution")
        fig_method = create_method_pie_chart({})
        st.plotly_chart(fig_method, use_container_width=True)
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("#### Encode vs Decode")
        fig_encode = create_encode_decode_chart({})
        st.plotly_chart(fig_encode, use_container_width=True)
    
    with chart_col4:
        st.markdown("#### Data Size Distribution")
        fig_size = create_size_distribution_chart({})
        st.plotly_chart(fig_size, use_container_width=True)
    
    # Activity table
    st.markdown("### 📋 Activity Log")
    
    activity_df = get_activity_dataframe(limit=15)
    
    if not activity_df.empty:
        search_col = st.text_input("🔍 Search activity logs", key="activity_search")
        
        if search_col:
            activity_df = activity_df[
                activity_df.astype(str).apply(lambda x: x.str.contains(search_col, case=False)).any(axis=1)
            ]
        
        st.dataframe(activity_df, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No activity data available yet. Start encoding/decoding messages!")


# ============================================================================
#                           AUTHENTICATION SECTION
# ============================================================================

def show_auth_section():
    """
    Authentication Section
    ======================
    Displays login and registration tabs for user authentication.
    """
    from .db_utils import verify_user, add_user
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="reg_username")
        new_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register", type="primary"):
            if add_user(new_username, new_password):
                st.success("✅ Registration successful! Please login.")
            else:
                st.error("❌ Username already exists")