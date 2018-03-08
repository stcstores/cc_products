from ccapi import CCAPI

from . import exceptions, productoptions
from .baseproduct import BaseProduct
from .variation import Variation


class ProductRange(BaseProduct):

    def __init__(self, data):
        self.load_from_cc_data(data)

        self._options = None
        self._products = None

    def load_from_cc_data(self, data):
        self.raw = data
        self.id = data['ID']
        self._name = data['Name']
        self.sku = data['ManufacturerSKU']
        self._end_of_line = data['EndOfLine']
        self.thumbnail = data['ThumbNail']
        self.pre_order = bool(data['PreOrder'])
        self.grouped = bool(data['Grouped'])
        self.products = [
            Variation.create_from_range(product_data, product_range=self)
            for product_data in data['Products']]

    def __iter__(self):
        for product in self.products:
            yield product

    @property
    def options(self):
        if self._options is None:
            self._options = productoptions.RangeOptions(self)
        return self._options

    @property
    def selected_options(self):
        return self.options.selected_options

    @property
    def variable_options(self):
        return self.options.variable_options

    @property
    def name(self):
        return self._name

    @property
    def end_of_line(self):
        return self._end_of_line

    @end_of_line.setter
    def end_of_line(self, value):
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
    def department(self):
        departments = [p.department for p in self.products if p.department]
        if len(departments) == 0:
            raise exceptions.NoDepartmentError(self)
        if len(departments) == len(self.products):
            if all([d == departments[0] for d in departments]):
                return departments[0]
        raise exceptions.MixedDepartmentsError(self)

    @department.setter
    def department(self, department):
        for product in self.products:
            product.department = department
