import pytest

from cc_products import exceptions


def test_ProductOptionsNotSetForProduct_exception():
    option_name = "test option name"
    with pytest.raises(KeyError) as execinfo:
        raise exceptions.ProductOptionNotSetForProduct(option_name)
    assert (
        str(execinfo.value)
        == "'Product Option \"test option name\" not set for this product.'"
    )


def test_FactoryDoesNotExist_exception():
    factory_name = "test factory name"
    with pytest.raises(KeyError) as execinfo:
        raise exceptions.FactoryDoesNotExist(factory_name)
    assert str(execinfo.value) == "'No factory exists with name \"test factory name\".'"


def test_DepartmentError_exception():
    message = "test message"
    with pytest.raises(ValueError) as execinfo:
        raise exceptions.DepartmentError(message)
    assert str(execinfo.value) == "test message"


def test_NoDepartmentError():
    product_range = "test product"
    with pytest.raises(exceptions.DepartmentError) as execinfo:
        raise exceptions.NoDepartmentError(product_range)
    assert str(execinfo.value) == "test product has no deparment set."


def test_MixedDepartmentsError():
    product_range = "test product"
    with pytest.raises(exceptions.DepartmentError) as execinfo:
        raise exceptions.MixedDepartmentsError(product_range)
    assert str(execinfo.value) == "test product has mixed departments."
