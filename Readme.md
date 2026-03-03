# 🕵️ AI-Integrated Stego Tool Box

A comprehensive web-based image steganography application built with Streamlit that supports multiple steganography methods (LSB, Hybrid DCT, Hybrid DWT) with **AES-256-CBC encryption**, batch processing, and detailed analytics.

---

## 🎯 Features

### Steganography Methods
- **LSB (Least Significant Bit)**: Spatial domain steganography with fast processing
- **Hybrid DCT (Discrete Cosine Transform)**: Frequency domain method using Y-channel
- **Hybrid DWT (Discrete Wavelet Transform)**: Wavelet-based encoding using Haar wavelets

### Core Functionality
- ✅ **Message Encoding**: Hide secret messages in images using three different methods
- ✅ **Message Decoding**: Extract hidden messages from encoded images
- ✅ **AES-256-CBC Encryption**: Military-grade encryption for message protection
- ✅ **Method Comparison**: Side-by-side comparison of all three steganography methods
- ✅ **Batch Processing**: Encode/decode multiple images efficiently via ZIP or multi-upload
- ✅ **Real-time Analytics**: Track operations and view detailed statistics

### Security Features
- 🔐 **AES-256-CBC Encryption**: 256-bit symmetric encryption in CBC mode
- 🔑 **PBKDF2-HMAC-SHA256**: Secure password-based key derivation (100,000 iterations)
- 🛡️ **Authenticated Encryption**: HMAC-SHA256 for tamper detection (encrypt-then-MAC)
- 🎲 **Random IV/Salt**: 16-byte random salt and IV per encryption
- ⏱️ **Constant-Time Comparison**: Resistance to timing attacks

### Analytics Dashboard
- 📊 **Operation Timeline**: Track operations over the last 7 days
- 📈 **Method Distribution**: Pie chart showing usage of LSB, DCT, and DWT
- 📉 **Encode vs Decode**: Bar chart comparing encode/decode operations
- 🔐 **Encryption Usage**: Statistics on encrypted vs unencrypted messages
- 💾 **Data Size Distribution**: Visualization of operation data sizes
- 📋 **Activity Log**: Real-time log of recent user operations

### User Management
- User authentication with SHA-256 password hashing
- Per-user operation tracking
- Activity logging and statistics
- Session management

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** (Python 3.10+ recommended)
- **PostgreSQL 9.1+** (for database operations)
- **pip** (Python package manager)

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/Faiz527/AI-integrated-Stego-tool-box-.git
cd AI-integrated-Stego-tool-box-
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

Create `.env` file in project root:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stegnography
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

5. **Create PostgreSQL Database**
```bash
python create_db.py
```

6. **Initialize Database Tables**
```bash
python -c "from src.db.db_utils import initialize_database; initialize_database()"
```

7. **Test Database Connection**
```bash
python test_db.py
```

---

## 🚀 Running the Application

Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open at: `http://localhost:8501`

---

## 🔐 Encryption Details

### AES-256-CBC Encryption (Updated)

The application now uses **AES-256-CBC** encryption with authenticated message authentication and secure key derivation.

#### Key Specifications
| Property | Value |
|----------|-------|
| **Algorithm** | AES-256 in CBC mode |
| **Key Size** | 256 bits (32 bytes) |
| **Block Size** | 128 bits (16 bytes) |
| **IV Size** | 128 bits (16 bytes random) |
| **Salt Size** | 128 bits (16 bytes random) |
| **Key Derivation** | PBKDF2-HMAC-SHA256 (100,000 iterations) |
| **Authentication** | HMAC-SHA256 (encrypt-then-MAC) |
| **Padding** | PKCS7 |

#### Encryption Format (Base64-encoded)
```
salt (16 B) || IV (16 B) || ciphertext (variable) || HMAC tag (32 B)
```

#### Security Properties
- ✅ **Symmetric Encryption**: Same password encrypts/decrypts
- ✅ **Authenticated**: HMAC prevents tampering and ensures integrity
- ✅ **Non-deterministic**: Random salt + IV = different ciphertext each time
- ✅ **Secure KDF**: 100,000 PBKDF2 iterations resist brute-force attacks
- ✅ **Timing-Safe**: Constant-time MAC comparison prevents timing attacks
- ✅ **Modern Standard**: NIST-approved algorithms

#### Usage Example
```python
from src.encryption.encryption import encrypt_message, decrypt_message

# Encrypt
password = "my_secure_password"
secret_text = "This is a secret message"
encrypted = encrypt_message(secret_text, password)
print(f"Encrypted: {encrypted}")

# Decrypt
decrypted = decrypt_message(encrypted, password)
print(f"Decrypted: {decrypted}")
assert decrypted == secret_text  # ✓ Success
```

#### Error Handling
```python
from src.encryption.encryption import encrypt_message, decrypt_message

try:
    # Wrong password raises ValueError
    decrypt_message(encrypted_text, "wrong_password")
except ValueError as e:
    print(f"Decryption failed: {e}")
    # "Authentication failed: wrong password or tampered data"
```

---

## 📁 Project Structure

```
AI-integrated-Stego-tool-box-/
├── .env                          # Environment variables (PostgreSQL credentials)
├── .gitignore                    # Git ignore rules
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml             # Streamlit secrets
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── pytest.ini                   # Pytest configuration
├── streamlit_app.py             # Main Streamlit application entry point
├── create_db.py                 # Database creation script
├── test_db.py                   # Database connection test
├── test_steganography.py        # Steganography methods test
├── data/
│   ├── input/                   # Input images and zips
│   ├── output/                  # Encoded output, reports
│   └── temp/                    # Temporary processing files
├── src/
│   ├── __init__.py              # Main package initialization
│   │
│   ├── stego/                   # Core Steganography Engine
│   │   ├── __init__.py
│   │   ├── lsb_steganography.py         # LSB (Spatial Domain) method
│   │   ├── dct_steganography.py         # Hybrid DCT (Y-Channel) method
│   │   └── dwt_steganography.py         # Hybrid DWT (Haar Wavelet) method
│   │
│   ├── db/                      # Database Layer
│   │   ├── __init__.py
│   │   ├── db_utils.py          # User management, operation logging, statistics
│   │   └── db_utils_minimal.py  # Minimal DB utilities
│   │
│   ├── analytics/               # Analytics & Statistics
│   │   ├── __init__.py
│   │   └── stats.py             # Chart generation, statistics calculations
│   │
│   ├── encryption/              # Encryption Module (AES-256-CBC)
│   │   ├── __init__.py
│   │   └── encryption.py        # AES-256-CBC with PBKDF2-HMAC-SHA256 key derivation
│   │
│   ├── ui/                      # User Interface
│   │   ├── __init__.py
│   │   ├── config_dict.py       # Centralized UI configuration & constants
│   │   ├── reusable_components.py # Reusable Streamlit components
│   │   ├── styles.py            # Dark theme styling & CSS
│   │   └── ui_components.py     # Main UI sections (encode, decode, etc.)
│   │
│   └── batch_processing/        # Batch Processing Module
│       ├── __init__.py
│       ├── batch_encoder.py     # Batch encoding functions
│       ├── controller.py        # Batch processing orchestration
│       ├── report_generator.py  # JSON/CSV report generation
│       └── zip_handler.py       # ZIP extraction and validation
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_encryption.py       # AES-256-CBC encryption tests
│   ├── test_steganography.py    # Steganography method tests
│   └── test_batch_processing.py # Batch processing tests
│
├── logs/                        # Application logs
└── htmlcov/                     # Coverage reports
```

### Module Organization

**`src/stego/`** - Steganography Engine
- Independent implementations of LSB, DCT, and DWT methods
- Each method has encode/decode functions
- No external dependencies between methods

**`src/db/`** - Database Layer
- PostgreSQL connection management
- User authentication with SHA-256 password hashing
- Operation logging (encode/decode history)
- Statistics retrieval for analytics

**`src/analytics/`** - Analytics & Visualization
- Chart generation (Plotly)
- Statistics calculations
- Activity logs and dataframes
- Real-time metrics

**`src/encryption/`** - Message Security (AES-256-CBC)
- **AES-256 symmetric encryption** in CBC mode
- **PBKDF2-HMAC-SHA256 key derivation** (100,000 iterations)
- **HMAC-SHA256 authentication** for tamper detection
- **Random salt & IV** per encryption
- Optional message protection

**`src/ui/`** - Web Interface
- Streamlit UI components
- Dark theme styling
- Authentication section
- Encode/Decode sections
- Comparison and Statistics sections
- Centralized configuration via `config_dict.py`
- Reusable components via `reusable_components.py`

**`src/batch_processing/`** - Batch Processing Module
- ZIP extraction and image validation
- Multi-method batch encoding
- JSON and CSV report generation
- Download ZIP creation
- File validation and error handling
- Integration with core steganography engine

---

## 🔐 Usage Guide

### 1. **Create Account**
- Click "Create New Account" on the login screen
- Enter username and password (minimum 6 characters)
- Account is created in PostgreSQL database

### 2. **Encode Message**
- Go to **Encode** tab
- Select steganography method (LSB, DCT, or DWT)
- Upload cover image (PNG/JPG)
- Enter secret message
- (Optional) Enable AES-256 encryption with password
- Click "Encode Message"
- Download the encoded image

### 3. **Decode Message**
- Go to **Decode** tab
- Upload encoded image
- Auto-detection tries all methods (LSB → DCT → DWT)
- (If encrypted) Enter decryption password
- Click "Decode Message"
- View extracted message

### 4. **Compare Methods**
- Go to **Compare Methods** tab
- Upload cover image
- Enter test message
- View side-by-side comparison of all three methods
- See PSNR (Peak Signal-to-Noise Ratio) for each method

### 5. **View Analytics**
- Go to **Statistics** tab
- View operation timeline (last 7 days)
- See method distribution pie chart
- Check encode vs decode statistics
- Monitor encryption usage
- View data size distribution
- See recent activity log

### 6. **Batch Processing**
- Go to **Batch Processing** tab
- Choose upload method: ZIP file or multiple images
- Select steganography method and enter secret message
- (Optional) Enable AES-256 encryption
- Click "Start Batch Encoding" or "Start Batch Decoding"
- Download processed images and reports

---

## 🔧 Technical Details

### Steganography Methods

#### LSB (Least Significant Bit)
- **Domain**: Spatial
- **Capacity**: ~180 KB / ~2.5% of image size
- **Detection Resistance**: Low
- **Computational Cost**: Very Low
- **Quality**: Excellent (PSNR > 50 dB)
- **JPEG Safe**: No

#### Hybrid DCT
- **Domain**: Frequency (Y-channel only)
- **Capacity**: ~60 KB / ~1.5% of image size
- **Detection Resistance**: Medium
- **Computational Cost**: Medium
- **Quality**: Good (PSNR > 40 dB)
- **JPEG Safe**: Yes

#### Hybrid DWT (Haar Wavelet)
- **Domain**: Frequency (Wavelet)
- **Capacity**: ~15 KB / ~2% of image size
- **Detection Resistance**: High
- **Computational Cost**: Medium-High
- **Quality**: Very Good (PSNR > 45 dB)
- **JPEG Safe**: No

### Encryption Security (AES-256-CBC)

**Algorithm**: AES-256 in CBC mode with HMAC-SHA256 authentication

**Key Derivation**:
- **Function**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000 (NIST recommendation)
- **Key Size**: 256 bits (32 bytes)
- **Salt**: 16 bytes (random per encryption)
- **Output**: 64 bytes (32 for AES key + 32 for HMAC key)

**Encryption**:
- **Mode**: CBC (Cipher Block Chaining)
- **IV**: 16 bytes (random per encryption)
- **Padding**: PKCS7
- **Authentication**: HMAC-SHA256 (encrypt-then-MAC pattern)
- **Format**: base64(salt || IV || ciphertext || HMAC tag)

**Security Properties**:
- ✅ **Non-Deterministic**: Different ciphertext for same plaintext (random IV + salt)
- ✅ **Authenticated**: HMAC prevents unauthorized modifications
- ✅ **Brute-Force Resistant**: 100,000 PBKDF2 iterations slow down attacks
- ✅ **Timing-Secure**: Constant-time MAC comparison (no information leakage)
- ✅ **Future-Proof**: 256-bit key resists quantum computing threats (in theory)

### Database Schema

**users**
```sql
id SERIAL PRIMARY KEY
username VARCHAR(255) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**operations**
```sql
id SERIAL PRIMARY KEY
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
method VARCHAR(50)
input_image VARCHAR(255)
output_image VARCHAR(255)
message_size INTEGER
encoding_time FLOAT
status VARCHAR(50)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**activity_log**
```sql
id SERIAL PRIMARY KEY
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
action VARCHAR(255)
details TEXT
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

---

## 📊 Analytics & Statistics

The application tracks:
- **Total Operations**: Count of all encode/decode operations
- **Method Usage**: Distribution of LSB, DCT, DWT usage
- **Encryption Rate**: Percentage of operations using AES-256 encryption
- **Operation Timeline**: Operations per day over 7 days
- **Data Size Distribution**: Breakdown of message sizes
- **User Activity**: Recent operations by all users

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Encryption Tests Only
```bash
pytest tests/test_encryption.py -v
```

### Run Steganography Tests
```bash
pytest tests/test_steganography.py -v
```

### Run Specific Test
```bash
pytest tests/test_encryption.py::TestAES256Encryption::test_encrypt_decrypt_basic -v
```

### Test with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Database Connection
```bash
python test_db.py
```

### Test Steganography Methods
```bash
python test_steganography.py
```

---

## ⚙️ Configuration

### Streamlit Configuration (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#238636"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#161B22"
textColor = "#C9D1D9"
font = "sans serif"

[client]
showErrorDetails = true
showWarningOnDirectExecution = true

[logger]
level = "info"

[server]
port = 8501
headless = true
```

### Environment Variables (`.env`)
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stegnography
DB_USER=postgres
DB_PASSWORD=your_password
```

### Pytest Configuration (`pytest.ini`)
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

---

## 🐛 Troubleshooting

### Database Connection Failed
- Ensure PostgreSQL is running: `Get-Service postgresql-x64-*`
- Verify database exists: `psql -U postgres -h localhost -l`
- Check `.env` credentials are correct

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Verify all files are in correct locations

### Image Upload Issues
- Ensure image is PNG or JPG format
- Image size should be at least 100x100 pixels
- File size should be less than 100 MB

### Encoding/Decoding Errors
- Verify correct method is selected for decoding
- Ensure image format matches (no format conversion)
- Check that image hasn't been compressed or modified

### Encryption/Decryption Fails
- Verify correct password is used for decryption
- Check that encrypted data hasn't been corrupted or tampered with
- Ensure message was encrypted with the same AES-256-CBC implementation

### Tests Not Running
- Ensure pytest is installed: `pip install pytest`
- Run from project root directory
- Check `pytest.ini` configuration
- Verify `src/` directory is in Python path

---

## 📈 Performance Metrics

Typical performance on modern hardware:

| Operation | Time | Memory |
|-----------|------|--------|
| LSB Encode (1MB) | 0.5s | 50MB |
| DCT Encode (1MB) | 1.2s | 80MB |
| DWT Encode (1MB) | 1.5s | 100MB |
| AES-256 Encrypt | 10ms | <5MB |
| Decode Any Method | 0.3s | 40MB |
| AES-256 Decrypt | 10ms | <5MB |

---

## 🔒 Security Considerations

### Encryption Security
- ✅ **AES-256-CBC**: Industry-standard symmetric encryption (NIST-approved)
- ✅ **PBKDF2-HMAC-SHA256**: Secure password-based key derivation
- ✅ **HMAC Authentication**: Prevents tampering and ensures integrity
- ✅ **Random Salt/IV**: 16-byte random nonces for each encryption
- ✅ **Constant-Time Comparison**: Prevents timing attacks on MAC verification
- ✅ **PKCS7 Padding**: Standard padding removes information leakage

### Application Security
- ✅ Passwords hashed with SHA-256
- ✅ HTTPS recommended for production deployment
- ✅ Database access controlled via credentials
- ✅ No sensitive data in logs
- ✅ Session-based authentication
- ✅ User isolation in database

### Steganography Security
- ✅ Three independent methods (LSB, DCT, DWT)
- ✅ Optional message encryption before embedding
- ✅ Method auto-detection on decode
- ✅ Image integrity checks

### Recommendations for Production
1. Use HTTPS/TLS for all network communication
2. Store database credentials in secure secret manager
3. Enable PostgreSQL SSL connections
4. Implement rate limiting on authentication
5. Add audit logging for sensitive operations
6. Regular security updates for dependencies
7. Use strong passwords (20+ characters recommended)
8. Keep encryption passwords separate from files

---

## 👨‍💻 Developer Information

**Application**: AI-Integrated Stego Tool Box
**Version**: 1.0.0
**Author**: [Faiz527](https://github.com/Faiz527)
**Built with**:
- Streamlit (Frontend)
- PostgreSQL (Database)
- Python 3.10+

**Key Libraries**:
- `Pillow` (10.0.0+) - Image processing
- `NumPy/SciPy` (1.24.0+ / 1.11.0+) - Scientific computing
- `PyWavelets` (1.4.0+) - Wavelet transforms
- `Plotly` (5.18.0+) - Interactive visualizations
- `psycopg2` (2.9.0+) - PostgreSQL adapter
- `cryptography` (41.0.0+) - Cryptographic primitives (AES-256-CBC, PBKDF2)
- `python-dotenv` (1.0.0+) - Environment variable management

---

## 🚀 Future Enhancements

- [ ] AI-based steganalysis detection
- [ ] Quality Metrics Module - PSNR, MSE, SSIM calculations
- [ ] Auto-detection Module - Automatically select best method per image
- [ ] Additional image formats (BMP, TIFF, WebP)
- [ ] Video steganography support
- [ ] Report generation (PDF)
- [ ] Cloud storage integration (AWS S3, Google Drive)
- [ ] Docker containerization
- [ ] Distributed computing for large-scale batch processing
- [ ] Two-factor authentication (2FA)
- [ ] API endpoint for programmatic access

---

## 📚 Module Development Guide

### Adding New Steganography Method

1. Create new file in `src/stego/` (e.g., `new_method_steganography.py`)
2. Implement `encode_method(img, secret_text)` and `decode_method(img)`
3. Export functions in `src/stego/__init__.py`
4. Add method to `METHODS` list in `src/ui/config_dict.py`
5. Add UI handling in `src/ui/ui_components.py`
6. Update imports in `streamlit_app.py`
7. Add tests in `tests/test_steganography.py`

### Adding New Chart/Statistic

1. Create function in `src/analytics/stats.py`
2. Export in `src/analytics/__init__.py`
3. Import in `src/ui/ui_components.py`
4. Add UI element in `show_statistics_section()`

### Database Operations

1. Add function in `src/db/db_utils.py`
2. Export in `src/db/__init__.py`
3. Call from appropriate UI component

### Working with Encryption

```python
from src.encryption.encryption import encrypt_message, decrypt_message

# Encrypt before embedding
encrypted_msg = encrypt_message("secret", "password")
# Now embed encrypted_msg in image

# Decrypt after extraction
decrypted_msg = decrypt_message(encrypted_blob, "password")
```

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify all dependencies are installed
4. Test database connection with `test_db.py`
5. Run test suite with `pytest tests/ -v`
6. Check logs in `logs/` directory
7. Open an issue on [GitHub](https://github.com/Faiz527/AI-integrated-Stego-tool-box-/issues)

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 📋 Changelog

### v1.0.0 (Current)
- ✨ **NEW**: Upgraded encryption from Fernet (AES-128) to **AES-256-CBC**
- ✨ **NEW**: PBKDF2-HMAC-SHA256 key derivation (100,000 iterations)
- ✨ **NEW**: HMAC-SHA256 authentication (encrypt-then-MAC pattern)
- ✨ **NEW**: Comprehensive encryption test suite
- 🔧 Updated `requirements.txt` with cryptography library
- 📚 Enhanced README with encryption security details
- 🧪 Added `pytest.ini` for test configuration
- 🎨 Professional SaaS-style UI/UX improvements

---

**Last Updated**: 3-FEB-2026
**Project Structure**: Modular Architecture v1.0
**Security**: Military-grade AES-256-CBC encryption + HMAC authentication
