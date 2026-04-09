"""
selector_utils.py
Utility functions for Module 3: entropy, patch extraction, scoring helpers.
"""

from typing import Tuple
import numpy as np
import cv2

def get_gray(image_rgb: np.ndarray) -> np.ndarray:
    """Convert RGB numpy image to grayscale (uint8)."""
    if image_rgb.ndim == 2:
        return image_rgb
    return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)

def compute_laplacian_map(gray: np.ndarray) -> np.ndarray:
    """
    Compute Laplacian map for entire image (vectorized).
    Returns: HxW array of Laplacian variance values (float64).
    """
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return lap.astype(np.float64)

def compute_variance_map(gray: np.ndarray, patch_size: int = 3) -> np.ndarray:
    """
    Compute local variance map (vectorized using sliding window).
    Returns: HxW array of local variance values.
    """
    gray_float = gray.astype(np.float32)
    
    # Compute mean and squared mean efficiently using filter2D
    kernel = np.ones((patch_size, patch_size), dtype=np.float32) / (patch_size * patch_size)
    mean = cv2.filter2D(gray_float, -1, kernel)
    sq_mean = cv2.filter2D(gray_float**2, -1, kernel)
    
    var_map = sq_mean - mean**2
    return np.maximum(var_map, 0).astype(np.float32)

def compute_entropy_map_fast(gray: np.ndarray, patch_size: int = 3) -> np.ndarray:
    """
    Compute entropy approximation map (fast version using edge detection).
    For very fast computation, use Sobel edges as proxy for entropy.
    Returns: HxW array of entropy approximation values.
    """
    # Use edge detection as fast approximation to entropy
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.sqrt(sobelx**2 + sobely**2)
    
    # Smooth edges to get entropy-like map
    entropy_map = cv2.GaussianBlur(edges, (patch_size, patch_size), 0)
    return entropy_map.astype(np.float32)
