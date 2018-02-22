from .baseproduct import BaseProduct


class ProductRange(BaseProduct):

    def __init__(self, product_range):
        self.range = product_range
        self.id = self.range.id
        self.name = self.range.name
