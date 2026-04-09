"""
selector_analyzer.py
Analysis and utility functions for pixel selection.

Provides:
- Capacity calculation
- Coordinate export (JSON/CSV/NPY)
- Selection metrics and statistics
- Format validation
"""

import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Literal
import numpy as np

logger = logging.getLogger(__name__)

def calculate_capacity(
    image_height: int,
    image_width: int,
    lsb_bits: int = 1
) -> Dict[str, Any]:
    """
    Calculate maximum embedding capacity for given image and LSB settings.
    
    Args:
        image_height: Image height in pixels
        image_width: Image width in pixels
        lsb_bits: LSB bits per channel (1-8)
    
    Returns:
        {
            'total_pixels': int,
            'available_bits': int,
            'available_bytes': int,
            'available_kb': float,
            'per_pixel_bits': int,
            'lsb_bits': int
        }
    """
    total_pixels = image_height * image_width
    available_bits = total_pixels * 3 * lsb_bits  # 3 RGB channels
    available_bytes = available_bits // 8
    available_kb = available_bytes / 1024
    per_pixel_bits = 3 * lsb_bits
    
    return {
        'total_pixels': total_pixels,
        'available_bits': available_bits,
        'available_bytes': available_bytes,
        'available_kb': available_kb,
        'per_pixel_bits': per_pixel_bits,
        'lsb_bits': lsb_bits,
        'dimensions': f'{image_width}×{image_height}'
    }

def calculate_batch_capacity(
    image_paths: List[str],
    lsb_bits: int = 1
) -> Dict[str, Any]:
    """
    Calculate total capacity across multiple images.
    
    Args:
        image_paths: List of image file paths
        lsb_bits: LSB bits per channel
    
    Returns:
        {
            'num_images': int,
            'total_pixels': int,
            'total_bits': int,
            'total_bytes': int,
            'total_kb': float,
            'per_image': [...],  # individual capacities
            'uniform_mode_payload': int,  # max message all images can hold
            'packetized_mode_payload': int  # sum of all capacities
        }
    """
    from PIL import Image
    
    per_image_caps = []
    for img_path in image_paths:
        try:
            img = Image.open(img_path).convert('RGB')
            w, h = img.size
            cap = calculate_capacity(h, w, lsb_bits)
            per_image_caps.append({
                'path': img_path,
                'dimensions': f'{w}×{h}',
                'capacity_bytes': cap['available_bytes']
            })
        except Exception as e:
            logger.warning(f"Failed to analyze {img_path}: {e}")
            continue
    
    total_pixels = sum(img['capacity_bytes'] for img in per_image_caps)
    
    # UNIFORM MODE: min capacity (all images must hold same message)
    uniform_capacity = min((img['capacity_bytes'] for img in per_image_caps), default=0)
    
    # PACKETIZED MODE: sum of all capacities (message split across images)
    packetized_capacity = sum(img['capacity_bytes'] for img in per_image_caps)
    
    return {
        'num_images': len(per_image_caps),
        'total_image_bytes': total_pixels,
        'per_image': per_image_caps,
        'uniform_mode_max_bytes': uniform_capacity,
        'packetized_mode_max_bytes': packetized_capacity,
        'recommendation': 'PACKETIZED' if packetized_capacity > uniform_capacity * 3 else 'UNIFORM'
    }

def export_coordinates(
    coordinates: List[Tuple[int, int]],
    output_path: str,
    format: Literal['json', 'csv', 'npy'] = 'json'
) -> str:
    """
    Export selected pixel coordinates to file.
    
    Args:
        coordinates: List of (x, y) tuples
        output_path: Path to save file
        format: Export format ('json', 'csv', or 'npy')
    
    Returns:
        Path to saved file
    
    Raises:
        ValueError: If format not supported
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'json':
        data = {
            'num_pixels': len(coordinates),
            'coordinates': [{'x': int(x), 'y': int(y)} for x, y in coordinates]
        }
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Exported {len(coordinates)} coordinates to {output_path} (JSON)")
    
    elif format == 'csv':
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['x', 'y'])
            for x, y in coordinates:
                writer.writerow([int(x), int(y)])
        logger.info(f"Exported {len(coordinates)} coordinates to {output_path} (CSV)")
    
    elif format == 'npy':
        arr = np.array(coordinates, dtype=np.int32)
        np.save(output_path, arr)
        logger.info(f"Exported {len(coordinates)} coordinates to {output_path} (NPY)")
    
    else:
        raise ValueError(f"Unsupported format: {format}. Must be 'json', 'csv', or 'npy'")
    
    return str(output_path)

def get_selection_metrics(
    coordinates: List[Tuple[int, int]],
    image_shape: Tuple[int, int, int]
) -> Dict[str, Any]:
    """
    Compute statistics about a pixel selection.
    
    Args:
        coordinates: List of (x, y) tuples
        image_shape: (height, width, channels)
    
    Returns:
        {
            'num_pixels': int,
            'coverage_percent': float,
            'bounds': {'x_min', 'x_max', 'y_min', 'y_max'},
            'spatial_distribution': 'uniform' | 'clustered' | 'mixed',
            'duplicates': int
        }
    """
    if not coordinates:
        return {
            'num_pixels': 0,
            'coverage_percent': 0.0,
            'bounds': None,
            'spatial_distribution': 'empty',
            'duplicates': 0
        }
    
    h, w, _ = image_shape
    total_pixels = h * w
    
    # Check duplicates
    coords_set = set(coordinates)
    duplicates = len(coordinates) - len(coords_set)
    
    # Compute bounds
    xs = [x for x, y in coordinates]
    ys = [y for x, y in coordinates]
    bounds = {
        'x_min': min(xs),
        'x_max': max(xs),
        'y_min': min(ys),
        'y_max': max(ys)
    }
    
    # Analyze spatial distribution (simplified)
    coverage_x = (bounds['x_max'] - bounds['x_min']) / w if w > 0 else 0
    coverage_y = (bounds['y_max'] - bounds['y_min']) / h if h > 0 else 0
    avg_coverage = (coverage_x + coverage_y) / 2
    
    if avg_coverage > 0.8:
        distribution = 'uniform'
    elif avg_coverage < 0.3:
        distribution = 'clustered'
    else:
        distribution = 'mixed'
    
    return {
        'num_pixels': len(coordinates),
        'num_unique': len(coords_set),
        'coverage_percent': (len(coords_set) / total_pixels) * 100,
        'bounds': bounds,
        'spatial_coverage': avg_coverage,
        'spatial_distribution': distribution,
        'duplicates': duplicates
    }

def validate_coordinates(
    coordinates: List[Tuple[int, int]],
    image_shape: Tuple[int, int, int]
) -> bool:
    """
    Validate that all coordinates are within image bounds and unique.
    
    Args:
        coordinates: List of (x, y) tuples
        image_shape: (height, width, channels)
    
    Returns:
        True if valid, raises ValueError otherwise
    """
    h, w, _ = image_shape
    
    for i, (x, y) in enumerate(coordinates):
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(f"Coordinate {i} ({x}, {y}) out of bounds for {w}×{h} image")
    
    coords_set = set(coordinates)
    if len(coords_set) < len(coordinates):
        raise ValueError(f"Found {len(coordinates) - len(coords_set)} duplicate coordinates")
    
    return True