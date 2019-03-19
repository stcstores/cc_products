"""
Variation class.

Wrapper for Cloud Commerce Products.
"""

from ccapi import CCAPI, VatRates
from ccapi.cc_objects import Factory

from . import exceptions, optiondescriptors, productoptions
from .baseproduct import BaseProduct


class VAT:
    """Descriptor for handeling product VAT rate."""

    def __get__(self, instance, owner):
        if instance._vat_rate_id is None:
            instance._reload()
        return VatRates.get_vat_rate_by_id(int(instance._vat_rate_id))

    def __set__(self, instance, value):
        try:
            vat_rate_id = VatRates.get_vat_rate_id_by_rate(value)
        except KeyError:
            raise Exception("{}% is not a valid VAT rate.".format(value))
        CCAPI.set_product_vat_rate(product_ids=[instance.id], vat_rate=value)
        instance._vat_rate_id = vat_rate_id


class ProductScopeDescriptor:
    """Base class for descriptors handeling product scope attributes."""

    def __get__(self, instance, owner):
        value = getattr(instance, self.instance_attr)
        if value is None:
            instance._reload()
        return getattr(instance, self.instance_attr)

    def __set__(self, instance, value):
        setattr(instance, self.instance_attr, value)
        CCAPI.set_product_scope(
            product_id=instance.id,
            weight=instance.weight,
            height=instance.cloud_commerce_height,
            length=instance.cloud_commerce_length,
            width=instance.cloud_commerce_width,
            large_letter_compatible=instance.large_letter_compatible,
            external_id=instance.external_product_id,
        )


class WeightDescriptor(ProductScopeDescriptor):
    """Descriptor for product wieght."""

    instance_attr = "_weight"


class LengthDescriptor(ProductScopeDescriptor):
    """Descriptor for product length."""

    instance_attr = "_length"


class WidthDescriptor(ProductScopeDescriptor):
    """Descriptor for product width."""

    instance_attr = "_width"


class HeightDescriptor(ProductScopeDescriptor):
    """Descriptor for product height."""

    instance_attr = "_height"


class LargeLetterCompatibleDescriptor(ProductScopeDescriptor):
    """Descriptor for product large letter compatibility."""

    instance_attr = "_large_letter_compatible"


class ExternalProductIDDescriptor(ProductScopeDescriptor):
    """Descriptor for product external ID."""

    instance_attr = "_external_product_id"


class Variation(BaseProduct):
    """Wrapper for Cloud Commerce Products."""

    LARGE_LETTER = "Large Letter"
    LARGE_LETTER_SINGLE = "Large Letter (Single)"
    PACKET = "Packet"
    HEAVY_AND_LARGE = "Heavy and Large"
    COURIER = "Courier"

    MENS = "mens"
    GIRLS = "girls"
    WOMENS = "womens"
    BOYS = "boys"
    BABY_BOYS = "baby-boys"
    BABY_GIRLS = "baby-girls"
    UNISEX_BABY = "unisex-baby"

    department = optiondescriptors.OptionDescriptor("Department")
    purchase_price = optiondescriptors.FloatOption("Purchase Price")
    retail_price = optiondescriptors.FloatOption("Retail Price")
    supplier_sku = optiondescriptors.OptionDescriptor("Supplier SKU")
    brand = optiondescriptors.OptionDescriptor("Brand")
    manufacturer = optiondescriptors.OptionDescriptor("Manufacturer")
    package_type = optiondescriptors.PackageTypeOption()
    international_shipping = optiondescriptors.OptionDescriptor(
        "International Shipping"
    )
    date_created = optiondescriptors.DateOption("Date Created")
    design = optiondescriptors.OptionDescriptor("Design")
    colour = optiondescriptors.OptionDescriptor("Colour")
    size = optiondescriptors.OptionDescriptor("Size")
    linn_sku = optiondescriptors.OptionDescriptor("Linn SKU")
    linn_title = optiondescriptors.OptionDescriptor("Linn Title")
    discontinued = optiondescriptors.BoolOption(
        "Discontinued", true="Discontinued", false="Not Discontinued"
    )
    amazon_bullets = optiondescriptors.ListOption("Amazon Bullets")
    amazon_search_terms = optiondescriptors.ListOption("Amazon Search Terms")
    gender = optiondescriptors.OptionDescriptor("Gender")
    weight = WeightDescriptor()
    length = optiondescriptors.IntegerOption("Length MM")
    width = optiondescriptors.IntegerOption("Width MM")
    height = optiondescriptors.IntegerOption("Height MM")
    vat_rate = VAT()
    weight = WeightDescriptor()
    cloud_commerce_length = LengthDescriptor()
    cloud_commerce_width = WidthDescriptor()
    cloud_commerce_height = HeightDescriptor()
    large_letter_compatible = LargeLetterCompatibleDescriptor()
    external_product_id = ExternalProductIDDescriptor()

    def __init__(self, data, product_range=None):
        """Initialise hidden attributes."""
        self._product_range = product_range
        self._options = None
        self._bays = None
        self._price = None
        self._vat_rate = None
        self._vat_rate_id = None
        self.load_from_cc_data(data)
        if self._product_range is not None:
            self.range_id = self._product_range.id

    def __repr__(self):
        return self.full_name

    def load_from_cc_data(self, data):
        """Load initial data from Cloud Commerce Product data."""
        self.raw = data
        self.id = data["ID"]
        self.full_name = data["FullName"]
        self.sku = data["ManufacturerSKU"]
        self.range_id = data["RangeID"]
        self.default_image_url = data["defaultImageUrl"]
        self._external_product_id = data["ExternalProductId"]
        self._name = data["Name"]
        self._description = data["Description"]
        self._barcode = data["Barcode"]
        self._end_of_line = data["EndOfLine"]
        self._stock_level = data["StockLevel"]
        self._length = data["LengthMM"]
        self._width = data["WidthMM"]
        self._height = data["HeightMM"]
        self._large_letter_compatible = data["LargeLetterCompatible"]
        self._weight = data["WeightGM"]
        self._handling_time = data["DeliveryLeadTimeDays"]
        self._price = data["BasePrice"]
        self._vat_rate_id = data["VatRateID"]

    @classmethod
    def create_from_range(cls, data, product_range):
        """Load initial data from Cloud Commerce Product Range data."""
        data["BasePrice"] = None
        data["VatRateID"] = None
        data["WeightGM"] = None
        data["LengthMM"] = None
        data["WidthMM"] = None
        data["HeightMM"] = None
        data["LargeLetterCompatible"] = None
        data["ExternalProductId"] = None
        return cls(data, product_range=product_range)

    @property
    def bays(self):
        """Return a list of IDs for Bays in which this product is located."""
        if self._bays is None:
            self._bays = [b.id for b in CCAPI.get_bays_for_product(self.id)]
        return self._bays

    @bays.setter
    def bays(self, new_bays):
        """
        Update Warehouse Bays for product.

        Args:
            new_bays: list<int> of Warehouse Bay IDs.
        """
        new_bays = [int(bay) for bay in new_bays]
        old_bays = self.bays
        bays_to_remove = [b for b in old_bays if b not in new_bays]
        bays_to_add = [b for b in new_bays if b not in old_bays]
        for bay in bays_to_remove:
            CCAPI.remove_warehouse_bay_from_product(self.id, bay)
        for bay in bays_to_add:
            CCAPI.add_warehouse_bay_to_product(self.id, bay)
        self._bays = None

    @property
    def barcode(self):
        """Return the barcode of the product."""
        return self._barcode

    @barcode.setter
    def barcode(self, barcode):
        """Set the barcode for the product."""
        CCAPI.set_product_barcode(product_id=self.id, barcode=barcode)

    @property
    def description(self):
        """Return the description of the product."""
        if self._description is None:
            self._description = CCAPI.get_product(self.id).description
        return self._description

    @description.setter
    def description(self, value):
        """Set the description of the product."""
        if value is None or value == "":
            value = self.name
        CCAPI.set_product_description(product_ids=[self.id], description=value)
        self._description = value

    @property
    def handling_time(self):
        """Return the handling time for the product."""
        return self._handling_time

    @handling_time.setter
    def handling_time(self, handling_time):
        """Set the handling time for the product."""
        CCAPI.set_product_handling_time(product_id=self.id, handling_time=handling_time)
        self._handling_time = handling_time

    @property
    def name(self):
        """Return the name of the product."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the product's name."""
        CCAPI.set_product_name(name=name, product_ids=[self.id])
        self._name = name
        self.full_name = None

    @property
    def options(self):
        """Return the Product Options of the product."""
        if self._options is None:
            self._options = productoptions.VariationOptions(self, self.product_range)
        return self._options

    @property
    def price(self):
        """Return the base price for the product."""
        if self._price is None:
            self._reload()
        return float(self._price)

    @price.setter
    def price(self, price):
        """Set the base price for the product."""
        CCAPI.set_product_base_price(product_id=self.id, price=price)
        self._price = price

    @property
    def product_range(self):
        """Return the Product Range to whicth this product belongs."""
        if self._product_range is None:
            from .functions import get_range

            self._product_range = get_range(self.range_id)
        return self._product_range

    @property
    def stock_level(self):
        """Return the current stock level for the product."""
        return self._stock_level

    @stock_level.setter
    def stock_level(self, new_stock_level):
        """Update the stock level of the product."""
        CCAPI.update_product_stock_level(
            product_id=self.id,
            new_stock_level=new_stock_level,
            old_stock_level=self._stock_level,
        )
        self._stock_level = new_stock_level

    @property
    def supplier(self):
        """
        Return the Factory Link associated with the product.

        Returns:
            CCAPI.FactoryLink if exactly one exists.
            None if no factory link exists.

        Raises:
            Exception if more than one Factory Link exists for the product.

        """
        factories = self._get_factory_links()
        if len(factories) == 0:
            return None
        if len(factories) == 1:
            return factories[0]
        else:
            raise Exception("Too Many Suppliers.")

    @supplier.setter
    def supplier(self, factory_name):
        """
        Set the supplier of the product.

        Remove all Factory Links and create a new Factory Link to the Factory
        named factory_name.

        Set Product Option Supplier to factory name.
        """
        if not isinstance(factory_name, Factory):
            factories = CCAPI.get_factories()
            if factory_name in factories.names:
                factory = factories.names[factory_name]
            else:
                raise exceptions.FactoryDoesNotExist(factory_name)
        self._update_product_factory_link(factory.id)
        self.options["Supplier"] = factory.name

    def _reload(self):
        self.load_from_cc_data(CCAPI.get_product(self.id).json)

    def _get_factory_links(self):
        return CCAPI.get_product_factory_links(self.id)

    def _update_product_factory_link(
        self, factory_id, dropship=False, supplier_sku="", price=0
    ):
        factory_links = self._get_factory_links()
        for link in factory_links:
            link.delete()
        return CCAPI.update_product_factory_link(
            product_id=self.id,
            factory_id=factory_id,
            dropship=dropship,
            supplier_sku=supplier_sku,
            price=price,
        )
