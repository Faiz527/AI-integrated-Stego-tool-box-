"""
Module 3: Pixel Selector
Advanced heuristic-based pixel selection for steganography.

Main API:
    select_pixels() - Select pixels for embedding
    
Analysis tools:
    calculate_capacity() - How many bits fit in image
    export_coordinates() - Save selected pixels
    
Optimization:
    super_fast_select_pixels() - Auto-optimized for 4K
"""

from .selector_baseline import select_pixels
from .selector_analyzer import (
    calculate_capacity,
    calculate_batch_capacity,
    export_coordinates,
    get_selection_metrics,
    validate_coordinates
)
from .selector_optimizer import (
    super_fast_select_pixels,
    benchmark_selection,
    recommend_settings
)

__version__ = "2.0.0"  # Updated version with fixes
__all__ = [
    # Core API
    "select_pixels",
    # Analysis
    "calculate_capacity",
    "calculate_batch_capacity",
    "export_coordinates",
    "get_selection_metrics",
    "validate_coordinates",
    # Optimization
    "super_fast_select_pixels",
    "benchmark_selection",
    "recommend_settings"
]
