# 🔐 Image Steganography Toolkit (ITR)

Advanced web-based image steganography application with ML-based detection, batch processing, error correction, and watermarking capabilities.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🌟 Features

### Core Steganography
- **🔐 LSB (Least Significant Bit)** - Fast, high capacity (~180KB)
- **🛡️ Hybrid DCT** - Frequency domain, JPEG-safe (~60KB capacity)
- **🔒 Hybrid DWT** - Wavelet-based, maximum security (~15KB capacity)

### Advanced Features
- ✅ **User Authentication** - Secure login & registration
- ✅ **Message Encryption** - Optional AES-256 encryption
- ✅ **Batch Processing** - Encode/decode multiple images
- ✅ **ML-based Detection** - Steganalysis using Logistic Regression
- ✅ **Error Correction** - Reed-Solomon codes for data protection
- ✅ **Watermarking** - Add visible watermarks to images
- ✅ **Pixel Optimization** - Intelligent pixel selection
- ✅ **Analytics** - Real-time activity tracking & statistics
- ✅ **Dark Theme** - Professional SaaS-style UI

---

## 📋 Requirements

- **Python**: 3.10 or higher
- **PostgreSQL**: 13 or higher
- **RAM**: Minimum 4GB
- **Disk Space**: 2GB for models and data

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Faiz527/AI-integrated-Stego-tool-box-.git
cd ITR
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

```bash
# Create database (Windows)
psql -U postgres -c "CREATE DATABASE steganography;"

# Or manually in pgAdmin
# Create new database named: steganography
```

### 5. Initialize Database Tables

```bash
python src/db/create_db.py
```

### 6. Train ML Detection Model (Optional but Recommended)

```bash
# Quick training (100 samples, ~1-2 minutes)
python src/detect_stego/train_ml_detector.py --samples 100

# Production training (500 samples, ~5-10 minutes)
python src/detect_stego/train_ml_detector.py --samples 500

# High quality (1000 samples, ~20-30 minutes)
python src/detect_stego/train_ml_detector.py --samples 1000
```

### 7. Run the Application

```bash
# Use streamlit_app.py (recommended)
streamlit run streamlit_app.py

# The app will open at http://localhost:8501
```

The app will open at `http://localhost:8501`

---

## 🎯 Quick Start

### Encoding a Message

1. **Login** → Create account or sign in
2. **Navigate** → Click "🔐 Encode"
3. **Upload** → Select your image (PNG recommended)
4. **Enter** → Type your secret message
5. **Configure** → Select method (LSB/DCT/DWT)
6. **Encrypt** → Optionally add AES-256 encryption
7. **Encode** → Click "🔐 Encode Message"
8. **Download** → Save the encoded image

### Decoding a Message

1. **Navigate** → Click "🔍 Decode"
2. **Upload** → Select the encoded image
3. **Configure** → If encrypted, enter the password
4. **Decode** → Click "🔓 Extract Message"
5. **View** → Read the hidden message

### Batch Processing

1. **Navigate** → Click "⚙️ Batch Processing"
2. **Choose** → Basic or Advanced mode
3. **Upload** → Multiple images or ZIP file
4. **Configure** → Set method and message
5. **Process** → Run batch operation
6. **Download** → Get results + report

### Detecting Steganography

1. **Navigate** → Click "🔍 Detect Steganography"
2. **Upload** → Image to analyze
3. **Configure** → Set detection sensitivity
4. **Analyze** → Click "🔎 Analyze Image"
5. **Review** → Check detection score & metrics

---

## 🏗️ Project Structure

```
ITR/
├── streamlit_app.py              # Main entry point
├── requirements.txt              # Dependencies
├── README.md                     # Documentation
│
├── src/
│   ├── db/                      # Database operations
│   │   ├── create_db.py         # Database initialization
│   │   ├── db_utils.py          # DB helper functions
│   │   └── test_db.py           # Database tests
│   │
│   ├── stego/                   # Steganography methods
│   │   ├── lsb_steganography.py    # LSB method
│   │   ├── dct_steganography.py    # Hybrid DCT method
│   │   ├── dwt_steganography.py    # Hybrid DWT method
│   │   └── test_steganography.py   # Method tests
│   │
│   ├── encryption/              # Encryption module
│   │   └── encryption.py        # AES-256 encryption
│   │
│   ├── detect_stego/            # ML-based detection
│   │   ├── ml_detector.py       # Logistic Regression model
│   │   ├── ui_section.py        # Detection UI
│   │   ├── train_ml_detector.py # Model training script
│   │   └── models/              # Trained models (pkl files)
│   │
│   ├── batch_processing/        # Batch operations
│   │   ├── batch_encode.py      # Batch encoding
│   │   ├── batch_decode.py      # Batch decoding
│   │   └── batch_utils.py       # Batch helpers
│   │
│   ├── analytics/               # Statistics & charts
│   │   └── stats.py             # Analytics functions
│   │
│   ├── ui/                      # User interface
│   │   ├── ui_components.py     # Main UI sections
│   │   ├── reusable_components.py  # Reusable widgets
│   │   ├── config_dict.py       # UI configuration
│   │   ├── styles.py            # CSS styling
│   │   └── __init__.py          # Module exports
│   │
│   └── Watermarking/            # Watermarking module
│       └── watermark.py         # Text watermarking
│
└── .env                         # Environment variables (create this)
```

---

## 🔐 Environment Setup

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=steganography
DB_USER=postgres
DB_PASSWORD=your_password

# Encryption
ENCRYPTION_KEY=your_secret_key_here

# ML Model Path
MODEL_PATH=src/detect_stego/models/stego_detector_lr.pkl
```

---

## 📊 Database Schema

The application uses PostgreSQL with the following main tables:

- **users** - User authentication data
- **operations** - Encoding/decoding operations log
- **activity** - User activity tracking

---

## 🤖 ML Detection Model

### Training Overview

The detection model uses **Logistic Regression** to identify steganographic content by analyzing:

- LSB entropy and statistics
- DCT coefficient patterns
- DWT wavelet coefficients
- Chi-square statistics
- Autocorrelation metrics
- ASCII ratio analysis
- High-frequency energy
- Histogram variance

### Model Performance

| Training Samples | Time | Accuracy | Use Case |
|-----------------|------|----------|----------|
| 100 | 1-2 min | 80-85% | Testing |
| 500 | 5-10 min | 85-90% | **Recommended** |
| 1000 | 20-30 min | 88-93% | Production |

### Train Custom Model

```bash
# Standard training
python src/detect_stego/train_ml_detector.py --samples 500

# With custom output path
python src/detect_stego/train_ml_detector.py --samples 1000 -o ./models/custom_detector.pkl

# View help
python src/detect_stego/train_ml_detector.py --help
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Test database operations
python src/db/test_db.py

# Test steganography methods
python src/stego/test_steganography.py
```

---

## 📈 Analytics Dashboard

The Statistics section provides:

- **Activity Timeline** - Encode/decode operations over time
- **Method Distribution** - Pie chart of methods used
- **Message Sizes** - Distribution of message lengths
- **Encryption Usage** - Encrypted vs plain messages
- **Activity History** - Searchable operation log

---

## 🛡️ Security Features

✅ **User Authentication** - Password-protected accounts  
✅ **Message Encryption** - Optional AES-256 encryption  
✅ **Secure Database** - PostgreSQL with prepared statements  
✅ **Session Management** - Secure session state handling  
✅ **Error Correction** - Reed-Solomon codes  
✅ **Imperceptibility** - Multiple embedding methods  

---

## ⚠️ Important Notes

### Best Practices

1. **Use PNG Format** - JPEG compression destroys hidden data
2. **Keep Originals** - Save original images for comparison
3. **Enable Encryption** - Always encrypt sensitive messages
4. **Don't Resize** - Resizing corrupts hidden messages
5. **Secure Passwords** - Use strong encryption passwords

### Limitations

| Limitation | Details |
|-----------|---------|
| JPEG Support | Limited for DWT/DCT methods |
| File Size | Max image: 50MB recommended |
| Message Capacity | Depends on method (15KB-180KB) |
| Database | PostgreSQL only (v13+) |
| Browser | Modern browsers (Chrome, Firefox, Edge) |

---

## 🔧 Troubleshooting

### Issue: "Import Error"

```bash
# Make sure you're in the project root directory
cd c:\Users\faizn\OneDrive\Desktop\Projects\ITR

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Database Connection Error"

```bash
# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Verify .env file has correct credentials
cat .env
```

### Issue: "No ML Model Found"

```bash
# Train the detection model
python src/detect_stego/train_ml_detector.py --samples 500

# Check model exists
ls src/detect_stego/models/
```

### Issue: "Streamlit Not Found"

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall streamlit
pip install streamlit==1.28.1
```

---

## 📚 Technical Documentation

### Steganography Methods

**LSB (Least Significant Bit)**
- Embeds data in the least significant bits of pixel values
- Spatial domain method
- High capacity, low security
- Fast encoding/decoding

**Hybrid DCT (Discrete Cosine Transform)**
- Frequency domain method
- Converts to YCbCr, applies DCT to Y channel
- JPEG-compatible
- Medium capacity, medium security

**Hybrid DWT (Discrete Wavelet Transform)**
- Wavelet transform based
- Applies Haar wavelets to image blocks
- Highest security, lowest capacity
- Resistant to various attacks

### Encryption

- **Algorithm**: AES-256 (Cryptodome)
- **Mode**: CBC with PKCS7 padding
- **Key Derivation**: PBKDF2 with SHA256

### Detection

- **Algorithm**: Logistic Regression
- **Features**: 9 statistical measures
- **Accuracy**: 85-93% (depends on training data)

---

## 📝 Usage Examples

### Python API Usage

```python
from PIL import Image
from src.stego.lsb_steganography import encode_image, decode_image
from src.encryption.encryption import encrypt_message, decrypt_message

# Encode
image = Image.open("cover.png")
encoded = encode_image(image, "Secret message")
encoded.save("encoded.png")

# Decode
encoded = Image.open("encoded.png")
message = decode_image(encoded)
print(message)  # "Secret message"

# With encryption
encrypted_msg = encrypt_message("Secret", "password123")
encoded = encode_image(image, encrypted_msg)

# Decrypt
decrypted_msg = decrypt_message(encrypted_msg, "password123")
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💼 Author

**Faiz Ahmed**
- GitHub: [@Faiz527](https://github.com/Faiz527)
- Email: faiz527@example.com

---

## 🌐 Live Demo

Check out the live application: [ITR Steganography](https://itr-stego.streamlit.app)

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review the troubleshooting section

---

## 🎉 Acknowledgments

- Streamlit for the amazing web framework
- scikit-learn for ML capabilities
- The cryptography community for best practices
- PostgreSQL for reliable database management

---

**Last Updated**: March 2, 2026  
**Version**: 2.0  
**Status**: Active Development ✅
