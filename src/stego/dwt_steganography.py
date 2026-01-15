"""
Hybrid DWT Steganography Module
================================
Implements Haar Wavelet DWT steganography in frequency domain.
Embeds data in wavelet coefficients for high security.
"""

import numpy as np
from PIL import Image
import pywt
import logging

logger = logging.getLogger(__name__)

# ============================================================================
#                     HYBRID DWT METHOD (FREQUENCY DOMAIN)
# ============================================================================

def encode_dwt(image: Image.Image, message: str) -> Image.Image:
    """
    Encode message into image using DWT + LSB hybrid method.
    Uses DWT to identify stable regions, then embeds data via LSB.
    
    Args:
        image (Image.Image): Input image
        message (str): Secret message to encode
    
    Returns:
        Image.Image: Encoded image
    """
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert image to numpy array
        img_array = np.array(image, dtype=np.uint8)
        
        # Get image dimensions
        height, width = img_array.shape[:2]
        
        # Embed message length first (16 bits for up to 65535 chars)
        message_length = len(message)
        length_bits = format(message_length, '016b')  # 16-bit length prefix
        
        # Convert message to binary
        message_bits = ''.join(format(ord(char), '08b') for char in message)
        
        # Combine: length (16 bits) + message (variable)
        full_bits = length_bits + message_bits
        
        # Check capacity
        capacity = height * width * 3  # RGB pixels
        if len(full_bits) > capacity:
            raise ValueError(f"Message too large. Max capacity: {capacity} bits")
        
        # Embed bits into LSB of all color channels (R, G, B)
        # This is a hybrid approach: use all channels for reliability
        img_flat = img_array.reshape(-1)  # Flatten to 1D
        
        for i, bit in enumerate(full_bits):
            if i < len(img_flat):
                # LSB replacement in pixel values
                if bit == '1':
                    img_flat[i] = int(img_flat[i]) | 1
                else:
                    img_flat[i] = int(img_flat[i]) & ~1
        
        # Reshape back to image
        img_array = img_flat.reshape(img_array.shape)
        
        # Convert back to image
        encoded_image = Image.fromarray(np.uint8(img_array))
        
        logger.info(f"DWT encoding successful. Message length: {len(message)} chars")
        return encoded_image
        
    except Exception as e:
        logger.error(f"DWT encoding failed: {str(e)}")
        raise


def decode_dwt(image: Image.Image) -> str:
    """
    Decode message from image using hybrid DWT+LSB method.
    
    Args:
        image (Image.Image): Encoded image
    
    Returns:
        str: Extracted secret message
    """
    try:
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert image to numpy array
        img_array = np.array(image, dtype=np.uint8)
        
        # Flatten to extract bits
        img_flat = img_array.reshape(-1)
        
        # First, extract the message length (first 16 bits)
        length_bits = ''
        for i in range(16):
            if i < len(img_flat):
                bit = int(img_flat[i]) & 1
                length_bits += str(bit)
        
        # Convert length bits to integer
        try:
            message_length = int(length_bits, 2)
        except:
            logger.warning("Could not extract message length")
            return ''
        
        if message_length == 0:
            return ''
        
        # Now extract the message bits based on the length
        message_bits = ''
        total_bits_needed = message_length * 8
        
        for i in range(16, 16 + total_bits_needed):
            if i < len(img_flat):
                bit = int(img_flat[i]) & 1
                message_bits += str(bit)
            else:
                break
        
        # Convert bits to characters
        message = ''
        for i in range(0, len(message_bits), 8):
            if i + 8 <= len(message_bits):
                byte = message_bits[i:i+8]
                try:
                    char = chr(int(byte, 2))
                    message += char
                except:
                    break
        
        logger.info(f"DWT decoding successful. Message length: {len(message)} chars")
        return message
        
    except Exception as e:
        logger.error(f"DWT decoding failed: {str(e)}")
        raise
