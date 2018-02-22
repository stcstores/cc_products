from .baseproduct import BaseProduct
from .options import ProductOptions


class Variation(BaseProduct):

    def __init__(self, product, product_range=None):
        self.product = product
        self._product_range = product_range

        self.is_checked = product.is_checked
        self.is_listed = product.is_listed
        self.supplier_sku = product.supplier_sku
        self.id = product.id
        self.sku = product.sku
        self.vat_rate_id = product.vat_rate_id
        self.vat_rate = product.vat_rate
        self.end_of_line = product.end_of_line
        self.default_image_url = product.default_image_url

        self._bays = None
        self._options = None

    def __repr__(self):
        return self.product.__repr__()

    @classmethod
    def create(cls, product_range, form_data):
        data, options = form_data
        new_product = product_range.add_product(name, barcode)
        product = cls(new_product, product_range)
        return product

    @property
    def product_range(self):
        if self._product_range is not None:
            return self._product_range
        from . functions import get_range
        return get_range(self.product.range_id)

    @property
    def name(self):
        return self.product.name

    @property
    def full_name(self):
        return self.product.full_name

    @property
    def stock_level(self):
        return self.product.stock_level

    @stock_level.setter
    def stock_level(self, stock_level):
        self.product.set_stock_level(stock_level)
        self.stock_level = stock_level
        self.product.stock_level = stock_level

    @property
    def weight(self):
        return self.product.weight

    @weight.setter
    def weight(self, weight):
        self.product.set_product_scope(weight=weight)
        self.product.weight = weight

    @property
    def height(self):
        return self.product.height_mm

    @height.setter
    def height(self, height):
        self.product.set_product_scope(height=height)

    @property
    def width(self):
        return self.product.width_mm

    @width.setter
    def width(self, width):
        self.product.set_product_scope(width=width)

    @property
    def length(self):
        return self.product.length_mm

    @length.setter
    def length(self, length):
        self.product.set_product_scope(length=length)

    @property
    def large_letter_compatible(self):
        return self.product.large_letter_compatible

    @large_letter_compatible.setter
    def large_letter_compatible(self, compatible):
        self.product.set_product_scope(large_letter_compatible=compatible)

    @property
    def handling_time(self):
        return self.product.delivery_lead_time

    @handling_time.setter
    def handling_time(self, handling_time):
        self.product.set_handling_time(handling_time)

    @property
    def price(self):
        return self.product.base_price

    @price.setter
    def price(self, price):
        self.product.set_base_price(price)

    @property
    def supplier(self):
        factories = self.product.get_factory_links()
        if len(factories) == 0:
            return None
        if len(factories) == 1:
            return factories[0]
        else:
            raise Exception('Too Many Suppliers.')

    @supplier.setter
    def supplier(self, factory):
        if isinstance(factory, str):
            if factory.isdigit():
                factory_id = int(factory)
            factory_id = CCAPI.get_factories().names[factory].id
        else:
            factory_id = factory.id
        self.product.update_product_factory_link(factory_id)

    @property
    def barcode(self):
        return self.product.barcode

    @property
    def description(self):
        return self.product.description

    @description.setter
    def description(self, description):
        if not description:
            description = self.name
        self.product.set_description(description)
        self.product.description = description

    @property
    def options(self):
        if self._options is None:
            options = self.product.options
            return ProductOptions(options, self, self.product_range)

    @property
    def purchase_price(self):
        PURCHASE_PRICE = self.options.DEPARTMENT
        if PURCHASE_PRICE in self.options:
            return float(self.options[PURCHASE_PRICE])
        return None

    @purchase_price.setter
    def purchase_price(self, price):
        self.options[self.options.PURCHASE_PRICE] = float(price)

    @property
    def department(self):
        DEPARTMENT = self.options.DEPARTMENT
        if DEPARTMENT in self.options:
            return str(self.options[DEPARTMENT])
        return None
