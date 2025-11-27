"""
Steganography Module
====================
Implements two independent steganography methods:
1. LSB (Least Significant Bit) - Spatial domain encoding
2. Hybrid DCT (Y-Channel LSB) - Frequency domain inspired encoding

Both methods embed secret messages into images with different
capacity/security trade-offs.
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


# ============================================================================
#                     HYBRID DCT METHOD (FREQUENCY DOMAIN)
# ============================================================================

def encode_dct(img, secret_text):
    """
    Encode secret message into image using Hybrid DCT (Y-Channel LSB) method.
    
    Uses Y-channel LSBs instead of true DCT because:
    - True DCT LSB modifications cause 10-100x amplification during IDCT
    - Results in complete data loss
    - Y-channel has frequency properties while avoiding reconstruction issues
    
    Advantages over RGB LSB:
    - Better steganalysis resistance (Y-channel only)
    - Better JPEG compatibility (Y survives compression)
    - Professional steganography standard
    
    Capacity: 1 bit per pixel (800×600 = 60 KB)
    
    Args:
        img (PIL.Image): Input image
        secret_text (str): Secret message to embed
    
    Returns:
        PIL.Image: Encoded image in RGB format
    
    Raises:
        ValueError: If message exceeds capacity
    """
    # Convert RGB to YCbCr color space
    img_ycbcr = img.convert('YCbCr')
    y_channel, cb_channel, cr_channel = img_ycbcr.split()
    
    # Convert Y-channel to numpy array
    y_array = np.array(y_channel, dtype=np.uint8)
    height, width = y_array.shape
    
    # Prepare message with length header (16 bits)
    msg_length = len(secret_text)
    length_bits = format(msg_length, '016b')
    binary_message = ''.join([format(ord(char), '08b') for char in secret_text])
    payload = length_bits + binary_message
    
    # Calculate capacity
    max_bits = height * width
    
    # Check if message fits
    if len(payload) > max_bits:
        raise ValueError(
            f"Message too large for Hybrid DCT. "
            f"Max: {(max_bits - 16)} characters, "
            f"Your message: {len(binary_message) // 8} characters"
        )
    
    # Embed payload bits into Y-channel LSBs
    payload_idx = 0
    for i in range(height):
        for j in range(width):
            if payload_idx < len(payload):
                bit = int(payload[payload_idx])
                y_array[i, j] = (y_array[i, j] & 254) | bit
                payload_idx += 1
    
    # Reconstruct YCbCr image with modified Y-channel
    y_img = Image.fromarray(y_array, mode='L')
    result = Image.merge('YCbCr', (y_img, cb_channel, cr_channel))
    
    return result.convert('RGB')


def decode_dct(img, debug=False):
    """
    Decode secret message from image using Hybrid DCT method.
    
    Algorithm:
    1. Convert image from RGB to YCbCr
    2. Extract Y-channel
    3. Extract LSB from each Y-channel pixel
    4. First 16 bits = message length header
    5. Remaining bits = message content
    6. Validate and convert to characters
    7. Return decoded message
    
    Args:
        img (PIL.Image): Encoded image
        debug (bool): If True, print debug information
    
    Returns:
        str: Decoded message, or None if decoding fails
    """
    try:
        # Convert RGB to YCbCr color space
        img_ycbcr = img.convert('YCbCr')
        y_channel = img_ycbcr.split()[0]
        y_array = np.array(y_channel, dtype=np.uint8)
        
        height, width = y_array.shape
        all_bits = []
        
        if debug:
            print(f"\n=== HYBRID DCT DECODE ===")
            print(f"Y-channel shape: {height}×{width}")
            print(f"Capacity: {height * width} bits = {(height * width) // 8} characters")
        
        # Extract LSB from each Y-channel pixel
        for i in range(height):
            for j in range(width):
                bit = y_array[i, j] & 1
                all_bits.append(str(bit))
        
        binary_data = ''.join(all_bits)
        
        if debug:
            print(f"Extracted {len(binary_data)} bits")
            print(f"First 32 bits: {binary_data[:32]}")
        
        # ===== Parse Message Header =====
        
        if len(binary_data) < 16:
            if debug:
                print(f"❌ Not enough bits for header")
            return None
        
        try:
            msg_length = int(binary_data[:16], 2)
            if debug:
                print(f"Message length: {msg_length}")
        except ValueError:
            if debug:
                print(f"❌ Failed to parse header")
            return None
        
        # ===== Validate Message Length =====
        
        if msg_length <= 0 or msg_length > 10000:
            if debug:
                print(f"❌ Invalid message length: {msg_length}")
            return None
        
        # ===== Extract Message Content =====
        
        message_bits = binary_data[16:]
        required_bits = msg_length * 8
        
        if debug:
            print(f"Message Extraction:")
            print(f"  Required bits: {required_bits}")
            print(f"  Available bits: {len(message_bits)}")
        
        if len(message_bits) < required_bits:
            if debug:
                print(f"❌ Not enough bits")
            return None
        
        # ===== Convert Binary to Characters =====
        
        decoded_text = ''
        for i in range(msg_length):
            byte_bits = message_bits[i*8:(i+1)*8]
            
            try:
                char_code = int(byte_bits, 2)
                
                if (32 <= char_code <= 126) or char_code in [9, 10, 13]:
                    decoded_text += chr(char_code)
                else:
                    if debug:
                        print(f"❌ Non-printable character at position {i}: {char_code}")
                    return None
                    
            except (ValueError, OverflowError):
                if debug:
                    print(f"❌ Failed to parse character at position {i}")
                return None
        
        # ===== Validate Result =====
        
        if debug:
            print(f"✅ Decoded: '{decoded_text}'")
        
        return decoded_text if len(decoded_text) == msg_length else None
    
    except Exception as e:
        if debug:
            print(f"❌ Error during decoding: {str(e)}")
        return None
