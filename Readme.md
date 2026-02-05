# ITR - Advanced Image Steganography System

A comprehensive, modular image steganography application built with Streamlit that supports multiple steganography methods (LSB, Hybrid DCT, Hybrid DWT) with encryption, batch processing, error correction, pixel selection optimization, watermarking, and detailed analytics.

## 🎯 Features

### Core Steganography Methods
- **LSB (Least Significant Bit)**: Fast spatial domain steganography
- **Hybrid DCT (Discrete Cosine Transform)**: JPEG-compatible frequency domain method using Y-channel
- **Hybrid DWT (Haar Wavelet)**: Robust wavelet-based frequency domain encoding
- **Pixel Selector (Module 3)**: ML-based intelligent pixel selection using PyTorch
- **Redundancy/Error Correction (Module 6)**: Reed-Solomon ECC for corruption resistance

### Advanced Features
- ✅ **Intelligent Pixel Selection**: ML model selects optimal pixels for embedding
- ✅ **Error Correction**: Reed-Solomon encoding for image corruption recovery
- ✅ **Message Encryption**: XOR cipher with SHA-256 key derivation
- ✅ **Method Comparison**: Side-by-side analysis of all methods with PSNR metrics
- ✅ **Batch Processing**: Encode/decode multiple images in one operation
- ✅ **Stego Detection**: Detect presence of hidden data in images
- ✅ **Watermarking**: Add visible text watermarks for copyright protection
- ✅ **Real-time Analytics**: Dashboard with detailed statistics and visualizations
- ✅ **User Authentication**: Secure login with per-user operation tracking

### Watermarking
- 💧 **Text-based Watermark**: Add visible text overlays to images
- 🎨 **Customizable Settings**: Font size, position, opacity, and color
- 📍 **Position Options**: Top-left, center, or bottom-right placement
- 🖼️ **Transparency Support**: Preserves PNG transparency when watermarking

### Analytics Dashboard
- 📊 **Operation Timeline**: Track operations over customizable time periods
- 📈 **Method Distribution**: Usage statistics for LSB, DCT, and DWT
- 📉 **Encode vs Decode**: Comparative statistics on operation types
- 🔐 **Encryption Metrics**: Encrypted vs unencrypted message statistics
- 💾 **Capacity Analysis**: Data size distribution and capacity visualization
- 📋 **Activity Log**: Real-time log of recent user operations

### User Management
- User authentication with SHA-256 password hashing
- Per-user operation tracking and statistics
- Activity logging and audit trails
- Session management with automatic logout

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** (3.10+ recommended)
- **PostgreSQL 9.1+** with proper credentials
- **pip** (Python package manager)
- **Virtual Environment** (strongly recommended)

### Step-by-Step Installation

1. **Clone or Download the Project**
```bash
git clone https://github.com/yourusername/ITR-Steganography.git
cd ITR
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
streamlit run app.py
```

The app will open at: `http://localhost:8501`

---

## 📁 Project Structure

```
ITR/
├── .env                              # Environment variables (PostgreSQL)
├── .gitignore                        # Git ignore rules
├── .streamlit/
│   ├── config.toml                  # Streamlit configuration
│   └── secrets.toml                 # Optional: Streamlit secrets for deployment
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── app.py                           # Main Streamlit application entry point
├── streamlit_app.py                # Alternative Streamlit entry point
├── create_db.py                    # PostgreSQL database initialization
├── test_db.py                      # Database connection test script
├── test_steganography.py           # Steganography methods unit tests
├── demo_hide_extract.py            # Demo script with full workflow
├── make_demo_images.py             # Generate synthetic test images
│
├── src/                            # Main source code package
│   ├── __init__.py
│   │
│   ├── stego/                      # ⭐ Core Steganography Engine
│   │   ├── __init__.py
│   │   ├── lsb_steganography.py           # LSB spatial domain method
│   │   ├── dct_steganography.py           # Hybrid DCT frequency domain
│   │   └── dwt_steganography.py           # Hybrid DWT wavelet method
│   │
│   ├── watermark/                  # 💧 Watermarking Module
│   │   ├── __init__.py
│   │   └── watermark.py            # Text watermark implementation
│   │
│   ├── db/                         # 🗄️ Database Layer
│   │   ├── __init__.py
│   │   ├── db_utils.py             # PostgreSQL operations & user management
│   │   └── db_utils_minimal.py     # Minimal database utilities
│   │
│   ├── analytics/                  # 📊 Analytics & Statistics Engine
│   │   ├── __init__.py
│   │   └── stats.py                # Chart generation & statistics calculations
│   │
│   ├── encryption/                 # 🔐 Encryption Module
│   │   ├── __init__.py
│   │   └── encryption.py           # XOR cipher with SHA-256 key derivation
│   │
│   ├── batch_processing/           # ⚙️ Batch Processing Module
│   │   ├── __init__.py
│   │   ├── batch_encoder.py        # Batch encoding operations
│   │   ├── controller.py           # Batch processing controller
│   │   ├── zip_handler.py          # ZIP archive handling
│   │   └── report_generator.py     # Report generation (JSON/CSV)
│   │
│   └── ui/                         # 🎨 User Interface Components
│       ├── __init__.py
│       ├── styles.py               # Dark theme CSS & styling
│       ├── config_dict.py          # UI text and labels configuration
│       ├── reusable_components.py  # Common UI components
│       └── ui_components.py        # Streamlit page sections
│
├── stegotool/                      # 🧠 Advanced AI/ML Modules
│   ├── __init__.py
│   │
│   ├── data/                       # Training data and models
│   │   └── module3/
│   │       └── sample.npz          # Sample training data
│   │
│   ├── models/                     # Pre-trained models
│   │   └── module3_pixel_selector/
│   │       └── best.pth            # Trained PyTorch model
│   │
│   └── modules/
│       ├── module3_pixel_selector/         # 🎯 Intelligent Pixel Selection
│       │   ├── __init__.py
│       │   ├── selector_baseline.py        # Heuristic pixel selection
│       │   ├── selector_model.py           # PyTorch neural network model
│       │   ├── selector_model_infer.py     # Model inference & predictions
│       │   ├── selector_utils.py           # Utility functions
│       │   ├── generate_training_data.py   # Training data generation
│       │   ├── generate_labels_robust.py   # Robust label generation
│       │   ├── train_selector_model.py     # Model training script
│       │   └── test_selector.py            # Unit tests
│       │
│       └── module6_redundancy/             # 🛡️ Error Correction Module
│           ├── __init__.py
│           ├── rs_wrapper.py               # Reed-Solomon error correction
│           ├── capacity_checker.py         # Payload capacity validation
│           ├── corruption_simulator.py     # Image corruption testing
│           ├── test_rs_wrapper.py          # Reed-Solomon unit tests
│           └── test_rs_stress.py           # Stress testing
│
└── data/                           # 📦 Data directories
    ├── input/
    │   ├── images/                 # Input images for processing
    │   └── zips/                   # ZIP archives for batch processing
    ├── output/
    │   ├── encoded/                # Encoded output images
    │   ├── decoded/                # Decoded messages
    │   ├── batches/                # Batch processing results
    │   └── reports/                # Processing reports (JSON/CSV)
    └── temp/                       # Temporary files

├── logs/                           # Application logs

└── __pycache__/                    # Python cache (ignored)
```

### Module Organization

**`src/stego/`** - Steganography Engine
- Independent implementations of LSB, DCT, and DWT methods
- Each method has encode/decode functions
- No external dependencies between methods

**`src/watermark/`** - Watermarking Module
- Text-based visible watermarking
- Customizable font size, position, opacity, and color
- Preserves image transparency for PNG files

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

**`src/encryption/`** - Message Security
- XOR cipher with SHA-256 key derivation
- Symmetric encryption/decryption
- Optional message protection

**`src/ui/`** - Web Interface
- Streamlit UI components
- Dark theme styling
- Authentication section
- Encode/Decode sections
- Comparison, Statistics, and Watermarking sections

**`src/batch_processing/`** - Batch Processing Module
- Batch encoding and decoding functions
- File validation and error handling
- Integration with core steganography engine

---

## 🔐 Usage Guide

### 1. **Create Account**
- Click "Create New Account" on the login screen
- Enter username and password
- Account is created in PostgreSQL database

### 2. **Encode Message**
- Go to **Encode** tab
- Select steganography method (LSB, DCT, or DWT)
- Upload cover image (PNG/JPG)
- Enter secret message
- (Optional) Enable encryption with AES-256
- Click "Encode Message"
- Download the encoded image

### 3. **Decode Message**
- Go to **Decode** tab
- Upload encoded image
- Select the method used for encoding
- Click "Decode Message"
- View extracted message
- (If encrypted) Message is automatically decrypted

### 4. **Compare Methods**
- Go to **Comparison** tab
- Upload cover image
- Enter secret message
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

### 6. **Pixel Selector**
- Go to **Pixel Selector** tab
- Upload an image for analysis
- Configure payload bits, patch size, and LSB bits
- Analyze to find optimal pixels for hiding data
- View visualization of best pixel locations

### 7. **Detect Stego**
- Go to **Detect Stego** tab
- Upload a suspicious image
- Adjust detection sensitivity
- Analyze image for hidden content
- View detection score and metrics

### 8. **Error Correction**
- Go to **Error Correction** tab
- Upload image and enter message
- Configure ECC strength (parity bytes)
- Check capacity and test corruption recovery
- Simulate JPEG recompression, bit flips, or noise

### 9. **Watermarking**
- Go to **Watermarking** tab
- Upload image to watermark
- Enter watermark text (e.g., "© Your Name")
- Customize font size, position, opacity, and color
- Click "Apply Watermark"
- Download watermarked image

### 10. **Batch Processing**
- Go to **Batch Processing** tab
- Select folder with images for encoding/decoding
- Choose steganography method and encryption options
- Click "Start Batch Processing"
- Download link for processed images will be provided

---

## 🔧 Technical Details

### Steganography Methods

#### LSB (Least Significant Bit)
- **Domain**: Spatial
- **Capacity**: ~2.5% of image size
- **Detection Resistance**: Low
- **Computational Cost**: Very Low
- **Quality**: Excellent (PSNR > 50 dB)

#### Hybrid DCT
- **Domain**: Frequency (Y-channel only)
- **Capacity**: ~1.5% of image size
- **Detection Resistance**: Medium
- **Computational Cost**: Medium
- **Quality**: Good (PSNR > 40 dB)

#### Hybrid DWT (Haar Wavelet)
- **Domain**: Frequency (Wavelet)
- **Capacity**: ~2% of image size
- **Detection Resistance**: High
- **Computational Cost**: Medium-High
- **Quality**: Very Good (PSNR > 45 dB)

### Watermarking

#### Text-based Watermark
- **Type**: Visible overlay
- **Customization**: Font size (10-100), position, opacity (50-255), color
- **Positions**: Top-left, Center, Bottom-right
- **Transparency**: Preserves PNG alpha channel
- **Output Format**: PNG

### Encryption
- **Algorithm**: XOR cipher with SHA-256 key derivation
- **Key Size**: 256-bit (derived from password)
- **Security**: Suitable for steganography; recommended AES-256 for highly sensitive data
- **Performance**: Very fast (negligible overhead)

### Database Schema

**users**
```sql
user_id (PK) | username | password_hash | created_at
```

**operations**
```sql
operation_id (PK) | user_id (FK) | operation_type | method | 
data_size | is_encrypted | status | created_at
```

**activity_log**
```sql
activity_id (PK) | user_id (FK) | action | details | created_at
```

---

## 📊 Analytics & Statistics

The application tracks:
- **Total Operations**: Count of all encode/decode operations
- **Method Usage**: Distribution of LSB, DCT, DWT usage
- **Encryption Rate**: Percentage of operations using encryption
- **Operation Timeline**: Operations per day over 7 days
- **Data Size Distribution**: Breakdown of message sizes
- **User Activity**: Recent operations by all users

---

## 🧪 Testing

Run steganography tests:
```bash
python test_steganography.py
```

Test database connection:
```bash
python test_db.py
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
DB_HOST=localhost              # PostgreSQL host
DB_PORT=5432                   # PostgreSQL port
DB_NAME=stegnography           # Database name
DB_USER=postgres               # PostgreSQL username
DB_PASSWORD=your_password      # PostgreSQL password
```

### Secrets Configuration (`.streamlit/secrets.toml`)
Optional for cloud deployments:
```toml
[postgres]
host = "your_host"
port = "5432"
dbname = "your_db"
user = "your_user"
password = "your_password"
sslmode = "require"
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

### Watermarking Issues
- For transparent PNGs, the watermark preserves transparency
- If text is not visible, try changing the text color
- Adjust opacity for better visibility

---

## 📈 Performance Metrics

Typical performance on modern hardware:

| Operation | Time | Memory |
|-----------|------|--------|
| LSB Encode (1MB) | 0.5s | 50MB |
| DCT Encode (1MB) | 1.2s | 80MB |
| DWT Encode (1MB) | 1.5s | 100MB |
| Decode Any Method | 0.3s | 40MB |
| Watermark (1MB) | 0.2s | 30MB |

---

## 🔒 Security Considerations

- ✅ Passwords hashed with SHA-256
- ✅ XOR encryption with SHA-256 key derivation for message protection
- ✅ HTTPS recommended for production deployment
- ✅ Database access controlled via credentials
- ✅ No sensitive data in logs

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 👨‍💻 Developer Information

**Application**: Image Steganography & Watermarking (ITR)
**Version**: 2.0.0
**Built with**: 
- Streamlit (Frontend)
- PostgreSQL (Database)
- Python 3.10+

**Key Libraries**:
- `Pillow` - Image processing & watermarking
- `NumPy/SciPy` - Scientific computing
- `PyWavelets` - Wavelet transforms
- `Plotly` - Interactive visualizations
- `psycopg2` - PostgreSQL adapter
- `cryptography` - Encryption
- `reedsolo` - Reed-Solomon error correction

---

## 🚀 Future Enhancements

Potential improvements:
- [ ] Quality Metrics Module - PSNR, MSE, SSIM calculations
- [ ] Auto-detection Module - Automatically select best method per image
- [ ] Additional image formats (BMP, TIFF, WebP, etc.)
- [ ] Video steganography support
- [ ] Real-time image preview during encoding
- [ ] Report generation (PDF, CSV, JSON)
- [ ] Advanced steganalysis detection
- [ ] Cloud storage integration (AWS S3, Google Drive)
- [ ] Mobile app support
- [ ] Docker containerization
- [ ] Distributed computing for large-scale batch processing
- [ ] LSB-based invisible watermarking
- [ ] Alpha blending watermark with logo images

---

## 📚 Module Development Guide

### Adding New Steganography Method

1. Create new file in `src/stego/` (e.g., `new_method_steganography.py`)
2. Implement `encode_method(img, secret_text)` and `decode_method(img)`
3. Export functions in `src/stego/__init__.py`
4. Add UI section in `src/ui/ui_components.py`
5. Update imports in `app.py`

### Adding New Watermarking Method

1. Add function in `src/watermark/watermark.py`
2. Export in `src/watermark/__init__.py`
3. Add UI section in `show_watermarking_section()` in `ui_components.py`

### Adding New Chart/Statistic

1. Create function in `src/analytics/stats.py`
2. Export in `src/analytics/__init__.py`
3. Import in `src/ui/ui_components.py`
4. Add UI element in `show_statistics_section()`

### Database Operations

1. Add function in `src/db/db_utils.py`
2. Export in `src/db/__init__.py`
3. Call from appropriate UI component

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify all dependencies are installed
4. Test database connection with `test_db.py`

---

**Last Updated**: February 5, 2026
**Project Structure**: Modular Architecture v2.0
**Latest Changes**: Added Watermarking module with text-based visible watermarks
