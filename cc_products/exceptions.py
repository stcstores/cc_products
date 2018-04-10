"""Exceptions for cc_products."""


class ProductOptionNotSetForProduct(KeyError):
    """No value set for Product Option for Product."""

    def __init__(self, option_name):
        """Return exception message."""
        return super().__init__(
            'Product Option "{}" not set for this product.'.format(
                option_name))


class FactoryDoesNotExist(KeyError):
    """No factory exists with given name."""

    def __init__(self, factory_name):
        """Return exception message."""
        return super().__init__(
            'No factory exists with name "{}".'.format(factory_name))


class DepartmentError(ValueError):
    """Base exeption for errors relating to product Departments."""

    def __init__(self, message):
        """Return exception message."""
        return super().__init__(message)


class NoDepartmentError(DepartmentError):
    """Product Range has no Department set."""

    def __init__(self, product_range):
        """Return exception message."""
        return super().__init__(
            '{} has no deparment set.'.format(product_range))


class MixedDepartmentsError(DepartmentError):
    """Products beloning to Product Range have mixed Departments."""

    def __init__(self, product_range):
        """Return exception message."""
        return super().__init__(
            '{} has mixed departments.'.format(product_range))
