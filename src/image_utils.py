from PIL import Image, ImageFilter
import numpy as np
import hashlib

def apply_filter(img, filter_type):
    filters = {
        "None": lambda x: x,
        "Blur": lambda x: x.filter(ImageFilter.BLUR),
        "Sharpen": lambda x: x.filter(ImageFilter.SHARPEN),
        "Grayscale": lambda x: x.convert('L').convert('RGB')
    }
    return filters[filter_type](img)

def encode_image(img, secret_text, filter_type="None"):
    img = apply_filter(img, filter_type)
    img_array = np.array(img, dtype=np.uint8)
    binary_secret = ''.join(format(ord(i), '08b') for i in secret_text) + '11111110'
    
    if len(binary_secret) > img_array.shape[0] * img_array.shape[1] * 3:
        raise ValueError("Secret message too large for this image")
    
    data_index = 0
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):
                if data_index < len(binary_secret):
                    img_array[i, j, k] = (img_array[i, j, k] & 254) | int(binary_secret[data_index])
                    data_index += 1
    
    return Image.fromarray(img_array)

def decode_image(img):
    img_array = np.array(img, dtype=np.uint8)
    binary_data = ''
    
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            for k in range(3):
                binary_data += str(img_array[i, j, k] & 1)
    
    decoded_text = ''
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if byte == '11111110':
            break
        decoded_text += chr(int(byte, 2))
    
    return decoded_text

def encrypt_message(message, password):
    key = hashlib.sha256(password.encode()).digest()
    encrypted_chars = []
    for i, c in enumerate(message):
        encrypted_c = chr(ord(c) ^ key[i % len(key)])
        encrypted_chars.append(encrypted_c)
    return ''.join(encrypted_chars)

def decrypt_message(encrypted_text, password):
    # XOR encryption is symmetric, so we use the same function
    return encrypt_message(encrypted_text, password)