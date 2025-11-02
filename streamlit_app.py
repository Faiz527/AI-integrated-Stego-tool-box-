import os
import sys

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_path)

# Import and run the steganography app directly
import streamlit as st
from src.steganography import main

if __name__ == "__main__":
    main()