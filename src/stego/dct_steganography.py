"""
Hybrid DCT Steganography Module
================================
Implements Hybrid DCT (Y-Channel LSB) steganography in frequency domain.
Uses Y-channel for JPEG compatibility while avoiding reconstruction issues.
"""

import numpy as np
from PIL import Image
import logging
from scipy.fftpack import dct, idct

logger = logging.getLogger(__name__)

# ============================================================================
#                     HYBRID DCT METHOD (FREQUENCY DOMAIN)
# ============================================================================

def rgb_to_ycbcr(rgb_array):
    """Convert RGB to YCbCr color space."""
    # Standard conversion matrix
    mat = np.array([[0.299, 0.587, 0.114],
                    [-0.169, -0.331, 0.5],
                    [0.5, -0.419, -0.081]])
    
    # Reshape for matrix multiplication
    result = np.dot(rgb_array, mat.T)
    result[:, :, 1:] += 128
    return np.uint8(np.clip(result, 0, 255))


def ycbcr_to_rgb(ycbcr_array):
    """Convert YCbCr to RGB color space."""
    # Inverse conversion matrix
    mat = np.array([[1, 0, 1.402],
                    [1, -0.344, -0.714],
                    [1, 1.772, 0]])
    
    ycbcr = ycbcr_array.astype(np.float32)
    ycbcr[:, :, 1:] -= 128
    result = np.dot(ycbcr, mat.T)
    return np.uint8(np.clip(result, 0, 255))


def encode_dct(image: Image.Image, message: str) -> Image.Image:
    """
    Encode message into image using Hybrid DCT method.
    
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
        rgb_array = np.array(image, dtype=np.float32)
        
        # Convert to YCbCr
        ycbcr_array = rgb_to_ycbcr(rgb_array)
        
        # Extract Y channel
        y_channel = ycbcr_array[:, :, 0].astype(np.float32)
        
        # Get dimensions
        height, width = y_channel.shape
        
        # Convert message to binary
        message_bits = ''.join(format(ord(char), '08b') for char in message)
        message_bits += '00000000'  # Add null terminator
        
        # Check capacity
        capacity = (height // 8) * (width // 8) * 16  # 2 bits per 8x8 block
        if len(message_bits) > capacity:
            raise ValueError(f"Message too large. Max capacity: {capacity} bits")
        
        # Process image in 8x8 blocks
        bit_index = 0
        
        for y in range(0, height - 7, 8):
            for x in range(0, width - 7, 8):
                # Extract 8x8 block
                block = y_channel[y:y+8, x:x+8]
                
                # Apply DCT
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Embed bits in AC coefficients (avoiding DC component)
                if bit_index < len(message_bits):
                    # Embed in low-frequency AC coefficients
                    for i in range(1, min(3, 8)):
                        for j in range(1, min(3, 8)):
                            if bit_index < len(message_bits):
                                bit = int(message_bits[bit_index])
                                # LSB replacement
                                if bit == 1:
                                    dct_block[i, j] = int(dct_block[i, j]) | 1
                                else:
                                    dct_block[i, j] = int(dct_block[i, j]) & ~1
                                bit_index += 1
                
                # Apply inverse DCT
                idct_block = idct(idct(dct_block.T, norm='ortho').T, norm='ortho')
                
                # Update Y channel
                y_channel[y:y+8, x:x+8] = np.clip(idct_block, 0, 255)
        
        # Update YCbCr array
        ycbcr_array[:, :, 0] = np.uint8(y_channel)
        
        # Convert back to RGB
        rgb_result = ycbcr_to_rgb(ycbcr_array)
        
        # Convert to image
        encoded_image = Image.fromarray(rgb_result)
        
        logger.info(f"DCT encoding successful. Message length: {len(message)} chars")
        return encoded_image
        
    except Exception as e:
        logger.error(f"DCT encoding failed: {str(e)}")
        raise


def decode_dct(image: Image.Image) -> str:
    """
    Decode message from image using Hybrid DCT method.
    
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
        rgb_array = np.array(image, dtype=np.float32)
        
        # Convert to YCbCr
        ycbcr_array = rgb_to_ycbcr(rgb_array)
        
        # Extract Y channel
        y_channel = ycbcr_array[:, :, 0].astype(np.float32)
        
        # Get dimensions
        height, width = y_channel.shape
        
        # Extract bits from 8x8 blocks
        message_bits = ''
        
        for y in range(0, height - 7, 8):
            for x in range(0, width - 7, 8):
                # Extract 8x8 block
                block = y_channel[y:y+8, x:x+8]
                
                # Apply DCT
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                
                # Extract bits from AC coefficients
                for i in range(1, min(3, 8)):
                    for j in range(1, min(3, 8)):
                        bit = int(dct_block[i, j]) & 1
                        message_bits += str(bit)
        
        # Convert bits to characters
        message = ''
        for i in range(0, len(message_bits) - 8, 8):
            byte = message_bits[i:i+8]
            char = chr(int(byte, 2))
            if char == '\0':  # Null terminator
                break
            message += char
        
        logger.info(f"DCT decoding successful. Message length: {len(message)} chars")
        return message
        
    except Exception as e:
        logger.error(f"DCT decoding failed: {str(e)}")
        raise
