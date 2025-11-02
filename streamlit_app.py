import streamlit as st
from PIL import Image
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db_utils import init_db, verify_user, add_user, log_activity
from src.image_utils import apply_filter, encode_image, decode_image

def main():
    st.title("🕵️ Image Steganography")
    # Your main app code here

if __name__ == "__main__":
    main()