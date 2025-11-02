import streamlit as st
from PIL import Image
import io
import pandas as pd
import zipfile
from streamlit_option_menu import option_menu
from db_utils import init_db, verify_user, add_user, log_activity, get_user_stats
from image_utils import apply_filter, encode_image, decode_image, encrypt_message, decrypt_message

# Initialize session state - Add this at the top, after imports
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# Custom styling without background
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
    }
    .stTextInput>div>div>input {
        border-radius: 4px;
    }
    .stSelectbox>div>div>select {
        border-radius: 4px;
    }
    div.stButton > button:hover {
        background-color: #45a049;
        color: white;
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
    .info-box b {
        color: #856404;
    }
    .info-box ul {
        color: #856404;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Replace the title section with this cleaner version
st.markdown("""
    <div class="main-header">
        <h1>🕵️ Image Steganography</h1>
        <p style='color: #666;'>Secure Message Hiding Tool</p>
    </div>
""", unsafe_allow_html=True)

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

# Main app content (only shown to logged-in users)
if st.session_state.logged_in:
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    menu = st.sidebar.radio("Menu", ["Encode", "Decode", "History"])

    if menu == "Encode":
        st.subheader("Encode Secret Message into Image")
        uploaded_img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        secret_text = st.text_area("Enter your secret message:")
        
        # Add filter selection
        filter_type = st.selectbox(
            "Apply filter (optional)", 
            ["None", "Blur", "Sharpen", "Grayscale"]
        )

        # Add encryption option
        use_encryption = st.checkbox("Encrypt message")
        encryption_password = st.text_input("Encryption password", type="password") if use_encryption else None

        if uploaded_img and secret_text:
            with st.spinner('Encoding your message...'):
                try:
                    # Encrypt message if option selected
                    if use_encryption and encryption_password:
                        secret_text = encrypt_message(secret_text, encryption_password)
                    
                    img = Image.open(uploaded_img).convert("RGB")
                    encoded_img = encode_image(img, secret_text, filter_type)
                    st.image(encoded_img, caption="Encoded Image", use_container_width=True)
                    
                    # Download button
                    buf = io.BytesIO()
                    encoded_img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button("Download Encoded Image", data=byte_im, file_name="encoded.png", mime="image/png")
                    
                    log_activity(st.session_state.username, "encode")
                    st.success('✅ Message encoded successfully!')
                    
                except ValueError as e:
                    st.error(f"Error: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

        # Add this info section
        st.markdown("""
            <div class="info-box">
            💡 <b>Tips:</b>
            <ul>
                <li>Use PNG images for best quality</li>
                <li>Larger images can store longer messages</li>
                <li>Enable encryption for sensitive data</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

    elif menu == "Decode":
        st.subheader("Decode Secret Message from Image")
        uploaded_img = st.file_uploader("Upload an encoded image", type=["png", "jpg", "jpeg"])
        
        # Add decryption option
        is_encrypted = st.checkbox("Message is encrypted")
        decryption_password = st.text_input("Decryption password", type="password") if is_encrypted else None

        if uploaded_img:
            with st.spinner('Decoding message...'):
                try:
                    img = Image.open(uploaded_img).convert("RGB")
                    hidden_text = decode_image(img)
                    
                    if hidden_text:
                        if is_encrypted and decryption_password:
                            try:
                                decrypted_text = decrypt_message(hidden_text, decryption_password)
                                st.success(f"🔍 Decrypted Message: {decrypted_text}")
                            except Exception as e:
                                st.error("Failed to decrypt: Invalid password or corrupted message")
                        else:
                            st.success(f"🔍 Hidden Message: {hidden_text}")
                    else:
                        st.warning("No hidden message found in this image.")
                    
                    log_activity(st.session_state.username, "decode")
                except Exception as e:
                    st.error(f"Error decoding image: {str(e)}")
        
        # Add this info section
        st.markdown("""
            <div class="info-box">
            💡 <b>Note:</b>
            <ul>
                <li>Select the encrypted option if the message was encrypted</li>
                <li>Use the same password that was used for encryption</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)
        st.info("⚠️ For best results, use images encoded with this tool. Messages encoded with other tools may not decode correctly.")

    elif menu == "History":
        st.subheader("Your Activity")
        stats = get_user_stats(st.session_state.username)
        for action, count in stats:
            st.write(f"{action.title()}: {count} times")
        
        # Show activity timeline
        st.line_chart(pd.DataFrame(stats, columns=["Action", "Count"]))

    elif menu == "Batch Process":
        st.subheader("Batch Image Processing")
        uploaded_files = st.file_uploader("Upload multiple images", 
                                        type=["png", "jpg", "jpeg"],
                                        accept_multiple_files=True)
        secret_text = st.text_area("Enter your secret message:")
        
        if uploaded_files and secret_text:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for uploaded_file in uploaded_files:
                    try:
                        img = Image.open(uploaded_file).convert("RGB")
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

else:
    st.warning("Please login to use the application")

def encode_text(image, text):
    """
    Encode text in image
    """
    # Convert text to binary
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    # Add header
    binary_text = ''.join(format(ord(char), '08b') for char in "ITR_STEG_V1:") + binary_text
    
    # Get image data
    width, height = image.size
    pixels = image.load()
    
    # Check if image can hold the text
    if len(binary_text) > width * height * 3:
        raise ValueError("Text too long for this image")
    
    idx = 0
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for n in range(3):
                if idx < len(binary_text):
                    # Replace least significant bit
                    pixel[n] = pixel[n] & ~1 | int(binary_text[idx])
                    idx += 1
            pixels[x, y] = tuple(pixel)
    
    return image

def decode_text(image):
    """
    Decode text from image
    """
    binary_text = ""
    pixels = image.load()
    width, height = image.size
    
    # Extract binary string from image
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for color in pixel[:3]:
                binary_text += str(color & 1)
    
    # Convert binary to text
    text = ""
    # Add null terminator detection
    for i in range(0, len(binary_text), 8):
        byte = binary_text[i:i+8]
        if len(byte) == 8:
            char = chr(int(byte, 2))
            # Stop if we hit null bytes or non-printable characters
            if char == '\0' or (ord(char) > 127):
                break
            text += char
    
    # Clean the output text
    text = ''.join(char for char in text if ord(char) < 127 and ord(char) >= 32)
    
    return text.strip()


