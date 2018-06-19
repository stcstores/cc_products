"""Main methods for cc_products."""

from ccapi import CCAPI

from .productrange import ProductRange
from .variation import Variation


def get_product(product_id):
    """Retrive a Product from Cloud Commerce."""
    product = CCAPI.get_product(product_id).json
    return Variation(product)


def get_range(range_id):
    """Retrive a Product Range from Cloud Commerce."""
    product_range = ProductRange(CCAPI.get_range(range_id).json)
    return product_range


def create_range(title):
    """Create a new Product Range."""
    range_id = CCAPI.create_range(title)
    return get_range(range_id)
