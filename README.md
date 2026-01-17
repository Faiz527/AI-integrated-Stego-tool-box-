# StegoTool: Advanced Image Steganography System

## Overview

**StegoTool** is a comprehensive, modular steganography framework that enables secure hiding and recovery of secret messages within digital images. It combines three advanced encoding techniques (LSB, DCT, DWT), intelligent analysis algorithms, and robust error correction to create a resilient steganography system.

The system is designed for:
- **Secure Communication**: Hide confidential messages within innocent-looking images
- **Research & Development**: Modular architecture for testing different steganography techniques
- **Robustness Testing**: Validate message recovery after JPEG compression and other corruptions
- **Statistical Analysis**: Detect hidden data using advanced stochastic methods

---

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL database (for user management and logging)
- pip package manager

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**
   - Create a new PostgreSQL database and user
   - Update `database/config.py` with your database credentials
   - Run the provided SQL scripts to set up tables and initial data

3. **Run the application**
   ```bash
   streamlit run app_streamlit.py
   ```
   - Access the web interface at `http://localhost:8501`

---

## Project Structure
soban-module-main/src/
├── stegotool/
│ ├── init.py
│ ├── app_streamlit.py # Web UI (Streamlit)
│ ├── modules/
│ │ ├── module3_pixel_selector/ # Smart pixel selection
│ │ │ ├── selector_baseline.py # Heuristic baseline selection
│ │ │ ├── selector_model.py # Neural network-based selection
│ │ │ ├── selector_model_infer.py # Model inference
│ │ │ ├── selector_utils.py # Utility functions
│ │ │ ├── generate_labels_robust.py # Training data generation
│ │ │ ├── generate_training_data.py # Extended data generation
│ │ │ ├── train_selector_model.py # Model training pipeline
│ │ │ └── test_selector.py # Unit tests
│ │ ├── module4_freq_embed/ # Frequency domain embedding
│ │ │ ├── freq_map.py # Frequency mapping
│ │ │ └── freq_selector.py # Frequency-based selection
│ │ ├── module5_steg_detector/ # Steganography detection
│ │ │ ├── model.py # Detection model
│ │ │ ├── preprocess.py # Image preprocessing
│ │ │ └── train.py # Training pipeline
│ │ ├── module6_redundancy/ # Error correction & resilience
│ │ │ ├── rs_wrapper.py # Reed-Solomon ECC
│ │ │ ├── capacity_checker.py # Capacity calculations
│ │ │ ├── corruption_simulator.py # JPEG and corruption 
testing
│ │ │ ├── test_rs_wrapper.py # ECC tests
│ │ │ └── test_rs_stress.py # Stress tests
│ │ └── module9_integration/ # End-to-end flows
│ │ ├── hide_flow.py # Embedding pipeline
│ │ └── extract_flow.py # Extraction pipeline
│ ├── utils/
│ │ ├── helpers.py # General utilities
│ │ ├── image_preproc.py # Image preprocessing
│ │ ├── metrics.py # Performance metrics
│ │ └── payload_reader.py # Payload handling
│ ├── data/
│ │ ├── dev_images/ # Development test images
│ │ └── module3/
│ │ └── sample.npz # Cached training data
│ └── models/
│ └── module3_pixel_selector/
│ └── best.pth # Pre-trained selection model
├── demo_hide_extract.py # Complete end-to-end demo
├── make_demo_images.py # Generate synthetic test images
├── diag_groups.py # Diagnostic: pixel grouping
├── diag_dev_images.py # Diagnostic: image inspection
└── requirements.txt # Python dependencies

---

## Core Modules

### Module 3: Intelligent Pixel Selection

**Purpose**: Select the optimal pixels for embedding secret data to maximize both capacity and imperceptibility.

**Key Features**:
- **Baseline Heuristic Selector** (`selector_baseline.py`):
  - Scores pixels based on local entropy, Laplacian variance, and patch variance
  - Selects highest-scoring pixels to minimize visual artifacts
  - Works with configurable patch sizes and LSB bit depths

- **ML-based Selector** (`selector_model.py`):
  - Neural network trained to predict optimal pixel locations
  - Learns complex patterns for even better imperceptibility
  - Inference via `selector_model_infer.py`

- **Pixel Capacity**:
  - Each pixel has 3 color channels (RGB)
  - Each channel can hide 1-8 LSB bits
  - Total per-pixel capacity: channels × lsb_bits bits

**API**:
```python
from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels

coords = select_pixels(
    image_np,           # HxWx3 RGB numpy array
    payload_bits=512,   # Bits to embed
    patch_size=5,       # Neighborhood size
    lsb_bits=1          # Bits per channel
)
# Returns: List[(x, y)] ordered by quality
```
