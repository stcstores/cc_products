from unittest.mock import Mock, patch

import pytest

from cc_products import exceptions
from cc_products.productrange import ProductRange


@pytest.fixture
def mock_CCAPI():
    with patch("cc_products.productrange.CCAPI") as mock:
        yield mock


@pytest.fixture
def channel_ids():
    return ["321654897645", "1796465168964"]


@pytest.fixture
def mock_channel_ids(mock_CCAPI, channel_ids):
    channel_ids = [Mock(id=channel_id) for channel_id in channel_ids]
    mock_CCAPI.get_sales_channels_for_range.return_value = channel_ids
    return channel_ids


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


def test_set_description_proerty_sets__description(mock_CCAPI, product_range):
    description = "Test Description"
    product_range._description = None
    product_range.description = description
    assert product_range._description == description


def test_set_description_property_updates_products(mock_CCAPI, product_range):
    description = "Test Description"
    product_ids = ["123456798", "32164597", "147258369"]
    product_range.products = [Mock(id=product_id) for product_id in product_ids]
    product_range.description = description
    mock_CCAPI.set_product_description.assert_called_once_with(
        product_ids=product_ids, description=description
    )


def test_get_end_of_line_property(product_range):
    sential = ...
    product_range._end_of_line = sential
    assert product_range.end_of_line is sential


def test_end_of_line_property_setter_updates_products(mock_CCAPI, product_range):
    products = [Mock(discontinued=False) for i in range(3)]
    product_range.products = products
    product_range.end_of_line = True
    for product in products:
        assert product.discontinued is True


def test_end_of_line_property_setter_updates__end_of_line(mock_CCAPI, product_range):
    product_range._end_of_line = False
    product_range.end_of_line = True
    assert product_range._end_of_line is True


def test_end_of_line_property_setter_sends_request(mock_CCAPI, product_range):
    product_range._end_of_line = False
    product_range.end_of_line = True
    mock_CCAPI.update_range_settings.assert_called_once_with(
        product_range.id,
        current_name=product_range.name,
        current_sku=product_range.sku,
        current_end_of_line=False,
        current_pre_order=product_range.pre_order,
        current_group_items=product_range.grouped,
        new_name=product_range.name,
        new_sku=product_range.sku,
        new_end_of_line=True,
        new_pre_order=product_range.pre_order,
        new_group_items=product_range.grouped,
        channels=[],
    )


def test_get_name_property(product_range):
    sential = ...
    product_range._name = sential
    assert product_range.name is sential


def test_name_property_setter_updates_product_names(mock_CCAPI, product_range):
    new_name = "New Product Name"
    product_ids = ["13245679", "31654987", "1564891"]
    product_range.products = [Mock(id=product_id) for product_id in product_ids]
    product_range.name = new_name
    mock_CCAPI.set_product_name.assert_called_once_with(
        product_ids=product_ids, name=new_name
    )


def test_name_property_setter_updates_range_name(
    mock_CCAPI, channel_ids, product_range
):
    product_range._get_sales_channel_ids = Mock(return_value=channel_ids)
    new_name = "New Product Name"
    product_range.name = new_name
    mock_CCAPI.update_range_settings.assert_called_once_with(
        product_range.id,
        current_name=product_range.name,
        current_sku=product_range.sku,
        current_end_of_line=False,
        current_pre_order=product_range.pre_order,
        current_group_items=product_range.grouped,
        new_name=new_name,
        new_sku=product_range.sku,
        new_end_of_line=product_range.end_of_line,
        new_pre_order=product_range.pre_order,
        new_group_items=product_range.grouped,
        channels=channel_ids,
    )


def test_get_options_property_when__options_is_set(product_range):
    sential = ...
    product_range._options = sential
    assert product_range.options is sential


def test_get_options_property__sets__options_when__options_is_None(
    mock_CCAPI, product_range
):
    sential = ...
    product_range._options = None
    with patch(
        "cc_products.productrange.productoptions.RangeOptions"
    ) as mock_RangeOptions:
        mock_RangeOptions.return_value = sential
        assert product_range.options is sential
        assert product_range._options is sential


def test_selected_options_property(product_range):
    sential = ...
    product_range._options = Mock(selected_options=sential)
    assert product_range.selected_options is sential


def test_variable_options_property(product_range):
    sential = ...
    product_range._options = Mock(variable_options=sential)
    assert product_range.variable_options is sential
