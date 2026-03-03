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
import logging

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
except ImportError as e:
    print(f"Cryptography import error: {e}")
    print("Trying alternative import...")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf import pbkdf2 as pbkdf2_module
    PBKDF2 = pbkdf2_module.PBKDF2

logger = logging.getLogger(__name__)


def encrypt_message(message, password):
    """
    Encrypt message using AES-256-GCM with PBKDF2 key derivation.
    """
    try:
        # Ensure password is string
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        
        # Generate random salt (16 bytes)
        salt = os.urandom(16)
        
        # Derive 256-bit key from password using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=480000
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Generate random nonce (12 bytes)
        nonce = os.urandom(12)
        
        # Encrypt using AES-256-GCM
        cipher = AESGCM(key)
        ciphertext = cipher.encrypt(nonce, message.encode('utf-8'), None)
        
        # Combine salt + nonce + ciphertext
        encrypted_data = salt + nonce + ciphertext
        
        # Encode to base64
        encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
        
        logger.info("Message encrypted successfully")
        return encrypted_str
        
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_message(encrypted_text, password):
    """
    Decrypt message using AES-256-GCM with PBKDF2 key derivation.
    """
    try:
        # Ensure inputs are strings
        if isinstance(encrypted_text, bytes):
            encrypted_text = encrypted_text.decode('utf-8')
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
        
        # Validate minimum length
        if len(encrypted_data) < 44:
            raise ValueError("Invalid encrypted data: too short")
        
        # Extract components
        salt = encrypted_data[:16]          # First 16 bytes
        nonce = encrypted_data[16:28]       # Next 12 bytes
        ciphertext = encrypted_data[28:]    # Remaining bytes
        
        # Derive same key using stored salt
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=480000
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Decrypt using AES-256-GCM
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(nonce, ciphertext, None)
        
        logger.info("Message decrypted successfully")
        return plaintext.decode('utf-8')
        
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise ValueError(f"Decryption failed: Wrong password or corrupted data - {str(e)}")


def decrypt_message_legacy_xor(encrypted_text, password):
    """
    Decrypt messages encrypted with the old XOR method (backward compatibility).
    """
    try:
        # Ensure inputs are strings
        if isinstance(encrypted_text, bytes):
            encrypted_text = encrypted_text.decode('utf-8')
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        
        # XOR is symmetric
        key = hashlib.sha256(password.encode('utf-8')).digest()
        
        decrypted_chars = []
        for i, c in enumerate(encrypted_text):
            decrypted_c = chr(ord(c) ^ key[i % len(key)])
            decrypted_chars.append(decrypted_c)
        
        logger.info("Message decrypted using legacy XOR method")
        return ''.join(decrypted_chars)
    except Exception as e:
        logger.error(f"Legacy XOR decryption failed: {str(e)}")
        raise ValueError(f"Legacy XOR decryption failed: {str(e)}")
