"""
Provides the ProductRange class.

A wrapper for Cloud Commerce Product Ranges.
"""

from ccapi import CCAPI

from . import exceptions, productoptions
from .baseproduct import BaseProduct
from .variation import Variation


class ProductRange(BaseProduct):
    """Wrapper for Cloud Commerce Product Ranges."""

    def __init__(self, data):
        """Initialise attributes."""
        self.load_from_cc_data(data)
        self._options = None
        self._products = None

    def __repr__(self):
        return self.name

    def __iter__(self):
        for product in self.products:
            yield product

    def load_from_cc_data(self, data):
        """Set attributes from Cloud Commerce API data."""
        self.raw = data
        self.id = data['ID']
        self._name = data['Name']
        self.sku = data['ManufacturerSKU']
        self._end_of_line = data['EndOfLine']
        self._description = None
        self.thumbnail = data['ThumbNail']
        self.pre_order = bool(data['PreOrder'])
        self.grouped = bool(data['Grouped'])
        self.products = [
            Variation.create_from_range(product_data, product_range=self)
            for product_data in data['Products']
        ]

    @property
    def department(self):
        """Return the name of the Department to which the range belongs."""
        departments = [p.department for p in self.products if p.department]
        if len(departments) == 0:
            raise exceptions.NoDepartmentError(self)
        if len(departments) == len(self.products):
            if all([d == departments[0] for d in departments]):
                return departments[0]
        raise exceptions.MixedDepartmentsError(self)

    @department.setter
    def department(self, department):
        """Set the Department to which the range belongs."""
        for product in self.products:
            product.department = department

    @property
    def description(self):
        """Return the description of the Range."""
        if self._description is None:
            self._description = self.products[0].description
        return self._description

    @description.setter
    def description(self, description):
        """Set the description for the Range."""
        CCAPI.set_product_description(
            product_ids=[p.id for p in self.products], description=description)
        self._description = description

    @property
    def end_of_line(self):
        """Return the end of line status of the range."""
        return self._end_of_line

    @end_of_line.setter
    def end_of_line(self, value):
        """
        Set the end of line status of the range.

        Args:
            value <bool>: True if product is End of Line, else False.

        """
        CCAPI.update_range_settings(
            self.id,
            current_name=self.name,
            current_sku=self.sku,
            current_end_of_line=self.end_of_line,
            current_pre_order=self.pre_order,
            current_group_items=self.grouped,
            new_name=self.name,
            new_sku=self.sku,
            new_end_of_line=bool(value),
            new_pre_order=self.pre_order,
            new_group_items=self.grouped,
            channels=[])
        self._end_of_line = bool(value)
        for product in self.products:
            product.discontinued = True

    @property
    def name(self):
        """Return the name of the range."""
        return self._name

    @name.setter
    def name(self, name):
        CCAPI.set_product_name(
            product_ids=[p.id for p in self.products], name=name)
        CCAPI.update_range_settings(
            self.id,
            current_name=self.name,
            current_sku=self.sku,
            current_end_of_line=self.end_of_line,
            current_pre_order=self.pre_order,
            current_group_items=self.grouped,
            new_name=name,
            new_sku=self.sku,
            new_end_of_line=self.end_of_line,
            new_pre_order=self.pre_order,
            new_group_items=self.grouped,
            channels=self._get_sales_channel_ids())

    @property
    def options(self):
        """Return Product Options for the range."""
        if self._options is None:
            self._options = productoptions.RangeOptions(self)
        return self._options

    @property
    def selected_options(self):
        """Return list of Product Options which are set for the range."""
        return self.options.selected_options

    @property
    def variable_options(self):
        """Return list of Product Options which are variable for the range."""
        return self.options.variable_options

    def add_product(self, barcode, description, vat_rate):
        """Create a new product belonging to this range."""
        from .functions import get_product
        product_id = CCAPI.create_product(
            range_id=self.id,
            name=self.name,
            barcode=barcode,
            description=description,
            vat_rate=vat_rate)
        return get_product(product_id)

    def delete(self):
        """Delete this Product Range."""
        CCAPI.delete_range(self.id)

    def _get_sales_channels(self):
        """Get Sales Channels for this Product Range."""
        return CCAPI.get_sales_channels_for_range(self.id)

    def _get_sales_channel_ids(self):
        """Get IDs of Sales Channels on which this Product Range is listed."""
        return [channel.id for channel in self._get_sales_channels()]
