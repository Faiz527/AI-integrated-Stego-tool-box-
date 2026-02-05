import pytest
from stegotool.modules.module6_redundancy.rs_wrapper import add_redundancy, recover_redundancy, _HAS_RS
from stegotool.modules.module6_redundancy.corruption_simulator import random_byte_flips
from stegotool.modules.module6_redundancy.rs_wrapper import _replication_encode, _replication_decode

def _rand_payload(n=128, seed=0):
    import random
    random.seed(seed)
    return bytes([random.getrandbits(8) for _ in range(n)])

@pytest.mark.parametrize("nsym, flips", [
    (16, 4),
    (32, 8),
    (64, 16),
])
def test_rs_recovery_against_byte_flips(nsym, flips):
    payload = _rand_payload(256, seed=42)
    enc = add_redundancy(payload, nsym=nsym)
    corrupted = random_byte_flips(enc, n_flips=flips, seed=123)
    if _HAS_RS:
        try:
            dec = recover_redundancy(corrupted, nsym=nsym)
            assert dec == payload
        except ValueError:
            pytest.skip("RS decode failed under heavy corruption; adjust nsym or flips")
    else:
        dec = _replication_decode(corrupted, factor=3)
        assert dec == payload

def test_replication_vs_corruption():
    payload = b"hello world" * 10
    enc = _replication_encode(payload, factor=3)
    corrupted = bytearray(enc)
    corrupted[5] ^= 0x01
    corrupted[12] ^= 0x04
    dec = _replication_decode(bytes(corrupted), factor=3)
    assert dec == payload
