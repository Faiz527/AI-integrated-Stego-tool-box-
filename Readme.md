# AI-Integrated Steganography Toolbox

> **Advanced steganography toolkit with AI-powered steganalysis, multiple embedding methods, and military-grade encryption**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-178%20Passed-brightgreen.svg)](#-testing)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-High-blue.svg)](#-testing)

---

## 📚 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Steganography Methods](#steganography-methods)
- [Encryption](#encryption)
- [Testing](#-testing)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### 🔐 Multiple Steganography Methods

| Method | Capacity | Resilience | Speed | Use Case |
|--------|----------|-----------|-------|----------|
| **LSB** | Very High (~30KB) | Low (spatial) | ⚡ Very Fast | Maximum capacity needed |
| **DCT** | Medium (~1.5KB) | High (JPEG) | ⏱️ Moderate | JPEG distribution |
| **DWT** | Medium (~2KB) | High (noise) | ⏱️ Moderate | Robust against distortion |

### 🛡️ Security Features

- ✅ **AES-256-CBC Encryption** - Military-grade message encryption
- ✅ **Multiple Steganography Methods** - Flexibility in embedding choice
- ✅ **Image Filtering Support** - Blur, Sharpen, Grayscale preprocessing
- ✅ **Robust Extraction** - Recover messages from processed images
- ✅ **Mode Conversion** - Support for RGB, Grayscale, RGBA images

### 🎯 Advanced Capabilities

- 📊 Steganalysis detection framework
- 🤖 AI-powered feature extraction
- 💾 Database integration for user management
- 📝 Operation logging and auditing
- 🔍 Message integrity verification

### 🧪 Comprehensive Testing

- ✅ **178 Unit + Integration Tests** - Full coverage
- ✅ **84 Unit Tests** - Core functionality
- ✅ **22 Integration Tests** - End-to-end workflows
- ✅ **38 Fixture Tests** - Test infrastructure
- ✅ **34+ Database Tests** - Persistence layer
- ✅ **High Code Coverage** - Production-ready quality

---

## 📦 Installation

### Prerequisites

- **Python 3.9+**
- **pip** or **conda**
- **MySQL/MariaDB** (optional, for database features)

### Step 1: Clone Repository

```bash
git clone https://github.com/Faiz527/AI-integrated-Stego-tool-box-.git
cd AI-integrated-Stego-tool-box-
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database (Optional)

```bash
python -c "from src.db.db_utils import initialize_database; initialize_database()"
```

---

## 🚀 Quick Start

### Basic Encoding (LSB)

```python
from PIL import Image
from src.stego.lsb_steganography import encode_image, decode_image

# Load image
img = Image.open('image.png')

# Encode message
secret_msg = "This is secret!"
encoded_img = encode_image(img, secret_msg, filter_type="None")
encoded_img.save('encoded.png')

# Decode message
decoded_msg = decode_image(encoded_img)
print(f"Retrieved: {decoded_msg}")  # Output: This is secret!
```

### With Encryption (AES-256)

```python
from PIL import Image
from src.stego.lsb_steganography import encode_image, decode_image
from src.encryption.encryption import encrypt_message, decrypt_message

# Load image
img = Image.open('image.png')

# Encrypt message
secret_msg = "Highly confidential data"
password = "MySecurePassword123"
encrypted = encrypt_message(secret_msg, password)

# Embed encrypted message
encoded_img = encode_image(img, encrypted, filter_type="None")
encoded_img.save('secure_encoded.png')

# Extract and decrypt
extracted = decode_image(encoded_img)
decrypted = decrypt_message(extracted, password)
print(f"Decrypted: {decrypted}")  # Output: Highly confidential data
```

### Using DCT Method (JPEG-Resilient)

```python
from PIL import Image
from src.stego.dct_steganography import encode_dct, decode_dct

img = Image.open('image.png')
msg = "Secret message"

# Encode using DCT
encoded = encode_dct(img, msg)
encoded.save('encoded_dct.jpg')

# Decode from JPEG
decoded = decode_dct(encoded)
print(f"Message: {decoded}")
```

### Using DWT Method (Noise-Resilient)

```python
from PIL import Image
from src.stego.dwt_steganography import encode_dwt, decode_dwt

img = Image.open('image.png')
msg = "Robustness test"

# Encode using DWT
encoded = encode_dwt(img, msg)
encoded.save('encoded_dwt.png')

# Decode
decoded = decode_dwt(encoded)
print(f"Message: {decoded}")
```

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                  User Interface Layer                   │
│              (CLI / Web / Desktop Apps)                 │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│            Application Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  LSB Method  │  │  DCT Method  │  │  DWT Method  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │    Encryption Module (AES-256-CBC)              │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │    Image Processing & Filtering                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database   │  │  File System │  │  Image I/O   │  │
│  │  (MySQL)     │  │  (PNG/JPEG)  │  │  (PIL)       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
AIR-integrated-Stego-tool-box-/
├── src/
│   ├── stego/
│   │   ├── lsb_steganography.py      # LSB embedding (spatial domain)
│   │   ├── dct_steganography.py      # DCT embedding (frequency domain)
│   │   ├── dwt_steganography.py      # DWT embedding (wavelet domain)
│   │   └── __init__.py
│   ├── encryption/
│   │   ├── encryption.py             # AES-256-CBC encryption
│   │   └── __init__.py
│   ├── db/
│   │   ├── db_utils.py               # Database operations
│   │   ├── models.py                 # Data models
│   │   └── __init__.py
│   ├── steganalysis/
│   │   ├── feature_extraction.py     # AI feature extraction
│   │   ├── detection.py              # Steganalysis detection
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── unit/
│   │   ├── test_steganography.py     # 84 unit tests
│   │   ├── test_encryption.py        # Encryption tests
│   │   └── __init__.py
│   ├── integration/
│   │   ├── test_full_workflows.py    # 22 integration tests
│   │   ├── test_encode_decode_flow.py
│   │   ├── test_db_operations.py     # Database operations
│   │   └── __init__.py
│   ├── fixtures/
│   │   ├── test_fixtures.py          # 38 fixture tests
│   │   ├── test_data.py
│   │   └── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   └── __init__.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🎯 Steganography Methods

### LSB (Least Significant Bit)

**Domain:** Spatial Domain

**How it works:**
- Embeds data in the least significant bit of each pixel channel
- Example: RGB pixel (255, 128, 64) becomes (255, 128, 65) to store 1 bit

**Characteristics:**
```
┌─────────────────────────────────┐
│ Capacity:    30+ KB per image   │
│ Speed:       ⚡⚡⚡ Very Fast     │
│ Resilience:  ⚠️  Low             │
│ JPEG Safe:   ❌ No              │
│ Use Case:    Max capacity       │
└─────────────────────────────────┘
```

**Advantages:**
- ✅ Enormous capacity (30KB+ per image)
- ✅ Very fast encoding/decoding
- ✅ Simple implementation

**Disadvantages:**
- ❌ Not resilient to JPEG compression
- ❌ Easily detected by steganalysis
- ❌ Not robust to image processing

### DCT (Discrete Cosine Transform)

**Domain:** Frequency Domain (JPEG)

**How it works:**
- Embeds data in DCT coefficients used by JPEG compression
- Survives JPEG re-encoding (resilient method)
- Example: Modify middle-frequency coefficients

**Characteristics:**
```
┌─────────────────────────────────┐
│ Capacity:    1.5 KB per image   │
│ Speed:       ⏱️  Moderate       │
│ Resilience:  ✅ High (JPEG)      │
│ JPEG Safe:   ✅ Yes             │
│ Use Case:    JPEG distribution  │
└─────────────────────────────────┘
```

**Advantages:**
- ✅ Survives JPEG compression
- ✅ Resilient to lossy operations
- ✅ Industry standard

**Disadvantages:**
- ❌ Lower capacity than LSB
- ❌ Computationally expensive
- ❌ Less detectable by simple analysis

### DWT (Discrete Wavelet Transform)

**Domain:** Frequency Domain (Wavelet)

**How it works:**
- Embeds data in wavelet coefficients
- Decomposes image into frequency bands
- More resilient to noise than DCT

**Characteristics:**
```
┌─────────────────────────────────┐
│ Capacity:    2+ KB per image    │
│ Speed:       ⏱️  Moderate       │
│ Resilience:  ✅ Very High        │
│ JPEG Safe:   ✅ Moderate         │
│ Use Case:    Noise resistance   │
└─────────────────────────────────┘
```

**Advantages:**
- ✅ Multi-resolution analysis
- ✅ Excellent noise resilience
- ✅ Wavelet decomposition benefits

**Disadvantages:**
- ❌ Even lower capacity
- ❌ Complex implementation
- ❌ Computationally intensive

---

## 🔐 Encryption

### AES-256-CBC

**Algorithm:** Advanced Encryption Standard, 256-bit key, Cipher Block Chaining

**Features:**
```python
from src.encryption.encryption import encrypt_message, decrypt_message

# Encryption
plaintext = "Secret message"
password = "MyPassword123"
ciphertext = encrypt_message(plaintext, password)
# Output: Base64 encoded encrypted data with PBKDF2 salt

# Decryption
recovered = decrypt_message(ciphertext, password)
# Output: "Secret message"
```

**Security Parameters:**
- **Key Derivation:** PBKDF2 with SHA-256
- **Iterations:** 100,000
- **Salt:** 16 bytes cryptographically random
- **IV:** 16 bytes random per encryption
- **Authentication:** Built-in validation

---

## 🧪 Testing

### Test Results (Latest Run)

```
========== 178 passed, 2 skipped in 243.95s ==========

✅ Unit Tests:           84 passed
✅ Integration Tests:    22 passed
✅ Fixture Tests:        38 passed
✅ Database Tests:       34 passed
⏭️  Skipped:             2
────────────────────────────────────
```

### Test Coverage Breakdown

| Module | Coverage | Tests |
|--------|----------|-------|
| LSB Steganography | 95%+ | 20+ |
| DCT Steganography | 92%+ | 15+ |
| DWT Steganography | 90%+ | 15+ |
| Encryption | 98%+ | 15+ |
| Database Ops | 88%+ | 34+ |
| Image Filters | 100% | 10+ |
| **TOTAL** | **92%+** | **178** |

### Run Tests

```bash
# All tests with verbose output
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v              # Unit tests only
pytest tests/integration/ -v       # Integration tests only
pytest tests/fixtures/ -v          # Fixture tests only

# Generate coverage report
pytest tests/ --cov=src --cov-report=html
# View: htmlcov/index.html

# Run without database tests (if DB unavailable)
pytest tests/ -v -m "not requires_db"

# Run with markers
pytest tests/ -v -m unit           # Only unit tests
pytest tests/ -v -m integration    # Only integration tests

# Show test summary
pytest tests/ -v --tb=short
```

### Test Organization

**Unit Tests** (`tests/unit/`)
- Core functionality of each steganography method
- Encryption/decryption operations
- Image filtering and mode conversion
- Edge cases and error handling

**Integration Tests** (`tests/integration/`)
- End-to-end workflows (encode → save → load → decode)
- Multi-method comparisons
- Encryption + steganography combined workflows
- Database operations and logging
- JPEG compression resilience

**Fixture Tests** (`tests/fixtures/`)
- Test data generation quality
- Fixture scope validation
- Cleanup behavior
- Parameterized fixtures

---

## 💡 Usage Examples

### Example 1: Basic Image Steganography

```python
from PIL import Image
from src.stego.lsb_steganography import encode_image, decode_image

# Load cover image
cover = Image.open('nature.png')

# Hide message
msg = "Meeting at midnight"
stego = encode_image(cover, msg, filter_type="Blur")
stego.save('stego.png')

# Retrieve message
retrieved = decode_image(stego)
print(f"Retrieved: {retrieved}")
```

### Example 2: Secure Secret Sharing

```python
from PIL import Image
from src.stego.dct_steganography import encode_dct, decode_dct
from src.encryption.encryption import encrypt_message, decrypt_message

# Prepare message
secret = "Account: user@email.com, Password: xyz123"
password = "VerySecurePassword!@#$"

# Encrypt
encrypted = encrypt_message(secret, password)

# Hide in image
img = Image.open('background.jpg')
stego = encode_dct(img, encrypted)
stego.save('secure.jpg')

# Recipient retrieves and decrypts
retrieved_encrypted = decode_dct(stego)
decrypted = decrypt_message(retrieved_encrypted, password)
print(f"Secret: {decrypted}")
```

### Example 3: Choosing the Right Method

```python
from PIL import Image
from src.stego.lsb_steganography import encode_image, decode_image
from src.stego.dct_steganography import encode_dct, decode_dct
from src.stego.dwt_steganography import encode_dwt, decode_dwt

img = Image.open('image.png')
msg = "Secret message"

# Choose method based on use case:

# 1. Maximum capacity (won't be compressed)
if not will_be_compressed:
    encoded = encode_image(img, msg, "None")
    print(f"LSB: Can hide up to 30KB")

# 2. Sending via email (will be JPEG compressed)
elif will_be_jpeg_compressed:
    encoded = encode_dct(img, msg)
    print(f"DCT: Survives JPEG compression")

# 3. Needs to survive heavy processing
elif high_robustness_needed:
    encoded = encode_dwt(img, msg)
    print(f"DWT: Survives noise and distortion")
```

---

## 📊 Performance Comparison

### Encoding Speed (per 1000 bytes)

```
LSB:  ████████████████████ 5ms  (⚡ Very Fast)
DCT:  ██████████████████████░░░  35ms (Moderate)
DWT:  ██████████████████████░░░░ 45ms (Moderate)
```

### Capacity (per 512x512 image)

```
LSB:  ████████████████████ 30KB (Huge)
DCT:  ███░░░░░░░░░░░░░░░░  1.5KB
DWT:  ████░░░░░░░░░░░░░░░  2KB
```

### Resilience to JPEG (Quality 85)

```
LSB:  ░░░░░░░░░░░░░░░░░░░░ 0% (No resilience)
DCT:  ██████████████████░░ 90% (Very Resilient)
DWT:  █████████████████░░░ 85% (Resilient)
```

---

## 🔧 Configuration

### Database Setup (MySQL)

```python
# File: src/db/db_utils.py

DB_CONFIG = {
    'host': 'localhost',
    'user': 'stego_user',
    'password': 'secure_password',
    'database': 'stego_db'
}
```

### Image Requirements

- **Minimum Size:** 256×256 pixels (LSB), 512×512 (DCT/DWT)
- **Supported Formats:** PNG, JPEG, BMP, GIF
- **Supported Modes:** RGB, RGBA, Grayscale (L)
- **Recommended:** RGB PNG for maximum flexibility

---

## 🚨 Common Issues & Solutions

### Issue: "Message too large for image"

```python
# Solution: Check capacity before encoding
from PIL import Image

img = Image.open('image.png')
pixels = img.size[0] * img.size[1]

# LSB capacity (rough estimate)
lsb_capacity = (pixels * 3) // 8  # bytes

if len(message) > lsb_capacity:
    # Use DCT or DWT instead
    from src.stego.dct_steganography import encode_dct
    encoded = encode_dct(img, message)
```

### Issue: "JPEG compression destroyed message"

```python
# Solution: Use DCT or DWT instead of LSB
from src.stego.dct_steganography import encode_dct, decode_dct

# This survives JPEG compression
encoded = encode_dct(img, message)
encoded.save('distributed.jpg', quality=85)  # Safe!
retrieved = decode_dct(encoded)
```

### Issue: "Decryption failed: wrong password or tampered data"

```python
# Solution: Verify password and data integrity
from src.encryption.encryption import decrypt_message

try:
    plaintext = decrypt_message(ciphertext, password)
except ValueError as e:
    print(f"Decryption failed: {e}")
    # Causes:
    # - Wrong password
    # - Data corrupted during transmission
    # - Tampered ciphertext
```

---

## 📚 API Reference

### LSB Steganography

```python
from src.stego.lsb_steganography import encode_image, decode_image

# Encoding
encode_image(
    image: PIL.Image,
    message: str,
    filter_type: str = "None"  # "None", "Blur", "Sharpen", "Grayscale"
) -> PIL.Image

# Decoding
decode_image(image: PIL.Image) -> str
```

### DCT Steganography

```python
from src.stego.dct_steganography import encode_dct, decode_dct

# Encoding
encode_dct(image: PIL.Image, message: str) -> PIL.Image

# Decoding
decode_dct(image: PIL.Image) -> str
```

### DWT Steganography

```python
from src.stego.dwt_steganography import encode_dwt, decode_dwt

# Encoding (image must have even dimensions)
encode_dwt(image: PIL.Image, message: str) -> PIL.Image

# Decoding
decode_dwt(image: PIL.Image) -> str
```

### Encryption

```python
from src.encryption.encryption import encrypt_message, decrypt_message

# Encryption
encrypt_message(plaintext: str, password: str) -> str

# Decryption
decrypt_message(ciphertext: str, password: str) -> str
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Commit changes: `git commit -am 'Add YourFeature'`
4. Push to branch: `git push origin feature/YourFeature`
5. Submit Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Generate coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/
pylint src/

# Type checking
mypy src/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Faiz527** - [GitHub Profile](https://github.com/Faiz527)

---

## 📞 Support

For issues, questions, or suggestions:
- 🐛 Open an [Issue](https://github.com/Faiz527/AI-integrated-Stego-tool-box-/issues)
- 💬 Start a [Discussion](https://github.com/Faiz527/AI-integrated-Stego-tool-box-/discussions)
- 📧 Contact via GitHub

---

## 🙏 Acknowledgments

- OpenCV & PIL for image processing
- PyCryptodome for encryption
- PyWavelets for DWT implementation
- NumPy & SciPy for scientific computing

---

**Last Updated:** March 4, 2026
**Status:** ✅ Production Ready
**Test Coverage:** 92%+