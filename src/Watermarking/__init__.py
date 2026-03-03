"""
Watermarking Module
===================
Provides watermarking functionality for image protection.
"""

from .watermark import apply_text_watermark, apply_lsb_watermark, apply_alpha_blending_watermark
from .ui_section import show_watermarking_section

__all__ = [
    'apply_text_watermark',
    'apply_lsb_watermark', 
    'apply_alpha_blending_watermark',
    'show_watermarking_section'
]