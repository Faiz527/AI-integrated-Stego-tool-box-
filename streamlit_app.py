import streamlit as st
from PIL import Image
import os
import sys
from pathlib import Path

# Configure base path
BASE_PATH = Path(__file__).parent.absolute()
sys.path.append(str(BASE_PATH))

# Import dependencies
from src.db_utils import init_db, verify_user, add_user, log_activity
from src.image_utils import apply_filter, encode_image, decode_image

def main():
    st.title("🕵️ Image Steganography")
    st.write("Welcome to the Image Steganography Tool")
    
    # Basic functionality to test deployment
    st.write("This is a test deployment")
    st.success("If you can see this, the app is working!")

if __name__ == "__main__":
    main()