"""
Batch Encoder Module
====================
Encodes secret messages into multiple images using three methods:
LSB, Hybrid DCT, and Haar DWT.
"""

import os
import time
import logging
from pathlib import Path
from PIL import Image
from datetime import datetime

from ..stego import encode_image, encode_dct, encode_dwt
from ..encryption.encryption import encrypt_message

logger = logging.getLogger(__name__)

DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output' / 'encoded'


def batch_encode_images(
    image_paths: list,
    secret_message: str,
    methods: list = None,
    encrypt_password: str = None,
    encrypt: bool = False,
    batch_id: str = None
) -> dict:
    """
    Encode secret message into multiple images using selected methods.
    
    Args:
        image_paths (list): List of image file paths
        secret_message (str): Message to encode
        methods (list): Methods to use ['LSB', 'DCT', 'DWT', 'Hybrid DCT', 'Hybrid DWT', 'all']
        encrypt_password (str): Password for encryption
        encrypt (bool): Whether to encrypt message
        batch_id (str): Unique batch identifier for output folder
    
    Returns:
        dict: {
            'success': bool,
            'total_processed': int,
            'total_failed': int,
            'methods_used': list,
            'results': {
                'LSB': [...],
                'DCT': [...],
                'DWT': [...]
            },
            'timings': {...},
            'message': str,
            'output_path': str
        }
    """
    # Normalize method names (handle "Hybrid DCT" -> "DCT", etc.)
    normalized_methods = []
    if methods is None or 'all' in methods:
        normalized_methods = ['LSB', 'DCT', 'DWT']
    else:
        method_mapping = {
            'Hybrid DCT': 'DCT',
            'Hybrid DWT': 'DWT',
            'DCT': 'DCT',
            'DWT': 'DWT',
            'LSB': 'LSB'
        }
        for m in methods:
            normalized = method_mapping.get(m, m)
            if normalized not in normalized_methods:
                normalized_methods.append(normalized)
    
    methods = normalized_methods
    
    # Use batch-specific output directory
    if batch_id:
        DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output' / 'batches' / batch_id / 'encoded'
    else:
        DATA_OUTPUT_PATH = Path(__file__).parent.parent.parent / 'data' / 'output' / 'encoded'
    
    result = {
        'success': True,
        'total_processed': 0,
        'total_failed': 0,
        'methods_used': methods,
        'results': {method: [] for method in methods},
        'timings': {},
        'message': '',
        'output_path': str(DATA_OUTPUT_PATH)
    }
    
    # Prepare message (encrypt if requested)
    if encrypt and encrypt_password:
        try:
            message_to_encode = encrypt_message(secret_message, encrypt_password)
            logger.info(f"Message encrypted with password")
        except Exception as e:
            result['message'] = f"Error Encryption failed: {str(e)}"
            result['success'] = False
            return result
    else:
        message_to_encode = secret_message
    
    # Create output directories
    for method in methods:
        method_dir = DATA_OUTPUT_PATH / method
        os.makedirs(method_dir, exist_ok=True)
    
    # Process each image
    for idx, img_path in enumerate(image_paths, 1):
        try:
            img = Image.open(img_path)
            img_path_obj = Path(img_path)
            filename = img_path_obj.stem
            original_extension = img_path_obj.suffix.lower()  # Get original extension (.jpg, .png, etc.)
            
            logger.info(f"Processing {idx}/{len(image_paths)}: {filename}")
            
            # Encode with each method
            for method in methods:
                start_time = time.time()
                
                try:
                    logger.debug(f"  {method}: Starting encoding...")
                    
                    if method == 'LSB':
                        logger.debug(f"  {method}: Calling encode_image()")
                        encoded_img = encode_image(img, message_to_encode)
                    elif method == 'DCT':
                        logger.debug(f"  {method}: Calling encode_dct()")
                        encoded_img = encode_dct(img, message_to_encode)
                    elif method == 'DWT':
                        logger.debug(f"  {method}: Calling encode_dwt()")
                        encoded_img = encode_dwt(img, message_to_encode)
                    else:
                        logger.warning(f"  {method}: Unknown method")
                        continue
                    
                    # Save encoded image with appropriate format
                    output_dir = DATA_OUTPUT_PATH / method
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # For frequency domain methods (DCT, DWT), use PNG to preserve coefficients
                    # For LSB, original format is fine
                    if method in ['DCT', 'DWT']:
                        # Always use PNG for frequency domain methods to avoid lossy compression
                        output_extension = '.png'
                        pil_format = 'PNG'
                    else:
                        # For LSB, preserve original format
                        output_extension = original_extension if original_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'] else '.png'
                        pil_format = output_extension.lstrip('.').upper()
                        if pil_format == 'JPG':
                            pil_format = 'JPEG'
                    
                    output_path = output_dir / f"{filename}_{method}{output_extension}"
                    
                    # Save with appropriate format
                    encoded_img.save(output_path, pil_format)
                    
                    elapsed_time = time.time() - start_time
                    
                    result['results'][method].append({
                        'filename': filename,
                        'input_path': img_path,
                        'output_path': str(output_path),
                        'size': img.size,
                        'encoding_time': round(elapsed_time, 3),
                        'status': 'Success'
                    })
                    
                    logger.info(f"  {method}: Encoded in {elapsed_time:.3f}s - {output_path}")
                    result['total_processed'] += 1
                
                except ValueError as e:
                    result['results'][method].append({
                        'filename': filename,
                        'status': f'Failed: {str(e)}'
                    })
                    result['total_failed'] += 1
                    logger.error(f"  {method}: ValueError - {str(e)}")
                
                except Exception as e:
                    result['results'][method].append({
                        'filename': filename,
                        'status': f'Error: {str(e)}'
                    })
                    result['total_failed'] += 1
                    logger.error(f"  {method}: Exception - {str(e)}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Failed to process image {img_path}: {str(e)}", exc_info=True)
            for method in methods:
                result['results'][method].append({
                    'filename': Path(img_path).stem,
                    'status': f'Error: {str(e)}'
                })
            result['total_failed'] += 1
    
    result['message'] = f"Processed {result['total_processed']} images successfully"
    logger.info(result['message'])
    
    return result


def get_encoding_capacity(image_path: str) -> dict:
    """
    Calculate message capacity for each method.
    
    Args:
        image_path (str): Path to image
    
    Returns:
        dict: Capacity information for each method
    """
    try:
        img = Image.open(image_path)
        width, height = img.size
        pixels = width * height
        
        return {
            'LSB': {
                'bits': pixels * 3,
                'bytes': (pixels * 3) // 8,
                'kb': ((pixels * 3) // 8) / 1024
            },
            'DCT': {
                'bits': pixels,
                'bytes': pixels // 8,
                'kb': (pixels // 8) / 1024
            },
            'DWT': {
                'bits': pixels // 4 * 3,
                'bytes': (pixels // 4 * 3) // 8,
                'kb': ((pixels // 4 * 3) // 8) / 1024
            }
        }
    except Exception as e:
        logger.error(f"Capacity calculation failed: {str(e)}")
        return {}
