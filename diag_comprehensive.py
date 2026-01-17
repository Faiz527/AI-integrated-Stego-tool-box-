"""
diag_comprehensive.py
Enhanced diagnostic tool with flexible parameters (no hardcoding)
"""
from pathlib import Path
from PIL import Image
import numpy as np
import argparse
import sys

# Module imports
from stegotool.modules.module3_pixel_selector.selector_baseline import select_pixels
from stegotool.modules.module6_redundancy.capacity_checker import image_capacity_bytes, can_fit_payload


def find_dev_images(search_from=None):
    """
    Intelligently find dev_images directory by searching upward from current location
    or from a specified path.
    """
    if search_from is None:
        search_from = Path.cwd()
    
    # Try common locations
    candidates = [
        Path.cwd() / "stegotool" / "data" / "dev_images",
        Path(__file__).parent / "stegotool" / "data" / "dev_images",
        (Path.cwd().parent if Path.cwd().name == "stegotool" else Path.cwd()) / "stegotool" / "data" / "dev_images",
    ]
    
    for path in candidates:
        if path.exists() and list(path.glob("*.png")) + list(path.glob("*.jpg")):
            return path
    
    raise FileNotFoundError(
        f"❌ Could not find stegotool/data/dev_images directory.\n"
        f"   Searched in: {[str(p) for p in candidates]}\n"
        f"   Run 'python make_demo_images.py' first."
    )


def analyze_images(img_dir, payload_bytes=43, nsym=32, patch_size=5, lsb_bits=1, verbose=False):
    """
    Analyze all images in directory.
    
    Args:
        img_dir: Path to images
        payload_bytes: Payload size in bytes (not bits!)
        nsym: Reed-Solomon parity symbols
        patch_size: Neighborhood size for pixel scoring
        lsb_bits: LSB bits per channel
        verbose: Print detailed info
    """
    imgs = sorted(list(img_dir.glob("*.png")) + list(img_dir.glob("*.jpg")))
    
    if not imgs:
        print(f"❌ No images found in {img_dir}")
        return
    
    print(f"\n{'='*80}")
    print(f"ANALYZING {len(imgs)} IMAGES")
    print(f"{'='*80}")
    print(f"Parameters:")
    print(f"  • Payload size: {payload_bytes} bytes")
    print(f"  • Reed-Solomon parity: {nsym} symbols")
    print(f"  • Patch size: {patch_size}x{patch_size}")
    print(f"  • LSB bits per channel: {lsb_bits}")
    print(f"  • Total capacity per pixel: {3 * lsb_bits} bits")
    print(f"\n{'='*80}\n")
    
    total_pixels_needed = 0
    results = []
    
    for img_path in imgs:
        im = Image.open(img_path).convert("RGB")
        arr = np.array(im)
        h, w, _ = arr.shape
        
        # Calculate requirements
        payload_bits = payload_bytes * 8
        ecc_payload_bytes = payload_bytes + nsym
        ecc_payload_bits = ecc_payload_bytes * 8
        
        # Get capacity
        total_capacity = image_capacity_bytes(w, h, channels=3, lsb_bits=lsb_bits)
        pixels_needed = int(np.ceil(ecc_payload_bits / (3 * lsb_bits)))
        capacity_ok = total_capacity >= ecc_payload_bytes
        
        # Select pixels
        ranked = select_pixels(arr, payload_bits=ecc_payload_bits, patch_size=patch_size, lsb_bits=lsb_bits)
        
        # Group analysis
        group_size = 64
        num_groups = len(ranked) // group_size
        
        # Capacity check with header
        fits, available = can_fit_payload((w, h), payload_bytes, nsym, channels=3, lsb_bits=lsb_bits)
        
        result = {
            'name': img_path.name,
            'size': f"{w}×{h}",
            'pixels_total': w * h,
            'capacity_total_bytes': total_capacity,
            'pixels_needed': pixels_needed,
            'pixels_ranked': len(ranked),
            'capacity_ok': capacity_ok,
            'fits_with_header': fits,
            'available_after_header': available,
            'num_groups_of_64': num_groups,
        }
        results.append(result)
        total_pixels_needed += pixels_needed
        
        # Print summary
        status = "✓" if fits else "✗"
        print(f"{status} {img_path.name}")
        print(f"   Size: {w}×{h} pixels ({w*h:,} total)")
        print(f"   Capacity: {total_capacity:,} bytes total, {available} bytes available (after {42}B header)")
        print(f"   Pixels ranked: {len(ranked)}")
        print(f"   Pixels needed for payload: {pixels_needed}")
        print(f"   Groups of {group_size}: {num_groups}")
        print(f"   Fits payload+ECC: {fits}")
        
        if verbose:
            print(f"   Ranked pixels (first 10): {ranked[:10]}")
        print()
    
    # Summary
    print(f"{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total images: {len(results)}")
    print(f"Total pixels needed (sum): {total_pixels_needed:,}")
    print(f"Average pixels per image: {total_pixels_needed // len(results) if results else 0}")
    fits_count = sum(1 for r in results if r['fits_with_header'])
    print(f"Images that fit payload: {fits_count}/{len(results)}")
    
    return results


def capacity_breakdown(width, height, payload_bytes, nsym, lsb_bits=1):
    """Show capacity breakdown for an image size."""
    print(f"\n{'='*80}")
    print(f"CAPACITY BREAKDOWN: {width}×{height} image")
    print(f"{'='*80}")
    
    total_pixels = width * height
    capacity_bits_lsb1 = total_pixels * 3 * 1
    capacity_bits_lsb2 = total_pixels * 3 * 2
    capacity_bits_lsb4 = total_pixels * 3 * 4
    capacity_bits_lsb8 = total_pixels * 3 * 8
    
    payload_bits = payload_bytes * 8
    ecc_bits = (payload_bytes + nsym) * 8
    
    print(f"\nImage capacity:")
    print(f"  LSB bits=1: {capacity_bits_lsb1:,} bits = {capacity_bits_lsb1//8:,} bytes")
    print(f"  LSB bits=2: {capacity_bits_lsb2:,} bits = {capacity_bits_lsb2//8:,} bytes")
    print(f"  LSB bits=4: {capacity_bits_lsb4:,} bits = {capacity_bits_lsb4//8:,} bytes")
    print(f"  LSB bits=8: {capacity_bits_lsb8:,} bits = {capacity_bits_lsb8//8:,} bytes")
    
    print(f"\nPayload requirements:")
    print(f"  Payload: {payload_bytes} bytes = {payload_bits:,} bits")
    print(f"  + ECC (nsym={nsym}): {payload_bytes + nsym} bytes = {ecc_bits:,} bits")
    print(f"  Total required: {ecc_bits:,} bits = {(ecc_bits+7)//8} bytes")
    
    print(f"\nPixels needed (LSB bits=1): {int(np.ceil(ecc_bits / 3))}")
    print(f"Pixels needed (LSB bits=2): {int(np.ceil(ecc_bits / 6))}")
    print(f"Pixels needed (LSB bits=4): {int(np.ceil(ecc_bits / 12))}")
    
    fits_1, avail_1 = can_fit_payload((width, height), payload_bytes, nsym, lsb_bits=1)
    fits_2, avail_2 = can_fit_payload((width, height), payload_bytes, nsym, lsb_bits=2)
    
    print(f"\nFits with LSB=1: {fits_1} ({avail_1} bytes available)")
    print(f"Fits with LSB=2: {fits_2} ({avail_2} bytes available)")


def main():
    parser = argparse.ArgumentParser(description="Comprehensive steganography diagnostic")
    parser.add_argument("--payload", type=int, default=43, help="Payload size in bytes (default: 43)")
    parser.add_argument("--nsym", type=int, default=32, help="Reed-Solomon parity symbols (default: 32)")
    parser.add_argument("--patch-size", type=int, default=5, help="Patch size for scoring (default: 5)")
    parser.add_argument("--lsb-bits", type=int, default=1, help="LSB bits per channel (default: 1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--capacity-only", action="store_true", help="Show capacity breakdown only")
    parser.add_argument("--width", type=int, default=512, help="Width for capacity breakdown (default: 512)")
    parser.add_argument("--height", type=int, default=384, help="Height for capacity breakdown (default: 384)")
    
    args = parser.parse_args()
    
    try:
        img_dir = find_dev_images()
        print(f"\n✓ Found images at: {img_dir}\n")
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    
    if args.capacity_only:
        capacity_breakdown(args.width, args.height, args.payload, args.nsym, args.lsb_bits)
    else:
        analyze_images(img_dir, args.payload, args.nsym, args.patch_size, args.lsb_bits, args.verbose)


if __name__ == "__main__":
    main()