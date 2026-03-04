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


def encode_dct(image, message):
    """
    ACTUAL DCT implementation - embeds in DCT coefficients.
    
    Process:
    1. Convert image to grayscale Y-channel
    2. Divide into 8×8 blocks
    3. Apply DCT to each block
    4. Modify AC coefficients (not DC) for message bits
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
    img_array = np.array(gray, dtype=np.float32)
    
    h, w = img_array.shape
    
    # Message encoding
    message_bytes = message.encode('utf-8')
    message_length = len(message_bytes)
    
    # Calculate capacity: 1 bit per 8×8 block (very conservative for robustness)
    num_blocks_h = h // 8
    num_blocks_w = w // 8
    total_blocks = num_blocks_h * num_blocks_w
    max_bits = total_blocks  # 1 bit per block
    max_bytes = max_bits // 8
    
    if message_length + 2 > max_bytes:
        raise ValueError(
            f"Message too large for DCT! "
            f"Image capacity: {max_bytes - 2} bytes, "
            f"Message size: {message_length} bytes. "
            f"Required image size: at least {int(np.sqrt((message_length + 2) * 8))*8}x{int(np.sqrt((message_length + 2) * 8))*8} pixels"
        )
    
    # Prepare bit string: 16-bit length prefix + message bits
    bit_string = format(message_length, '016b')
    for byte in message_bytes:
        bit_string += format(byte, '08b')
    
    logger.info(f"DCT: Encoding {message_length} bytes in {total_blocks} 8x8 blocks")
    logger.debug(f"DCT: Total bits to embed: {len(bit_string)}, Capacity: {max_bits} bits")
    
    # Flatten block grid and embed bits
    bit_index = 0
    
    for i in range(num_blocks_h):
        for j in range(num_blocks_w):
            if bit_index >= len(bit_string):
                break
            
            # Extract 8×8 block
            y_start = i * 8
            x_start = j * 8
            block = img_array[y_start:y_start+8, x_start:x_start+8].copy()
            
            # Apply DCT
            dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
            
            # Embed 1 bit per block in middle frequency coefficient
            # Use (2, 2) position - good robustness
            bit = int(bit_string[bit_index])
            
            # Quantize to reasonable level for JPEG robustness
            quantize = 32  # Larger quantization = more robust to JPEG
            coeff_value = dct_block[2, 2]
            coeff_int = int(round(coeff_value / quantize))
            
            # Embed bit into LSB
            coeff_int = (coeff_int & ~1) | bit
            
            # Dequantize
            dct_block[2, 2] = coeff_int * quantize
            
            # Apply inverse DCT
            restored_block = idct(idct(dct_block, axis=0, norm='ortho'), axis=1, norm='ortho')
            
            # Place back in image with clipping
            img_array[y_start:y_start+8, x_start:x_start+8] = np.clip(restored_block, 0, 255)
            
            bit_index += 1
    
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
        img_array = np.array(gray, dtype=np.float32)
        
        h, w = img_array.shape
        num_blocks_h = h // 8
        num_blocks_w = w // 8
        
        bits = []
        
        logger.debug(f"DCT: Decoding from {num_blocks_h}x{num_blocks_w} blocks")
        
        # Extract bits from blocks (must match encoding order!)
        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                y_start = i * 8
                x_start = j * 8
                block = img_array[y_start:y_start+8, x_start:x_start+8]
                
                # Apply DCT
                dct_block = dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho')
                
                # Extract bit from (2, 2) position
                quantize = 32
                coeff_int = int(round(dct_block[2, 2] / quantize))
                bit = coeff_int & 1
                bits.append(str(bit))
        
        bit_string = ''.join(bits)
        logger.debug(f"DCT: Extracted {len(bit_string)} bits from image")
        
        # Extract message length (first 16 bits)
        if len(bit_string) < 16:
            logger.warning("DCT: Not enough bits to extract message length header")
            return ''
        
        message_length = int(bit_string[:16], 2)
        logger.debug(f"DCT: Message length header = {message_length}")
        
        # Validate message length
        if message_length == 0:
            logger.warning("DCT: Message length is 0")
            return ''
        
        if message_length > 100_000:
            logger.warning(f"DCT: Message length {message_length} seems invalid")
            return ''
        
        # Check if enough bits available
        total_bits_needed = 16 + (message_length * 8)
        if total_bits_needed > len(bit_string):
            logger.warning(
                f"DCT: Not enough bits. Need {total_bits_needed}, got {len(bit_string)}"
            )
            return ''
        
        # Extract and decode message
        message_bits = bit_string[16 : 16 + (message_length * 8)]
        message_bytes = bytearray()
        
        for i in range(0, len(message_bits), 8):
            byte_bits = message_bits[i : i + 8]
            if len(byte_bits) == 8:
                message_bytes.append(int(byte_bits, 2))
        
        # Decode UTF-8
        message = message_bytes.decode('utf-8', errors='replace')
        logger.info(f"DCT: Successfully decoded message ({len(message)} characters)")
        
        return message
    
    except Exception as e:
        logger.error(f"DCT decode error: {str(e)}", exc_info=True)
        return ''