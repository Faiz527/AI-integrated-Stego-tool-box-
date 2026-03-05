"""
Module 6 — Error Correction Code (ECC)
========================================
Reed-Solomon error correction for steganographic messages.

Public API:
- add_redundancy() — Add ECC to message
- recover_redundancy() — Recover from errors
- show_redundancy_section() — UI components
- encode_message_with_ecc() — Encode + ECC
- decode_message_with_ecc_recovery() — Decode + ECC recovery
"""

from .rs_wrapper import (
    add_redundancy,
    recover_redundancy,
    estimate_overhead_rs,
    estimate_overhead_replication,
    _HAS_RS
)
from .capacity_checker import can_fit_payload, pretty_report
from .ui_section import (
    show_ecc_encode_section,
    show_ecc_decode_section,
    show_redundancy_section,
    encode_message_with_ecc,
    decode_message_with_ecc_recovery,
    validate_capacity,
    check_capacity_and_warn,
    get_ecc_config
)

__all__ = [
    'add_redundancy',
    'recover_redundancy',
    'estimate_overhead_rs',
    'estimate_overhead_replication',
    'can_fit_payload',
    'pretty_report',
    'show_ecc_encode_section',
    'show_ecc_decode_section',
    'show_redundancy_section',
    'encode_message_with_ecc',
    'decode_message_with_ecc_recovery',
    'validate_capacity',
    'check_capacity_and_warn',
    'get_ecc_config',
    '_HAS_RS'
]