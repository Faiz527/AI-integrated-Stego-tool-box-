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
#                    HELPER FUNCTION: MESSAGE VALIDATION
# ============================================================================

def is_valid_message(message):
    """Validate if extracted message is valid (non-empty string)."""
    if not isinstance(message, str):
        return False
    return len(message.strip()) > 0


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
    
    batch_mode = st.radio("Select operation", ["📤 Batch Encode", "📥 Batch Decode"], horizontal=True)
    
    st.divider()
    
    if batch_mode == "📤 Batch Encode":
        show_batch_encode()
    else:
        show_batch_decode()


def show_batch_encode():
    """Display batch encoding interface with Basic and Advanced modes."""
    st.markdown("### Batch Image Encoding")
    
    # ========================================================================
    # MODE SELECTION - Basic vs Advanced
    # ========================================================================
    
    st.markdown("#### Select Encoding Mode")
    
    encoding_mode = st.radio(
        "Choose how to embed your message:",
        options=[
            "🔄 Basic Mode - Same message in ALL images (each image independently decodable)",
            "📦 Advanced Mode - Split message across images (ALL images required to decode)"
        ],
        index=0,
        horizontal=False,
        key="batch_encoding_mode"
    )
    
    is_advanced_mode = "Advanced" in encoding_mode
    
    # Show mode explanation
    if is_advanced_mode:
        st.info("""
        **📦 Advanced Mode (Packetized Message Distribution)**
        - Your message will be **split into equal packets**
        - Each image receives **one unique packet**
        - **ALL encoded images are required** to reconstruct the message
        - Maximum security: no single image reveals the complete secret
        """)
    else:
        st.success("""
        **🔄 Basic Mode (Uniform Message Embedding)**
        - The **complete message** is embedded in **every** image
        - Each image can be decoded **independently**
        - Perfect for backups or sending to multiple recipients
        """)
    
    st.divider()
    
    # ========================================================================
    # FILE UPLOAD
    # ========================================================================
    
    st.markdown("#### Upload Images")
    upload_type, uploaded_files = create_batch_upload_section()
    
    # Count and validate files
    file_count = 0
    if uploaded_files:
        if isinstance(uploaded_files, list):
            file_count = len(uploaded_files)
        else:
            file_count = 1  # Single file (ZIP)
        
        st.success(f"✅ **{file_count} file(s) selected**")
        
        # Validation for Advanced mode
        if is_advanced_mode:
            if file_count < 2:
                st.error("⚠️ **Advanced Mode requires at least 2 images.** Upload more images or switch to Basic Mode.")
                return
            else:
                st.info(f"📦 Message will be split into **{file_count} packets** (one per image)")
    
    if not uploaded_files:
        return
    
    st.divider()
    
    # ========================================================================
    # ENCODING OPTIONS
    # ========================================================================
    
    st.markdown("#### Configure Encoding")
    
    col1, col2 = st.columns(2)
    
    with col1:
        method, message, use_encryption, encryption_password = create_batch_options_section()
    
    with col2:
        st.markdown("**📋 Configuration Summary:**")
        mode_name = "Advanced (Packetized)" if is_advanced_mode else "Basic (Uniform)"
        st.write(f"- **Mode:** {mode_name}")
        st.write(f"- **Method:** {method}")
        st.write(f"- **Encryption:** {'Yes' if use_encryption else 'No'}")
        st.write(f"- **Images:** {file_count}")
        
        if message:
            st.write(f"- **Message Length:** {len(message)} characters")
            if is_advanced_mode and file_count >= 2:
                import math
                packet_size = math.ceil(len(message) / file_count)
                st.write(f"- **Packet Size:** ~{packet_size} chars/image")
        
        if is_advanced_mode:
            st.warning("⚠️ Keep ALL encoded images together for decoding!")
    
    # ========================================================================
    # ENCODE BUTTON
    # ========================================================================
    
    col1, col2, col3 = st.columns(3)
    with col2:
        start_btn = st.button("▶️ Start Batch Encoding", use_container_width=True, type="primary")
    
    if start_btn:
        if not message:
            show_error("Please enter a message to encode")
            return
        
        if is_advanced_mode:
            _perform_advanced_batch_encode(
                uploaded_files, upload_type, message, method, 
                use_encryption, encryption_password, file_count
            )
        else:
            _perform_basic_batch_encode(
                uploaded_files, message, method, 
                use_encryption, encryption_password
            )
    
    # ========================================================================
    # HELP SECTION
    # ========================================================================
    
    st.divider()
    
    if is_advanced_mode:
        show_info_box(
            "Advanced Batch Encoding (Packetized)",
            """
            In Advanced mode, your message is split into equal packets and distributed across images.
            This provides maximum security as no single image contains the complete message.
            All encoded images must be collected together for successful decoding.
            """,
            [
                "Message is divided equally across all images",
                "Each image contains only a fragment (packet) of the message",
                "ALL encoded images are required for decoding",
                "Missing even one image prevents message reconstruction",
                "Images are sorted by filename for deterministic ordering",
                "Perfect for high-security distributed storage"
            ]
        )
    else:
        show_info_box(
            "Basic Batch Encoding (Uniform)",
            """
            Basic batch encoding hides the same complete message in every image.
            Each encoded image is independent and can be decoded on its own.
            Perfect for creating backups or sending to multiple recipients.
            """,
            [
                "Same message embedded in every image",
                "Each image can be decoded independently",
                "Create multiple copies with the same hidden data",
                "Perfect for redundancy and backup purposes",
                "Any single image reveals the complete message"
            ]
        )


def _perform_basic_batch_encode(uploaded_files, message, method, use_encryption, encryption_password):
    """Execute basic batch encoding - same message in all images."""
    try:
        with st.spinner("Processing batch (Basic Mode)..."):
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
                    
                    # Save to output directory
                    import os
                    output_dir = f"data/output/encoded/{method}"
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = f"{output_dir}/{uploaded_file.name}"
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
                        "status": f"❌ Failed: {str(e)[:30]}"
                    })
                    failed_count += 1
                
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("Complete!")
            
            # Display results
            st.divider()
            st.markdown("### 📊 Batch Results (Basic Mode)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(uploaded_files))
            with col2:
                st.metric("Success", success_count, delta="✅")
            with col3:
                st.metric("Failed", failed_count, delta="❌" if failed_count > 0 else None)
            
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            if success_count > 0:
                show_success(f"Successfully encoded {success_count} images! Each contains the complete message.")
                
    except Exception as e:
        show_error(f"Batch encoding error: {str(e)}")


def _perform_advanced_batch_encode(uploaded_files, upload_type, message, method, 
                                    use_encryption, encryption_password, file_count):
    """Execute advanced batch encoding - split message across images (packetized)."""
    try:
        from src.batch_processing.packet_handler import packetize_message, get_packet_map
        import zipfile
        import tempfile
        
        with st.spinner("Processing batch (Advanced Mode - Packetized)..."):
            results = []
            success_count = 0
            failed_count = 0
            encoded_images = []  # Store encoded images for download
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Prepare message (encrypt BEFORE packetizing)
            message_to_use = message
            if use_encryption and encryption_password:
                message_to_use = encrypt_message(message, encryption_password)
            
            # Sort files by name for deterministic ordering
            if isinstance(uploaded_files, list):
                sorted_files = sorted(uploaded_files, key=lambda x: x.name.lower())
            else:
                sorted_files = [uploaded_files]
            
            # Create packets
            status_text.text("Creating message packets...")
            try:
                packets = packetize_message(message_to_use, len(sorted_files))
            except Exception as e:
                show_error(f"Packetization failed: {str(e)}")
                return
            
            progress_bar.progress(0.1)
            
            # Encode each image with its packet
            import os
            output_dir = f"data/output/encoded/{method}/packetized"
            os.makedirs(output_dir, exist_ok=True)
            
            packet_map = {}
            
            for idx, (uploaded_file, packet) in enumerate(zip(sorted_files, packets)):
                status_text.text(f"Encoding packet {idx+1}/{len(sorted_files)}: {uploaded_file.name}")
                
                try:
                    image = Image.open(uploaded_file)
                    
                    # Encode packet into image
                    if method == "LSB":
                        encoded = lsb_encode(image, packet)
                    elif method == "Hybrid DCT":
                        encoded = dct_encode(image, packet)
                    elif method == "Hybrid DWT":
                        encoded = dwt_encode(image, packet)
                    else:
                        encoded = lsb_encode(image, packet)
                    
                    # Save with packet info in filename
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    output_filename = f"{base_name}_pkt{idx+1}of{len(sorted_files)}.png"
                    output_path = f"{output_dir}/{output_filename}"
                    encoded.save(output_path, "PNG")
                    
                    # Store for download
                    encoded_images.append({
                        "image": encoded,
                        "filename": output_filename
                    })
                    
                    results.append({
                        "filename": uploaded_file.name,
                        "packet": f"{idx+1}/{len(sorted_files)}",
                        "status": "✅ Success",
                        "output": output_path
                    })
                    
                    packet_map[uploaded_file.name] = {
                        "packet_id": idx,
                        "total_packets": len(sorted_files),
                        "output_file": output_filename
                    }
                    
                    success_count += 1
                    
                except Exception as e:
                    results.append({
                        "filename": uploaded_file.name,
                        "packet": f"{idx+1}/{len(sorted_files)}",
                        "status": f"❌ Failed: {str(e)[:30]}"
                    })
                    failed_count += 1
                
                progress_bar.progress(0.1 + (0.9 * (idx + 1) / len(sorted_files)))
            
            status_text.text("Complete!")
            
            # Display results
            st.divider()
            st.markdown("### 📊 Batch Results (Advanced Mode - Packetized)")
            
            st.info(f"**Mode:** Packetized Distribution | **Total Packets:** {len(sorted_files)}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Images", len(sorted_files))
            with col2:
                st.metric("Packets Created", len(packets))
            with col3:
                st.metric("Success", success_count, delta="✅")
            with col4:
                st.metric("Failed", failed_count, delta="❌" if failed_count > 0 else None)
            
            # Show packet distribution
            with st.expander("📦 Packet Distribution Map"):
                st.json(packet_map)
            
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            if success_count > 0:
                show_success(f"Successfully created {success_count} encoded images with packetized message!")
                st.warning(f"⚠️ **IMPORTANT:** You need ALL {success_count} images to decode the complete message!")
                
                st.divider()
                st.markdown("### 📥 Download Encoded Images")
                
                # Create ZIP file for download
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for img_data in encoded_images:
                        img_buffer = BytesIO()
                        img_data["image"].save(img_buffer, format="PNG")
                        img_buffer.seek(0)
                        zip_file.writestr(img_data["filename"], img_buffer.getvalue())
                
                zip_buffer.seek(0)
                
                # Download button for ZIP
                st.download_button(
                    label=f"⬇️ Download All {success_count} Encoded Images (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"packetized_batch_{method}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
                
                st.caption(f"📁 Files also saved to: `{output_dir}`")
                
                # Individual download option
                with st.expander("📥 Download Individual Images"):
                    for img_data in encoded_images:
                        img_buffer = BytesIO()
                        img_data["image"].save(img_buffer, format="PNG")
                        img_buffer.seek(0)
                        
                        st.download_button(
                            label=f"⬇️ {img_data['filename']}",
                            data=img_buffer.getvalue(),
                            file_name=img_data["filename"],
                            mime="image/png",
                            key=f"download_{img_data['filename']}"
                        )
                
            if failed_count > 0:
                show_error(f"⚠️ {failed_count} images failed. The message cannot be fully reconstructed without all images!")
                
    except ImportError:
        show_error("Advanced mode requires the packet_handler module. Please ensure it's installed.")
    except Exception as e:
        show_error(f"Advanced batch encoding error: {str(e)}")
        logger.error(f"Advanced batch encode error: {e}", exc_info=True)


def show_batch_decode():
    """Display batch decoding interface with auto-detection for packetized messages."""
    st.markdown("### Batch Image Decoding")
    
    st.info("""
    **Auto-Detection:** The system will automatically detect if images contain:
    - **Basic Mode:** Same message in each image (decode any single image)
    - **Advanced Mode:** Packetized messages (need ALL images to reconstruct)
    """)
    
    upload_type, uploaded_files = create_batch_upload_section()
    
    if uploaded_files:
        # Handle both single file (ZIP) and multiple files
        if isinstance(uploaded_files, list):
            file_count = len(uploaded_files)
        else:
            file_count = 1  # Single ZIP file
        
        st.markdown(f"**Files selected:** {file_count}")
        
        st.divider()
        
        use_encryption = create_checkbox("🔐 Messages are encrypted - I have the password", key="batch_decode_encrypt")
        decryption_password = None
        if use_encryption:
            decryption_password = create_text_input(
                label="Decryption password",
                placeholder="Enter the password",
                password=True,
                key="batch_decode_password"
            )
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("▶️ Start Batch Decoding", use_container_width=True, type="primary"):
                _perform_batch_decode(uploaded_files, upload_type, use_encryption, decryption_password)
    
    show_info_box(
        "Batch Decoding",
        """
        Batch decoding extracts hidden messages from multiple images.
        The system automatically detects whether images contain uniform messages (Basic Mode)
        or packetized data (Advanced Mode) and handles them appropriately.
        """,
        [
            "Automatic mode detection (Basic vs Advanced)",
            "For Basic Mode: decode each image independently",
            "For Advanced Mode: reconstruct message from all packets",
            "Supports encrypted message decryption",
            "Detailed results for each processed image"
        ]
    )


def _perform_batch_decode(uploaded_files, upload_type, use_encryption, decryption_password):
    """Execute batch decoding with auto-detection for packetized messages."""
    try:
        import tempfile
        import os
        
        with st.spinner("Processing batch..."):
            results = []
            success_count = 0
            failed_count = 0
            detected_packets = []  # For Advanced mode reconstruction
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Handle ZIP file upload vs multiple images
            if upload_type == "ZIP File" and uploaded_files:
                status_text.text("Extracting ZIP file...")
                
                # Extract ZIP to temp directory
                from src.batch_processing.zip_handler import extract_zip
                temp_dir = tempfile.mkdtemp()
                extract_result = extract_zip(uploaded_files, temp_dir)
                
                if not extract_result['success']:
                    show_error(f"ZIP extraction failed: {extract_result['message']}")
                    return
                
                # Create file-like objects from extracted files
                files_to_process = []
                for file_path in extract_result['extracted_files']:
                    files_to_process.append({
                        'path': file_path,
                        'name': os.path.basename(file_path)
                    })
                
                progress_bar.progress(0.1)
            else:
                # Multiple individual images
                files_to_process = []
                for f in uploaded_files:
                    files_to_process.append({
                        'file': f,
                        'name': f.name
                    })
            
            # Process each file
            total_files = len(files_to_process)
            
            for idx, file_info in enumerate(files_to_process):
                filename = file_info['name']
                status_text.text(f"Processing: {filename}")
                
                try:
                    # Open image from path or uploaded file
                    if 'path' in file_info:
                        image = Image.open(file_info['path'])
                    else:
                        image = Image.open(file_info['file'])
                    
                    decoded_message = None
                    method_used = None
                    
                    # Try each decoding method
                    for method_name, method_func in [("LSB", lsb_decode), ("DCT", dct_decode), ("DWT", dwt_decode)]:
                        try:
                            decoded = method_func(image)
                            if decoded and is_valid_message(decoded):
                                decoded_message = decoded
                                method_used = method_name
                                break
                        except:
                            continue
                    
                    if decoded_message:
                        # Check if it's a packetized message
                        try:
                            from src.batch_processing.packet_handler import is_packetized_message, extract_packet_data
                            
                            if is_packetized_message(decoded_message):
                                packet_data = extract_packet_data(decoded_message)
                                if packet_data:
                                    header, payload = packet_data
                                    detected_packets.append((header, payload, filename))
                                    results.append({
                                        "filename": filename,
                                        "status": f"✅ Packet {header['packet_id']+1}/{header['total_packets']}",
                                        "method": method_used,
                                        "type": "Packetized"
                                    })
                                    success_count += 1
                                    progress_bar.progress(0.1 + (0.9 * (idx + 1) / total_files))
                                    continue
                        except ImportError:
                            pass  # packet_handler not available
                        
                        # Regular message (Basic Mode)
                        if use_encryption and decryption_password:
                            try:
                                decoded_message = decrypt_message(decoded_message, decryption_password)
                            except:
                                pass  # Keep original if decryption fails
                        
                        results.append({
                            "filename": filename,
                            "status": "✅ Success",
                            "method": method_used,
                            "message_length": len(decoded_message),
                            "preview": decoded_message[:50] + "..." if len(decoded_message) > 50 else decoded_message,
                            "full_message": decoded_message,  # Store full message for display
                            "type": "Uniform"
                        })
                        success_count += 1
                    else:
                        results.append({
                            "filename": filename,
                            "status": "❌ No message found",
                            "type": "Unknown"
                        })
                        failed_count += 1
                        
                except Exception as e:
                    results.append({
                        "filename": filename,
                        "status": f"❌ Error: {str(e)[:20]}"
                    })
                    failed_count += 1
                
                progress_bar.progress(0.1 + (0.9 * (idx + 1) / total_files))
            
            status_text.text("Complete!")
            
            st.divider()
            st.markdown("### 📊 Batch Decode Results")
            
            # Check if we found packetized messages
            if detected_packets:
                st.info(f"**Detected Mode:** Advanced (Packetized) - Found {len(detected_packets)} packets")
                
                # Try to reconstruct the message
                try:
                    from src.batch_processing.packet_handler import reconstruct_message
                    
                    packets_for_reconstruction = [(h, p) for h, p, _ in detected_packets]
                    success, reconstructed, details = reconstruct_message(packets_for_reconstruction)
                    
                    if success:
                        # Decrypt if needed
                        if use_encryption and decryption_password:
                            try:
                                reconstructed = decrypt_message(reconstructed, decryption_password)
                            except:
                                st.warning("Decryption failed - showing encrypted message")
                        
                        st.success(f"✅ **Message Reconstructed Successfully!** ({details})")
                        st.markdown("### 📩 Reconstructed Message:")
                        st.text_area("Complete Message", value=reconstructed, height=200, disabled=True)
                    else:
                        st.error(f"❌ **Reconstruction Failed:** {details}")
                        st.warning("Make sure you have uploaded ALL encoded images from the batch.")
                        
                except ImportError:
                    st.warning("Packet reconstruction not available. Install packet_handler module.")
            else:
                st.info("**Detected Mode:** Basic (Uniform) - Each image decoded independently")
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", total_files)
            with col2:
                st.metric("Success", success_count, delta="✅")
            with col3:
                st.metric("Failed", failed_count, delta="❌" if failed_count > 0 else None)
            
            # Show detailed results
            st.dataframe(pd.DataFrame(results), use_container_width=True)
            
            # For Basic/Uniform mode, display all decoded messages
            if success_count > 0 and not detected_packets:
                show_success(f"Successfully decoded {success_count} messages!")
                
                st.markdown("### 📩 Decoded Messages:")
                for idx, result in enumerate(results):
                    if result.get("status") == "✅ Success" and result.get("type") == "Uniform":
                        with st.expander(f"📄 {result['filename']} ({result.get('method', 'Unknown')} method)", expanded=(idx == 0)):
                            full_message = result.get('full_message', result.get('preview', 'No message'))
                            st.text_area(
                                "Message",
                                value=full_message,
                                height=150,
                                disabled=True,
                                key=f"decode_msg_{idx}_{result['filename']}"
                            )
                
    except Exception as e:
        show_error(f"Batch decoding error: {str(e)}")
        logger.error(f"Batch decode error: {e}", exc_info=True)


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
                    h, w, _ = arr.shape
                    
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
                        st.image(arr, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Best Pixels (marked in red)**")
                        overlay = arr.copy()
                        for x, y in selected_coords[:100]:
                            if 0 <= x < w and 0 <= y < h:
                                overlay[y, x] = [255, 0, 0]
                        st.image(overlay, use_container_width=True)
                    
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
#                    MODULE 5: STEGANOGRAPHY DETECTOR
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
                    
                    detection_score, analysis_data = _analyze_image_for_steganography(arr, sensitivity)
                    
                    st.divider()
                    st.markdown("### Analysis Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Image Statistics**")
                        stats_df = pd.DataFrame(analysis_data)
                        st.dataframe(stats_df, use_container_width=True)
                    
                    with col2:
                        st.markdown("**Detection Result**")
                        
                        if detection_score < 25:
                            emoji = "🟢"
                            verdict = "Clean Image"
                            explanation = "This image shows natural patterns. No hidden data detected."
                        elif detection_score < 50:
                            emoji = "🟡"
                            verdict = "Uncertain"
                            explanation = "Image shows some anomalies but could be due to compression."
                        else:
                            emoji = "🔴"
                            verdict = "Suspicious - Possible Hidden Data"
                            explanation = "Image shows signs of data embedding."
                        
                        st.metric(f"{emoji} Detection Score", f"{detection_score:.1f}%")
                        st.subheader(verdict)
                        st.write(explanation)
                    
                    show_success("Analysis complete!")
                    
            except Exception as e:
                show_error(f"Detection error: {str(e)}")
                logger.error(f"Detection error: {str(e)}")
    
    show_info_box(
        "Steganography Detection",
        """
        This tool checks if an image contains hidden data by analyzing statistical patterns.
        Images with hidden messages often show different patterns than normal images.
        """,
        [
            "Detect if an image contains hidden messages",
            "Verify image authenticity and integrity",
            "Analyze image for suspicious patterns",
            "Investigate potentially compromised images"
        ]
    )


def _analyze_image_for_steganography(img_array, sensitivity):
    """Analyze image for steganography indicators."""
    try:
        from scipy.stats import entropy
        
        detection_indicators = []
        
        # LSB Entropy
        lsb_plane = (img_array & 1).flatten()
        lsb_entropy = entropy(np.bincount(lsb_plane, minlength=2))
        
        if lsb_entropy > 0.85:
            detection_indicators.append(("LSB Entropy (High)", lsb_entropy, 30))
        else:
            detection_indicators.append(("LSB Entropy (Normal)", lsb_entropy, 0))
        
        # Histogram analysis
        hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
        expected_freq = len(img_array.flatten()) / 256
        chi2_stat = np.sum((hist - expected_freq) ** 2 / (expected_freq + 1))
        
        if chi2_stat < 100:
            detection_indicators.append(("Histogram Flatness", chi2_stat, 20))
        else:
            detection_indicators.append(("Histogram Flatness", chi2_stat, 0))
        
        # Bit-plane analysis
        bit_plane_entropies = []
        for bit in range(8):
            bit_plane = ((img_array >> bit) & 1).flatten()
            bp_entropy = entropy(np.bincount(bit_plane, minlength=2))
            bit_plane_entropies.append(bp_entropy)
        
        if bit_plane_entropies[0] > 0.95:
            detection_indicators.append(("Bit-Plane Randomness (High)", bit_plane_entropies[0], 25))
        else:
            detection_indicators.append(("Bit-Plane Randomness", bit_plane_entropies[0], 0))
        
        # Calculate final score
        total_score = 0
        sensitivity_factor = sensitivity / 5.0
        
        for metric_name, metric_value, base_score in detection_indicators:
            adjusted_score = base_score * sensitivity_factor
            total_score += adjusted_score
        
        detection_score = min(100, total_score)
        
        analysis_data = [
            {"Metric": ind[0], "Value": f"{ind[1]:.3f}" if isinstance(ind[1], float) else str(ind[1])[:20]}
            for ind in detection_indicators
        ]
        
        return detection_score, analysis_data
        
    except Exception as e:
        logger.error(f"Error in steganography detection: {str(e)}")
        return 0, [{"Metric": "Error", "Value": str(e)}]


# ============================================================================
#                    MODULE 6: ERROR CORRECTION & REDUNDANCY
# ============================================================================

def show_redundancy_section():
    """Display error correction and redundancy features."""
    st.subheader("🛡️ Module 6: Error Correction & Redundancy")
    
    st.markdown("""
    This module adds redundancy to your messages using Reed-Solomon error correction.
    This allows recovery of messages even if the image gets corrupted or compressed.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Step 1: Upload Image & Message")
        
        image_file = create_file_uploader(file_type="images", key="redundancy_img")
        if image_file:
            try:
                image = Image.open(image_file)
                st.image(image, caption="Your Image", use_container_width=True)
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
        
        message = create_text_area(
            label="Message to protect",
            max_chars=5000
        )
    
    with col2:
        st.markdown("### Step 2: Configure ECC")
        
        ecc_strength = st.slider(
            "Error correction strength (parity bytes)",
            min_value=8,
            max_value=128,
            value=32,
            step=8,
            help="More parity = can recover from more corruption, but needs more space"
        )
        
        st.info(f"""
        **Configuration Summary:**
        - **Parity Bytes:** {ecc_strength}
        - **Can recover from:** ~{ecc_strength//2} byte errors
        """)
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if image_file and message and st.button("🔧 Test ECC", use_container_width=True, type="primary"):
            try:
                with st.spinner("Testing error correction..."):
                    from stegotool.modules.module6_redundancy.rs_wrapper import add_redundancy, recover_redundancy
                    
                    message_bytes = message.encode()
                    encoded_with_ecc = add_redundancy(message_bytes, nsym=ecc_strength)
                    
                    st.divider()
                    st.markdown("### ✅ ECC Test Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original Message**")
                        st.code(message[:100] + ("..." if len(message) > 100 else ""))
                        st.caption(f"Size: {len(message_bytes)} bytes")
                    
                    with col2:
                        st.markdown("**After ECC Encoding**")
                        st.code(f"{len(encoded_with_ecc)} bytes")
                        overhead = (len(encoded_with_ecc) - len(message_bytes)) / len(message_bytes) * 100
                        st.caption(f"Overhead: +{overhead:.1f}%")
                    
                    show_success(f"ECC encoding successful with {ecc_strength} parity bytes!")
                    
            except Exception as e:
                show_error(f"ECC test error: {str(e)}")
                logger.error(f"Redundancy test error: {str(e)}")
    
    show_info_box(
        "Error Correction & Redundancy (Module 6)",
        """
        This module protects your messages from corruption using Reed-Solomon codes.
        Even if the image gets compressed or damaged, the error correction can recover the message.
        """,
        [
            "Recover messages from corrupted images",
            "Add redundancy to protect against JPEG recompression",
            "Test error correction strength before embedding",
            "Choose parity bytes based on expected corruption level"
        ]
    )


# ============================================================================
#                           WATERMARKING SECTION
# ============================================================================

def show_watermarking_section():
    """Display the Watermarking interface."""
    st.subheader("💧 Watermarking")
    
    st.markdown("""
    Add visible text watermarks to your images to protect your intellectual property 
    or mark ownership. Perfect for copyright notices and branding.
    """)
    
    st.divider()
    
    st.markdown("### 📝 Text-based Watermark")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Upload Your Image")
        image_file = create_file_uploader(file_type="images", key="watermark_image_upload")
        
        if image_file:
            try:
                original_image = Image.open(image_file)
                st.image(original_image, caption="Original Image", use_container_width=True)
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    with col2:
        st.markdown("#### Watermark Settings")
        
        watermark_text = st.text_input(
            "Watermark Text",
            value="© Your Name",
            placeholder="Enter your watermark text",
            max_chars=200
        )
        
        font_size = st.slider("Font Size", min_value=10, max_value=100, value=30, step=5)
        
        position = st.selectbox(
            "Position",
            options=["top-left", "center", "bottom-right"],
            index=2
        )
        
        opacity = st.slider("Opacity", min_value=50, max_value=255, value=180, step=10)
        
        text_color_hex = st.color_picker("Text Color", value="#FFFFFF")
        text_color = tuple(int(text_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col2:
        apply_button = st.button("💧 Apply Watermark", use_container_width=True, type="primary", disabled=not image_file)
    
    if apply_button and image_file:
        if not watermark_text or watermark_text.strip() == "":
            show_error("Please enter watermark text")
        else:
            try:
                with st.spinner("Applying watermark..."):
                    from src.watermark.watermark import apply_text_watermark
                    
                    original_image = Image.open(image_file)
                    
                    watermarked_image = apply_text_watermark(
                        image=original_image,
                        watermark_text=watermark_text,
                        font_size=font_size,
                        position=position,
                        text_color=text_color,
                        opacity=opacity
                    )
                    
                    st.divider()
                    st.markdown("### ✅ Watermark Applied!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(original_image, caption="Original", use_container_width=True)
                    with col2:
                        st.image(watermarked_image, caption="Watermarked", use_container_width=True)
                    
                    buf = BytesIO()
                    watermarked_image.save(buf, format="PNG")
                    buf.seek(0)
                    
                    st.download_button(
                        label="⬇️ Download Watermarked Image",
                        data=buf.getvalue(),
                        file_name="watermarked_image.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    show_success("Watermark applied successfully!")
                    
            except Exception as e:
                show_error(f"Error applying watermark: {str(e)}")
                logger.error(f"Watermark error: {str(e)}")
    
    show_info_box(
        "Image Watermarking",
        """
        Watermarking adds visible text to your images for copyright protection or branding.
        Customize the text, position, size, color, and opacity.
        """,
        [
            "Add copyright notices to protect your work",
            "Brand images with your name or company",
            "Customize text color, size, position, and opacity",
            "Download watermarked images in PNG format"
        ]
    )
