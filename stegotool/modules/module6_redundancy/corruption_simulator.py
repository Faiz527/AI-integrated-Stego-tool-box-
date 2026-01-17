"""
corruption_simulator.py

Utilities to simulate common corruptions for testing ECC:
- random_byte_flips: flip N random bytes in a bytes buffer
- flip_bits_in_bytes: flip bits by absolute bit positions
- jpg recompression helpers (Pillow)
"""
from typing import Tuple
import random
import io

try:
    from PIL import Image
    _HAS_PIL = True
except Exception:
    Image = None
    _HAS_PIL = False

def random_byte_flips(data: bytes, n_flips: int, seed: int = 0) -> bytes:
    """
    Randomly flip one random bit in `n_flips` distinct bytes.
    """
    if n_flips <= 0:
        return data
    random.seed(seed)
    b = bytearray(data)
    L = len(b)
    if L == 0:
        return data
    positions = random.sample(range(L), min(n_flips, L))
    for pos in positions:
        bit = 1 << random.randint(0,7)
        b[pos] ^= bit
    return bytes(b)

def flip_bits_in_bytes(data: bytes, bit_positions: Tuple[int, ...]) -> bytes:
    """
    Flip specific absolute bit positions.
    """
    if not data:
        return data
    b = bytearray(data)
    nbits = len(b) * 8
    for bitpos in bit_positions:
        if bitpos < 0 or bitpos >= nbits:
            continue
        byte_idx = bitpos // 8
        inner = bitpos % 8
        b[byte_idx] ^= (1 << inner)
    return bytes(b)

def jpeg_recompress_image_bytes(pil_image, quality: int = 80) -> bytes:
    """
    Recompress PIL.Image to JPEG in-memory and return new bytes.
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow not available")
    buf = io.BytesIO()
    pil_image.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()

def recompress_and_reload(pil_image, quality: int = 80):
    """
    Recompress and return a reloaded PIL.Image object (RGB).
    """
    if not _HAS_PIL:
        raise RuntimeError("Pillow not available")
    jpeg_bytes = jpeg_recompress_image_bytes(pil_image, quality=quality)
    return Image.open(io.BytesIO(jpeg_bytes)).convert("RGB")
