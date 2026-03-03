"""Encryption module using AES-256-CBC with HMAC-SHA256 authentication."""
from .encryption import encrypt_message, decrypt_message

__all__ = [
    'encrypt_message',
    'decrypt_message'
]
