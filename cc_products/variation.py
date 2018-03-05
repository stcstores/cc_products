from ccapi import CCAPI, VatRates
from ccapi.inventoryitems import Factory

from . import exceptions, optiondescriptors, productoptions
from .baseproduct import BaseProduct


class VAT:

    def __get__(self, instance, owner):
        return VatRates.get_vat_rate_by_id(instance._vat_rate_id)

    def __set__(self, instance, value):
        try:
            vat_rate_id = VatRates.get_vat_rate_id_by_rate(value)
        except KeyError:
            raise Exception('{}% is not a valid VAT rate.'.format(value))
        CCAPI.set_product_vat_rate([instance.id], value)
        instance._vat_rate_id = vat_rate_id


class Variation(BaseProduct):

    LARGE_LETTER = 'Large Letter'
    PACKET = 'Packet'
    HEAVY_AND_LARGE = 'Heavy and Large'
    COURIER = 'Courier'

    department = optiondescriptors.OptionDescriptor('Department')
    purchase_price = optiondescriptors.FloatOption('Purchase Price')
    supplier_sku = optiondescriptors.OptionDescriptor('Supplier SKU')
    brand = optiondescriptors.OptionDescriptor('Brand')
    manufacturer = optiondescriptors.OptionDescriptor('Manufacturer')
    package_type = optiondescriptors.PackageTypeOption()
    international_shipping = optiondescriptors.OptionDescriptor(
        'International_Shipping')
    date_created = optiondescriptors.DateOption('Date Created')
    design = optiondescriptors.OptionDescriptor('Design')
    colour = optiondescriptors.OptionDescriptor('Colour')
    size = optiondescriptors.OptionDescriptor('Size')
    linn_sku = optiondescriptors.OptionDescriptor('Linn SKU')
    linn_title = optiondescriptors.OptionDescriptor('Linn Title')
    discontinued = optiondescriptors.BoolOption(
        'Discontinued', true='Discontinued', false='Not Discontinued')
    amazon_bullets = optiondescriptors.ListOption('Amazon Bullets')
    amazon_search_terms = optiondescriptors.ListOption('Amazon Search Terms')
    vat_rate = VAT()

    def __init__(self, data, product_range=None):
        self._product_range = product_range
        self._options = None
        self._bays = None
        self._price = None
        self.load_from_cc_data(data)
        if self._product_range is not None:
            self.range_id = self._product_range.id

    def load_from_cc_data(self, data):
        self.raw = data
        self.id = data['ID']
        self.full_name = data['FullName']
        self.sku = data['ManufacturerSKU']
        self.range_id = int(data['RangeID'])
        self.default_image_url = data['defaultImageUrl']
        self._external_product_id = data['ExternalProductId']
        self._name = data['Name']
        self._description = data['Description']
        self._barcode = data['Barcode']
        self._end_of_line = data['EndOfLine']
        self._stock_level = data['StockLevel']
        self._length = data['LengthMM']
        self._width = data['WidthMM']
        self._height = data['HeightMM']
        self._large_letter_compatible = data['LargeLetterCompatible']
        self._weight = data['WeightGM']
        self._handling_time = data['DeliveryLeadTimeDays']
        self._vat_rate_id = int(data['VatRateID'])

    def __repr__(self):
        return self.full_name

    @classmethod
    def create(cls, product_range, form_data):
        """
        data, options = form_data
        new_product = product_range.add_product(name, barcode)
        product = cls(new_product, product_range)
        return product
        """
        pass

    @property
    def product_range(self):
        if self._product_range is None:
            from . functions import get_range
            self._product_range = get_range(self.range_id)
        return self._product_range

    @property
    def name(self):
        return self._name

    @property
    def stock_level(self):
        return self._stock_level

    @stock_level.setter
    def stock_level(self, new_stock_level):
        self.CCAPI.update_product_stock_level(
            self.id, new_stock_level, self._stock_level)
        self._stock_level = new_stock_level

    def _set_product_scope(
            self, weight=None, height=None, length=None, width=None,
            large_letter_compatible=None, external_id=None):
        if weight is not None:
            self._weight = weight
        if height is not None:
            self._height = height
        if length is not None:
            self._length = length
        if width is not None:
            self._width = width
        if large_letter_compatible is not None:
            self._large_letter_compatible = large_letter_compatible
        if external_id is not None:
            self._external_product_id = external_id
        CCAPI.set_product_scope(
            self.id, self._weight, self._height, self._length, self._width,
            self._large_letter_compatible, self._external_product_id)

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._set_product_scope(weight=weight)
        self._weight = weight

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._set_product_scope(height=height)
        self._height = height

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._set_product_scope(width=width)
        self._width = width

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, length):
        self._set_product_scope(length=length)
        self._length = length

    @property
    def large_letter_compatible(self):
        return bool(self._large_letter_compatible)

    @large_letter_compatible.setter
    def large_letter_compatible(self, compatible):
        self._set_product_scope(large_letter_compatible=compatible)
        self._large_letter_compatible = compatible

    @property
    def handling_time(self):
        return self._handling_time

    @handling_time.setter
    def handling_time(self, handling_time):
        self.product.set_handling_time(handling_time)

    @property
    def price(self):
        if self._price is None:
            self._price = float(CCAPI.get_product(self.id).base_price)
        return self._price

    @price.setter
    def price(self, price):
        CCAPI.set_product_base_price(self.id, price)
        self._price = price

    @property
    def supplier(self):
        factories = self._get_factory_links()
        if len(factories) == 0:
            return None
        if len(factories) == 1:
            return factories[0]
        else:
            raise Exception('Too Many Suppliers.')

    @supplier.setter
    def supplier(self, factory_name):
        if not isinstance(factory_name, Factory):
            factories = CCAPI.get_factories()
            if factory_name in factories.names:
                factory = factories.names[factory_name]
            else:
                raise exceptions.FactoryDoesNotExist(factory_name)
        self._update_product_factory_link(factory.id)
        self.options['Supplier'] = factory.name

    @property
    def barcode(self):
        return self._barcode

    @barcode.setter
    def barcode(self, barcode):
        #  TODO
        pass

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is None or value == '':
            value = self.name
        self.product.CCAPI.set_product_description(value, [self.id])
        self._description = value

    @property
    def options(self):
        if self._options is None:
            self._options = productoptions.VariationOptions(
                self, self.product_range)
        return self._options

    def _get_factory_links(self):
        return CCAPI.get_product_factory_links(self.id)

    def _update_product_factory_link(
            self, factory_id, dropship=False, supplier_sku='', price=0):
        factory_links = self._get_factory_links()
        for link in factory_links:
            link.delete()
        return CCAPI.update_product_factory_link(
            product_id=self.id, factory_id=factory_id, dropship=dropship,
            supplier_sku=supplier_sku, price=price)

    @property
    def bays(self):
        if self._bays is None:
            self._bays = [b.id for b in CCAPI.get_bays_for_product(self.id)]
        return self._bays

    @bays.setter
    def bays(self, new_bays):
        new_bays = [int(bay) for bay in new_bays]
        old_bays = self.bays
        bays_to_remove = [b for b in old_bays if b not in new_bays]
        bays_to_add = [b for b in new_bays if b not in old_bays]
        for bay in bays_to_remove:
            CCAPI.remove_warehouse_bay_from_product(self.id, bay)
        for bay in bays_to_add:
            CCAPI.add_warehouse_bay_to_product(self.id, bay)
        self._bays = None
