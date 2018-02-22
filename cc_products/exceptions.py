class ProductOptionNotSetForProduct(KeyError):

    def __init__(self, option_name):
        return super().__init__(
            'Product Option "{}" not set for this product.'.format(
                option_name))


class FactoryDoesNotExist(KeyError):

    def __init__(self, factory_name):
        return super().__init__(
            'No factory exists with name "{}".'.format(factory_name))
