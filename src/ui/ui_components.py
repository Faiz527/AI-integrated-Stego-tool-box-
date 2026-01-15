"""
Main UI Components
==================
Contains the main section components for the application interface.
These components orchestrate reusable UI components to build complete sections.
"""

import streamlit as st
import logging
from io import BytesIO
from PIL import Image

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
#                           AUTHENTICATION SECTION
# ============================================================================

def show_auth_section():
    """Display authentication interface (login/register)."""
    st.subheader(SECTION_HEADERS["auth"])
    
    auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
    
    with auth_tab1:
        show_login_form()
    
    with auth_tab2:
        show_register_form()


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
        
        if st.form_submit_button("Login", use_container_width=True, type="primary"):
            if username and password:
                try:
                    from src.db.db_utils import verify_user
                    user_data = verify_user(username, password)
                    
                    if user_data:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user_data.get('user_id')
                        show_success(SUCCESS_MESSAGES["login_success"])
                        st.rerun()
                    else:
                        show_error(ERROR_MESSAGES["invalid_credentials"])
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
#                           ENCODE SECTION
# ============================================================================

def show_encode_section():
    """Display encoding interface."""
    st.subheader(SECTION_HEADERS["encode"])
    show_method_details()
    show_divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Input")
        
        image_file = create_file_uploader(file_type="images")
        
        method = create_method_selector()
        
        message = create_text_area(
            label=FORM_LABELS["message"]["label"],
            max_chars=FORM_LABELS["message"]["max_chars"]
        )
        
        use_encryption = create_checkbox("Encrypt message")
        encryption_password = None
        if use_encryption:
            encryption_password = create_text_input(
                label="Encryption password",
                password=True
            )
    
    with col2:
        st.write("### Preview & Output")
        
        if image_file:
            try:
                original_image = Image.open(image_file)
                st.image(original_image, caption="Selected Image", use_column_width=True)
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    if st.button("Encode Message", use_container_width=True, type="primary"):
        if not image_file or not message:
            show_error(ERROR_MESSAGES["empty_fields"])
        else:
            try:
                with st.spinner("Encoding..."):
                    original_image = Image.open(image_file)
                    
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
                    display_image_comparison(original_image, encoded_image, method)
                    
                    if hasattr(st.session_state, 'user_id'):
                        log_activity(
                            st.session_state.user_id,
                            "ENCODE",
                            f"Encoded message using {method}"
                        )
                    
                    show_success(SUCCESS_MESSAGES["encode_success"])
                    
            except Exception as e:
                show_error(f"Encoding error: {str(e)}")
                logger.error(f"Encoding error: {str(e)}")


# ============================================================================
#                           DECODE SECTION
# ============================================================================

def show_decode_section():
    """Display decoding interface."""
    st.subheader(SECTION_HEADERS["decode"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Input")
        
        image_file = create_file_uploader(file_type="images")
        
        use_encryption = create_checkbox("Message was encrypted")
        decryption_password = None
        if use_encryption:
            decryption_password = create_text_input(
                label="Decryption password",
                password=True
            )
    
    with col2:
        st.write("### Preview")
        
        if image_file:
            try:
                image = Image.open(image_file)
                st.image(image, caption="Selected Image", use_column_width=True)
            except Exception as e:
                show_error(f"Error loading image: {str(e)}")
    
    if st.button("Decode Message", use_container_width=True, type="primary"):
        if not image_file:
            show_error(ERROR_MESSAGES["empty_fields"])
        else:
            try:
                with st.spinner("Decoding..."):
                    image = Image.open(image_file)
                    
                    decoded_message = None
                    method_used = None
                    
                    for method_name, method_func in [
                        ("LSB", lsb_decode),
                        ("Hybrid DCT", dct_decode),
                        ("Hybrid DWT", dwt_decode)
                    ]:
                        try:
                            decoded_message = method_func(image)
                            if decoded_message:
                                method_used = method_name
                                break
                        except:
                            continue
                    
                    if decoded_message:
                        if use_encryption and decryption_password:
                            decoded_message = decrypt_message(decoded_message, decryption_password)
                        
                        st.divider()
                        display_decoded_message(decoded_message)
                        
                        if hasattr(st.session_state, 'user_id'):
                            log_activity(
                                st.session_state.user_id,
                                "DECODE",
                                f"Decoded message using {method_used}"
                            )
                        
                        show_success(SUCCESS_MESSAGES["decode_success"])
                    else:
                        show_error(ERROR_MESSAGES["decode_failed"])
                        
            except Exception as e:
                show_error(f"Decoding error: {str(e)}")
                logger.error(f"Decoding error: {str(e)}")


# ============================================================================
#                           COMPARISON SECTION
# ============================================================================

def show_comparison_section():
    """Display method comparison interface."""
    st.subheader(SECTION_HEADERS["comparison"])
    
    st.write("### Steganography Methods Comparison")
    
    comparison_data = {
        "Method": ["LSB", "Hybrid DCT", "Hybrid DWT"],
        "Speed": ["Very Fast", "Fast", "Fast"],
        "Capacity": ["High", "Medium", "Medium"],
        "Robustness": ["Low", "High", "High"],
        "Visibility": ["Imperceptible", "Imperceptible", "Imperceptible"]
    }
    
    create_comparison_table(comparison_data)
    
    st.divider()
    
    st.write("### Test Methods on Image")
    
    image_file = create_file_uploader(file_type="images")
    message = create_text_area(
        label="Test message",
        max_chars=100
    )
    
    if st.button("Compare Methods", use_container_width=True, type="primary"):
        if not image_file or not message:
            show_error(ERROR_MESSAGES["empty_fields"])
        else:
            try:
                with st.spinner("Comparing methods..."):
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
                    
                    cols = st.columns(3)
                    for col, method in zip(cols, methods):
                        with col:
                            if results[method]:
                                st.image(results[method], caption=method, use_column_width=True)
                            else:
                                st.warning(f"{method} encoding failed")
                    
            except Exception as e:
                show_error(f"Comparison error: {str(e)}")


# ============================================================================
#                           STATISTICS SECTION
# ============================================================================

def show_statistics_section():
    """Display statistics and analytics."""
    st.subheader(SECTION_HEADERS["statistics"])
    
    try:
        from src.analytics.stats import get_statistics_summary, get_activity_dataframe
        
        st.write("### Summary Statistics")
        stats = get_statistics_summary()
        
        if stats:
            cols = st.columns(3)
            for col, (key, value) in zip(cols, stats.items()):
                with col:
                    st.metric(key, value)
        
        st.divider()
        
        st.write("### Activity Log")
        activity_df = get_activity_dataframe()
        
        if activity_df is not None and not activity_df.empty:
            show_activity_search(activity_df)
        else:
            st.info("No activity recorded yet")
            
    except Exception as e:
        show_error(f"Statistics error: {str(e)}")
        logger.error(f"Statistics error: {str(e)}")


# ============================================================================
#                           BATCH PROCESSING SECTION
# ============================================================================

def show_batch_processing_section():
    """Display batch processing interface."""
    st.subheader(SECTION_HEADERS["batch"])
    
    batch_mode = st.radio("Select operation", ["Batch Encode", "Batch Decode"])
    
    st.divider()
    
    if batch_mode == "Batch Encode":
        show_batch_encode()
    else:
        show_batch_decode()


def show_batch_encode():
    """Display batch encoding interface."""
    st.write("### Batch Image Encoding")
    
    upload_type, uploaded_files = create_batch_upload_section()
    
    if uploaded_files:
        method, message, use_encryption, encryption_password = create_batch_options_section()
        
        if st.button("Start Batch Encoding", use_container_width=True, type="primary"):
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
                                "status": "Success",
                                "encoding_time": "N/A"
                            })
                            success_count += 1
                            
                        except Exception as e:
                            results.append({
                                "filename": uploaded_file.name,
                                "status": f"Failed: {str(e)}"
                            })
                            failed_count += 1
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    st.divider()
                    display_batch_results({
                        "total": len(uploaded_files),
                        "success": success_count,
                        "failed": failed_count
                    })
                    
                    display_detailed_results(results, "encode")
                    
                    if success_count > 0:
                        show_success(SUCCESS_MESSAGES["batch_encode_success"])
                    
            except Exception as e:
                show_error(f"Batch encoding error: {str(e)}")


def show_batch_decode():
    """Display batch decoding interface."""
    st.write("### Batch Image Decoding")
    
    upload_type, uploaded_files = create_batch_upload_section()
    
    if uploaded_files:
        use_encryption = create_checkbox("Messages were encrypted")
        decryption_password = None
        if use_encryption:
            decryption_password = create_text_input(
                label="Decryption password",
                password=True
            )
        
        if st.button("Start Batch Decoding", use_container_width=True, type="primary"):
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
                                    "status": "Success",
                                    "message_length": len(decoded_message)
                                })
                                success_count += 1
                            else:
                                results.append({
                                    "filename": uploaded_file.name,
                                    "status": "Failed: No message found"
                                })
                                failed_count += 1
                                
                        except Exception as e:
                            results.append({
                                "filename": uploaded_file.name,
                                "status": f"Failed: {str(e)}"
                            })
                            failed_count += 1
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    st.divider()
                    display_batch_results({
                        "total": len(uploaded_files),
                        "success": success_count,
                        "failed": failed_count
                    })
                    
                    display_detailed_results(results, "decode")
                    
                    if success_count > 0:
                        show_success(SUCCESS_MESSAGES["batch_decode_success"])
                    
            except Exception as e:
                show_error(f"Batch decoding error: {str(e)}")

