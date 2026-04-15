"""
TRUE Hybrid DWT Steganography
==============================
Implements ACTUAL DWT wavelet domain embedding.
Uses Haar wavelets for robustness to filtering.

Key Features:
- Single-level Haar wavelet decomposition
- Detail coefficient embedding (cH, cV, cD)
- Robust to JPEG compression and noise
- Better survival through image operations
- Higher steganalysis resistance than LSB
"""

import pywt
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Quantization step for robust embedding
QUANT_STEP = 25


def _embed_bits_in_subband(subband, bit_string, bit_index):
    """Embed bits into a wavelet subband using QIM."""
    for i in range(subband.shape[0]):
        for j in range(subband.shape[1]):
            if bit_index >= len(bit_string):
                return bit_index
            bit = int(bit_string[bit_index])
            coeff = subband[i, j]
            
            quantized = round(coeff / QUANT_STEP) * QUANT_STEP
            quant_index = round(coeff / QUANT_STEP)
            if quant_index % 2 != bit:
                if coeff > quantized:
                    quantized += QUANT_STEP
                else:
                    quantized -= QUANT_STEP
            
            subband[i, j] = float(quantized)
            bit_index += 1
        if bit_index >= len(bit_string):
            return bit_index
    return bit_index


def _extract_bits_from_subband(subband, bits, message_length_ref, total_bits_ref):
    """
    Extract bits from a wavelet subband using QIM.
    Returns True if we should stop (got all bits or invalid length).
    """
    for i in range(subband.shape[0]):
        for j in range(subband.shape[1]):
            coeff = subband[i, j]
            quant_index = round(coeff / QUANT_STEP)
            bit = quant_index % 2
            bits.append(str(bit))
            
            # Check if we have 16 bits to read length
            if len(bits) == 16 and message_length_ref[0] is None:
                msg_len = int(''.join(bits[:16]), 2)
                if msg_len == 0:
                    message_length_ref[0] = 0
                    return True  # invalid length
                message_length_ref[0] = msg_len
                total_bits_ref[0] = 16 + (msg_len * 8)
            
            if total_bits_ref[0] and len(bits) >= total_bits_ref[0]:
                return True  # got all bits
        
        if total_bits_ref[0] and len(bits) >= total_bits_ref[0]:
            return True
    return False


def encode_dwt(image, message, update_progress=None, use_ecc=False, ecc_strength=32):
    """
    ACTUAL DWT implementation - embeds in wavelet coefficients.

    Args:
        image (PIL.Image): Input image
        message (str): Secret message (UTF-8)
        update_progress (callable): Optional callback for progress updates
                                   Called with float 0.0-1.0 at various stages
        use_ecc (bool): Enable Reed-Solomon error correction
        ecc_strength (int): ECC parity bytes (higher = more robust but larger)

    Returns:
        PIL.Image: Encoded image with hidden message

    Raises:
        ValueError: If message is too large for image capacity
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')

    gray = image.convert('L')
    img_array = np.array(gray, dtype=np.float64)

    h, w = img_array.shape

    # Ensure dimensions are even (required for wavelet decomposition)
    # Pad instead of truncate to preserve data
    if h % 2 != 0:
        h += 1
    if w % 2 != 0:
        w += 1
    # Pad with edge values (better than truncation)
    img_array = np.pad(
        img_array,
        ((0, h - img_array.shape[0]), (0, w - img_array.shape[1])),
        mode='edge'
    )

    # Message encoding
    if isinstance(message, (bytes, bytearray)):
        message_bytes = bytes(message)
    else:
        message_bytes = message.encode('utf-8')
    
    # Apply ECC if enabled (BEFORE embedding)
    if use_ecc:
        try:
            from stegotool.modules.module6_redundancy import add_redundancy
            message_bytes = add_redundancy(message_bytes, nsym=ecc_strength)
        except Exception as e:
            logger.warning(f"DWT ECC encoding failed: {e}. Proceeding without ECC.")
    
    message_length = len(message_bytes)

    # Calculate capacity
    subband_size = (h // 2) * (w // 2)
    max_bits = subband_size * 3  # cH + cV + cD
    max_bytes = max_bits // 8

    if message_length + 2 > max_bytes:
        raise ValueError(
            f"Message too large for DWT! "
            f"Image capacity: {max_bytes - 2} bytes, "
            f"Message size: {message_length} bytes. "
            f"Required image size: at least {int(np.sqrt(message_length * 8 * 2))}x{int(np.sqrt(message_length * 8 * 2))} pixels"
        )

    # Prepare bit string
    bit_string = format(message_length, '016b')
    for byte in message_bytes:
        bit_string += format(byte, '08b')

    logger.info(f"DWT: Encoding {message_length} bytes")
    logger.debug(f"DWT: Total bits: {len(bit_string)}, Subband capacity: {max_bits} bits")

    if update_progress:
        update_progress(0.1)

    # Apply single-level Haar DWT
    cA, (cH, cV, cD) = pywt.dwt2(img_array, 'haar')

    # Embed bits using QIM in each subband
    bit_index = 0
    
    logger.debug(f"DWT: Embedding in cH ({cH.shape[0]}x{cH.shape[1]})")
    bit_index = _embed_bits_in_subband(cH, bit_string, bit_index)
    
    if update_progress:
        update_progress(0.4)
    
    if bit_index < len(bit_string):
        logger.debug(f"DWT: Embedding in cV ({cV.shape[0]}x{cV.shape[1]})")
        bit_index = _embed_bits_in_subband(cV, bit_string, bit_index)
    
    if update_progress:
        update_progress(0.7)
    
    if bit_index < len(bit_string):
        logger.debug(f"DWT: Embedding in cD ({cD.shape[0]}x{cD.shape[1]})")
        bit_index = _embed_bits_in_subband(cD, bit_string, bit_index)

    # Reconstruct image
    reconstructed = pywt.idwt2((cA, (cH, cV, cD)), 'haar')

    result = np.clip(reconstructed[:h, :w], 0, 255).astype(np.uint8)
    encoded_image = Image.fromarray(result, 'L').convert('RGB')

    if update_progress:
        update_progress(1.0)

    logger.info(f"DWT: Successfully encoded {bit_index} bits")

    return encoded_image
def decode_dwt(image, update_progress=None, use_ecc=False, ecc_strength=32):
    """
    Decode message from DWT-encoded image.

    Args:
        image (PIL.Image): Encoded image
        update_progress (callable): Optional callback for progress updates
                                   Called with float 0.0-1.0 at various stages
        use_ecc (bool): Enable Reed-Solomon error correction recovery
        ecc_strength (int): ECC parity bytes (must match encoding)

    Returns:
        str: Decoded message (empty string if extraction fails)
    """
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')

        gray = image.convert('L')
        img_array = np.array(gray, dtype=np.float64)

        h, w = img_array.shape
        # Ensure dimensions are even (required for wavelet decomposition)
        # Pad instead of truncate for consistency with encoding
        if h % 2 != 0:
            h += 1
        if w % 2 != 0:
            w += 1
        # Pad with edge values
        img_array = np.pad(
            img_array,
            ((0, h - img_array.shape[0]), (0, w - img_array.shape[1])),
            mode='edge'
        )

        if update_progress:
            update_progress(0.1)

        # Apply single-level Haar DWT
        cA, (cH, cV, cD) = pywt.dwt2(img_array, 'haar')

        bits = []
        # Use mutable references so the helper can update them
        message_length_ref = [None]
        total_bits_ref = [None]

        if update_progress:
            update_progress(0.2)

        # Extract from cH
        done = _extract_bits_from_subband(cH, bits, message_length_ref, total_bits_ref)

        if update_progress:
            update_progress(0.5)

        # Extract from cV if needed
        if not done and (total_bits_ref[0] is None or len(bits) < total_bits_ref[0]):
            done = _extract_bits_from_subband(cV, bits, message_length_ref, total_bits_ref)

        if update_progress:
            update_progress(0.8)

        # Extract from cD if needed
        if not done and (total_bits_ref[0] is None or len(bits) < total_bits_ref[0]):
            done = _extract_bits_from_subband(cD, bits, message_length_ref, total_bits_ref)

        # Validate
        if len(bits) < 16:
            logger.warning("DWT: Not enough bits extracted")
            return ""

        message_length = message_length_ref[0]
        if message_length is None:
            message_length = int(''.join(bits[:16]), 2)
        
        logger.debug(f"DWT: Extracted message length = {message_length}")

        # Validate message length against actual subband capacity (not hardcoded limit)
        subband_size = (h // 2) * (w // 2)
        max_capacity = (subband_size * 3) // 8  # 3 subbands * subband_size / 8 bits per byte
        if message_length == 0 or message_length > max_capacity:
            logger.warning(f"DWT: Invalid message length {message_length} (capacity: {max_capacity} bytes)")
            return ""

        total_bits_needed = 16 + (message_length * 8)
        if len(bits) < total_bits_needed:
            logger.warning(f"DWT: Not enough bits. Have {len(bits)}, need {total_bits_needed}")
            return ""

        # Convert bits to bytes
        message_bytes = bytearray()
        for k in range(message_length):
            byte_bits = ''.join(bits[16 + k*8 : 16 + (k+1)*8])
            message_bytes.append(int(byte_bits, 2))

        # Apply ECC recovery if enabled (AFTER extraction)
        if use_ecc:
            try:
                from stegotool.modules.module6_redundancy import recover_redundancy
                message_bytes = recover_redundancy(message_bytes, nsym=ecc_strength)
                logger.debug(f"DWT: ECC recovery succeeded")
            except Exception as e:
                logger.warning(f"DWT: ECC recovery failed - {e}. Data may be corrupted.")
        
        # Try UTF-8 decode
        try:
            decoded = message_bytes.decode('utf-8')
            
            if update_progress:
                update_progress(1.0)

            logger.info(f"DWT: Successfully decoded {len(decoded)} characters")
            return decoded
        
        except UnicodeDecodeError:
            # Can't decode as UTF-8, use error handling
            decoded_binary = message_bytes.decode('utf-8', errors='replace')
            
            if update_progress:
                update_progress(1.0)
            
            logger.debug(f"DWT: UTF-8 decode with error handling ({len(message_bytes)} bytes)")
            return decoded_binary

    except UnicodeDecodeError:
        logger.warning("DWT: UTF-8 decode failed - not a valid DWT-encoded image")
        return ""
    except Exception as e:
        logger.error(f"DWT decode error: {e}")
        return ""