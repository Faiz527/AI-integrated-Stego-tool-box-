"""
Wavelet Steganography Module (INVISIBLE VERSION - FIXED)
=========================================================
Implements Haar DWT-based steganography in CHROMINANCE channels.

CRITICAL FIX: Proper handling of signed DWT coefficients
- DWT coefficients can be negative (NOT just 0-255)
- Use int32/int64 for bit manipulation
- Handle negative numbers correctly in Python
- Preserve coefficient magnitude during embedding

Strategy:
- Y-channel: UNTOUCHED (original luminance preserved)
- Cb-channel: Embed full message with error correction
- Bit-planes 2-4: Safe embedding without destroying data

Technical Details:
- Uses bit-planes 2-4 in Cb (safer than 5-7)
- 3x bit repetition for error correction
- Majority voting for decode
- Proper signed integer handling
- Capacity: ~160K bits in Cb channel
"""

import numpy as np
import pywt
from PIL import Image


def encode_dct_dwt(img, secret_text, debug=False):
    """
    Encode secret message using Haar DWT in CHROMINANCE (Cb) channel.
    Y-channel remains UNTOUCHED for invisible embedding.
    
    Args:
        img (PIL.Image): Input image (PNG, JPG, JPEG)
        secret_text (str): Secret message to embed
        debug (bool): Enable debug output
    
    Returns:
        PIL.Image: Encoded image in RGB format (looks identical to original)
    
    Raises:
        ValueError: If message exceeds capacity
    """
    
    if debug:
        print(f"\n{'='*60}")
        print(f"DWT ENCODING - CHROMINANCE CHANNEL (Cb)")
        print(f"{'='*60}")
        print(f"Input message: '{secret_text}'")
        print(f"Message length: {len(secret_text)} chars")
        print(f"\n✅ Y-channel will remain UNTOUCHED (original)")
        print(f"✅ Cb-channel will be modified (invisible to eye)")
    
    # ===== STAGE 1: Color Space Conversion =====
    
    img_ycbcr = img.convert('YCbCr')
    y_channel, cb_channel, cr_channel = img_ycbcr.split()
    
    # CRITICAL: Keep Y-channel as-is (untouched)
    y_array = np.array(y_channel, dtype=np.float64)
    orig_height, orig_width = y_array.shape
    
    # Embed message in Cb channel
    cb_array = np.array(cb_channel, dtype=np.float64)
    
    if debug:
        print(f"\nOriginal image shape: {orig_height}×{orig_width}")
        print(f"Y-channel value range: {y_array.min():.2f} to {y_array.max():.2f}")
        print(f"Cb-channel value range (before): {cb_array.min():.2f} to {cb_array.max():.2f}")
    
    # ===== STAGE 2: Prepare Message =====
    
    msg_length = len(secret_text)
    length_bits = format(msg_length, '016b')
    binary_message = ''.join([format(ord(char), '08b') for char in secret_text])
    payload = length_bits + binary_message
    
    # 3x bit repetition for error correction
    repeated_payload = ''.join([bit * 3 for bit in payload])
    
    if debug:
        print(f"\nMessage preparation:")
        print(f"  Length header (16 bits): {length_bits} → {int(length_bits, 2)}")
        print(f"  Message bits: {len(binary_message)} bits ({len(binary_message)//8} bytes)")
        print(f"  Original payload: {len(payload)} bits")
        print(f"  With 3x redundancy: {len(repeated_payload)} bits")
    
    # ===== STAGE 3: Haar DWT Decomposition (Cb Channel) =====
    
    try:
        cA, (cH, cV, cD) = pywt.dwt2(cb_array, 'haar')
        
        ll_height, ll_width = cA.shape
        max_capacity = ll_height * ll_width * 3
        
        if debug:
            print(f"\nDWT Decomposition (Cb channel):")
            print(f"  LL band shape: {ll_height}×{ll_width}")
            print(f"  LL band capacity: {max_capacity} bits (positions 2-4)")
            print(f"  Effective capacity (with 3x redundancy): {ll_height * ll_width} bits")
            print(f"  LL band value range: {cA.min():.2f} to {cA.max():.2f}")
        
    except Exception as e:
        raise Exception(f"DWT decomposition failed: {str(e)}")
    
    # ===== STAGE 4: Validate Message Size =====
    
    if len(repeated_payload) > max_capacity:
        raise ValueError(
            f"Message too large! Capacity: {(ll_height * ll_width)} bits (~{(ll_height * ll_width)//8} bytes), "
            f"Your message: {len(payload)} bits (~{len(payload)//8} bytes)"
        )
    
    # ===== STAGE 5: Embed Message in Cb LL Band =====
    
    cA_flat = cA.flatten()
    
    if debug:
        before_sample = [int(round(x)) for x in cA_flat[:10]]
        print(f"\nEmbedding process (Cb channel, BIT-PLANES 2-4):")
        print(f"  LL coefficients (before): first 10 = {before_sample}")
    
    # CRITICAL FIX: Use int64 to handle large/negative DWT coefficients
    cA_int = np.round(cA_flat).astype(np.int64)
    
    if debug:
        print(f"  Coefficient types: {cA_int.dtype}")
        print(f"  Coefficient range: {cA_int.min()} to {cA_int.max()}")
    
    # Embed repeated_payload into bit-planes 2, 3, 4
    # CRITICAL: Use mask 0xFFFFFFE3 for 64-bit to preserve sign and magnitude
    bit_idx = 0
    for coeff_idx in range(len(cA_int)):
        if bit_idx >= len(repeated_payload):
            break
        
        coeff = cA_int[coeff_idx]
        
        # Extract magnitude and sign
        is_negative = coeff < 0
        coeff_abs = abs(coeff)
        
        # Clear bits 2, 3, 4 in absolute value
        coeff_abs = int(coeff_abs) & 0xFFFFFFE3
        
        # Embed bit at position 2
        if bit_idx < len(repeated_payload):
            bit_value = int(repeated_payload[bit_idx]) << 2
            coeff_abs = int(coeff_abs) | bit_value
            bit_idx += 1
        
        # Embed bit at position 3
        if bit_idx < len(repeated_payload):
            bit_value = int(repeated_payload[bit_idx]) << 3
            coeff_abs = int(coeff_abs) | bit_value
            bit_idx += 1
        
        # Embed bit at position 4
        if bit_idx < len(repeated_payload):
            bit_value = int(repeated_payload[bit_idx]) << 4
            coeff_abs = int(coeff_abs) | bit_value
            bit_idx += 1
        
        # Restore sign
        coeff_final = -coeff_abs if is_negative else coeff_abs
        cA_int[coeff_idx] = np.int64(coeff_final)
    
    if debug:
        after_sample = [int(x) for x in cA_int[:10]]
        print(f"  LL coefficients (after): first 10 = {after_sample}")
        print(f"  Successfully embedded: {bit_idx} bits")
        
        # Verify magnitudes are preserved
        diffs = [abs(int(b) - int(a)) for b, a in zip(before_sample, after_sample)]
        print(f"  Magnitude changes: {diffs}")
        print(f"  Max change: {max(diffs) if diffs else 0}")
    
    # Convert back to float for IDWT
    cA_float = cA_int.astype(np.float64).reshape((ll_height, ll_width))
    
    # ===== STAGE 6: Inverse DWT (Cb Channel) =====
    
    try:
        cb_reconstructed = pywt.idwt2((cA_float, (cH, cV, cD)), 'haar')
        
        if cb_reconstructed.shape[0] != orig_height or cb_reconstructed.shape[1] != orig_width:
            cb_reconstructed = cb_reconstructed[:orig_height, :orig_width]
        
        # Clip to valid uint8 range [0, 255]
        cb_reconstructed = np.uint8(np.clip(np.round(cb_reconstructed), 0, 255))
        
        if debug:
            print(f"\nIDWT Reconstruction (Cb channel):")
            print(f"  Reconstructed Cb-channel shape: {cb_reconstructed.shape}")
            print(f"  Reconstructed Cb value range: {cb_reconstructed.min()} to {cb_reconstructed.max()}")
            
    except Exception as e:
        raise Exception(f"IDWT reconstruction failed: {str(e)}")
    
    # ===== STAGE 7: Reconstruct YCbCr Image =====
    # Keep Y and Cr unchanged, use modified Cb
    
    y_img = Image.fromarray(y_array.astype(np.uint8), mode='L')
    cb_img = Image.fromarray(cb_reconstructed, mode='L')
    cr_img = cr_channel  # Unchanged
    
    result_ycbcr = Image.merge('YCbCr', (y_img, cb_img, cr_img))
    result_rgb = result_ycbcr.convert('RGB')
    
    if debug:
        print(f"\n✅ Encoding successful!")
        print(f"   Y-channel: UNTOUCHED (original)")
        print(f"   Cb-channel: MODIFIED (message embedded)")
        print(f"   Cr-channel: UNTOUCHED (original)")
        print(f"{'='*60}\n")
    
    return result_rgb


def decode_dct_dwt(img, debug=False):
    """
    Decode secret message from image using Haar DWT in CHROMINANCE (Cb).
    
    Args:
        img (PIL.Image): Encoded image
        debug (bool): Enable debug output
    
    Returns:
        str: Decoded message, or None if decoding fails
    """
    
    if debug:
        print(f"\n{'='*60}")
        print(f"DWT DECODING - CHROMINANCE CHANNEL (Cb)")
        print(f"{'='*60}")
    
    # ===== STAGE 1: Color Space Conversion =====
    
    img_ycbcr = img.convert('YCbCr')
    y_channel, cb_channel, cr_channel = img_ycbcr.split()
    
    # Extract Cb channel (message is here)
    cb_array = np.array(cb_channel, dtype=np.float64)
    
    height, width = cb_array.shape
    
    if debug:
        print(f"Cb-channel shape: {height}×{width}")
        print(f"Cb-channel value range: {cb_array.min():.2f} to {cb_array.max():.2f}")
    
    # ===== STAGE 2: Haar DWT Decomposition (Cb Channel) =====
    
    try:
        cA, (cH, cV, cD) = pywt.dwt2(cb_array, 'haar')
        
        ll_height, ll_width = cA.shape
        
        if debug:
            print(f"\nDWT Decomposition (Cb channel):")
            print(f"  LL band shape: {ll_height}×{ll_width}")
            print(f"  LL band value range: {cA.min():.2f} to {cA.max():.2f}")
        
    except Exception as e:
        if debug:
            print(f"❌ DWT decomposition failed: {str(e)}")
        return None
    
    # ===== STAGE 3: Extract Bits from LL Band (Bit-Planes 2-4) =====
    
    cA_flat = cA.flatten()
    # CRITICAL FIX: Use int64 for proper bit extraction from large coefficients
    cA_int = np.round(cA_flat).astype(np.int64)
    
    if debug:
        sample = [int(x) for x in cA_int[:10]]
        print(f"\nLL coefficients (first 10): {sample}")
    
    # Extract bits from bit-planes 2, 3, 4
    all_bits = []
    for coeff in cA_int:
        coeff = int(coeff)
        
        # Extract from absolute value to handle negative coefficients
        coeff_abs = abs(coeff)
        
        bit2 = (coeff_abs >> 2) & 1
        all_bits.append(str(bit2))
        
        bit3 = (coeff_abs >> 3) & 1
        all_bits.append(str(bit3))
        
        bit4 = (coeff_abs >> 4) & 1
        all_bits.append(str(bit4))
    
    repeated_binary = ''.join(all_bits)
    
    if debug:
        print(f"\nBit Extraction (from Cb channel, positions 2-4):")
        print(f"  Extracted {len(repeated_binary)} bits (repeated 3x)")
        print(f"  First 96 bits (sample): {repeated_binary[:96]}")
    
    # ===== STAGE 4: Error Correction via Majority Voting =====
    
    binary_data = ''
    for i in range(0, len(repeated_binary), 3):
        chunk = repeated_binary[i:i+3]
        
        if len(chunk) == 3:
            ones = chunk.count('1')
            bit = '1' if ones >= 2 else '0'
            binary_data += bit
    
    if debug:
        print(f"\nError Correction (Majority Voting):")
        print(f"  After error correction: {len(binary_data)} bits")
        print(f"  First 32 bits: {binary_data[:32]}")
    
    # ===== STAGE 5: Parse Message Header =====
    
    if len(binary_data) < 16:
        if debug:
            print(f"❌ Not enough bits for header")
        return None
    
    try:
        msg_length = int(binary_data[:16], 2)
        if debug:
            print(f"\nMessage Header:")
            print(f"  Header bits: {binary_data[:16]}")
            print(f"  Parsed length: {msg_length}")
    except ValueError:
        if debug:
            print(f"❌ Failed to parse header")
        return None
    
    if msg_length <= 0 or msg_length > 65535:
        if debug:
            print(f"❌ Invalid message length: {msg_length}")
        return None
    
    # ===== STAGE 6: Extract Message Content =====
    
    message_bits = binary_data[16:]
    required_bits = msg_length * 8
    
    if debug:
        print(f"\nMessage Extraction:")
        print(f"  Required bits: {required_bits}")
        print(f"  Available bits: {len(message_bits)}")
    
    if len(message_bits) < required_bits:
        if debug:
            print(f"❌ Not enough bits")
        return None
    
    # ===== STAGE 7: Convert Binary to Characters =====
    
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
    
    # ===== STAGE 8: Validate Result =====
    
    if debug:
        print(f"\n✅ Decoding successful!")
        print(f"  Decoded message: '{decoded_text}'")
        print(f"  Message length: {len(decoded_text)}")
        print(f"{'='*60}\n")
    
    return decoded_text
