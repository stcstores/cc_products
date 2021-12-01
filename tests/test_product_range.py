from unittest.mock import Mock

import pytest

from cc_products import exceptions
from cc_products.productrange import ProductRange


@pytest.fixture
def range_id():
    return "93094893"


@pytest.fixture
def name():
    return "Test Product Range Name"


@pytest.fixture
def range_sku():
    return "RNG_ABC_DEF_GHI"


@pytest.fixture
def thumbnail():
    return "thumbnail"


@pytest.fixture
def products():
    return []


@pytest.fixture
def cc_data(range_id, name, range_sku, thumbnail, products):
    return {
        "ID": range_id,
        "Name": name,
        "ManufacturerSKU": range_sku,
        "EndOfLine": False,
        "ThumbNail": thumbnail,
        "PreOrder": False,
        "Grouped": False,
        "Products": products,
    }


@pytest.fixture
def product_range(cc_data):
    return ProductRange(cc_data)


def test_sets_raw(cc_data, product_range):
    assert product_range.raw == cc_data


def test_sets__options(product_range):
    assert product_range._options is None


def test_sets__products(product_range):
    assert product_range._products is None


def test_sets_range_id(range_id, product_range):
    assert product_range.id == range_id


def test_sets__name(name, product_range):
    assert product_range.name == name


def test_sets_sku(range_sku, product_range):
    assert product_range.sku == range_sku


def test_sets__end_of_line(cc_data, product_range):
    assert product_range._end_of_line is cc_data["EndOfLine"]


def test_sets__description(product_range):
    assert product_range._description is None


def test_sets_thumbnail(thumbnail, product_range):
    assert product_range.thumbnail == thumbnail


def test_sets_pre_order(cc_data, product_range):
    assert product_range.pre_order is cc_data["PreOrder"]


def test_sets_grouped(cc_data, product_range):
    assert product_range.grouped is cc_data["Grouped"]


def test_department_property_returns_product_department(product_range):
    department = "test department"
    products = [Mock(department=department) for i in range(3)]
    product_range.products = products
    assert product_range.department == department


def test_department_property_raises_if_no_department_exists(product_range):
    products = [Mock(department=None) for i in range(3)]
    product_range.products = products
    with pytest.raises(exceptions.NoDepartmentError):
        product_range.department


def test_department_property_raises_if_multiple_departments_exists(product_range):
    products = [
        Mock(department="Test Department 1"),
        Mock(department="Test Department 2"),
    ]
    product_range.products = products
    with pytest.raises(exceptions.MixedDepartmentsError):
        product_range.department


def test_department_property_raises_if_any_products_are_missing_department(
    product_range,
):
    products = [
        Mock(department="Test Department 1"),
        Mock(department=None),
    ]
    product_range.products = products
    with pytest.raises(exceptions.MixedDepartmentsError):
        product_range.department


def test_department_setter(product_range):
    department = "Test Department"
    products = [Mock() for i in range(3)]
    product_range.products = products
    product_range.department = department
    for product in products:
        assert product.department == department


def test_get_description_returns_product_description_when__description_is_none(
    product_range,
):
    description = "Test Product Description"
    product_range.products = [Mock(description=description)]
    product_range._description = None
    assert product_range.description == description


def test_get_description_sets__description(product_range):
    description = "Test Product Description"
    product_range.products = [Mock(description=description)]
    product_range._description = None
    product_range.description
    assert product_range._description == description


def test_get_description_returns__description_when_not_none(product_range):
    range_description = "Test Range Description"
    product_range.products = [Mock(description="Test Product Description")]
    product_range._description = range_description
    assert product_range.description == range_description
