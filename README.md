# 🕵️ Image Steganography Application

A secure web application built with Streamlit that enables users to hide encrypted messages within images using steganography techniques. The application provides a user-friendly interface for encoding messages into images and decoding them later.

## 🌟 Key Features

- **User Authentication**
  - Secure login/register system
  - Password hashing using SHA-256
  - Session management
  
- **Image Operations**
  - Message encoding in images using LSB (Least Significant Bit) technique
  - Message extraction from encoded images
  - Support for PNG, JPG, and JPEG formats
  - Optional image filters (Blur, Sharpen, Grayscale)
  
- **Security Features**
  - Optional message encryption
  - Password-protected hidden messages
  - Secure database storage
  
- **User Activity Tracking**
  - Activity logging
  - Usage statistics visualization
  - Personal history tracking

## 🔧 Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: PostgreSQL
- **Key Libraries**:
  ```txt
  streamlit >= 1.27.0
  pillow >= 10.0.0
  numpy >= 1.23.5
  psycopg2-binary >= 2.9.7
  python-dotenv >= 1.0.0
  cryptography >= 41.0.0
  pandas >= 2.0.0
  streamlit-option-menu >= 0.3.2
  ```

## 📁 Project Structure

```
ITR/
│   streamlit_app.py    # Application entry point
│   launcher.py         # Alternative launcher
│   requirements.txt    # Project dependencies
│   README.md          # Project documentation
│
├───.streamlit/
│       config.toml    # Streamlit configuration
│       secrets.toml   # Secrets configuration
│
└───src/
    │   steganography.py # Main Streamlit application
    │   db_utils.py     # Database utilities
    │   db.py          # Core database operations
    │   image_utils.py  # Image processing functions
    │   app.py         # Application logic
    │   .env           # Environment configuration
```

## 🚀 Getting Started

### Prerequisites

1. Python 3.8 or higher
2. PostgreSQL database server
3. Git (for cloning the repository)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/image-steganography.git
cd image-steganography
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Unix or MacOS:
source .venv/bin/activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Configure PostgreSQL:
   - Create a new database named 'steganography'
   - Update `.streamlit/secrets.toml` with your database credentials:
   ```toml
   [postgres]
   host = "localhost"
   port = 5432
   dbname = "steganography"
   user = "your_username"
   password = "your_password"
   ```

5. Launch the application:
```bash
python streamlit_app.py
# or alternatively
python launcher.py
```

## 💡 Usage Guide

### Encoding Messages

1. Log in to your account or register a new one
2. Select "Encode" from the menu
3. Upload an image (PNG recommended for best quality)
4. Enter your secret message
5. Optionally:
   - Apply an image filter
   - Enable message encryption
   - Set an encryption password
6. Download the encoded image

### Decoding Messages

1. Select "Decode" from the menu
2. Upload the encoded image
3. If the message was encrypted:
   - Check "Message is encrypted"
   - Enter the correct decryption password
4. View the decoded message

## 🔒 Security Considerations

- Use PNG format for lossless image quality
- Enable encryption for sensitive messages
- Keep encryption passwords secure
- Larger images can store longer messages
- Don't compress encoded images as it may corrupt the hidden message

## 🤝 Contributing

Contributions are welcome! This is a collaborative platform for working on modules independently.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Troubleshooting

If you encounter issues:

1. Verify PostgreSQL is running
2. Check database credentials in `.streamlit/secrets.toml`
3. Ensure all dependencies are installed correctly
4. Verify encryption passwords when decoding
5. Check console logs for detailed error messages

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👥 Contact

For any inquiries or support, please contact: nadaffaiz10@gmail.com
