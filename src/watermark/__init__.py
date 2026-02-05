"""
Watermark Module
================
Contains watermarking functions for visible and invisible watermarks.
"""

from .watermark import (
    apply_text_watermark,
    apply_lsb_watermark,
    apply_alpha_blending_watermark
)

__all__ = [
    'apply_text_watermark',
    'apply_lsb_watermark', 
    'apply_alpha_blending_watermark'
]