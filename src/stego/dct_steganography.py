"""
TRUE Hybrid DCT Steganography
==============================
Implements ACTUAL DCT frequency domain embedding.
Uses JPEG-DCT compatible coefficient modification.

Key Features:
- 8×8 block DCT transformation
- AC coefficient embedding (skips DC for robustness)
- Grayscale Y-channel processing
- Robust to JPEG compression
- Better steganalysis resistance than LSB
"""

from PIL import Image
import numpy as np
from scipy.fftpack import dct, idct
import logging

logger = logging.getLogger(__name__)

# Quantization step — must be large enough to survive float→uint8→float round-trip
# A step of 2 means we quantize coefficients to even/odd multiples of QUANT_STEP
QUANT_STEP = 25


def encode_dct(image, message):
    """
    ACTUAL DCT implementation - embeds in DCT coefficients.
    
    Process:
    1. Convert image to grayscale Y-channel
    2. Divide into 8×8 blocks
    3. Apply DCT to each block
    4. Modify AC coefficients using quantization embedding
    5. Apply inverse DCT
    6. Reconstruct image
    
    Args:
        image (PIL.Image): Input image (recommended: 1024x768 or larger)
        message (str): Secret message to encode (UTF-8)
    
    Returns:
        PIL.Image: Encoded image with hidden message
    
    Raises:
        ValueError: If message is too large for image capacity
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to grayscale (Y channel equivalent)
    gray = image.convert('L')
    img_array = np.array(gray, dtype=np.float64)
    
    h, w = img_array.shape
    
    # Message encoding
    if isinstance(message, (bytes, bytearray)):
        message_bytes = bytes(message)
    else:
        message_bytes = message.encode('utf-8')
    message_length = len(message_bytes)
    
    # Calculate capacity: 1 bit per 8×8 block
    num_blocks_h = h // 8
    num_blocks_w = w // 8
    total_blocks = num_blocks_h * num_blocks_w
    max_bits = total_blocks
    max_bytes = max_bits // 8
    
    if message_length + 2 > max_bytes:
        raise ValueError(
            f"Message too large for DCT! "
            f"Image capacity: {max_bytes - 2} bytes, "
            f"Message size: {message_length} bytes. "
            f"Required image size: at least {int(np.sqrt((message_length + 2) * 8)) * 8}x{int(np.sqrt((message_length + 2) * 8)) * 8} pixels"
        )
    
    # Prepare bit string: 16-bit length prefix + message bits
    bit_string = format(message_length, '016b')
    for byte in message_bytes:
        bit_string += format(byte, '08b')
    
    logger.info(f"DCT: Encoding {message_length} bytes in {total_blocks} 8x8 blocks")
    logger.debug(f"DCT: Total bits to embed: {len(bit_string)}, Capacity: {max_bits} bits")
    
    bit_index = 0
    
    for i in range(num_blocks_h):
        for j in range(num_blocks_w):
            if bit_index >= len(bit_string):
                break
            
            # Extract 8×8 block
            block = img_array[i*8:(i+1)*8, j*8:(j+1)*8].copy()
            
            # Apply 2D DCT
            dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            
            # Embed using quantization index modulation (QIM)
            # This is far more robust than simple parity embedding
            coeff = dct_block[4, 4]
            bit = int(bit_string[bit_index])
            
            # Quantize: map coefficient to nearest value where
            # floor(coeff / QUANT_STEP) % 2 == bit
            quantized = round(coeff / QUANT_STEP) * QUANT_STEP
            # Check if quantized index has correct parity
            quant_index = round(coeff / QUANT_STEP)
            if quant_index % 2 != bit:
                # Shift to adjacent quantization level with correct parity
                if coeff > quantized:
                    quantized += QUANT_STEP
                else:
                    quantized -= QUANT_STEP
            
            dct_block[4, 4] = float(quantized)
            
            # Apply inverse 2D DCT
            block_reconstructed = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
            img_array[i*8:(i+1)*8, j*8:(j+1)*8] = block_reconstructed
            
            bit_index += 1
        
        if bit_index >= len(bit_string):
            break
    
    # Convert back to image
    result = np.clip(img_array, 0, 255).astype(np.uint8)
    encoded_image = Image.fromarray(result, 'L').convert('RGB')
    
    logger.info(f"DCT: Successfully encoded {bit_index} bits")
    
    return encoded_image


def decode_dct(image):
    """
    Decode message from DCT-encoded image.
    
    Args:
        image (PIL.Image): Encoded image
    
    Returns:
        str: Decoded message (empty string if extraction fails)
    """
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to grayscale
        gray = image.convert('L')
        img_array = np.array(gray, dtype=np.float64)
        
        h, w = img_array.shape
        num_blocks_h = h // 8
        num_blocks_w = w // 8
        
        bits = []
        message_length = None
        total_bits_needed = None
        
        logger.debug(f"DCT: Decoding from {num_blocks_h}x{num_blocks_w} blocks")
        
        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                block = img_array[i*8:(i+1)*8, j*8:(j+1)*8]
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Extract bit using same QIM scheme
                coeff = dct_block[4, 4]
                quant_index = round(coeff / QUANT_STEP)
                bit = quant_index % 2
                bits.append(str(bit))
                
                # Early exit once we know the message length
                if len(bits) == 16 and message_length is None:
                    message_length = int(''.join(bits[:16]), 2)
                    if message_length == 0 or message_length > (num_blocks_h * num_blocks_w) // 8:
                        logger.warning(f"DCT: Invalid message length: {message_length}")
                        return ""
                    total_bits_needed = 16 + (message_length * 8)
                
                if total_bits_needed and len(bits) >= total_bits_needed:
                    break
            else:
                continue
            break
        
        if len(bits) < 16:
            logger.warning("DCT: Not enough bits extracted")
            return ""
        
        # Extract message length (first 16 bits)
        if message_length is None:
            message_length = int(''.join(bits[:16]), 2)
        
        logger.debug(f"DCT: Extracted message length = {message_length}")
        
        if message_length == 0 or message_length > 100000:
            logger.warning(f"DCT: Invalid message length: {message_length}")
            return ""
        
        total_bits_needed = 16 + (message_length * 8)
        if len(bits) < total_bits_needed:
            logger.warning(f"DCT: Not enough bits. Have {len(bits)}, need {total_bits_needed}")
            return ""
        
        # Convert bits to bytes
        message_bytes = bytearray()
        for k in range(message_length):
            byte_bits = ''.join(bits[16 + k*8 : 16 + (k+1)*8])
            message_bytes.append(int(byte_bits, 2))
        
        decoded = message_bytes.decode('utf-8')
        logger.info(f"DCT: Successfully decoded {len(decoded)} characters")
        return decoded
    
    except UnicodeDecodeError:
        logger.warning("DCT: UTF-8 decode failed - not a valid DCT-encoded image")
        return ""
    except Exception as e:
        logger.error(f"DCT decode error: {e}")
        return ""