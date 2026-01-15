"""
Encryption Module
=================
Handles message encryption and decryption using XOR cipher
with SHA-256 key derivation.

Security Note:
- XOR encryption suitable for steganography applications
- For highly sensitive data, consider AES or other modern ciphers
"""

import hashlib


def encrypt_message(message, password):
    """
    Encrypt message using XOR cipher with SHA-256 key derivation.
    
    Algorithm:
    1. Derive a key from password using SHA-256
    2. XOR each character with the corresponding key byte
    3. Return encrypted string
    
    Args:
        message (str): Plain text message to encrypt
        password (str): Password/passphrase for encryption
    
    Returns:
        str: Encrypted message
    
    Example:
        >>> encrypted = encrypt_message("hello", "mypassword")
        >>> decrypted = decrypt_message(encrypted, "mypassword")
    """
    # Derive 32-byte key from password using SHA-256
    key = hashlib.sha256(password.encode()).digest()
    
    # XOR each character with corresponding key byte
    encrypted_chars = []
    for i, c in enumerate(message):
        encrypted_c = chr(ord(c) ^ key[i % len(key)])
        encrypted_chars.append(encrypted_c)
    
    return ''.join(encrypted_chars)


def decrypt_message(encrypted_text, password):
    """
    Decrypt message using XOR cipher with SHA-256 key derivation.
    
    Note: XOR is symmetric, so decryption uses same operation as encryption.
    
    Args:
        encrypted_text (str): Encrypted message to decrypt
        password (str): Password/passphrase used for encryption
    
    Returns:
        str: Decrypted plain text message
    
    Example:
        >>> encrypted = encrypt_message("hello", "mypassword")
        >>> decrypted = decrypt_message(encrypted, "mypassword")
        >>> print(decrypted)  # Output: hello
    """
    return encrypt_message(encrypted_text, password)
