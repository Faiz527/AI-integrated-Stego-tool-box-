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

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

def main():
    st.title("🕵️ Image Steganography")
    
    # Initialize database
    init_db()
    
    # Login/Register section
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                if verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            st.subheader("Register")
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register"):
                if add_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
    
    # Main app content
    else:
        st.write(f"Welcome, {st.session_state.username}!")
        
        # Add logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        menu = st.sidebar.radio("Menu", ["Encode", "Decode"])

        if menu == "Encode":
            st.subheader("Encode Secret Message")
            uploaded_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
            secret_text = st.text_area("Enter secret message:")
            
            if uploaded_img and secret_text:
                img = Image.open(uploaded_img)
                encoded_img = encode_image(img, secret_text)
                st.image(encoded_img, caption="Encoded Image")
                
                # Download button
                import io
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                st.download_button("Download", buf.getvalue(), "encoded.png")
                log_activity(st.session_state.username, "encode")

        elif menu == "Decode":
            st.subheader("Decode Message")
            uploaded_img = st.file_uploader("Upload encoded image", type=["png", "jpg", "jpeg"])
            
            if uploaded_img:
                img = Image.open(uploaded_img)
                message = decode_image(img)
                if message:
                    st.success(f"Decoded message: {message}")
                    log_activity(st.session_state.username, "decode")
                else:
                    st.error("No hidden message found")

if __name__ == "__main__":
    main()