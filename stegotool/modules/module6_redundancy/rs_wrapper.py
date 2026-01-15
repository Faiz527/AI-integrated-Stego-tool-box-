"""
rs_wrapper.py
Module 6 — Noise & Compression Resistance Layer

Primary: Reed-Solomon using `reedsolo` (recommended).
Fallback: Triple-replication + majority-vote decoder (simple fallback).

Public API:
- add_redundancy(payload: bytes, nsym: int = 32) -> bytes
- recover_redundancy(data: bytes, nsym: int = 32) -> bytes
- estimate_overhead_rs(payload_len: int, nsym: int) -> int
- estimate_overhead_replication(payload_len: int, factor: int) -> int
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Try import reedsolo
try:
    from reedsolo import RSCodec, ReedSolomonError  # type: ignore
    _HAS_RS = True
except Exception:
    RSCodec = None
    ReedSolomonError = Exception
    _HAS_RS = False

# -----------------------
# Public API
# -----------------------
def add_redundancy(payload: bytes, nsym: int = 32) -> bytes:
    """
    Add redundancy to payload.
    If reedsolo is available: returns RS encoded bytes (payload + parity).
    Else: returns triplicated payload for fallback.

    Args:
        payload: original bytes
        nsym: number of parity bytes for reed-solomon (ignored by fallback)

    Returns:
        bytes: redundancy-augmented payload to be embedded
    """
    if _HAS_RS:
        return _rs_encode(payload, nsym)
    else:
        logger.warning(
            "reedsolo not available — using triple-replication fallback ECC. Install reedsolo for robust ECC."
        )
        return _replication_encode(payload, factor=3)


def recover_redundancy(data: bytes, nsym: int = 32) -> bytes:
    """
    Attempt to recover original payload from redundancy-augmented data.

    Args:
        data: received bytes (RS-coded or triplicated)
        nsym: parity bytes expected (for RS)

    Returns:
        original payload bytes on success

    Raises:
        ValueError if recovery fails.
    """
    if _HAS_RS:
        return _rs_decode(data, nsym)
    else:
        return _replication_decode(data, factor=3)


# -----------------------
# Reed-Solomon implementation (using reedsolo)
# -----------------------
def _rs_encode(payload: bytes, nsym: int) -> bytes:
    """
    Reed-Solomon encode payload -> returns payload_with_parity
    Uses RSCodec from reedsolo.
    """
    if not _HAS_RS:
        raise RuntimeError("reedsolo not available")
    if nsym <= 0:
        raise ValueError("nsym must be > 0 for RS encoding")
    rsc = RSCodec(nsym)
    # rsc.encode returns bytes(payload + parity)
    return rsc.encode(payload)


def _rs_decode(data: bytes, nsym: int) -> bytes:
    """
    Decode RS encoded data. Returns original payload bytes or raises ValueError on fail.
    """
    if not _HAS_RS:
        raise RuntimeError("reedsolo not available")
    rsc = RSCodec(nsym)
    try:
        decoded = rsc.decode(data)
        # reedsolo.decode can return (message, ecc) or bytes depending on version
        if isinstance(decoded, tuple):
            return decoded[0]
        elif isinstance(decoded, (bytes, bytearray)):
            return bytes(decoded)
        else:
            raise ValueError("Unexpected decode result type from reedsolo")
    except ReedSolomonError as e:
        raise ValueError(f"Reed-Solomon decode failed: {e}")


# -----------------------
# Simple fallback: replication + majority vote
# -----------------------
def _replication_encode(payload: bytes, factor: int = 3) -> bytes:
    """
    Naive fallback ECC: replicate each byte `factor` times.
    """
    if factor < 1:
        raise ValueError("factor must be >= 1")
    if factor == 1:
        return payload
    out = bytearray()
    for b in payload:
        out.extend(bytes([b]) * factor)
    return bytes(out)


def _replication_decode(data: bytes, factor: int = 3) -> bytes:
    """
    Decode replicated data using majority vote per byte group.
    Raises ValueError if length not multiple of factor.
    """
    if factor < 1:
        raise ValueError("factor must be >= 1")
    if factor == 1:
        return data
    if len(data) % factor != 0:
        raise ValueError("replication decode: data length not multiple of replication factor")
    out = bytearray()
    for i in range(0, len(data), factor):
        chunk = data[i:i+factor]
        counts = {}
        for b in chunk:
            counts[b] = counts.get(b, 0) + 1
        b, cnt = max(counts.items(), key=lambda kv: kv[1])
        out.append(b)
    return bytes(out)


# -----------------------
# Utility helpers
# -----------------------
def estimate_overhead_rs(payload_len: int, nsym: int) -> int:
    """
    Return number of bytes after RS encoding (approx).
    For RSCodec, encoded length = payload_len + nsym (parity).
    """
    return payload_len + nsym


def estimate_overhead_replication(payload_len: int, factor: int) -> int:
    return payload_len * factor


# -----------------------
# CLI quick test
# -----------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test RS wrapper encode/decode (Module 6)")
    parser.add_argument("--nsym", type=int, default=32, help="RS parity bytes (ignored in fallback)")
    parser.add_argument("--text", type=str, default="hello stego", help="text to encode")
    args = parser.parse_args()

    payload = args.text.encode("utf-8")
    enc = add_redundancy(payload, nsym=args.nsym)
    print("Encoded length:", len(enc))
    try:
        dec = recover_redundancy(enc, nsym=args.nsym)
        print("Decoded OK:", dec.decode())
    except Exception as e:
        print("Decode failed:", e)
