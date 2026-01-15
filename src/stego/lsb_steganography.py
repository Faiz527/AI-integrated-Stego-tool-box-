"""
LSB Steganography Module
=========================
Implements Least Significant Bit (LSB) steganography in spatial domain.
Supports optional image filtering for preprocessing.
"""

from PIL import Image, ImageFilter
import numpy as np


# ============================================================================
#                   IMAGE FILTERING (LSB Method)
# ============================================================================

def apply_filter(img, filter_type):
    """Apply optional image filter for preprocessing."""
    filters = {
        "None": lambda x: x,
        "Blur": lambda x: x.filter(ImageFilter.BLUR),
        "Sharpen": lambda x: x.filter(ImageFilter.SHARPEN),
        "Grayscale": lambda x: x.convert('L').convert('RGB')
    }
    return filters.get(filter_type, lambda x: x)(img)


# ============================================================================
#                          LSB METHOD (SPATIAL DOMAIN)
# ============================================================================

def encode_image(img, secret_text, filter_type="None"):
    """
    Encode secret message into image using LSB (Least Significant Bit) method.
    
    Algorithm:
    1. Apply optional image filter
    2. Convert image to numpy array
    3. Convert secret text to binary with terminator
    4. Replace LSB of each pixel channel with message bits
    5. Return encoded image
    
    Capacity:
    - 3 bits per pixel (RGB: 1 bit each)
    - Image size 800×600 = 1,440,000 bits ≈ 180 KB
    
    Args:
        img (PIL.Image): Input image
        secret_text (str): Secret message to embed
        filter_type (str): Optional filter ("None", "Blur", "Sharpen", "Grayscale")
    
    Returns:
        PIL.Image: Encoded image with hidden message
    
    Raises:
        ValueError: If message exceeds image capacity
    """
    # Apply image filter if specified
    img = apply_filter(img, filter_type)
    
    # Convert image to numpy array for efficient pixel manipulation
    img_array = np.array(img, dtype=np.uint8)
    
    # Convert secret text to binary format with terminator
    binary_secret = ''.join(format(ord(i), '08b') for i in secret_text) + '11111110'
    
    # Calculate maximum capacity (3 bits per pixel)
    max_bits = img_array.shape[0] * img_array.shape[1] * 3
    
    # Check if message fits in image
    if len(binary_secret) > max_bits:
        raise ValueError(
            f"Message too large for LSB. "
            f"Max capacity: {max_bits // 8} characters, "
            f"Your message: {len(binary_secret) // 8} characters"
        )
    
    # Embed message bits into LSB of each color channel
    data_index = 0
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):
                if data_index < len(binary_secret):
                    bit = int(binary_secret[data_index])
                    img_array[i, j, k] = (img_array[i, j, k] & 254) | bit
                    data_index += 1
    
    return Image.fromarray(img_array)


def decode_image(img):
    """
    Decode secret message from image using LSB method.
    
    Algorithm:
    1. Convert image to numpy array
    2. Extract LSB from each pixel channel sequentially
    3. Group bits into bytes (8 bits = 1 character)
    4. Convert bytes to ASCII characters
    5. Stop when terminator bit sequence found
    6. Return decoded message
    
    Args:
        img (PIL.Image): Encoded image containing hidden message
    
    Returns:
        str: Decoded message, or None if no valid message found
    """
    # Convert image to numpy array
    img_array = np.array(img, dtype=np.uint8)
    
    # Extract all LSBs from pixels in order
    binary_data = ''
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):
                binary_data += str(img_array[i, j, k] & 1)
    
    # Convert binary string to characters
    decoded_text = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        
        # Check for terminator sequence
        if byte == '11111110':
            break
        
        # Only process complete bytes
        if len(byte) == 8:
            decoded_text += chr(int(byte, 2))
    
    return decoded_text if decoded_text else None
