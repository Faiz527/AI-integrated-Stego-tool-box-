"""
Main UI Components
==================
Contains the main section components for the application interface.
Features consistent styling, comprehensive help sections, and user-friendly explanations.
"""

import streamlit as st
import logging
from io import BytesIO
from PIL import Image
import pandas as pd
import numpy as np

from src.stego.lsb_steganography import encode_image as lsb_encode, decode_image as lsb_decode
from src.stego.dct_steganography import encode_dct as dct_encode, decode_dct as dct_decode
from src.stego.dwt_steganography import encode_dwt as dwt_encode, decode_dwt as dwt_decode
from src.encryption.encryption import encrypt_message, decrypt_message
from src.db.db_utils import log_activity
from .reusable_components import (
    create_text_input, create_text_area, create_file_uploader,
    create_method_selector, create_checkbox, show_error, show_success,
    display_image_comparison, display_decoded_message,
    create_primary_button, display_results_summary, show_divider,
    show_method_details, create_comparison_table, show_activity_search,
    create_batch_upload_section, create_batch_options_section,
    display_batch_results, display_detailed_results
)
from .config_dict import FORM_LABELS, SECTION_HEADERS, TAB_NAMES, ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)


# ============================================================================
#                    HELPER FUNCTION: INFO BOXES
# ============================================================================

def show_info_box(title, description, use_cases):
    """Display a consistent info box explaining a feature."""
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown("ℹ️ **HELP**")
        
        with col2:
            st.markdown(f"**{title}**")
            st.markdown(description)
            st.markdown("**Use Cases:**")
            for use_case in use_cases:
                st.markdown(f"• {use_case}")
        
        st.markdown("---")


# ============================================================================
#                           AUTHENTICATION SECTION
# ============================================================================

def show_auth_section():
    """Display authentication interface (login/register)."""
    st.subheader(SECTION_HEADERS["auth"])
    
    auth_tab1, auth_tab2 = st.tabs(["🔓 Login", "📝 Register"])
    
    with auth_tab1:
        show_login_form()
    
    with auth_tab2:
        show_register_form()
    
    show_info_box(
        "Authentication System",
        """
        The login and registration system protects your account and keeps track of all your activities.
        Each user has their own private account where all encoding/decoding operations are recorded.
        """,
        [
            "Create a personal account to track your steganography activities",
            "Securely login to access your operation history",
            "Maintain privacy - your messages and data are associated with your account",
            "Enable activity logging for compliance and auditing purposes"
        ]
    )


def show_login_form():
    """Display login form."""
    with st.form("login_form"):
        username = create_text_input(
            label=FORM_LABELS["username"]["label"],
            placeholder="Enter username"
        )
        password = create_text_input(
            label=FORM_LABELS["password"]["label"],
            password=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.form_submit_button("Login", use_container_width=True, type="primary"):
                if username and password:
                    try:
                        from src.db.db_utils import verify_user
                        user_data = verify_user(username, password)
                        
                        if user_data:
                            st.session_state.logged_in = True
                            st.session_state.username = user_data['username']
                            st.session_state.user_id = user_data['user_id']
                            show_success(SUCCESS_MESSAGES["login_success"])
                            st.rerun()
                        else:
                            show_error("❌ Invalid username or password")
                    except Exception as e:
                        show_error(f"Login error: {str(e)}")
                else:
                    show_error(ERROR_MESSAGES["empty_fields"])


def show_register_form():
    """Display registration form."""
    with st.form("register_form"):
        username = create_text_input(
            label=FORM_LABELS["username"]["label"],
            placeholder="Choose a username"
        )
        password = create_text_input(
            label=FORM_LABELS["password"]["label"],
            password=True
        )
        confirm_password = create_text_input(
            label="Confirm Password",
            password=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.form_submit_button("Register", use_container_width=True, type="primary"):
                if not (username and password and confirm_password):
                    show_error(ERROR_MESSAGES["fields_required"])
                elif password != confirm_password:
                    show_error(ERROR_MESSAGES["passwords_mismatch"])
                elif len(password) < 6:
                    show_error(ERROR_MESSAGES["min_password_length"])
                else:
                    try:
                        from src.db.db_utils import add_user
                        add_user(username, password)
                        show_success(SUCCESS_MESSAGES["registration_success"])
                    except Exception as e:
                        show_error(f"Registration error: {str(e)}")


# ============================================================================
#                           ENCODE SECTION (UPDATED)
# ============================================================================

def show_encode_section():
    """Display encoding interface."""
    st.subheader(SECTION_HEADERS["encode"])
    
    st.markdown("### Step 1: Upload Your Image")
    col1, col2 = st.columns(2)
    
    with col1:
        image_file = create_file_uploader(file_type="images")
        if image_file:
            try:
                original_image = Image.open(image_file)
                # Check image format
                file_format = original_image.format
                st.image(original_image, caption="Your Image", use_container_width=True)
                if file_format == "JPEG":
                    st.warning("⚠️ JPG images use lossy compression which may corrupt encoded data. PNG recommended.")
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    with col2:
        st.info("📤 **Supported Formats:** PNG, JPG, BMP, GIF\n\n**📌 Best Format:** PNG (lossless)\n\n**Max Size:** 200MB")
    
    st.markdown("---")
    st.markdown("### Step 2: Choose Method & Message")
    
    col1, col2 = st.columns(2)
    
    with col1:
        method = create_method_selector()
        st.markdown("""
        **Method Explained:**
        - **LSB:** ⚡ Fastest, spatial domain, works with PNG/BMP
        - **DCT:** 🛡️ Frequency domain, requires PNG format
        - **DWT:** 🔐 Wavelet domain, requires PNG format
        
        **⚠️ Warning:** DCT and DWT methods don't work with JPG files (lossy compression destroys data)
        """)
    
    with col2:
        message = create_text_area(
            label=FORM_LABELS["message"]["label"],
            max_chars=FORM_LABELS["message"]["max_chars"]
        )
    
    st.markdown("---")
    st.markdown("### Step 3: Optional Encryption")
    
    use_encryption = create_checkbox("🔒 Encrypt message before hiding (Recommended)")
    encryption_password = None
    if use_encryption:
        encryption_password = create_text_input(
            label="Encryption password",
            placeholder="Create a strong password",
            password=True
        )
        st.info("Your message will be encrypted with AES-256 before being hidden in the image.")
    
    st.markdown("---")
    st.markdown("### Step 4: Encode")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔐 Encode Message", use_container_width=True, type="primary"):
            if not image_file or not message:
                show_error("Please provide both an image and a message")
            else:
                try:
                    with st.spinner("Encoding your message..."):
                        original_image = Image.open(image_file)
                        
                        # Check format compatibility
                        file_format = original_image.format
                        if file_format == "JPEG" and method in ["Hybrid DCT", "Hybrid DWT"]:
                            show_error(f"❌ {method} doesn't work with JPG files. Please use PNG, BMP, or GIF format.")
                        else:
                            message_to_embed = message
                            if use_encryption and encryption_password:
                                message_to_embed = encrypt_message(message, encryption_password)
                            
                            if method == "LSB":
                                encoded_image = lsb_encode(original_image, message_to_embed)
                            elif method == "Hybrid DCT":
                                encoded_image = dct_encode(original_image, message_to_embed)
                            elif method == "Hybrid DWT":
                                encoded_image = dwt_encode(original_image, message_to_embed)
                            else:
                                encoded_image = lsb_encode(original_image, message_to_embed)
                            
                            st.divider()
                            st.markdown("### ✅ Encoding Complete!")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.image(original_image, caption="Original Image", use_container_width=True)
                            with col2:
                                st.image(encoded_image, caption="Image with Hidden Message", use_container_width=True)
                            

                            # Download button
                            buf = BytesIO()
                            encoded_image.save(buf, format="PNG")
                            buf.seek(0)
                            
                            st.download_button(
                                label="⬇️ Download Encoded Image (as PNG)",
                                data=buf.getvalue(),
                                file_name=f"encoded_{method}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                            
                            if hasattr(st.session_state, 'user_id'):
                                log_activity(
                                    st.session_state.user_id,
                                    "ENCODE",
                                    f"Encoded message using {method}"
                                )
                            
                            show_success("Your message has been successfully hidden in the image!")
                        
                except Exception as e:
                    show_error(f"Encoding error: {str(e)}")
                    logger.error(f"Encoding error: {str(e)}")
    
    show_info_box(
        "Image Encoding (Steganography)",
        """
        Encoding hides your secret message inside an image file. The image looks completely normal,
        but it contains your hidden message that only someone with the password can extract.
        This is perfect for secure communication without anyone knowing a message exists.
        """,
        [
            "Send secret messages through images without anyone knowing",
            "Protect sensitive information from casual inspection",
            "Use encryption for double-layer security",
            "Share images publicly - only intended recipients can read the message",
            "Always save as PNG for maximum compatibility (never JPG)"
        ]
    )


# ============================================================================
#                           DECODE SECTION (UPDATED)
# ============================================================================

def show_decode_section():
    """Display decoding interface."""
    st.subheader(SECTION_HEADERS["decode"])
    
    st.markdown("### Step 1: Upload Encoded Image")
    
    col1, col2 = st.columns(2)
    
    with col1:
        image_file = create_file_uploader(file_type="images")
        if image_file:
            try:
                image = Image.open(image_file)
                file_format = image.format
                st.image(image, caption="Uploaded Image", use_container_width=True)
                if file_format == "JPEG":
                    st.warning("⚠️ JPG images use lossy compression. If data was encoded with DCT/DWT, it won't decode correctly.")
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    with col2:
        st.info("📥 Upload an image that contains a hidden message\n\n**💡 Tip:** Use the exact PNG file you downloaded from encoding")
    
    st.markdown("---")
    st.markdown("### Step 2: Decryption (if encrypted)")
    
    use_encryption = create_checkbox("🔓 Message is encrypted - I have the password")
    decryption_password = None
    if use_encryption:
        decryption_password = create_text_input(
            label="Enter decryption password",
            placeholder="Enter the password used during encryption",
            password=True
        )
    
    st.markdown("---")
    st.markdown("### Step 3: Extract Message")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔍 Decode Message", use_container_width=True, type="primary"):
            if not image_file:
                show_error("Please upload an image first")
            else:
                try:
                    with st.spinner("Extracting message..."):
                        image = Image.open(image_file)
                        
                        decoded_message = None
                        method_used = None
                        
                        # Try each method and validate the result
                        for method_name, method_func in [
                            ("LSB", lsb_decode),
                            ("Hybrid DCT", dct_decode),
                            ("Hybrid DWT", dwt_decode)
                        ]:
                            try:
                                extracted = method_func(image)
                                
                                # Validate extracted message
                                if extracted and is_valid_message(extracted):
                                    decoded_message = extracted
                                    method_used = method_name
                                    break
                            except:
                                continue
                        
                        if decoded_message and method_used:
                            if use_encryption and decryption_password:
                                try:
                                    decoded_message = decrypt_message(decoded_message, decryption_password)
                                except:
                                    show_error("❌ Decryption failed - wrong password?")
                                    decoded_message = None
                            
                            if decoded_message:
                                st.divider()
                                st.markdown("### ✅ Message Found!")
                                st.markdown(f"**Detected Method:** {method_used}")
                                
                                st.success("Your hidden message:")
                                st.text_area("Decoded Message", value=decoded_message, height=150, disabled=True)
                                
                                if hasattr(st.session_state, 'user_id'):
                                    log_activity(
                                        st.session_state.user_id,
                                        "DECODE",
                                        f"Decoded message using {method_used}"
                                    )
                        else:
                            st.error("❌ No hidden message found in this image")
                            st.markdown("**Possible reasons:**")
                            st.markdown("""
                            - Image doesn't contain an encoded message
                            - JPG compression corrupted the data (use PNG instead)
                            - Image was modified or resized
                            - Wrong encoding method or password
                            - Use the original PNG file you downloaded from encoding
                            """)
                            
                except Exception as e:
                    show_error(f"Decoding error: {str(e)}")
                    logger.error(f"Decoding error: {str(e)}")
    
    show_info_box(
        "Image Decoding (Message Extraction)",
        """
        Decoding extracts the hidden message from an image. The system automatically detects
        which encoding method was used. If the message was encrypted, you need the password
        to read it. Without the correct password, the decrypted message will be gibberish.
        """,
        [
            "Extract secret messages from received images",
            "Automatically detect the encoding method used",
            "Decrypt messages if they were encrypted",
            "Verify message integrity and authenticity",
            "Always use the original PNG file (never convert to JPG)"
        ]
    )


# ============================================================================
#                           COMPARISON SECTION (FIXED)
# ============================================================================

def show_comparison_section():
    """Display method comparison interface."""
    st.subheader(SECTION_HEADERS["comparison"])
    
    st.markdown("### Compare All Three Methods")
    
    comparison_data = {
        "Method": ["LSB", "Hybrid DCT", "Hybrid DWT"],
        "Speed": ["⚡ Very Fast", "⚡ Fast", "⚡ Fast"],
        "Capacity": ["📦 High", "📦 Medium", "📦 Medium"],
        "Robustness": ["🛡️ Low", "🛡️ High", "🛡️ High"],
        "Imperceptibility": ["👁️ Good", "👁️ Excellent", "👁️ Excellent"]
    }
    
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Test All Methods on Your Image")
    
    col1, col2 = st.columns(2)
    
    with col1:
        image_file = create_file_uploader(file_type="images", key="compare_img")
    
    with col2:
        # FIXED: Use st.text_area instead of create_text_area, use value parameter directly
        message = st.text_area(
            "Test message",
            value="Test message",
            max_chars=100
        )
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔄 Compare Methods", use_container_width=True, type="primary"):
            if not image_file or not message:
                show_error("Please provide both an image and a message")
            else:
                try:
                    with st.spinner("Comparing all methods..."):
                        original_image = Image.open(image_file)
                        
                        methods = ["LSB", "Hybrid DCT", "Hybrid DWT"]
                        results = {}
                        
                        for method in methods:
                            try:
                                if method == "LSB":
                                    encoded = lsb_encode(original_image, message)
                                elif method == "Hybrid DCT":
                                    encoded = dct_encode(original_image, message)
                                elif method == "Hybrid DWT":
                                    encoded = dwt_encode(original_image, message)
                                
                                results[method] = encoded
                            except Exception as e:
                                results[method] = None
                        
                        st.divider()
                        st.markdown("### Results")
                        
                        cols = st.columns(3)
                        for col, method in zip(cols, methods):
                            with col:
                                if results[method]:
                                    st.image(results[method], caption=f"✅ {method}", use_container_width=True)
                                    st.caption("Encoding successful")
                                else:
                                    st.warning(f"❌ {method} failed")
                        
                except Exception as e:
                    show_error(f"Comparison error: {str(e)}")
    
    show_info_box(
        "Method Comparison",
        """
        Different methods hide messages in different ways. This feature lets you test all three methods
        on the same image to compare results visually. Some methods are better for certain types of images.
        """,
        [
            "See visual differences between encoding methods",
            "Test which method works best for your images",
            "Understand trade-offs between speed and robustness",
            "Choose the best method for your use case",
            "Compare file sizes and image quality"
        ]
    )


# ============================================================================
#                           STATISTICS SECTION (FIXED)
# ============================================================================

def show_statistics_section():
    """Display statistics and analytics."""
    st.subheader(SECTION_HEADERS["statistics"])
    
    try:
        from src.analytics.stats import (
            get_statistics_summary, 
            get_activity_dataframe,
            create_timeline_chart,
            create_method_pie_chart,
            create_size_distribution_chart
        )
        
        # Get user ID from session state if logged in
        user_id = st.session_state.get('user_id') if hasattr(st.session_state, 'user_id') else None
        
        st.markdown("### 📊 Your Activity Summary")
        stats = get_statistics_summary(user_id=user_id)
        
        if stats and isinstance(stats, dict):
            # FIXED: Filter and convert stats to proper numeric format
            metric_cols = st.columns(min(3, len(stats)))
            col_idx = 0
            
            for key, value in stats.items():
                # Skip empty or non-numeric values
                if value is None or value == {} or value == []:
                    continue
                
                try:
                    # Convert to int if possible
                    numeric_value = int(value) if isinstance(value, (int, float)) else str(value);
                    
                    with metric_cols[col_idx % 3]:
                        st.metric(key, numeric_value)
                    col_idx += 1
                except (ValueError, TypeError):
                    # Skip values that can't be converted
                    pass
        else:
            st.info("📊 No activity recorded yet. Start encoding/decoding to see statistics!")
        
        st.divider()
        
        st.markdown("### 📈 Activity Charts")
        
        try:
            activity_df = get_activity_dataframe(user_id=user_id)
            
            if activity_df is not None and not activity_df.empty:
                # Create three columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Activity Timeline (Last 7 Days)")
                    timeline_fig = create_timeline_chart(user_id=user_id)
                    st.plotly_chart(timeline_fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### Methods Used")
                    method_fig = create_method_pie_chart(user_id=user_id)
                    st.plotly_chart(method_fig, use_container_width=True)
                
                st.divider()
                
                st.markdown("#### Message Sizes")
                size_fig = create_size_distribution_chart(user_id=user_id)
                st.plotly_chart(size_fig, use_container_width=True)
                
                st.divider()
                st.markdown("#### Activity History")
                
                # Display activity dataframe with filtering
                if 'Timestamp' in activity_df.columns:
                    activity_df['Timestamp'] = pd.to_datetime(activity_df['Timestamp'])
                    activity_df = activity_df.sort_values('Timestamp', ascending=False)
                    
                    # Simple display of recent activities
                    st.dataframe(
                        activity_df[['Action', 'Details', 'Timestamp']].head(20),
                        use_container_width=True
                    )
                else:
                    st.dataframe(activity_df.head(20), use_container_width=True)
            else:
                st.info("📋 No activities recorded yet. Start encoding/decoding to see your statistics!")
        except Exception as chart_error:
            logger.warning(f"Could not load activity charts: {str(chart_error)}")
            st.info("📊 Charts will appear after you perform encoding/decoding operations")
        
    except Exception as e:
        show_error(f"Statistics error: {str(e)}")
        logger.error(f"Statistics error: {str(e)}")
    
    show_info_box(
        "Activity Statistics & Analytics",
        """
        This dashboard shows your complete activity history - every encoding, decoding, and test
        you've performed. It helps you track what you've done and analyze your usage patterns.
        All data is private and associated only with your account.
        """,
        [
            "Track all your encoding and decoding activities",
            "See statistics about your usage patterns",
            "Filter and search through your activity history",
            "Maintain audit trail for compliance",
            "Understand which methods you use most"
        ]
    )


# ============================================================================
#                           BATCH PROCESSING SECTION
# ============================================================================

def show_batch_processing_section():
    """Display batch processing interface."""
    st.subheader(SECTION_HEADERS["batch"])
    
    st.markdown("### Process Multiple Images at Once")
    
    batch_mode = st.radio("Select operation", ["⏱️ Batch Encode", "🔍 Batch Decode"], horizontal=True)
    
    st.divider()
    
    if batch_mode == "⏱️ Batch Encode":
        show_batch_encode()
    else:
        show_batch_decode()


def show_batch_encode():
    """Display batch encoding interface."""
    st.markdown("### Batch Image Encoding")
    
    upload_type, uploaded_files = create_batch_upload_section()
    
    if uploaded_files:
        st.markdown(f"**Files selected:** {len(uploaded_files)}")
        
        st.divider()
        st.markdown("### Configure Encoding")
        
        col1, col2 = st.columns(2)
        
        with col1:
            method, message, use_encryption, encryption_password = create_batch_options_section()
        
        with col2:
            st.info("⚙️ Same settings will be applied to all images")
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("▶️ Start Batch Encoding", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Processing batch..."):
                        results = []
                        success_count = 0
                        failed_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, uploaded_file in enumerate(uploaded_files):
                            status_text.text(f"Processing: {uploaded_file.name}")
                            
                            try:
                                image = Image.open(uploaded_file)
                                
                                message_to_embed = message
                                if use_encryption and encryption_password:
                                    message_to_embed = encrypt_message(message, encryption_password)
                                
                                if method == "LSB":
                                    encoded = lsb_encode(image, message_to_embed)
                                elif method == "Hybrid DCT":
                                    encoded = dct_encode(image, message_to_embed)
                                elif method == "Hybrid DWT":
                                    encoded = dwt_encode(image, message_to_embed)
                                else:
                                    encoded = lsb_encode(image, message_to_embed)
                                
                                output_path = f"data/output/encoded/{method}/{uploaded_file.name}"
                                encoded.save(output_path)
                                
                                results.append({
                                    "filename": uploaded_file.name,
                                    "status": "✅ Success",
                                    "output": output_path
                                })
                                success_count += 1
                                
                            except Exception as e:
                                results.append({
                                    "filename": uploaded_file.name,
                                    "status": f"❌ Failed"
                                })
                                failed_count += 1
                            
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                        
                        st.divider()
                        st.markdown("### 📊 Batch Results")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", len(uploaded_files))
                        with col2:
                            st.metric("Success", success_count, delta="✅")
                        with col3:
                            st.metric("Failed", failed_count, delta="❌")
                        
                        st.dataframe(pd.DataFrame(results), use_container_width=True)
                        
                        if success_count > 0:
                            show_success(f"Successfully encoded {success_count} images!")
                        
                except Exception as e:
                    show_error(f"Batch encoding error: {str(e)}")
    
    show_info_box(
        "Batch Encoding",
        """
        Batch encoding lets you hide the same message in multiple images at once.
        This is perfect when you need to send the same message to multiple people or create backups.
        All images will be processed with the same settings and saved automatically.
        """,
        [
            "Encode many images quickly without repeating steps",
            "Use the same message for multiple recipients",
            "Create multiple copies with the same hidden data",
            "Save time on repetitive encoding tasks",
            "Automatic progress tracking and error reporting"
        ]
    )


def show_batch_decode():
    """Display batch decoding interface."""
    st.markdown("### Batch Image Decoding")
    
    upload_type, uploaded_files = create_batch_upload_section()
    
    if uploaded_files:
        st.markdown(f"**Files selected:** {len(uploaded_files)}")
        
        st.divider()
        
        use_encryption = create_checkbox("🔐 Messages are encrypted - I have the password")
        decryption_password = None
        if use_encryption:
            decryption_password = create_text_input(
                label="Decryption password",
                placeholder="Enter the password",
                password=True
            )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("▶️ Start Batch Decoding", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Processing batch..."):
                        results = []
                        success_count = 0
                        failed_count = 0
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, uploaded_file in enumerate(uploaded_files):
                            status_text.text(f"Processing: {uploaded_file.name}")
                            
                            try:
                                image = Image.open(uploaded_file)
                                
                                decoded_message = None
                                for method_func in [lsb_decode, dct_decode, dwt_decode]:
                                    try:
                                        decoded_message = method_func(image)
                                        if decoded_message:
                                            break
                                    except:
                                        continue
                                
                                if decoded_message:
                                    if use_encryption and decryption_password:
                                        decoded_message = decrypt_message(decoded_message, decryption_password)
                                    
                                    results.append({
                                        "filename": uploaded_file.name,
                                        "status": "✅ Success",
                                        "message_length": len(decoded_message),
                                        "preview": decoded_message[:50] + "..." if len(decoded_message) > 50 else decoded_message
                                    })
                                    success_count += 1
                                else:
                                    results.append({
                                        "filename": uploaded_file.name,
                                        "status": "❌ No message found"
                                    })
                                    failed_count += 1
                                    
                            except Exception as e:
                                results.append({
                                    "filename": uploaded_file.name,
                                    "status": f"❌ Error"
                                })
                                failed_count += 1
                            
                            progress_bar.progress((idx + 1) / len(uploaded_files))
                        
                        st.divider()
                        st.markdown("### 📊 Batch Results")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total", len(uploaded_files))
                        with col2:
                            st.metric("Success", success_count, delta="✅")
                        with col3:
                            st.metric("Failed", failed_count, delta="❌")
                        
                        st.dataframe(pd.DataFrame(results), use_container_width=True)
                        
                        if success_count > 0:
                            show_success(f"Successfully decoded {success_count} messages!")
                        
                except Exception as e:
                    show_error(f"Batch decoding error: {str(e)}")
    
    show_info_box(
        "Batch Decoding",
        """
        Batch decoding extracts hidden messages from multiple images at once.
        Perfect for processing a collection of received images and seeing what messages they contain.
        The system automatically detects the encoding method used in each image.
        """,
        [
            "Extract messages from many images quickly",
            "See all messages in one organized view",
            "Automatic method detection for each image",
            "Handle encrypted messages with one password",
            "Get a summary of what was found in each image"
        ]
    )


# ============================================================================
#                    MODULE 3: ADVANCED PIXEL SELECTOR
# ============================================================================

def show_pixel_selector_section():
    """Display advanced pixel selection analysis."""
    st.subheader("🎯 Module 3: Intelligent Pixel Selection")
    
    st.markdown("""
    This advanced tool analyzes your image and identifies the best pixels for hiding messages.
    Better pixels mean more secure and imperceptible hiding.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Step 1: Upload Image")
        image_file = create_file_uploader(file_type="images", key="pixel_selector_img")
        
        if image_file:
            try:
                image = Image.open(image_file)
                st.image(image, caption="Your Image", use_container_width=True)
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    with col2:
        st.markdown("### Step 2: Configure Analysis")
        
        payload_bits = st.number_input(
            "How many bits do you want to hide?",
            min_value=8,
            max_value=100000,
            value=256,
            step=8,
            help="More bits = more hidden data = need more good pixels"
        )
        
        patch_size = st.slider(
            "Analysis detail level (3=detailed, 9=broad)",
            min_value=3,
            max_value=9,
            value=5,
            step=2
        )
        
        lsb_bits = st.selectbox(
            "Bits per channel to use",
            [1, 2, 4, 8],
            index=0,
            help="1 = safest, 8 = most capacity"
        )
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if image_file and st.button("🔬 Analyze Pixels", use_container_width=True, type="primary"):
            try:
                with st.spinner("Analyzing image quality..."):
                    from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels
                    
                    image = Image.open(image_file)
                    arr = np.array(image.convert("RGB"))
                    h, w, _ = arr.shape;
                    
                    # Select pixels
                    selected_coords = select_pixels(
                        arr,
                        payload_bits=payload_bits,
                        patch_size=patch_size,
                        lsb_bits=lsb_bits,
                        seed=0
                    )
                    
                    st.divider()
                    st.markdown("### ✅ Analysis Results")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Image Size", f"{w}×{h}")
                    with col2:
                        st.metric("Total Pixels", f"{w*h:,}")
                    with col3:
                        st.metric("Best Pixels Found", len(selected_coords))
                    with col4:
                        coverage = (len(selected_coords) / (w * h)) * 100
                        st.metric("Coverage", f"{coverage:.1f}%")
                    
                    st.divider()
                    
                    # Visualization
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original Image**")
                        st.image(arr, use_column_width=True)
                    
                    with col2:
                        st.markdown("**Best Pixels (marked in red)**")
                        overlay = arr.copy()
                        for x, y in selected_coords[:100]:
                            if 0 <= x < w and 0 <= y < h:
                                overlay[y, x] = [255, 0, 0]
                        st.image(overlay, use_column_width=True)
                    
                    st.divider()
                    st.markdown("**First 20 Best Pixel Locations:**")
                    coords_df = pd.DataFrame(selected_coords[:20], columns=["X", "Y"])
                    st.dataframe(coords_df, use_container_width=True)
                    
                    show_success("Analysis complete! The red pixels are the best places to hide your message.")
                    
            except Exception as e:
                show_error(f"Analysis error: {str(e)}")
                logger.error(f"Pixel selection error: {str(e)}")
    
    show_info_box(
        "Intelligent Pixel Selection",
        """
        This tool finds the perfect pixels in your image for hiding messages. Some pixels are better
        than others because they're less likely to be noticed when modified. The system analyzes texture
        and patterns to find pixels you can safely modify without visible changes.
        """,
        [
            "Find optimal pixels for maximum imperceptibility",
            "Understand which parts of your image are best for hiding",
            "Visualize where messages will be hidden",
            "Make better choices about images to use",
            "Learn about image properties and entropy"
        ]
    )


# ============================================================================
#                    MODULE 5: STEGANOGRAPHY DETECTOR (FIXED)
# ============================================================================

def show_steg_detector_section():
    """Display steganography detection analysis."""
    st.subheader("🔍 Module 5: Steganography Detector")
    
    st.markdown("""
    This tool analyzes images to check if they contain hidden messages.
    Perfect for verifying image authenticity or detecting suspicious images.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload Image to Analyze")
        
        suspicious_file = create_file_uploader(file_type="images", key="suspicious_img")
        if suspicious_file:
            suspicious_image = Image.open(suspicious_file)
            st.image(suspicious_image, caption="Image to Analyze", use_container_width=True)
    
    with col2:
        st.markdown("### Detection Settings")
        
        sensitivity = st.slider(
            "Detection Sensitivity (1=relaxed, 10=strict)",
            min_value=1,
            max_value=10,
            value=5
        )
        
        st.info(f"Sensitivity: {sensitivity}/10 - {'Low (few false positives)' if sensitivity < 4 else 'Balanced (recommended)' if sensitivity < 7 else 'High (strict detection)'}")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if suspicious_file and st.button("🔎 Analyze Image", use_container_width=True, type="primary"):
            try:
                with st.spinner("Analyzing image for hidden content..."):
                    arr = np.array(suspicious_image.convert("RGB"))
                    
                    # FIXED: Use multiple detection metrics for better accuracy
                    detection_score, analysis_data = analyze_image_for_steganography(arr, sensitivity)
                    
                    st.divider()
                    st.markdown("### Analysis Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Image Statistics**")
                        stats_df = pd.DataFrame(analysis_data)
                        st.dataframe(stats_df, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Detection Result**")
                        
                        # Determine verdict based on detection score
                        if detection_score < 25:
                            emoji = "🟢"
                            verdict = "Clean Image"
                            explanation = "This image shows natural patterns consistent with normal photography. No hidden data detected."
                        elif detection_score < 50:
                            emoji = "🟡"
                            verdict = "Uncertain"
                            explanation = "Image shows some statistical anomalies but could be due to compression or editing. Not conclusive."
                        else:
                            emoji = "🔴"
                            verdict = "Suspicious - Possible Hidden Data"
                            explanation = "Image shows multiple signs of data embedding. Hidden message might be present."
                        
                        st.metric(f"{emoji} Detection Score", f"{detection_score:.1f}%")
                        st.subheader(verdict)
                        st.write(explanation)
                    
                    st.divider()
                    st.markdown("**Detection Method:**")
                    st.markdown("""
                    This detector analyzes multiple image properties:
                    - **Bit-plane entropy:** Checks if LSBs appear random (LSB embedding signature)
                    - **Chi-square test:** Measures pixel value distribution (compression artifacts)
                    - **Local variance:** Looks for suspicious patterns in image regions
                    - **Histogram shape:** Checks for unusual peaks indicating manipulation
                    
                    **Note:** This is a heuristic detector and may have false positives/negatives.
                    """)
                    
                    show_success("Analysis complete!")
                    
            except Exception as e:
                show_error(f"Detection error: {str(e)}")
                logger.error(f"Detection error: {str(e)}")
    
    show_info_box(
        "Steganography Detection",
        """
        This tool checks if an image contains hidden data by analyzing statistical patterns.
        Images with hidden messages often show different patterns than normal images.
        This is useful for security checks, authenticating images, or investigative purposes.
        """,
        [
            "Detect if an image contains hidden messages",
            "Verify image authenticity and integrity",
            "Analyze image for suspicious patterns",
            "Investigate potentially compromised images",
            "Understand image randomness and entropy"
        ]
    )


def analyze_image_for_steganography(img_array, sensitivity):
    """
    Analyze image using multiple metrics to detect steganography.
    
    FIXED: Better detection algorithm that doesn't give false positives on clean images.
    
    Args:
        img_array (np.ndarray): Image pixel array (RGB)
        sensitivity (int): Detection sensitivity (1-10, where 10 is strictest)
    
    Returns:
        tuple: (detection_score, analysis_data_dict)
    """
    try:
        from scipy.stats import entropy, chisquare
        
        detection_indicators = []
        
        # ========== METRIC 1: LSB Entropy (Most important for LSB embedding) ==========
        # Extract LSB plane and check entropy
        lsb_plane = (img_array & 1).flatten()
        lsb_entropy = entropy(np.bincount(lsb_plane, minlength=2))
        
        # Clean images typically have LSB entropy around 0.5-0.8
        # Embedded data has entropy closer to 1.0
        if lsb_entropy > 0.85:
            detection_indicators.append(("LSB Entropy (High)", lsb_entropy, 30))
        else:
            detection_indicators.append(("LSB Entropy (Normal)", lsb_entropy, 0))
        
        # ========== METRIC 2: Histogram Flatness (Chi-square test) ==========
        # Check if pixel distribution is too uniform (sign of embedding)
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
        expected_freq = len(img_array.flatten()) / 256
        
        # Chi-square goodness of fit test
        chi2_stat = np.sum((hist - expected_freq) ** 2 / (expected_freq + 1))
        
        # Clean images have varied histogram
        # Embedded data can flatten it
        if chi2_stat < 100:
            detection_indicators.append(("Histogram Flatness", chi2_stat, 20))
        else:
            detection_indicators.append(("Histogram Flatness", chi2_stat, 0))
        
        # ========== METRIC 3: Bit-plane Analysis ==========
        # Check randomness in each bit plane
        bit_plane_entropies = []
        for bit in range(8):
            bit_plane = ((img_array >> bit) & 1).flatten()
            bp_entropy = entropy(np.bincount(bit_plane, minlength=2))
            bit_plane_entropies.append(bp_entropy)
        
        # Average entropy across bit planes
        avg_bp_entropy = np.mean(bit_plane_entropies)
        
        # Clean images have lower entropy in higher bits
        # Embedded LSB data makes LSB plane very random (≈1.0)
        if bit_plane_entropies[0] > 0.95:  # LSB is very random
            detection_indicators.append(("Bit-Plane Randomness (High)", bit_plane_entropies[0], 25))
        else:
            detection_indicators.append(("Bit-Plane Randomness", bit_plane_entropies[0], 0))
        
        # ========== METRIC 4: Regional Variance Analysis ==========
        # Divide image into regions and check for uniform patches
        h, w = img_array.shape[:2]
        region_size = 16
        variance_scores = []
        
        for y in range(0, h - region_size, region_size):
            for x in range(0, w - region_size, region_size):
                region = img_array[y:y+region_size, x:x+region_size]
                var = np.var(region)
                variance_scores.append(var)
        
        avg_variance = np.mean(variance_scores)
        
        # Very low regional variance might indicate encoding
        if avg_variance < 100 and len(variance_scores) > 0:
            detection_indicators.append(("Regional Variance (Low)", avg_variance, 15))
        else:
            detection_indicators.append(("Regional Variance", avg_variance, 0))
        
        # ========== METRIC 5: Pair-wise Difference (PWD) Test ==========
        # Check for inconsistent pixel pairs (embedding signature)
        # Randomly sample pixel pairs
        sample_size = min(5000, h * w // 2)
        y_coords = np.random.choice(h, sample_size, replace=True)
        x_coords = np.random.choice(w, sample_size, replace=True)
        
        pixel_values = img_array[y_coords, x_coords, 0]  # Use R channel
        differences = np.abs(np.diff(pixel_values[:1000]))
        
        # Count how many pixels differ by exactly 1 (LSB embedding signature)
        ones_count = np.sum(differences == 1)
        ones_ratio = ones_count / len(differences) if len(differences) > 0 else 0
        
        # Normal images have ~6-8% pixel pairs with difference of 1
        # Embedded images have >15%
        if ones_ratio > 0.15:
            detection_indicators.append(("Pixel Pair Anomaly (High)", ones_ratio, 20))
        else:
            detection_indicators.append(("Pixel Pair Anomaly", ones_ratio, 0))
        
        # ========== CALCULATE FINAL DETECTION SCORE ==========
        # Sum weighted scores based on sensitivity
        total_score = 0
        sensitivity_factor = sensitivity / 5.0  # Convert to 0.2-2.0 multiplier
        
        for metric_name, metric_value, base_score in detection_indicators:
            adjusted_score = base_score * sensitivity_factor
            total_score += adjusted_score
        
        # Normalize to 0-100
        detection_score = min(100, total_score)
        
        # ========== PREPARE OUTPUT DATA ==========
        analysis_data = [
            {"Metric": ind[0], "Value": f"{ind[1]:.3f}" if isinstance(ind[1], float) else str(ind[1])[:20]}
            for ind in detection_indicators
        ]
        
        return detection_score, analysis_data
        
    except Exception as e:
        logger.error(f"Error in steganography detection: {str(e)}")
        return 0, [{"Metric": "Error", "Value": str(e)}]

# ============================================================================

# ============================================================================
#                    HELPER FUNCTION: MESSAGE VALIDATION
# ============================================================================

def is_valid_message(text):
    """
    Validate if extracted text is a real message, not garbage.
    
    Checks:
    1. Not empty
    2. Has minimum length (at least 3 characters)
    3. At least 70% printable ASCII characters
    4. Not all whitespace
    
    Args:
        text (str): Text to validate
    
    Returns:
        bool: True if valid message, False otherwise
    """
    if not text or len(text) < 3:
        return False
    
    if text.isspace():
        return False
    
    # Count printable ASCII characters
    printable_count = sum(
        1 for c in text 
        if 32 <= ord(c) <= 126 or c in '\n\r\t'
    )
    
    # At least 70% should be printable
    return (printable_count / len(text)) >= 0.7
