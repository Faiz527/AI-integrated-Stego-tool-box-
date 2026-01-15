"""
Steganography Test Suite
=========================
Tests all three steganography methods: LSB, Hybrid DCT, and Hybrid DWT
Run from project root: python test_steganography.py
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from src.stego.lsb_steganography import encode_image, decode_image
from src.stego.dct_steganography import encode_dct, decode_dct
from src.stego.dwt_steganography import encode_dct_dwt, decode_dct_dwt


def create_test_image(width=800, height=800, filename="test_image.png"):
    """Create a test image with varied content"""
    print(f"📸 Creating test image: {width}×{height}")
    
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add gradient
    for y in range(height):
        color_value = int((y / height) * 255)
        draw.line([(0, y), (width, y)], fill=(color_value, color_value, color_value))
    
    # Add shapes
    draw.rectangle([50, 50, 150, 150], fill='red', outline='black', width=2)
    draw.ellipse([200, 50, 300, 150], fill='blue', outline='black', width=2)
    draw.polygon([(350, 50), (450, 150), (350, 150)], fill='green', outline='black')
    
    img.save(filename)
    print(f"✅ Test image saved: {filename}")
    return img


def test_method(method_name, encode_func, decode_func, test_messages):
    """Test a single steganography method"""
    print(f"\n{'='*70}")
    print(f"Testing: {method_name}")
    print(f"{'='*70}")
    
    img = create_test_image()
    passed = 0
    failed = 0
    
    for msg in test_messages:
        try:
            # Encode
            encoded_img = encode_func(img, msg)
            encoded_img.save("temp_encoded.png")
            
            # Decode
            decoded_msg = decode_func(encoded_img)
            
            # Verify
            if decoded_msg == msg:
                print(f"✅ PASS: '{msg}' (length: {len(msg)})")
                passed += 1
            else:
                print(f"❌ FAIL: Expected '{msg}', got '{decoded_msg}'")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
    
    print(f"\n{method_name} Results: {passed}/{passed+failed} passed")
    return passed, failed


def main():
    print("\n" + "🧪 "*35)
    print("STEGANOGRAPHY TEST SUITE")
    print("🧪 "*35)
    
    test_messages = [
        "Hi",
        "Hello",
        "Hello World!",
        "Test with numbers: 1234567890",
        "Special chars: !@#$%^&*()",
    ]
    
    total_passed = 0
    total_failed = 0
    
    # Test LSB
    p, f = test_method("LSB (Spatial Domain)", 
                       lambda img, msg: encode_image(img, msg, "None"),
                       decode_image, 
                       test_messages)
    total_passed += p
    total_failed += f
    
    # Test Hybrid DCT
    p, f = test_method("Hybrid DCT (Y-Channel LSB)", 
                       encode_dct, 
                       decode_dct, 
                       test_messages)
    total_passed += p
    total_failed += f
    
    # Test Hybrid DWT
    p, f = test_method("Hybrid DWT (Haar Wavelet)", 
                       encode_dct_dwt, 
                       decode_dct_dwt, 
                       test_messages)
    total_passed += p
    total_failed += f
    
    # Summary
    print(f"\n{'='*70}")
    print(f"TOTAL RESULTS")
    print(f"{'='*70}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed == 0:
        print(f"\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)