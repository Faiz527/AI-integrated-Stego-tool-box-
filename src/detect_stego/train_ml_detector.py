"""
Training Script for Random Forest Steganography Detector
========================================================
Generates synthetic training data and trains Random Forest model.

USAGE:
    python train_detector.py --samples 100
    python train_detector.py -n 200 -o ./models/my_detector.pkl
"""

import logging
import random
import string
import numpy as np
from pathlib import Path
from typing import Tuple
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from src.stego.lsb_steganography import encode_image as lsb_encode
    from src.stego.dct_steganography import encode_dct
    from src.stego.dwt_steganography import encode_dwt
    from src.detect_stego.ml_detector import StegoDetectorML, MODEL_PATH
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.stego.lsb_steganography import encode_image as lsb_encode
    from src.stego.dct_steganography import encode_dct
    from src.stego.dwt_steganography import encode_dwt
    from src.detect_stego.ml_detector import StegoDetectorML, MODEL_PATH


def generate_random_image(width=256, height=256):
    """Generate a random natural-looking image."""
    x = np.linspace(0, 255, width)
    y = np.linspace(0, 255, height)
    xx, yy = np.meshgrid(x, y)
    
    noise = np.random.normal(0, 30, (height, width, 3))
    r = (xx + noise[:, :, 0]) % 256
    g = (yy + noise[:, :, 1]) % 256
    b = ((xx + yy) / 2 + noise[:, :, 2]) % 256
    
    img_array = np.stack([r, g, b], axis=-1)
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array, 'RGB')


def generate_pattern_image(width=256, height=256, pattern_type='natural'):
    """Generate patterned images that simulate real photos."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    if pattern_type == 'stripes':
        for i in range(height):
            color = int(128 + 60 * np.sin(i / 20))
            img_array[i, :, :] = [color, color, color]
        noise = np.random.normal(0, 15, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
    elif pattern_type == 'checker':
        block_size = 32
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                color = 200 if ((i // block_size) + (j // block_size)) % 2 == 0 else 80
                img_array[i:i+block_size, j:j+block_size, :] = color
        noise = np.random.normal(0, 10, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
    elif pattern_type == 'gradient':
        for i in range(height):
            for j in range(width):
                r = int(255 * i / height)
                g = int(255 * j / width)
                b = int(128 + 50 * np.sin((i + j) / 30))
                img_array[i, j] = [r, g, b]
        noise = np.random.normal(0, 8, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
    else:  # natural
        base_r = np.random.randint(50, 200)
        base_g = np.random.randint(50, 200)
        base_b = np.random.randint(50, 200)
        
        for i in range(height):
            for j in range(width):
                r = base_r + int(30 * np.sin(i / 50) * np.cos(j / 40))
                g = base_g + int(30 * np.cos(i / 40) * np.sin(j / 50))
                b = base_b + int(20 * np.sin((i + j) / 60))
                img_array[i, j] = [
                    np.clip(r, 0, 255),
                    np.clip(g, 0, 255),
                    np.clip(b, 0, 255)
                ]
        noise = np.random.normal(0, 12, img_array.shape)
        img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array, 'RGB')


def generate_random_message(length=None):
    """Generate a random secret message."""
    if length is None:
        length = random.randint(20, 200)
    
    templates = [
        "Secret message: {}",
        "Confidential data: {}",
        "Hidden text: {}",
        "Encrypted: {}",
        "Private: {}"
    ]
    
    content = ''.join(random.choices(
        string.ascii_letters + string.digits + ' ',
        k=length
    ))
    
    return random.choice(templates).format(content)


def create_stego_image(cover_img, method='lsb'):
    """Create a stego image using the specified method."""
    message = generate_random_message()
    
    try:
        if method == 'lsb':
            return lsb_encode(cover_img.copy(), message)
        elif method == 'dct':
            return encode_dct(cover_img.copy(), message)
        elif method == 'dwt':
            return encode_dwt(cover_img.copy(), message)
        else:
            return lsb_encode(cover_img.copy(), message)
    except Exception as e:
        logger.warning(f"Encoding with {method} failed: {e}, using LSB fallback")
        return lsb_encode(cover_img.copy(), message[:50])


def generate_training_data(n_samples=100, image_sizes=[(256, 256)]) -> Tuple[list, list]:
    """Generate synthetic training data."""
    cover_images = []
    stego_images = []
    
    methods = ['lsb', 'dct', 'dwt']
    patterns = ['stripes', 'checker', 'gradient', 'natural', 'random']
    samples_per_type = n_samples // 2
    
    logger.info(f"Generating {samples_per_type} cover + {samples_per_type} stego images...")
    
    # Cover images
    for i in range(samples_per_type):
        size = random.choice(image_sizes)
        pattern = random.choice(patterns)
        
        try:
            if pattern == 'random':
                cover_img = generate_random_image(size[0], size[1])
            else:
                cover_img = generate_pattern_image(size[0], size[1], pattern)
            
            cover_array = np.array(cover_img.convert('RGB'))
            cover_images.append(cover_array)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Generated {i + 1}/{samples_per_type} cover images")
        except Exception as e:
            logger.warning(f"Failed to generate cover image {i}: {e}")
            continue
    
    # Stego images
    for i in range(samples_per_type):
        size = random.choice(image_sizes)
        pattern = random.choice(patterns)
        method = random.choice(methods)
        
        try:
            if pattern == 'random':
                cover_img = generate_random_image(size[0], size[1])
            else:
                cover_img = generate_pattern_image(size[0], size[1], pattern)
            
            stego_img = create_stego_image(cover_img, method)
            stego_array = np.array(stego_img.convert('RGB'))
            stego_images.append(stego_array)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Generated {i + 1}/{samples_per_type} stego images")
        except Exception as e:
            logger.warning(f"Failed to generate stego image {i}: {e}")
            continue
    
    logger.info(f"Generated {len(cover_images)} cover + {len(stego_images)} stego images")
    return cover_images, stego_images


def train_detector(n_samples=100, save_path=None):
    """Train the Random Forest ML detector with synthetic data."""
    logger.info("=" * 70)
    logger.info("TRAINING RANDOM FOREST STEGANOGRAPHY DETECTOR")
    logger.info("=" * 70)
    
    cover_images, stego_images = generate_training_data(n_samples)
    
    if len(cover_images) < 10 or len(stego_images) < 10:
        logger.error("Insufficient training data generated")
        return {"error": "Insufficient training data"}
    
    detector = StegoDetectorML()
    logger.info(f"\nTraining on {len(cover_images)} cover + {len(stego_images)} stego images...")
    metrics = detector.train(cover_images, stego_images, validation_split=0.2)
    
    if "error" not in metrics:
        save_path = save_path or MODEL_PATH
        detector.save_model(save_path)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Train Accuracy:      {metrics['train_accuracy']:.2%}")
        logger.info(f"Validation Accuracy: {metrics['val_accuracy']:.2%}")
        logger.info(f"Precision:           {metrics['val_precision']:.2%}")
        logger.info(f"Recall:              {metrics['val_recall']:.2%}")
        logger.info(f"F1 Score:            {metrics['val_f1']:.4f}")
        logger.info(f"Model saved to:      {save_path}")
        logger.info("=" * 70)
        
        importance = detector.get_feature_importance()
        logger.info("\n📊 Top Features (Random Forest):")
        for i, (name, imp) in enumerate(sorted(importance.items(), key=lambda x: x[1], reverse=True)):
            logger.info(f"  {i+1}. {name:.<40} {imp:.4f}")
    else:
        logger.error(f"Training failed: {metrics['error']}")
    
    return metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Train Random Forest steganography detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train_detector.py --samples 100
  python train_detector.py -n 200
        """
    )
    
    parser.add_argument(
        "--samples", "-n",
        type=int,
        default=100,
        help="Number of image pairs to generate (default: 100)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output path for model (default: src/detect_stego/models/stego_detector_rf.pkl)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting training with {args.samples} image pairs...")
    metrics = train_detector(n_samples=args.samples, save_path=args.output)
    
    if "error" not in metrics:
        print("\n✅ Model training completed successfully!")
        print(f"   Accuracy: {metrics['val_accuracy']:.1%}")
    else:
        print(f"\n❌ Training failed: {metrics['error']}")