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


def encode_dwt(image, message):
    """
    ACTUAL DWT implementation - embeds in wavelet coefficients.
    
    Args:
        image (PIL.Image): Input image
        message (str): Secret message (UTF-8)
    
    Returns:
        PIL.Image: Encoded image with hidden message
    
    Raises:
        ValueError: If message is too large for image capacity
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Work with grayscale (Y channel equivalent)
    gray = image.convert('L')
    img_array = np.array(gray, dtype=np.float32)
    
    h, w = img_array.shape
    
    # Ensure dimensions are even
    if h % 2 != 0:
        h -= 1
    if w % 2 != 0:
        w -= 1
    img_array = img_array[:h, :w]
    
    # Message encoding
    message_bytes = message.encode('utf-8')
    message_length = len(message_bytes)
    
    # Calculate capacity
    # Each subband is h/2 × w/2, we use 1 bit per coefficient
    subband_size = (h // 2) * (w // 2)
    max_bits = subband_size * 3  # cH + cV + cD (use only first few bits per coeff)
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
    
    # Apply single-level Haar DWT
    cA, (cH, cV, cD) = pywt.dwt2(img_array, 'haar')
    
    # Embed bits in detail coefficients (row-major order)
    bit_index = 0
    
    # Embed in cH (horizontal details) - row by row
    logger.debug(f"DWT: Embedding in cH ({cH.shape[0]}x{cH.shape[1]})")
    for i in range(cH.shape[0]):
        for j in range(cH.shape[1]):
            if bit_index < len(bit_string):
                bit = int(bit_string[bit_index])
                
                # Quantize for robustness (use larger quantization than DCT)
                quantize = 8
                coeff_int = int(round(cH[i, j] / quantize))
                
                # Embed bit into LSB
                coeff_int = (coeff_int & ~1) | bit
                
                # Dequantize
                cH[i, j] = coeff_int * quantize
                
                bit_index += 1
    
    # If more bits, embed in cV (vertical details)
    logger.debug(f"DWT: Embedding in cV ({cV.shape[0]}x{cV.shape[1]})")
    for i in range(cV.shape[0]):
        for j in range(cV.shape[1]):
            if bit_index < len(bit_string):
                bit = int(bit_string[bit_index])
                
                quantize = 8
                coeff_int = int(round(cV[i, j] / quantize))
                coeff_int = (coeff_int & ~1) | bit
                cV[i, j] = coeff_int * quantize
                
                bit_index += 1
    
    # If still more bits, embed in cD (diagonal details)
    logger.debug(f"DWT: Embedding in cD ({cD.shape[0]}x{cD.shape[1]})")
    for i in range(cD.shape[0]):
        for j in range(cD.shape[1]):
            if bit_index < len(bit_string):
                bit = int(bit_string[bit_index])
                
                quantize = 8
                coeff_int = int(round(cD[i, j] / quantize))
                coeff_int = (coeff_int & ~1) | bit
                cD[i, j] = coeff_int * quantize
                
                bit_index += 1
    
    # Reconstruct image
    reconstructed = pywt.idwt2((cA, (cH, cV, cD)), 'haar')
    
    # Ensure proper size and type
    result = np.clip(reconstructed[:h, :w], 0, 255).astype(np.uint8)
    encoded_image = Image.fromarray(result, 'L').convert('RGB')
    
    logger.info(f"DWT: Successfully encoded {bit_index} bits")
    
    return encoded_image


def decode_dwt(image):
    """
    Decode message from DWT-encoded image.
    
    Args:
        image (PIL.Image): Encoded image
    
    Returns:
        str: Decoded message (empty string if extraction fails)
    """
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        gray = image.convert('L')
        img_array = np.array(gray, dtype=np.float32)
        
        h, w = img_array.shape
        
        # Log dimensions for debugging
        logger.debug(f"DWT: Decoding from image {h}x{w}")
        
        # Ensure dimensions are even
        if h % 2 != 0:
            h -= 1
        if w % 2 != 0:
            w -= 1
        
        img_array = img_array[:h, :w]
        
        logger.debug(f"DWT: Adjusted dimensions to {h}x{w}")
        
        # Apply DWT
        try:
            cA, (cH, cV, cD) = pywt.dwt2(img_array, 'haar')
        except Exception as e:
            logger.warning(f"DWT decomposition failed: {str(e)}")
            return ''
        
        logger.debug(f"DWT: Decomposed to subbands: cA={cA.shape}, cH={cH.shape}, cV={cV.shape}, cD={cD.shape}")
        
        bits = []
        quantize = 8
        
        # Extract bits from cH (row-major order - must match encoding!)
        logger.debug(f"DWT: Extracting from cH ({cH.shape[0]}x{cH.shape[1]})")
        for i in range(cH.shape[0]):
            for j in range(cH.shape[1]):
                try:
                    coeff_int = int(round(cH[i, j] / quantize))
                    bit = coeff_int & 1
                    bits.append(str(bit))
                except Exception as e:
                    logger.debug(f"DWT: Error extracting bit at ({i},{j}): {e}")
                    continue
        
        logger.debug(f"DWT: Extracted {len(bits)} bits from cH")
        
        # Extract bits from cV
        logger.debug(f"DWT: Extracting from cV ({cV.shape[0]}x{cV.shape[1]})")
        for i in range(cV.shape[0]):
            for j in range(cV.shape[1]):
                try:
                    coeff_int = int(round(cV[i, j] / quantize))
                    bit = coeff_int & 1
                    bits.append(str(bit))
                except Exception as e:
                    logger.debug(f"DWT: Error extracting bit at ({i},{j}): {e}")
                    continue
        
        logger.debug(f"DWT: Extracted {len(bits)} bits total (cH + cV)")
        
        # Extract bits from cD
        logger.debug(f"DWT: Extracting from cD ({cD.shape[0]}x{cD.shape[1]})")
        for i in range(cD.shape[0]):
            for j in range(cD.shape[1]):
                try:
                    coeff_int = int(round(cD[i, j] / quantize))
                    bit = coeff_int & 1
                    bits.append(str(bit))
                except Exception as e:
                    logger.debug(f"DWT: Error extracting bit at ({i},{j}): {e}")
                    continue
        
        bit_string = ''.join(bits)
        logger.debug(f"DWT: Total bits extracted: {len(bit_string)}")
        
        # Extract message length
        if len(bit_string) < 16:
            logger.warning(f"DWT: Not enough bits for message length header (got {len(bit_string)}, need 16)")
            return ''
        
        message_length = int(bit_string[:16], 2)
        logger.debug(f"DWT: Message length = {message_length}")
        
        # Validate
        if message_length == 0:
            logger.debug("DWT: Empty message (length = 0)")
            return ''
        
        if message_length > 100_000:
            logger.warning(f"DWT: Invalid message length {message_length}")
            return ''
        
        if message_length * 8 + 16 > len(bit_string):
            logger.warning(
                f"DWT: Not enough bits. Need {message_length * 8 + 16}, got {len(bit_string)}"
            )
            return ''
        
        # Extract and decode message
        message_bits = bit_string[16 : 16 + (message_length * 8)]
        message_bytes = bytearray()
        
        for i in range(0, len(message_bits), 8):
            byte_bits = message_bits[i : i + 8]
            if len(byte_bits) == 8:
                message_bytes.append(int(byte_bits, 2))
        
        message = message_bytes.decode('utf-8', errors='replace')
        logger.info(f"DWT: Successfully decoded message ({len(message)} characters)")
        
        return message
    
    except Exception as e:
        logger.error(f"DWT decode error: {str(e)}", exc_info=True)
        return ''