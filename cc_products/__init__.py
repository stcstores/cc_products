"""
CC Products package.

Provides tools for easiliy working with Cloud Commerce Products.
"""

from .functions import create_range, get_product, get_range
from .variation import Variation

__all__ = ["get_product", "get_range", "create_range", "Variation"]
