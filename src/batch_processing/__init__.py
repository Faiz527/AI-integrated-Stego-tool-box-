"""
Batch Processing Module
=======================
Handles bulk steganography operations on multiple images.
Supports ZIP uploads, batch encoding, and comprehensive reporting.
"""

from .zip_handler import extract_zip, validate_images, cleanup_extracted
from .batch_encoder import batch_encode_images, get_encoding_capacity
from .report_generator import generate_batch_report, generate_csv_report, export_summary
from .controller import BatchProcessingController

__all__ = [
    'extract_zip',
    'validate_images',
    'cleanup_extracted',
    'batch_encode_images',
    'get_encoding_capacity',
    'generate_batch_report',
    'generate_csv_report',
    'export_summary',
    'BatchProcessingController'
]
