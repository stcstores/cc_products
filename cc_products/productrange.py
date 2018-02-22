from . import productoptions
from .baseproduct import BaseProduct


class ProductRange(BaseProduct):

    def __init__(self, product_range):
        self.product = product_range
        self.id = self.product.id
        self.sku = self.product.sku
        self.product_ids = [product.id for product in self.product.products]

        self._options = None
        self._products = None

    @property
    def options(self):
        if self._options is None:
            self._options = productoptions.RangeOptions(self)
        return self._options

    @property
    def products(self):
        if self._products is None:
            from . functions import get_product
            self._products = [
                get_product(product_id) for product_id in self.product_ids]
        return self._products

    @property
    def name(self):
        return self.product.name

    @property
    def end_of_line(self):
        return self.product.end_of_line
