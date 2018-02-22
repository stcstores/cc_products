from . import exceptions


class ProductOptions:

    PURCHASE_PRICE = 'Purchase Price'
    DEPARTMENT = 'Department'
    SUPPLIER = 'Supplier'
    MANUFACTURER = 'Manufacturer'
    BRAND = 'Brand'
    PACKEGE_TYPE = 'Package Type'
    INTERNATIONAL_SHIPPING = 'International_Shipping'
    DATE_CREATED = 'Date Created'
    SUPPLIER_SKU = 'Supplier SKU'
    INCOMPLETE = 'Incomplete'

    def __init__(self, options, product, product_range):
        self.options = options
        self.product = product
        self.product_range = product_range
        self.names = list(self.options.option_names.keys())

    def __getitem__(self, key):
        return str(self.options[key].value)

    def __setitem__(self, key, value):
        try:
            option = self.options[key]
        except KeyError:
            raise exceptions.ProductOptionNotSetForProduct(key)
        self.product.product.set_option_value(key, str(value), create=True)
        option.value.value = str(value)

    def __contains__(self, key):
        return key in self.names

    def __len__(self):
        return len(self.names)


class RangeOptions:

    def __init__(self, options, product_range):
        self.options = options
        self.product_range = product_ragne
