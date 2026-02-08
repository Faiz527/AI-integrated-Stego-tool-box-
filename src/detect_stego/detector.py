"""
Steganography Detection Logic
==============================
Core detection algorithms for identifying hidden data in images.
"""

import numpy as np
import logging
from scipy.fftpack import dct

logger = logging.getLogger(__name__)


def rgb_to_ycbcr(rgb_array):
    """Convert RGB to YCbCr color space."""
    mat = np.array([[0.299, 0.587, 0.114],
                    [-0.169, -0.331, 0.5],
                    [0.5, -0.419, -0.081]])
    result = np.dot(rgb_array.astype(np.float32), mat.T)
    result[:, :, 1:] += 128
    return np.uint8(np.clip(result, 0, 255))


def analyze_image_for_steganography(img_array, sensitivity):
    """
    Analyze image for steganography indicators.
    
    Detects:
    1. LSB steganography (RGB domain)
    2. Hybrid DCT steganography (Y-channel frequency domain)
    3. Statistical anomalies
    
    Args:
        img_array: numpy array of the image (RGB)
        sensitivity: Detection sensitivity (1-10)
    
    Returns:
        tuple: (detection_score, analysis_data)
    """
    try:
        from scipy.stats import entropy
        
        detection_indicators = []
        detection_score = 0
        
        # ====================================================================
        # METHOD 1: LSB Terminator Detection (11111110)
        # ====================================================================
        try:
            binary_data = ''
            flat_array = img_array.reshape(-1, 3)
            for pixel in flat_array[:15000]:
                for channel in range(3):
                    binary_data += str(pixel[channel] & 1)
            
            terminator_found = False
            valid_ascii_count = 0
            terminator_position = -1
            
            for i in range(0, min(len(binary_data) - 8, 80000), 8):
                byte = binary_data[i:i+8]
                if byte == '11111110':
                    terminator_found = True
                    terminator_position = i // 8
                    break
                char_val = int(byte, 2)
                if 32 <= char_val <= 126 or char_val in [10, 13, 9]:
                    valid_ascii_count += 1
            
            if terminator_found and valid_ascii_count >= 3:
                score = 45
                detection_score += score
                detection_indicators.append(("LSB Terminator", f"FOUND at byte {terminator_position}", score))
            elif terminator_found:
                score = 30
                detection_score += score
                detection_indicators.append(("LSB Terminator", f"Found (pos {terminator_position})", score))
            else:
                detection_indicators.append(("LSB Terminator", "Not found", 0))
                
        except Exception as e:
            detection_indicators.append(("LSB Terminator", f"Error", 0))
        
        # ====================================================================
        # METHOD 2: DCT Y-CHANNEL DETECTION (Hybrid DCT Method)
        # ====================================================================
        try:
            # Convert to YCbCr and extract Y channel
            ycbcr = rgb_to_ycbcr(img_array)
            y_channel = ycbcr[:, :, 0].astype(np.float32)
            
            height, width = y_channel.shape
            
            # Extract bits from DCT coefficients (same as your decoder)
            dct_bits = ''
            for y in range(0, min(height - 7, 200), 8):  # Check first ~25 blocks vertically
                for x in range(0, min(width - 7, 200), 8):
                    block = y_channel[y:y+8, x:x+8]
                    dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    
                    # Extract from AC coefficients (positions 1-2, 1-2)
                    for i in range(1, 3):
                        for j in range(1, 3):
                            bit = int(dct_block[i, j]) & 1
                            dct_bits += str(bit)
            
            # Look for null terminator (00000000) in DCT extracted data
            dct_terminator_found = False
            dct_ascii_count = 0
            dct_terminator_pos = -1
            
            for i in range(0, len(dct_bits) - 8, 8):
                byte = dct_bits[i:i+8]
                if byte == '00000000':
                    dct_terminator_found = True
                    dct_terminator_pos = i // 8
                    break
                char_val = int(byte, 2)
                if 32 <= char_val <= 126 or char_val in [10, 13, 9]:
                    dct_ascii_count += 1
            
            if dct_terminator_found and dct_ascii_count >= 3:
                score = 50
                detection_score += score
                detection_indicators.append(("DCT Terminator (Y-ch)", f"FOUND at byte {dct_terminator_pos}", score))
            elif dct_terminator_found:
                score = 35
                detection_score += score
                detection_indicators.append(("DCT Terminator (Y-ch)", f"Found (pos {dct_terminator_pos})", score))
            elif dct_ascii_count > 10:
                score = 25
                detection_score += score
                detection_indicators.append(("DCT ASCII (Y-ch)", f"{dct_ascii_count} chars found", score))
            else:
                detection_indicators.append(("DCT Analysis (Y-ch)", "No message detected", 0))
            
            # Check ASCII ratio in DCT extraction
            dct_total_bytes = len(dct_bits) // 8
            dct_ascii_ratio = dct_ascii_count / dct_total_bytes if dct_total_bytes > 0 else 0
            
            if dct_ascii_ratio > 0.5:
                score = 20
                detection_score += score
                detection_indicators.append(("DCT ASCII Ratio", f"{dct_ascii_ratio:.1%} - SUSPICIOUS", score))
            elif dct_ascii_ratio > 0.3:
                score = 10
                detection_score += score
                detection_indicators.append(("DCT ASCII Ratio", f"{dct_ascii_ratio:.1%} - borderline", score))
            else:
                detection_indicators.append(("DCT ASCII Ratio", f"{dct_ascii_ratio:.1%} - normal", 0))
                
        except Exception as e:
            detection_indicators.append(("DCT Analysis", f"Error: {str(e)[:15]}", 0))
        
        # ====================================================================
        # METHOD 3: Chi-Square PoV Attack (LSB detection)
        # ====================================================================
        try:
            hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            
            chi_sum = 0
            pair_count = 0
            for i in range(0, 256, 2):
                expected = (hist[i] + hist[i+1]) / 2 + 0.1
                chi_sum += ((hist[i] - expected) ** 2 + (hist[i+1] - expected) ** 2) / expected
                pair_count += 1
            
            chi_normalized = chi_sum / pair_count if pair_count > 0 else 999
            
            if chi_normalized < 1.5:
                score = 15
                detection_score += score
                detection_indicators.append(("Chi-Square (PoV)", f"{chi_normalized:.2f} - SUSPICIOUS", score))
            elif chi_normalized < 3.0:
                score = 8
                detection_score += score
                detection_indicators.append(("Chi-Square (PoV)", f"{chi_normalized:.2f} - borderline", score))
            else:
                detection_indicators.append(("Chi-Square (PoV)", f"{chi_normalized:.2f} - normal", 0))
                
        except Exception:
            detection_indicators.append(("Chi-Square", "Error", 0))
        
        # ====================================================================
        # METHOD 4: LSB 0/1 Ratio
        # ====================================================================
        try:
            lsb_plane = (img_array & 1).flatten()
            ones = np.sum(lsb_plane)
            total = len(lsb_plane)
            ratio = ones / total if total > 0 else 0
            
            if 0.49 <= ratio <= 0.51:
                score = 12
                detection_score += score
                detection_indicators.append(("LSB 0/1 Ratio", f"{ratio:.4f} - SUSPICIOUS", score))
            elif 0.47 <= ratio <= 0.53:
                score = 6
                detection_score += score
                detection_indicators.append(("LSB 0/1 Ratio", f"{ratio:.4f} - borderline", score))
            else:
                detection_indicators.append(("LSB 0/1 Ratio", f"{ratio:.4f} - natural", 0))
                
        except Exception:
            detection_indicators.append(("LSB Ratio", "Error", 0))
        
        # ====================================================================
        # METHOD 5: LSB Autocorrelation
        # ====================================================================
        try:
            lsb_r = (img_array[:, :, 0] & 1).flatten()
            
            if len(lsb_r) > 1000:
                autocorr = np.corrcoef(lsb_r[:-1], lsb_r[1:])[0, 1]
                
                if abs(autocorr) < 0.02:
                    score = 12
                    detection_score += score
                    detection_indicators.append(("LSB Correlation", f"{autocorr:.4f} - RANDOM", score))
                elif abs(autocorr) < 0.08:
                    score = 6
                    detection_score += score
                    detection_indicators.append(("LSB Correlation", f"{autocorr:.4f} - low", score))
                else:
                    detection_indicators.append(("LSB Correlation", f"{autocorr:.4f} - natural", 0))
                    
        except Exception:
            detection_indicators.append(("Correlation", "Error", 0))
        
        # ====================================================================
        # METHOD 6: ASCII in RGB LSB
        # ====================================================================
        try:
            ascii_count = 0
            total_bytes = 0
            
            for i in range(0, min(len(binary_data), 8000), 8):
                if i + 8 <= len(binary_data):
                    byte_val = int(binary_data[i:i+8], 2)
                    total_bytes += 1
                    if 32 <= byte_val <= 126:
                        ascii_count += 1
            
            ascii_ratio = ascii_count / total_bytes if total_bytes > 0 else 0
            
            if ascii_ratio > 0.6:
                score = 15
                detection_score += score
                detection_indicators.append(("ASCII in LSB", f"{ascii_ratio:.1%} - TEXT FOUND", score))
            elif ascii_ratio > 0.4:
                score = 10
                detection_score += score
                detection_indicators.append(("ASCII in LSB", f"{ascii_ratio:.1%} - suspicious", score))
            else:
                detection_indicators.append(("ASCII in LSB", f"{ascii_ratio:.1%} - normal", 0))
                
        except Exception:
            detection_indicators.append(("ASCII Pattern", "Error", 0))
        
        # ====================================================================
        # Apply sensitivity adjustment
        # ====================================================================
        sensitivity_factor = sensitivity / 5.0
        detection_score = detection_score * sensitivity_factor
        detection_score = min(100, detection_score)
        
        analysis_data = [
            {"Metric": ind[0], "Value": str(ind[1])}
            for ind in detection_indicators
        ]
        
        return detection_score, analysis_data
        
    except Exception as e:
        logger.error(f"Error in steganography detection: {str(e)}")
        return 0, [{"Metric": "Error", "Value": str(e)}]