"""
Reusable UI Components
======================
Contains all reusable Streamlit components to reduce code duplication.
"""

import streamlit as st
from io import BytesIO
from PIL import Image
from datetime import datetime
import logging

from .config_dict import (
    FORM_LABELS, FILE_UPLOAD_CONFIG, ERROR_MESSAGES, SUCCESS_MESSAGES,
    BUTTON_LABELS, METHODS, METHOD_DETAILS, COLUMN_LAYOUTS, METRIC_LABELS,
    VALIDATION, DOWNLOAD_FILENAMES
)

logger = logging.getLogger(__name__)


# ============================================================================
#                           FORM COMPONENTS
# ============================================================================

def create_text_input(label, placeholder="", password=False, key=None, max_chars=None):
    """
    Create a styled text input field.
    
    Args:
        label: Input label
        placeholder: Placeholder text
        password: If True, masks input
        key: Streamlit key
        max_chars: Maximum characters
    """
    input_type = "password" if password else "default"
    return st.text_input(
        label=label,
        placeholder=placeholder,
        type=input_type,
        key=key
    )


def create_text_area(label, max_chars=1000, key=None, placeholder=""):
    """Create a styled text area."""
    return st.text_area(
        label=label,
        max_chars=max_chars,
        key=key,
        placeholder=placeholder
    )


def create_file_uploader(file_type="images", multiple=False, key=None):
    """
    Create a file uploader with predefined config.
    
    Args:
        file_type: Type from FILE_UPLOAD_CONFIG
        multiple: Allow multiple files
        key: Streamlit key
    """
    config = FILE_UPLOAD_CONFIG.get(file_type, FILE_UPLOAD_CONFIG["images"])
    
    return st.file_uploader(
        label=config["label"],
        type=config["types"],
        accept_multiple_files=multiple,
        key=key
    )


def create_method_selector(key=None, index=0, disabled=False):
    """Create a method selection dropdown."""
    return st.selectbox(
        label="Steganography method",
        options=METHODS,
        index=index,
        key=key,
        disabled=disabled
    )


def create_checkbox(label, key=None, value=False):
    """Create a styled checkbox."""
    return st.checkbox(label=label, key=key, value=value)


# ============================================================================
#                           MESSAGE COMPONENTS
# ============================================================================

def show_error(message, key=None):
    """Display error message."""
    st.error(message)


def show_success(message, key=None):
    """Display success message."""
    st.success(message)


def show_warning(message):
    """Display warning message."""
    st.warning(message)


def show_info(message):
    """Display info message."""
    st.info(message)


def validate_credentials(username, password, min_length=VALIDATION["min_password_length"]):
    """
    Validate login credentials.
    
    Returns:
        (is_valid, error_message)
    """
    if not username or not password:
        return False, ERROR_MESSAGES["empty_fields"]
    
    if len(password) < min_length:
        return False, ERROR_MESSAGES["min_password_length"]
    
    return True, ""


def validate_registration(username, password, confirm_password):
    """
    Validate registration form.
    
    Returns:
        (is_valid, error_message)
    """
    if not username or not password or not confirm_password:
        return False, ERROR_MESSAGES["fields_required"]
    
    if password != confirm_password:
        return False, ERROR_MESSAGES["passwords_mismatch"]
    
    if len(password) < VALIDATION["min_password_length"]:
        return False, ERROR_MESSAGES["min_password_length"]
    
    return True, ""


# ============================================================================
#                           LAYOUT COMPONENTS
# ============================================================================

def create_two_column_layout(left_title=None, right_title=None):
    """
    Create a two-column layout.
    
    Returns:
        (left_col, right_col)
    """
    col1, col2 = st.columns(COLUMN_LAYOUTS["two_col"])
    
    if left_title:
        with col1:
            st.write(f"### {left_title}")
    if right_title:
        with col2:
            st.write(f"### {right_title}")
    
    return col1, col2


def create_three_column_layout(titles=None):
    """
    Create a three-column layout.
    
    Args:
        titles: List of 3 titles or None
    
    Returns:
        (col1, col2, col3)
    """
    cols = st.columns(COLUMN_LAYOUTS["three_col"])
    
    if titles:
        for col, title in zip(cols, titles):
            with col:
                st.write(f"### {title}")
    
    return cols


def create_metric_cards(metrics):
    """
    Create metric cards in a three-column layout.
    
    Args:
        metrics: Dict with structure {label: value}
    """
    cols = st.columns(COLUMN_LAYOUTS["three_col"])
    
    for col, (label, value) in zip(cols, metrics.items()):
        with col:
            st.metric(label, value)


# ============================================================================
#                           IMAGE COMPONENTS
# ============================================================================

def display_image_comparison(original_img, encoded_img, method=""):
    """
    Display side-by-side image comparison.
    
    Args:
        original_img: PIL Image
        encoded_img: PIL Image
        method: Method used (for naming)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Original Image")
        st.image(original_img, use_column_width=True)
        st.write(f"Size: {original_img.size}")
    
    with col2:
        st.write("### Encoded Image")
        st.image(encoded_img, use_column_width=True)
        
        # Download button
        buf = BytesIO()
        encoded_img.save(buf, format="PNG")
        buf.seek(0)
        
        st.download_button(
            label=BUTTON_LABELS["download"],
            data=buf.getvalue(),
            file_name=DOWNLOAD_FILENAMES["encoded_image"].format(
                method=method.replace(' ', '_').lower()
            ),
            mime="image/png",
            use_container_width=True
        )


def display_encoded_image(img):
    """Display encoded image."""
    st.image(img, use_column_width=True)


def display_decoded_message(message, height=150):
    """Display decoded message in a text area."""
    st.text_area(
        "Decoded Message",
        value=message,
        height=height,
        disabled=True
    )


# ============================================================================
#                           BUTTON COMPONENTS
# ============================================================================

def create_primary_button(label, key=None, use_full_width=True):
    """Create a primary action button."""
    return st.button(
        label=label,
        key=key,
        use_container_width=use_full_width,
        type="primary"
    )


def create_download_button(label, data, filename, mime_type="application/octet-stream", key=None):
    """Create a download button."""
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type,
        use_container_width=True,
        key=key
    )


def create_tab_section(tab_names, tab_contents=None):
    """
    Create tabs with optional content.
    
    Args:
        tab_names: List of tab names
        tab_contents: List of callables (one per tab)
    
    Returns:
        List of tab contexts
    """
    tabs = st.tabs(tab_names)
    
    if tab_contents:
        for tab, content in zip(tabs, tab_contents):
            with tab:
                content()
    
    return tabs


# ============================================================================
#                           SUMMARY/STATS COMPONENTS
# ============================================================================

def display_results_summary(results_dict):
    """
    Display a summary of results in three columns.
    
    Args:
        results_dict: Dict with keys as labels and values as values
    """
    cols = st.columns(3)
    
    for col, (label, value) in zip(cols, results_dict.items()):
        with col:
            st.metric(label, value)


def display_progress_indicator(current, total, message="Processing..."):
    """
    Display progress with status message.
    
    Args:
        current: Current progress (0-1)
        total: Total items
        message: Status message
    """
    progress_bar = st.progress(current)
    status_text = st.empty()
    status_text.text(message)
    
    return progress_bar, status_text


# ============================================================================
#                           BATCH PROCESSING COMPONENTS
# ============================================================================

def create_batch_upload_section():
    """
    Create upload method selector and file uploader.
    
    Returns:
        (upload_type, uploaded_files)
    """
    upload_type = st.radio(
        "Upload method",
        options=["ZIP File", "Multiple Images"]
    )
    
    if upload_type == "ZIP File":
        uploaded_files = create_file_uploader(file_type="zip", key="batch_upload_zip")
    else:
        uploaded_files = create_file_uploader(
            file_type="multiple_images",
            multiple=True,
            key="batch_upload_images"
        )
    
    return upload_type, uploaded_files


def create_batch_options_section(include_encryption=True):
    """
    Create encoding/decoding options.
    
    Returns:
        (method, message, use_encryption, encryption_password)
    """
    method = create_method_selector()
    message = create_text_area(
        label=FORM_LABELS["message"]["label"],
        max_chars=FORM_LABELS["message"]["max_chars"]
    )
    
    use_encryption = create_checkbox("Encrypt message before embedding")
    encryption_password = None
    
    if use_encryption:
        encryption_password = create_text_input(
            label=FORM_LABELS["encryption_password"]["label"],
            password=True
        )
    
    return method, message, use_encryption, encryption_password


def display_batch_results(results_summary):
    """
    Display batch processing results.
    
    Args:
        results_summary: Dict with keys like 'total', 'success', 'failed'
    """
    cols = st.columns(3)
    
    labels = ["Total Images", "Successful", "Failed"]
    keys = ["total", "success", "failed"]
    
    for col, label, key in zip(cols, labels, keys):
        with col:
            st.metric(label, results_summary.get(key, 0))


def display_detailed_results(results, result_type="encode"):
    """
    Display detailed results for batch operations.
    
    Args:
        results: List of result dicts
        result_type: 'encode' or 'decode'
    """
    with st.expander("View Detailed Results"):
        for result in results:
            if result.get('status', '').lower().startswith('success'):
                st.success(
                    f"✅ {result['filename']}: "
                    f"{result.get('encoding_time', result.get('message_length', 'N/A'))}"
                )
            else:
                st.error(f"❌ {result['filename']}: {result.get('status', 'Unknown error')}")


# ============================================================================
#                           UTILITY COMPONENTS
# ============================================================================

def show_divider():
    """Show a divider line."""
    st.divider()


def show_method_details():
    """Display detailed information about all methods."""
    with st.expander("📖 Detailed Information"):
        tabs = st.tabs(METHODS)
        
        for tab, method in zip(tabs, METHODS):
            with tab:
                details = METHOD_DETAILS[method]
                st.write(details["description"])


def create_comparison_table(table_data):
    """Display comparison table."""
    st.dataframe(table_data, use_container_width=True)


def show_activity_search(dataframe):
    """
    Show searchable activity log.
    
    Args:
        dataframe: DataFrame with 'Action' and 'Details' columns
    """
    with st.expander("🔍 Search Activity Log"):
        search_term = st.text_input("Search for action or details")
        
        if search_term and not dataframe.empty:
            filtered_df = dataframe[
                dataframe['Action'].str.contains(search_term, case=False, na=False) |
                dataframe['Details'].str.contains(search_term, case=False, na=False)
            ]
            st.dataframe(filtered_df, use_container_width=True)
        elif search_term:
            show_info("No matching activities found")


def create_sections_menu(sections):
    """
    Create a menu of sections.
    
    Args:
        sections: List of section names
    
    Returns:
        Selected section
    """
    return st.radio("Select Section", options=sections, horizontal=False)