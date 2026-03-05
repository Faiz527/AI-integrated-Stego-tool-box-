"""
ECC (Error Correction Code) UI Section
=======================================
Handles all UI logic for error correction features.
Moved from ui_components.py for better code organization.

Provides:
- ECC encoding with Reed-Solomon codes
- ECC recovery during decoding
- Capacity checking and warnings
- Interactive testing interface
"""

import streamlit as st
import logging
from typing import Tuple, Optional

from .rs_wrapper import (
    add_redundancy,
    recover_redundancy,
    estimate_overhead_rs,
    estimate_overhead_replication,
    _HAS_RS
)
from .capacity_checker import can_fit_payload, pretty_report
from src.ui.reusable_components import (
    show_warning, show_error, show_success, show_info, render_step
)

logger = logging.getLogger(__name__)


# ============================================================================
#                    ECC CONFIGURATION & VALIDATION
# ============================================================================

def get_ecc_config() -> dict:
    """Get ECC configuration from session state with defaults."""
    return {
        'use_ecc': st.session_state.get('use_ecc', False),
        'ecc_strength': st.session_state.get('ecc_strength', 32),
        'nsym': st.session_state.get('ecc_strength', 32)  # nsym = parity bytes
    }


def validate_capacity(image_size: Tuple[int, int], message_length: int, 
                     use_ecc: bool = False, nsym: int = 32,
                     channels: int = 3, lsb_bits: int = 1) -> Tuple[bool, str]:
    """
    Check if message + ECC overhead fits in the image.
    
    Args:
        image_size: (width, height) of image
        message_length: bytes in original message
        use_ecc: whether ECC is enabled
        nsym: parity bytes for ECC
        channels: color channels (3 for RGB)
        lsb_bits: bits per channel used
    
    Returns:
        (fits: bool, warning_msg: str)
    """
    if not message_length:
        return True, ""
    
    w, h = image_size
    
    # Calculate required size
    if use_ecc:
        required_size = message_length + nsym  # payload + parity
    else:
        required_size = message_length
    
    # Check capacity
    fits, available = can_fit_payload(
        image_size,
        message_length,
        nsym if use_ecc else 0,
        channels=channels,
        lsb_bits=lsb_bits
    )
    
    if not fits:
        overhead_msg = f"(+{nsym} bytes ECC overhead)" if use_ecc else ""
        warning = (
            f"⚠️ Message too large! {overhead_msg}\n\n"
            f"Required: {required_size:,} bytes\n"
            f"Available: {available:,} bytes\n"
            f"Shortfall: {required_size - available:,} bytes\n\n"
            f"**Solutions:**\n"
            f"- Use a larger image ({int(w*1.5)}×{int(h*1.5)} minimum)\n"
            f"- Reduce message length\n"
            f"- Disable ECC if not critical"
        )
        return False, warning
    
    # Calculate overhead percentage
    if use_ecc:
        overhead_pct = (nsym / message_length) * 100 if message_length > 0 else 0
        info = f"✅ Fits! ECC overhead: {nsym} bytes ({overhead_pct:.1f}%)"
    else:
        info = f"✅ Fits!"
    
    return True, info


# ============================================================================
#                    ECC ENCODE UI
# ============================================================================

def show_ecc_encode_section():
    """
    Display ECC configuration section for encoding.
    Shows checkboxes, sliders, and capacity warnings.
    
    Returns:
        dict with keys: 'use_ecc', 'ecc_strength', 'warning'
    """
    st.markdown('<div class="card animate-fade-in stagger-4">', unsafe_allow_html=True)
    
    render_step(5, "Error Correction (Optional)")
    
    st.markdown('<p style="color: #8B949E; font-size: 0.9rem;">Protect messages from corruption with Reed-Solomon codes</p>', 
                unsafe_allow_html=True)
    
    # ECC Checkbox
    use_ecc = st.checkbox(
        "🛡️ Enable Error Correction (ECC)",
        value=False,
        key="encode_use_ecc",
        help="Make message resistant to JPEG compression and noise"
    )
    
    ecc_strength = 32  # default
    ecc_warning = ""
    
    if use_ecc:
        st.divider()
        
        # ECC Strength Slider
        ecc_strength = st.slider(
            "ECC Strength (Parity Bytes)",
            min_value=8,
            max_value=128,
            value=32,
            step=8,
            key="encode_ecc_strength",
            help="Higher = more robust but larger file"
        )
        
        # ECC info
        error_correction_capacity = ecc_strength // 2
        overhead_pct = (ecc_strength / 100) * 100 if ecc_strength else 0
        
        st.markdown(f"""
            <div style="padding: 0.75rem; background: rgba(79, 171, 255, 0.1); border-radius: 6px; margin: 0.5rem 0;">
                <p style="margin: 0; font-size: 0.9rem;">
                    🔍 <strong>ECC Configuration:</strong><br>
                    • Can correct ~{error_correction_capacity} byte errors<br>
                    • Overhead: ~{ecc_strength} bytes per {100 if ecc_strength > 50 else 256} bytes payload<br>
                    • Best for: JPEG compression, high-noise images
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state['ecc_strength'] = ecc_strength
        st.session_state['use_ecc'] = True
    else:
        st.markdown("""
            <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 6px; margin: 0.5rem 0;">
                <p style="margin: 0; font-size: 0.9rem; color: #8B949E;">
                    ℹ️ ECC disabled — message won't be protected from corruption
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'use_ecc': use_ecc,
        'ecc_strength': ecc_strength,
        'warning': ecc_warning
    }


def check_capacity_and_warn(image_size: Tuple[int, int], message_text: str,
                            use_ecc: bool, ecc_strength: int) -> bool:
    """
    Check if message fits with ECC and display warning if needed.
    Returns True if fits, False otherwise.
    """
    if not message_text or not image_size:
        return True
    
    message_bytes = len(message_text.encode('utf-8'))
    fits, msg = validate_capacity(
        image_size,
        message_bytes,
        use_ecc=use_ecc,
        nsym=ecc_strength,
        channels=3,
        lsb_bits=1
    )
    
    # Display warning or info
    if not fits:
        show_warning(msg)
        return False
    else:
        # Show only on first check per encode session
        if 'last_capacity_check' not in st.session_state:
            st.caption(msg)
            st.session_state['last_capacity_check'] = True
        return True


# ============================================================================
#                    ECC DECODE UI
# ============================================================================

def show_ecc_decode_section() -> dict:
    """
    Display ECC recovery checkbox for decoding.
    
    Returns:
        dict with key 'use_ecc_recovery'
    """
    st.markdown('<div class="card animate-fade-in stagger-3">', unsafe_allow_html=True)
    
    render_step(4, "Error Correction Recovery")
    
    use_ecc_recovery = st.checkbox(
        "🔧 Try to recover from errors (if message was encoded with ECC)",
        value=True,
        key="decode_use_ecc_recovery",
        help="Automatically recover if message was encoded with Reed-Solomon"
    )
    
    if use_ecc_recovery:
        ecc_strength = st.slider(
            "Expected ECC Strength (if used)",
            min_value=8,
            max_value=128,
            value=32,
            step=8,
            key="decode_ecc_strength",
            help="Match the strength used during encoding"
        )
        
        st.caption(f"Will attempt recovery up to ~{ecc_strength//2} byte errors")
    else:
        ecc_strength = 0
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'use_ecc_recovery': use_ecc_recovery,
        'ecc_strength': ecc_strength if use_ecc_recovery else 0
    }


# ============================================================================
#                    ECC MESSAGE PROCESSING
# ============================================================================

def encode_message_with_ecc(message: str, use_ecc: bool, 
                           nsym: int = 32) -> bytes:
    """
    Encode message and optionally add ECC.
    
    Args:
        message: plain text message (already string or bytes)
        use_ecc: whether to add error correction
        nsym: parity bytes for ECC
    
    Returns:
        bytes to embed in image
    
    Raises:
        ValueError if encoding fails
    """
    try:
        # Handle both string and bytes input
        if isinstance(message, str):
            message_bytes = message.encode('utf-8')
        elif isinstance(message, (bytes, bytearray)):
            message_bytes = bytes(message)  # Convert bytearray to bytes
        else:
            raise ValueError(f"Invalid message type: {type(message)}")
        
        if use_ecc:
            logger.info(f"Adding ECC with {nsym} parity bytes")
            encoded = add_redundancy(message_bytes, nsym=nsym)
            logger.info(f"After ECC: {len(message_bytes)} → {len(encoded)} bytes")
            return encoded
        else:
            return message_bytes
    
    except Exception as e:
        logger.error(f"ECC encode failed: {e}")
        raise ValueError(f"Message encoding failed: {str(e)}")


def decode_message_with_ecc_recovery(decoded_data: str, use_ecc_recovery: bool,
                                     nsym: int = 32, 
                                     use_encryption: bool = False,
                                     decryption_password: Optional[str] = None) -> Tuple[str, str]:
    """
    Decode message and attempt ECC recovery if enabled.
    
    Args:
        decoded_data: raw extracted data from image
        use_ecc_recovery: whether to attempt ECC recovery
        nsym: expected parity bytes
        use_encryption: whether data is encrypted
        decryption_password: password if encrypted
    
    Returns:
        (recovered_message: str, status: str)
        status = 'success', 'ecc_recovered', 'ecc_failed', 'decrypt_failed'
    
    Raises:
        ValueError if critical error
    """
    try:
        # First, try to recover from ECC if enabled
        if use_ecc_recovery and decoded_data:
            try:
                logger.info(f"Attempting ECC recovery with nsym={nsym}")
                
                # Convert to bytes if string
                if isinstance(decoded_data, str):
                    decoded_bytes = decoded_data.encode('latin-1')  # preserve all byte values
                else:
                    decoded_bytes = decoded_data
                
                # Try to recover
                recovered = recover_redundancy(decoded_bytes, nsym=nsym)
                logger.info(f"ECC recovery successful: {len(decoded_bytes)} → {len(recovered)} bytes")
                
                # Now handle decryption if needed
                if use_encryption and decryption_password:
                    from src.encryption.encryption import decrypt_message
                    try:
                        final_message = decrypt_message(recovered.decode('utf-8'), decryption_password)
                        return final_message, 'ecc_recovered'
                    except Exception as e:
                        logger.error(f"Decryption after ECC failed: {e}")
                        return recovered.decode('utf-8', errors='replace'), 'ecc_recovered'
                else:
                    return recovered.decode('utf-8'), 'ecc_recovered'
            
            except ValueError as e:
                logger.warning(f"ECC recovery failed: {e}")
                # Fall through to try without ECC
                pass
        
        # If ECC recovery failed or not enabled, try direct decryption
        if use_encryption and decryption_password:
            from src.encryption.encryption import decrypt_message
            try:
                final_message = decrypt_message(decoded_data, decryption_password)
                return final_message, 'success'
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                raise ValueError(f"Decryption failed. Wrong password? {str(e)}")
        else:
            return decoded_data, 'success'
    
    except Exception as e:
        logger.error(f"Message decoding failed: {e}")
        raise ValueError(f"Message decoding failed: {str(e)}")


# ============================================================================
#                    ECC TESTING SECTION
# ============================================================================

def show_redundancy_section():
    """Display error correction testing interface."""
    
    from src.ui.reusable_components import show_divider
    
    st.markdown("""
        <div class="animate-fade-in-down">
            <h2>🛡️ Error Correction</h2>
            <p style="color: #8B949E; margin-bottom: 1rem;">Protect messages from corruption with Reed-Solomon codes</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    tab_test, tab_help, tab_capacity = st.tabs(["🧪 Test ECC", "❓ Help", "📊 Capacity Calculator"])
    
    with tab_test:
        _show_ecc_test_tab()
    
    with tab_help:
        _show_ecc_help_tab()
    
    with tab_capacity:
        _show_capacity_calculator_tab()


def _show_ecc_test_tab():
    """ECC testing interface."""
    col1, col2 = st.columns(2)
    
    with col1:
        render_step(1, "Enter Message")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        message = st.text_area(
            "Message to protect",
            placeholder="Enter a message to test error correction",
            height=150,
            key="ecc_test_message"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        render_step(2, "Configure ECC")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        ecc_strength = st.slider(
            "Parity bytes",
            min_value=8,
            max_value=128,
            value=32,
            step=8,
            key="ecc_test_strength",
            help="More parity = more recovery capability"
        )
        
        recovery_capacity = ecc_strength // 2
        st.info(f"""
        **Configuration:**
        - Parity: {ecc_strength} bytes
        - Can recover: ~{recovery_capacity} byte errors
        - Overhead: ~{(ecc_strength/256)*100:.1f}% (per 256 bytes payload)
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if message:
        if st.button("🔧 Test Error Correction", use_container_width=True, type="primary"):
            _run_ecc_test(message, ecc_strength)


def _run_ecc_test(message: str, nsym: int):
    """Run ECC test on message."""
    try:
        with st.spinner("Testing ECC..."):
            from .corruption_simulator import random_byte_flips
            
            message_bytes = message.encode('utf-8')
            
            # Encode with ECC
            encoded = add_redundancy(message_bytes, nsym=nsym)
            
            st.divider()
            st.markdown("### Test Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Original Size", f"{len(message_bytes)} B")
            with col2:
                st.metric("With ECC", f"{len(encoded)} B")
            with col3:
                overhead = len(encoded) - len(message_bytes)
                st.metric("Overhead", f"{overhead} B")
            
            # Simulate corruption
            st.divider()
            st.markdown("### Corruption Simulation")
            
            corruption_level = st.slider(
                "Simulate byte flips",
                min_value=0,
                max_value=min(nsym, len(encoded)//2),
                value=nsym//4,
                step=1,
                key="ecc_test_flips"
            )
            
            if corruption_level > 0:
                if st.button("💥 Corrupt & Recover", use_container_width=True):
                    corrupted = random_byte_flips(encoded, n_flips=corruption_level, seed=123)
                    
                    st.info(f"Corrupted {corruption_level} random bytes")
                    
                    try:
                        recovered = recover_redundancy(corrupted, nsym=nsym)
                        
                        if recovered == message_bytes:
                            st.success("✅ **Perfect Recovery!** Message recovered without loss")
                        else:
                            st.warning(f"⚠️ Partial recovery. Recovered: {len(recovered)}/{len(message_bytes)} bytes")
                        
                        st.code(recovered.decode('utf-8', errors='replace'))
                    
                    except ValueError as e:
                        st.error(f"❌ Recovery failed: {str(e)}")
                        st.info(f"💡 Try decreasing corruption level or increasing ECC strength")
            else:
                st.info("Slide to the right to simulate corruption")
            
            # Stats
            st.divider()
            st.markdown("### Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Recovery Capability", f"~{nsym//2} bytes")
            with col2:
                st.metric("Backend", "Reed-Solomon" if _HAS_RS else "Replication")
            with col3:
                overhead_pct = (nsym / len(message_bytes)) * 100 if message_bytes else 0
                st.metric("Efficiency", f"{overhead_pct:.1f}%")
    
    except Exception as e:
        show_error(f"ECC test error: {str(e)}")
        logger.error(f"ECC test failed: {e}", exc_info=True)


def _show_ecc_help_tab():
    """ECC help documentation."""
    st.markdown("""
    ### 🛡️ What is Error Correction?
    
    Error Correction Codes (ECC) add redundancy to your data so it can survive corruption.
    Think of it like **digital insurance** — if some data gets damaged, ECC can recover it.
    
    ---
    
    ### How Reed-Solomon Works
    
    **Encoding:**
    1. Message: `101010... (256 bytes)`
    2. Add parity: `[256 bytes] + [32 parity bytes]` = 288 bytes total
    3. Embed in image
    
    **Transmission (with corruption):**
    - Some bits flip due to JPEG compression or noise
    - Up to 16 bytes can be wrong
    
    **Decoding:**
    1. Extract messages: `[corrupted 256] + [32 parity]`
    2. Use parity to detect errors
    3. Calculate corrections
    4. Recover original `101010...`
    
    ---
    
    ### When to Use ECC
    
    ✅ **Enable ECC if:**
    - Sending images via email (JPEG compression)
    - Image will be screenshotted or photographed
    - Data is critical and must be recoverable
    - Working with phone photos (noisy capture)
    
    ❌ **Disable ECC if:**
    - Direct PNG transfer (no compression)
    - Message size is critical
    - Images are perfect quality
    
    ---
    
    ### Configuration Guide
    
    | Strength | Recovery | Overhead | Use Case |
    |----------|----------|----------|----------|
    | 8 bytes | ~4 errors | 0.3% | Quick tests |
    | 16 bytes | ~8 errors | 0.6% | Light corruption |
    | 32 bytes | ~16 errors | 1.2% | **Recommended** |
    | 64 bytes | ~32 errors | 2.5% | Heavy compression |
    | 128 bytes | ~64 errors | 5% | Maximum protection |
    
    **Recommendation:** Use **32 parity bytes** as default sweet spot.
    
    ---
    
    ### Common Questions
    
    **Q: Will ECC increase file size?**  
    A: Yes, by the number of parity bytes. With nsym=32, ~3% overhead.
    
    **Q: What if ECC recovery fails?**  
    A: System tries best-effort recovery, then falls back to raw message.
    
    **Q: Is ECC compatible with encryption?**  
    A: Yes! Encrypt → Encode with ECC → Embed. Decode → ECC recovery → Decrypt.
    
    **Q: Can I recover from any corruption?**  
    A: No, only up to nsym/2 byte errors. Extreme corruption can't be fixed.
    """)


def _show_capacity_calculator_tab():
    """Capacity calculator for ECC planning."""
    st.markdown("### 📊 Image Capacity Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Image Properties**")
        
        width = st.number_input("Image width (px)", min_value=100, value=800, step=100)
        height = st.number_input("Image height (px)", min_value=100, value=600, step=100)
        
        channels = st.selectbox("Color channels", [3, 4], index=0, format_func=lambda x: "RGB" if x == 3 else "RGBA")
        lsb_bits = st.selectbox("LSB bits per channel", [1, 2, 4, 8], index=0)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Message Properties**")
        
        message_len = st.number_input("Message length (bytes)", min_value=1, value=256, step=50)
        use_ecc = st.checkbox("Use ECC?", value=True)
        
        if use_ecc:
            nsym = st.number_input("Parity bytes", min_value=8, value=32, step=8)
        else:
            nsym = 0
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate
    st.divider()
    
    fits, available = can_fit_payload(
        (width, height),
        message_len,
        nsym,
        channels=channels,
        lsb_bits=lsb_bits
    )
    
    required = message_len + nsym
    total_capacity = (width * height * channels * lsb_bits) // 8
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Capacity", f"{total_capacity:,} B")
    with col2:
        st.metric("Required Size", f"{required:,} B")
    with col3:
        st.metric("Available", f"{available:,} B")
    with col4:
        status = "✅ FITS" if fits else "❌ DOESN'T FIT"
        st.metric("Status", status)
    
    # Detailed report
    st.divider()
    
    report = pretty_report(
        (width, height),
        message_len,
        nsym,
        channels=channels,
        lsb_bits=lsb_bits
    )
    
    st.code(report, language="text")
    
    # Recommendations
    if not fits:
        shortage = required - available
        rec_width = int(width * (required / available) ** 0.5)
        rec_height = int(height * (required / available) ** 0.5)
        
        st.warning(f"""
        **⚠️ Message doesn't fit!**
        
        Shortage: {shortage:,} bytes
        
        **Recommendations:**
        - Increase image to at least {rec_width}×{rec_height}
        - Reduce message by {shortage:,} bytes
        - Disable ECC (save {nsym} bytes)
        - Use 2 LSB bits (double capacity)
        """)
    else:
        safety_margin = (available / total_capacity) * 100
        st.success(f"✅ Message fits with {safety_margin:.1f}% safety margin!")