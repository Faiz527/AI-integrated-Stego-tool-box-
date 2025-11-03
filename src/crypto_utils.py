import base64
import hashlib
from cryptography.fernet import Fernet
import streamlit as st

def generate_key(password: str) -> bytes:
    """Generate a Fernet key from a password."""
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest()[:32])
    return key

def encrypt_message(message: str, password: str) -> str:
    """Encrypt a message using the password."""
    try:
        key = generate_key(password)
        f = Fernet(key)
        encrypted_message = f.encrypt(message.encode())
        return encrypted_message.decode()
    except Exception as e:
        st.error(f"Encryption failed: {e}")
        return None

def decrypt_message(encrypted_message: str, password: str) -> str:
    """Decrypt a message using the password."""
    try:
        key = generate_key(password)
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message.encode())
        return decrypted_message.decode()
    except Exception as e:
        st.error(f"Decryption failed: {e}")
        return None