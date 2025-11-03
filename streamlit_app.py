import streamlit as st
from PIL import Image
import os
import sys
from pathlib import Path
import io
import pandas as pd
import zipfile

# Configure base path
BASE_PATH = Path(__file__).parent.absolute()
sys.path.append(str(BASE_PATH))

# Import dependencies
from src.db_utils import init_db, verify_user, add_user, log_activity, get_user_stats
from src.image_utils import apply_filter, encode_image, decode_image
from src.crypto_utils import encrypt_message, decrypt_message

# Page configuration
st.set_page_config(page_title="Image Steganography", layout="wide")

# Custom styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
    }
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 4px;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

def main():
    st.markdown("""
        <div class="main-header">
            <h1>🕵️ Image Steganography</h1>
            <p style='color: #666;'>Secure Message Hiding Tool</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    if not init_db():
        st.error("Failed to initialize database. Please try again later.")
        return
    
    # Login/Register section
    if not st.session_state.get("logged_in", False):
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
        
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        # Menu options
        menu = st.sidebar.radio("Menu", ["Encode", "Decode", "Batch Process", "History"])

        if menu == "Encode":
            show_encode_section()
        elif menu == "Decode":
            show_decode_section()
        elif menu == "Batch Process":
            show_batch_process_section()
        elif menu == "History":
            show_history_section()

def show_encode_section():
    st.subheader("Encode Secret Message")
    uploaded_img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    secret_text = st.text_area("Enter secret message:")
    
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox("Apply filter", ["None", "Blur", "Sharpen", "Grayscale"])
    with col2:
        use_encryption = st.checkbox("Encrypt message")
        encryption_password = st.text_input("Encryption password", type="password") if use_encryption else None
    
    if uploaded_img and secret_text:
        with st.spinner('Processing...'):
            try:
                img = Image.open(uploaded_img)
                if use_encryption and encryption_password:
                    secret_text = encrypt_message(secret_text, encryption_password)
                
                encoded_img = encode_image(img, secret_text, filter_type)
                st.image(encoded_img, caption="Encoded Image")
                
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                st.download_button("Download", buf.getvalue(), "encoded.png")
                log_activity(st.session_state.username, "encode")
                st.success("Message encoded successfully!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_decode_section():
    st.subheader("Decode Message")
    uploaded_img = st.file_uploader("Upload encoded image", type=["png", "jpg", "jpeg"])
    use_decryption = st.checkbox("Decrypt message")
    decryption_password = st.text_input("Decryption password", type="password") if use_decryption else None
    
    if uploaded_img:
        with st.spinner('Decoding...'):
            try:
                img = Image.open(uploaded_img)
                message = decode_image(img)
                
                if message:
                    if use_decryption and decryption_password:
                        message = decrypt_message(message, decryption_password)
                    st.success(f"Decoded message: {message}")
                    log_activity(st.session_state.username, "decode")
                else:
                    st.error("No hidden message found")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_batch_process_section():
    st.subheader("Batch Image Processing")
    uploaded_files = st.file_uploader("Upload multiple images", 
                                    type=["png", "jpg", "jpeg"],
                                    accept_multiple_files=True)
    secret_text = st.text_area("Enter secret message:")
    
    if uploaded_files and secret_text:
        with st.spinner('Processing batch...'):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for uploaded_file in uploaded_files:
                    try:
                        img = Image.open(uploaded_file)
                        encoded_img = encode_image(img, secret_text)
                        img_buffer = io.BytesIO()
                        encoded_img.save(img_buffer, format="PNG")
                        zip_file.writestr(f"encoded_{uploaded_file.name}", 
                                        img_buffer.getvalue())
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            st.download_button("Download All Encoded Images",
                             data=zip_buffer.getvalue(),
                             file_name="encoded_images.zip",
                             mime="application/zip")
            log_activity(st.session_state.username, "batch_encode")

def show_history_section():
    st.subheader("Your Activity History")
    stats = get_user_stats(st.session_state.username)
    
    # Display stats in a nice format
    if stats:
        df = pd.DataFrame(stats, columns=["Action", "Count"])
        st.write("Activity Summary:")
        st.dataframe(df)
        
        # Show visualization
        st.subheader("Activity Timeline")
        st.bar_chart(df.set_index("Action"))
    else:
        st.info("No activity recorded yet")

if __name__ == "__main__":
    main()