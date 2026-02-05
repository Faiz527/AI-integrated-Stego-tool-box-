import pytest
from stegotool.modules.module6_redundancy.rs_wrapper import (
    add_redundancy,
    recover_redundancy,
    _HAS_RS,
    _replication_encode,
    _replication_decode
)

def test_roundtrip_basic():
    payload = b"this is a test message"
    enc = add_redundancy(payload, nsym=16)
    dec = recover_redundancy(enc, nsym=16)
    assert dec == payload

def test_replication_fallback():
    payload = b"\x00\xFF\x11\x22"
    enc = _replication_encode(payload, factor=3)
    corrupted = bytearray(enc)
    corrupted[1] ^= 0x01
    corrupted[7] ^= 0x03
    dec = _replication_decode(bytes(corrupted), factor=3)
    assert dec == payload

@pytest.mark.skipif(_HAS_RS, reason="skip replication length error test when reedsolo available")
def test_replication_length_error():
    payload = b"A"
    enc = _replication_encode(payload, factor=3)
    with pytest.raises(ValueError):
        _replication_decode(enc + b"\x00", factor=3)
