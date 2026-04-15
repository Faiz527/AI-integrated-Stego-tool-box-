"""
Test and Validate Trained ML Model
===================================
Tests the trained Random Forest model on various image types to ensure
real-world accuracy and generalization.
"""

import numpy as np
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import sys
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import only what we need, avoiding chain imports
import importlib.util

# Load ml_detector directly
ml_detector_path = Path(__file__).parent / "ml_detector.py"
spec = importlib.util.spec_from_file_location("ml_detector", ml_detector_path)
ml_detector = importlib.util.module_from_spec(spec)
sys.modules['ml_detector'] = ml_detector
spec.loader.exec_module(ml_detector)

get_detector = ml_detector.get_detector
StegoDetectorML = ml_detector.StegoDetectorML

# Load encoding methods with error handling
try:
    from src.stego.lsb_steganography import encode_image as lsb_encode
except ImportError:
    lsb_encode = None

try:
    from src.stego.dct_steganography import encode_dct
except ImportError:
    encode_dct = None

try:
    from src.stego.dwt_steganography import encode_dwt
except ImportError:
    encode_dwt = None

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# ============================================================================
#  Test Image Generation
# ============================================================================

def generate_realistic_cover_images(n_images=50):
    """
    Generate realistic-looking cover images (not heavily encoded).
    Various types: solid colors, gradients, textures, patterns.
    
    Returns:
        list of numpy arrays
    """
    logger.info(f"Generating {n_images} realistic cover images...")
    images = []
    
    for i in range(n_images):
        size = (256, 256)
        img_type = i % 4
        
        if img_type == 0:
            # Solid color or gradient
            img = Image.new('RGB', size, color=(np.random.randint(50, 200), 
                                                  np.random.randint(50, 200), 
                                                  np.random.randint(50, 200)))
            # Add slight noise
            arr = np.array(img, dtype=np.float32)
            noise = np.random.normal(0, 5, arr.shape)
            arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
            
        elif img_type == 1:
            # Gradient image
            arr = np.zeros((size[0], size[1], 3), dtype=np.uint8)
            for c in range(3):
                gradient = np.linspace(50, 200, size[1], dtype=np.uint8)
                arr[:, :, c] = np.tile(gradient, (size[0], 1))
            img = Image.fromarray(arr)
            
        elif img_type == 2:
            # Texture (random noise smoothed)
            arr = np.random.randint(100, 180, (*size, 3), dtype=np.uint8)
            img = Image.fromarray(arr)
            img = img.filter(ImageFilter.GaussianBlur(radius=3))
            
        else:  # img_type == 3
            # Simple geometric pattern
            img = Image.new('RGB', size, color=(128, 128, 128))
            draw = ImageDraw.Draw(img)
            for j in range(0, size[0], 32):
                draw.rectangle([j, 0, j+16, size[1]], fill=(200, 200, 200))
        
        images.append(np.array(img))
    
    logger.info(f"  ✓ Generated {len(images)} realistic cover images")
    return images


def generate_stego_test_images(cover_images, n_per_image=1):
    """
    Generate stego images from cover images for testing.
    
    Returns:
        list of numpy arrays (stego images)
    """
    logger.info(f"Generating stego test images from {len(cover_images)} covers...")
    stego_images = []
    
    methods = []
    if lsb_encode:
        methods.append(('lsb', lsb_encode))
    if encode_dct:
        methods.append(('dct', encode_dct))
    if encode_dwt:
        methods.append(('dwt', encode_dwt))
    
    if not methods:
        logger.warning("No encoding methods available! Cannot generate stego images.")
        return stego_images
    
    for i, cover_arr in enumerate(cover_images):
        # Generate secret message
        msg_len = np.random.randint(50, 200)
        secret_msg = ''.join(chr(np.random.randint(32, 126)) for _ in range(msg_len))
        
        cover_pil = Image.fromarray(cover_arr)
        
        # Try each method
        for method_name, method_func in methods:
            try:
                if method_name == 'lsb':
                    stego_pil = method_func(cover_pil, secret_msg)
                else:  # dct or dwt
                    stego_pil = method_func(cover_pil, secret_msg)
                
                stego_images.append(np.array(stego_pil))
                break  # Only need one successful embedding per cover
            except Exception as e:
                logger.debug(f"Method {method_name} failed for image {i}: {e}")
                continue
    
    logger.info(f"  ✓ Generated {len(stego_images)} stego test images")
    return stego_images


# ============================================================================
#  Model Validation
# ============================================================================

def validate_model():
    """
    Comprehensive model validation on multiple image types.
    
    Returns:
        dict: Validation results
    """
    logger.info("=" * 70)
    logger.info("STARTING MODEL VALIDATION")
    logger.info("=" * 70)
    
    try:
        # Load model
        logger.info("\n📦 Loading trained model...")
        detector = get_detector()
        
        if not detector.is_trained:
            logger.error("❌ Model not trained! Run: python train_ml_detector.py")
            return {"error": "Model not trained"}
        
        logger.info("✅ Model loaded successfully")
        
        # Test 1: Realistic cover images (should be low confidence)
        logger.info("\n" + "=" * 70)
        logger.info("TEST 1: Realistic Cover Images (Expected: Low Confidence)")
        logger.info("=" * 70)
        
        covers = generate_realistic_cover_images(n_images=50)
        cover_scores = []
        
        for i, cover_arr in enumerate(covers):
            try:
                pred, conf = detector.predict(cover_arr, return_confidence=True)
                cover_scores.append(conf)
                if (i + 1) % 10 == 0:
                    logger.info(f"  Processed {i + 1}/{len(covers)} cover images")
            except Exception as e:
                logger.warning(f"Error processing cover image {i}: {e}")
        
        cover_scores = np.array(cover_scores)
        logger.info(f"\nCover Image Statistics:")
        logger.info(f"  Mean Confidence: {np.mean(cover_scores):.1f}%")
        logger.info(f"  Std Deviation:   {np.std(cover_scores):.1f}%")
        logger.info(f"  Min Confidence:  {np.min(cover_scores):.1f}%")
        logger.info(f"  Max Confidence:  {np.max(cover_scores):.1f}%")
        
        # Count false positives (incorrectly classified as stego)
        false_positives = np.sum(cover_scores > 50)
        fp_rate = (false_positives / len(cover_scores)) * 100 if len(cover_scores) > 0 else 0
        logger.info(f"  False Positive Rate (>50%): {false_positives}/{len(cover_scores)} ({fp_rate:.1f}%)")
        
        # Test 2: Stego images (should be high confidence)
        logger.info("\n" + "=" * 70)
        logger.info("TEST 2: Stego Test Images (Expected: High Confidence)")
        logger.info("=" * 70)
        
        stego = generate_stego_test_images(covers[:20], n_per_image=1)
        stego_scores = []
        
        for i, stego_arr in enumerate(stego):
            try:
                pred, conf = detector.predict(stego_arr, return_confidence=True)
                stego_scores.append(conf)
                if (i + 1) % 10 == 0:
                    logger.info(f"  Processed {i + 1}/{len(stego)} stego images")
            except Exception as e:
                logger.warning(f"Error processing stego image {i}: {e}")
        
        stego_scores = np.array(stego_scores)
        logger.info(f"\nStego Image Statistics:")
        logger.info(f"  Mean Confidence: {np.mean(stego_scores):.1f}%")
        logger.info(f"  Std Deviation:   {np.std(stego_scores):.1f}%")
        logger.info(f"  Min Confidence:  {np.min(stego_scores):.1f}%")
        logger.info(f"  Max Confidence:  {np.max(stego_scores):.1f}%")
        
        # Count true positives (correctly classified as stego)
        true_positives = np.sum(stego_scores > 50)
        tp_rate = (true_positives / len(stego_scores)) * 100 if len(stego_scores) > 0 else 0
        logger.info(f"  True Positive Rate (>50%): {true_positives}/{len(stego_scores)} ({tp_rate:.1f}%)")
        
        # Test 3: Feature Analysis
        logger.info("\n" + "=" * 70)
        logger.info("TEST 3: Feature Analysis")
        logger.info("=" * 70)
        
        importance = detector.get_feature_importance()
        logger.info("\nTop Features by Importance:")
        for feature, importance_val in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  - {feature}: {importance_val:.4f}")
        
        # Test 4: Separation Analysis
        logger.info("\n" + "=" * 70)
        logger.info("TEST 4: Class Separation Analysis")
        logger.info("=" * 70)
        
        separation = np.mean(stego_scores) - np.mean(cover_scores)
        logger.info(f"\nSeparation Score: {separation:.1f}%")
        logger.info(f"  (Higher = better discrimination)")
        
        # Decision thresholds
        logger.info(f"\nDecision Thresholds:")
        logger.info(f"  Clean (≤30%):   {np.sum(cover_scores <= 30)}/{len(cover_scores)} covers")
        logger.info(f"  Suspicious (30-70%): {np.sum((cover_scores > 30) & (cover_scores < 70))}/{len(cover_scores)} covers")
        logger.info(f"  Stego (≥70%):   {np.sum(cover_scores >= 70)}/{len(cover_scores)} covers")
        
        # Build results dict
        results = {
            "status": "success",
            "cover_images_tested": len(covers),
            "stego_images_tested": len(stego),
            "cover_mean_confidence": float(np.mean(cover_scores)),
            "cover_std_confidence": float(np.std(cover_scores)),
            "stego_mean_confidence": float(np.mean(stego_scores)),
            "stego_std_confidence": float(np.std(stego_scores)),
            "false_positive_rate": float(fp_rate),
            "true_positive_rate": float(tp_rate),
            "separation_score": float(separation),
        }
        
        # Final verdict
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION VERDICT")
        logger.info("=" * 70)
        
        if fp_rate > 10:
            logger.warning(f"⚠️  High false positive rate: {fp_rate:.1f}%")
            logger.warning("   Model may over-detect stego in real images")
            results["verdict"] = "NEEDS_IMPROVEMENT"
        elif tp_rate < 80:
            logger.warning(f"⚠️  Low true positive rate: {tp_rate:.1f}%")
            logger.warning("   Model may miss stego images")
            results["verdict"] = "NEEDS_IMPROVEMENT"
        elif separation < 40:
            logger.warning(f"⚠️  Low separation score: {separation:.1f}%")
            logger.warning("   Model confidence ranges overlap too much")
            results["verdict"] = "ACCEPTABLE_WITH_CAUTION"
        else:
            logger.info("✅ Model validation PASSED")
            logger.info(f"   False Positive Rate: {fp_rate:.1f}% (Good)")
            logger.info(f"   True Positive Rate: {tp_rate:.1f}% (Good)")
            logger.info(f"   Separation Score: {separation:.1f}% (Good)")
            results["verdict"] = "READY_FOR_DEPLOYMENT"
        
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION COMPLETE ✓")
        logger.info("=" * 70)
        
        return results
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}", exc_info=True)
        return {"error": str(e), "status": "failed"}


def print_summary(results):
    """Print a summary of validation results."""
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    if "error" in results:
        print(f"❌ Validation Failed: {results['error']}")
        return
    
    print(f"\n📊 Test Statistics:")
    print(f"   Cover Images Tested: {results['cover_images_tested']}")
    print(f"   Stego Images Tested: {results['stego_images_tested']}")
    
    print(f"\n📈 Cover Image Results:")
    print(f"   Mean Confidence: {results['cover_mean_confidence']:.1f}%")
    print(f"   Std Deviation:   {results['cover_std_confidence']:.1f}%")
    
    print(f"\n📈 Stego Image Results:")
    print(f"   Mean Confidence: {results['stego_mean_confidence']:.1f}%")
    print(f"   Std Deviation:   {results['stego_std_confidence']:.1f}%")
    
    print(f"\n🎯 Performance Metrics:")
    print(f"   False Positive Rate: {results['false_positive_rate']:.1f}%")
    print(f"   True Positive Rate:  {results['true_positive_rate']:.1f}%")
    print(f"   Separation Score:    {results['separation_score']:.1f}%")
    
    print(f"\n🏆 Verdict:")
    verdict_emojis = {
        "READY_FOR_DEPLOYMENT": "✅",
        "ACCEPTABLE_WITH_CAUTION": "⚠️",
        "NEEDS_IMPROVEMENT": "❌"
    }
    emoji = verdict_emojis.get(results['verdict'], "❓")
    print(f"   {emoji} {results['verdict']}")
    
    print("\n" + "=" * 70)


def main():
    """CLI interface for model validation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate Trained ML Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_model.py                      # Run full validation
  python test_model.py --verbose            # Verbose logging
        """
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run validation
    results = validate_model()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if results.get('verdict') == 'READY_FOR_DEPLOYMENT':
        sys.exit(0)
    elif results.get('status') == 'failed':
        sys.exit(1)
    else:
        sys.exit(0)  # Acceptable with caution - still runnable


if __name__ == "__main__":
    main()
