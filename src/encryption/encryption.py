"""
Encryption Module
=================
Handles message encryption and decryption using AES-256-GCM.

Security Features:
- AES-256 bit symmetric encryption (NIST approved)
- GCM mode provides authenticated encryption
- PBKDF2 key derivation from password
- Random salt and IV per encryption
- Message authentication tag prevents tampering
"""

import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


def encrypt_message(message, password):
    """
    Encrypt message using AES-256-GCM with PBKDF2 key derivation.
    
    Algorithm:
    1. Generate random salt (16 bytes)
    2. Derive 256-bit (32-byte) key from password using PBKDF2
    3. Generate random nonce/IV (12 bytes for GCM)
    4. Encrypt message using AES-256-GCM
    5. Return: base64(salt + nonce + ciphertext + auth_tag)
    
    Args:
        message (str): Plain text message to encrypt
        password (str): Password/passphrase for encryption
    
    Returns:
        str: Base64-encoded encrypted message with salt and nonce
    
    Example:
        >>> encrypted = encrypt_message("secret message", "mypassword")
        >>> decrypted = decrypt_message(encrypted, "mypassword")
        >>> print(decrypted)  # Output: secret message
    """
    try:
        # Step 1: Generate random salt (16 bytes)
        salt = os.urandom(16)
        
        # Step 2: Derive 256-bit (32-byte) key from password using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=480000,  # NIST recommendation (as of 2023)
        )
        key = kdf.derive(password.encode())
        
        # Step 3: Generate random nonce/IV (12 bytes for GCM)
        nonce = os.urandom(12)
        
        # Step 4: Encrypt using AES-256-GCM
        cipher = AESGCM(key)
        ciphertext = cipher.encrypt(nonce, message.encode(), None)
        
        # Step 5: Combine salt + nonce + ciphertext (auth tag included)
        # Format: [16-byte salt][12-byte nonce][variable ciphertext+tag]
        encrypted_data = salt + nonce + ciphertext
        
        # Encode to base64 for safe transmission/storage
        encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
        
        return encrypted_str
        
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_message(encrypted_text, password):
    """
    Decrypt message using AES-256-GCM with PBKDF2 key derivation.
    
    Reverses the encryption process:
    1. Decode base64
    2. Extract salt (first 16 bytes)
    3. Extract nonce (next 12 bytes)
    4. Derive same key using PBKDF2 with stored salt
    5. Decrypt using AES-256-GCM
    6. Return plain text
    
    Args:
        encrypted_text (str): Base64-encoded encrypted message
        password (str): Password/passphrase used for encryption
    
    Returns:
        str: Decrypted plain text message
    
    Raises:
        ValueError: If decryption fails (wrong password or corrupted data)
    
    Example:
        >>> encrypted = encrypt_message("secret", "mypassword")
        >>> decrypted = decrypt_message(encrypted, "mypassword")
        >>> print(decrypted)  # Output: secret
    """
    try:
        # Step 1: Decode base64
        encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
        
        # Step 2: Extract components
        salt = encrypted_data[:16]          # First 16 bytes
        nonce = encrypted_data[16:28]       # Next 12 bytes
        ciphertext = encrypted_data[28:]    # Remaining bytes (includes auth tag)
        
        # Step 3: Derive same key using stored salt
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(password.encode())
        
        # Step 4: Decrypt using AES-256-GCM
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        
        # Step 5: Return decoded string
        return plaintext.decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Decryption failed: Wrong password or corrupted data - {str(e)}")


# ============================================================================
# OPTIONAL: Legacy XOR decryption (for backward compatibility)
# ============================================================================

def decrypt_message_legacy_xor(encrypted_text, password):
    """
    Decrypt messages encrypted with the old XOR method.
    
    ONLY use this to migrate old encrypted data to AES-256.
    Do NOT use XOR for new encryptions.
    
    Args:
        encrypted_text (str): XOR-encrypted message
        password (str): Password used for XOR encryption
    
    Returns:
        str: Decrypted message
    """
    # XOR is symmetric, encryption = decryption
    key = hashlib.sha256(password.encode()).digest()
    
    decrypted_chars = []
    for i, c in enumerate(encrypted_text):
        decrypted_c = chr(ord(c) ^ key[i % len(key)])
        decrypted_chars.append(decrypted_c)
    
    return ''.join(decrypted_chars)
