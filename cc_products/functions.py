from ccapi import CCAPI

from .productrange import ProductRange
from .variation import Variation


def get_product(product_id):
    product = CCAPI.get_product(product_id)
    return Variation(product)


def get_range(range_id):
    product_range = ProductRange(CCAPI.get_range(range_id))
    return product_range
