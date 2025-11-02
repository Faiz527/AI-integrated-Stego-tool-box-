import streamlit as st
from PIL import Image
import io
from app_controller import AppController

def main():
    controller = AppController()
    controller.init_session_state()

    st.title("🕵️ Image Steganography")

    if not st.session_state.logged_in:
        show_auth_page(controller)
    else:
        show_main_page(controller)

def show_auth_page(controller):
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if controller.handle_login(username, password):
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        new_username = st.text_input("Username", key="reg_username")
        new_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            if controller.handle_register(new_username, new_password):
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed")

def show_main_page(controller):
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Add logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    # Main menu
    menu = st.sidebar.radio("Menu", ["Encode", "Decode"])

    if menu == "Encode":
        st.subheader("Encode Secret Message into Image")
        uploaded_img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        secret_text = st.text_area("Enter your secret message:")
        
        # Image filter options
        filter_type = st.selectbox(
            "Apply filter (optional)", 
            ["None", "Grayscale", "Blur", "Sharpen"]
        )
        
        # Encryption options
        use_encryption = st.checkbox("Encrypt message")
        encryption_password = st.text_input("Encryption password", type="password") if use_encryption else None

        if uploaded_img and secret_text:
            try:
                encoded_img = controller.handle_encode(
                    uploaded_img, 
                    secret_text, 
                    filter_type, 
                    use_encryption, 
                    encryption_password
                )
                
                st.image(encoded_img, caption="Encoded Image", use_container_width=True)

                # Download button
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button("Download Encoded Image", 
                                 data=byte_im, 
                                 file_name="encoded.png", 
                                 mime="image/png")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    elif menu == "Decode":
        st.subheader("Decode Secret Message from Image")
        uploaded_img = st.file_uploader("Upload an encoded image", type=["png", "jpg", "jpeg"])
        
        # Decryption options
        is_encrypted = st.checkbox("Message is encrypted")
        decryption_password = st.text_input("Decryption password", type="password") if is_encrypted else None

        if uploaded_img:
            try:
                hidden_text = controller.handle_decode(
                    uploaded_img,
                    is_encrypted,
                    decryption_password
                )
                
                if hidden_text:
                    st.success(f"🔍 Hidden Message: {hidden_text}")
                else:
                    st.warning("No hidden message found in this image.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()