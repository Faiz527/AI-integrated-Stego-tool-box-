"""
capacity_checker.py

Helpers to compute whether payload (after ECC) will fit into an image
given the number of LSB bits used per channel.
"""

from typing import Tuple

def image_capacity_bytes(width: int, height: int, channels: int = 3, lsb_bits: int = 1) -> int:
    """
    Return capacity in BYTES.
    """
    if width <= 0 or height <= 0 or channels <= 0 or lsb_bits <= 0:
        raise ValueError("Invalid image params")
    capacity_bits = width * height * channels * lsb_bits
    return capacity_bits // 8

def can_fit_payload(image_size: Tuple[int,int], payload_len_bytes: int, nsym: int,
                    channels: int = 3, lsb_bits: int = 1, reserve_header_bytes: int = 42) -> Tuple[bool, int]:
    """
    Returns (fits, available_bytes_for_payload).
    """
    w, h = image_size
    cap = image_capacity_bytes(w, h, channels, lsb_bits)
    available = cap - reserve_header_bytes
    required = payload_len_bytes + nsym
    return (required <= available, available)

def pretty_report(image_size: Tuple[int,int], payload_len_bytes: int, nsym: int,
                  channels: int = 3, lsb_bits: int = 1, reserve_header_bytes: int = 42) -> str:
    fits, available = can_fit_payload(image_size, payload_len_bytes, nsym, channels, lsb_bits, reserve_header_bytes)
    req = payload_len_bytes + nsym
    return (
        f"Image: {image_size[0]}x{image_size[1]}, channels={channels}, lsb_bits={lsb_bits}\n"
        f"Capacity (bytes): {available + reserve_header_bytes} total, {available} available after header\n"
        f"Payload required (payload+nsym): {req} bytes (payload={payload_len_bytes}, nsym={nsym})\n"
        f"Fits: {fits}"
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--w", type=int, default=800)
    parser.add_argument("--h", type=int, default=600)
    parser.add_argument("--payload", type=int, default=256)
    parser.add_argument("--nsym", type=int, default=32)
    parser.add_argument("--lsb", type=int, default=1)
    args = parser.parse_args()
    print(pretty_report((args.w, args.h), args.payload, args.nsym, 3, args.lsb))