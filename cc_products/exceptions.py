class ProductOptionNotSetForProduct(KeyError):

    def __init__(self, option_name):
        return super().__init__(
            'Product Option "{}" not set for this product.'.format(
                option_name))


class FactoryDoesNotExist(KeyError):

    def __init__(self, factory_name):
        return super().__init__(
            'No factory exists with name "{}".'.format(factory_name))


class DepartmentError(ValueError):

    def __init__(self, message):
        return super().__init__(message)


class NoDepartmentError(DepartmentError):

    def __init__(self, product_range):
        return super().__init__(
            '{} has no deparment set.'.format(product_range))


class MixedDepartmentsError(DepartmentError):

    def __init__(self, product_range):
        return super().__init__(
            '{} has mixed departments.'.format(product_range))
