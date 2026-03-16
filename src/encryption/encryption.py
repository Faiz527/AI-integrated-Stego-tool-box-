"""
Encryption Module
=================
Handles message encryption and decryption using AES-256-CBC.

Security Features:
- AES-256 in CBC mode (256-bit key)
- PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)
- Random 16-byte salt per encryption
- Random 16-byte IV per encryption
- HMAC-SHA256 authentication (encrypt-then-MAC)
- PKCS7 padding
- Constant-time MAC comparison

Wire format (base64-encoded):
    salt (16 B) || IV (16 B) || ciphertext (N B) || HMAC tag (32 B)
"""

import os
import hmac
import hashlib
import logging
import base64
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_SALT_LEN = 16          # bytes
_IV_LEN = 16            # AES block size
_KEY_LEN = 32           # 256 bits  →  AES-256
_HMAC_LEN = 32          # SHA-256 digest
_KDF_ITERATIONS = 100_000
_AES_BLOCK_BITS = 128   # for PKCS7 padder


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _derive_keys(password: str, salt: bytes) -> tuple:
    """
    Derive separate AES-256 encryption key and HMAC-SHA256 key from a
    password using PBKDF2-HMAC-SHA256 (via hashlib, not cryptography lib).

    Args:
        password (str): User password
        salt (bytes): 16-byte random salt

    Returns:
        tuple: (enc_key, mac_key) — each 32 bytes
    """
    # 64 bytes of key material: first half → AES key, second half → HMAC key
    key_material = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        _KDF_ITERATIONS,
        dklen=_KEY_LEN * 2,
    )
    return key_material[:_KEY_LEN], key_material[_KEY_LEN:]


def _compute_mac(mac_key: bytes, data: bytes) -> bytes:
    """Return HMAC-SHA256 over *data*."""
    return hmac.new(mac_key, data, hashlib.sha256).digest()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def encrypt_message(plaintext, password):
    """
    Encrypt a message using AES-256-CBC with PBKDF2 key derivation.
    
    Args:
        plaintext (str or bytes or bytearray): Message to encrypt
        password (str): Password for encryption
    
    Returns:
        str: Base64-encoded encrypted message (JSON format)
    
    Raises:
        ValueError: If encryption fails
    
    Example:
        >>> encrypted = encrypt_message("Secret", "password123")
        >>> decrypted = decrypt_message(encrypted, "password123")
        >>> print(decrypted)
        Secret
    """
    try:
        # ✅ FIX: Accept bytes/bytearray from ECC
        if isinstance(plaintext, (bytes, bytearray)):
            plaintext_bytes = bytes(plaintext)
        else:
            plaintext_bytes = plaintext.encode('utf-8')
        
        # Generate random 16-byte salt
        salt = os.urandom(_SALT_LEN)
        
        # Derive keys using PBKDF2-HMAC-SHA256
        enc_key, mac_key = _derive_keys(password, salt)
        
        # Generate random 16-byte IV
        iv = os.urandom(_IV_LEN)
        
        # Create AES-256-CBC cipher
        cipher = Cipher(
            algorithms.AES(enc_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Apply PKCS7 padding
        padder = sym_padding.PKCS7(_AES_BLOCK_BITS).padder()
        padded_plaintext = padder.update(plaintext_bytes) + padder.finalize()
        
        # Encrypt
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        # Compute HMAC over salt + iv + ciphertext (for authentication)
        payload = salt + iv + ciphertext
        tag = _compute_mac(mac_key, payload)
        
        # Combine: salt + iv + ciphertext + hmac tag
        encrypted_data = payload + tag
        
        # Encode to base64 for safe transmission
        encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Wrap in JSON for clarity
        result = json.dumps({
            'algorithm': 'AES-256-CBC',
            'encrypted': encrypted_b64
        })
        
        logger.info("Message encrypted successfully with AES-256-CBC")
        return result
    
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_message(encrypted_text, password):
    """
    Decrypt a payload produced by encrypt_message().

    Args:
        encrypted_text (str or bytes): Base64-encoded JSON encrypted payload
        password (str or bytes): Password for key derivation

    Returns:
        str: Decrypted plaintext

    Raises:
        ValueError: Wrong password, tampered data, or malformed input

    Example:
        >>> encrypted = encrypt_message("Secret", "password123")
        >>> decrypted = decrypt_message(encrypted, "password123")
        >>> print(decrypted)
        Secret
        
        >>> # Wrong password raises ValueError
        >>> decrypt_message(encrypted, "wrong_password")
        ValueError: Authentication failed: wrong password or tampered data
    """
    try:
        # --- Normalise inputs -----------------------------------------------
        if isinstance(encrypted_text, bytes):
            encrypted_text = encrypted_text.decode("utf-8")
        if isinstance(password, bytes):
            password = password.decode("utf-8")

        # --- Parse JSON wrapper to get base64 payload -----------------------
        try:
            json_data = json.loads(encrypted_text)
            encrypted_b64 = json_data.get('encrypted', encrypted_text)
        except (json.JSONDecodeError, AttributeError):
            # Not JSON? Assume it's raw base64
            encrypted_b64 = encrypted_text

        # --- Decode base64 --------------------------------------------------
        raw = base64.b64decode(encrypted_b64.encode("utf-8"))

        # Minimum: salt + iv + one AES block + hmac
        _MIN_LEN = _SALT_LEN + _IV_LEN + 16 + _HMAC_LEN
        if len(raw) < _MIN_LEN:
            raise ValueError("Invalid encrypted data: payload too short")

        # --- Split components -----------------------------------------------
        salt = raw[:_SALT_LEN]
        iv = raw[_SALT_LEN : _SALT_LEN + _IV_LEN]
        tag_received = raw[-_HMAC_LEN:]
        ciphertext = raw[_SALT_LEN + _IV_LEN : -_HMAC_LEN]
        payload = raw[:-_HMAC_LEN]  # salt + iv + ciphertext

        # --- Key derivation -------------------------------------------------
        enc_key, mac_key = _derive_keys(password, salt)

        # --- Verify HMAC (constant-time comparison) -------------------------
        tag_computed = _compute_mac(mac_key, payload)
        if not hmac.compare_digest(tag_computed, tag_received):
            raise ValueError(
                "Authentication failed: wrong password or tampered data"
            )

        # --- AES-256-CBC decrypt --------------------------------------------
        cipher = Cipher(
            algorithms.AES(enc_key),
            modes.CBC(iv),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # --- Remove PKCS7 padding -------------------------------------------
        unpadder = sym_padding.PKCS7(_AES_BLOCK_BITS).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        logger.info("Message decrypted successfully with AES-256-CBC")
        return plaintext.decode("utf-8")

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError(f"Decryption failed: {e}")
