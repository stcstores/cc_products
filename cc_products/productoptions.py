"""Tools for working with Cloud Commerce Pro's Product Options."""

from ccapi import CCAPI


class OptionList:
    """Container for multiple Product Options."""

    def has_option(self, option_name):
        """Return True if option_name matches an option in list."""
        if option_name in self.names:
            return True
        return False

    @property
    def names(self):
        """Return list containing the names of product options in self."""
        return [o.name for o in self.options]

    def __contains__(self, key):
        return key in self.names

    def __len__(self):
        return len(self.names)


class VariationOptions(OptionList):
    """Container for Variation Product Options."""

    def __init__(self, product, product_range):
        """
        Configure Variation Product Option.

        Args:
            product: The cc_products.Variation to which this option belongs.
            product_range: The cc_product.ProductRange to which product
                belongs.
        """
        self._options = None
        self.product = product
        self.product_range = product_range

    def __getitem__(self, key):
        if self.product_has_option(key):
            return self.names[key].value
        return None

    def __setitem__(self, key, value):
        value = str(value)
        if self.product_has_option(key):
            option = self.names[key]
        else:
            range_option = self.product.product_range.options[key]
            range_option.selected = True
            option = range_option
        value_id = CCAPI.get_option_value_id(option.id, value, create=True)
        CCAPI.set_product_option_value(
            product_ids=[self.product.id], option_id=option.id, option_value_id=value_id
        )
        self._options = None

    def __repr__(self):
        return self.names.__repr__()

    def __iter__(self):
        for option in self.options:
            yield option.name, option.value

    def product_has_option(self, key):
        """Return True if key a Product Option contained here."""
        return key in self.names

    @property
    def options(self):
        """Return Variation Product Options belinging to self.product."""
        if self._options is None:
            options = CCAPI.get_options_for_product(self.product.id)
            self._options = [VariationOption(o) for o in options]
        return self._options

    @property
    def names(self):
        """Return dict contining Product Options Name and Product Options."""
        return {o.name: o for o in self.options}


class VariationOption:
    """Container for a single Variation Product Option."""

    def __init__(self, option):
        """Configure product option."""
        self.id = option.id
        self.name = option.option_name
        if option.value is None:
            self.value = None
        else:
            self.value = option.value.value

    def __repr__(self):
        return "{}: {}".format(self.name, self.value)


class RangeOptions(OptionList):
    """Container for Product Options belonging to a Product Range."""

    def __init__(self, product_range):
        """
        Configure product options for product range.

        Args:
            product_range: The cc_product.ProductRange for which to load
                Options.
        """
        self.product_range = product_range
        option_data = CCAPI.get_product_range_options(self.product_range.id)
        options = {o.id: o for o in option_data.options}
        self.options = [
            RangeOption(self.product_range, o, options.get(o.id))
            for o in option_data.shop_options
        ]

    def __getitem__(self, key):
        return self.names[key]

    def __repr__(self):
        return self.selected_options.__repr__()

    def __iter__(self):
        for option in self.options:
            yield option

    @property
    def variation_options(self):
        """Return the Range's Variation Options."""
        return [o.name for o in self.options if o.selected]

    @property
    def names(self):
        """Return dict of Product Option names to Product Options."""
        return {o.name: o for o in self.options}

    @property
    def ids(self):
        """Return dict of Product Option ids to Product Options."""
        return {o.id: o for o in self.options}

    @property
    def selected_options(self):
        """Return list of selected Product Options for the Product Range."""
        return [o for o in self.options if o.selected]

    @property
    def variable_options(self):
        """Return list of the Product Range's Variation Product Options."""
        return [o for o in self.options if o.variable]


class RangeOption:
    """Container for a single Product Range Product Option."""

    def __init__(self, product_range, product_option, shop_option=None):
        """
        Configure Product Range Option.

        Args:
            product_range: The Product Range to which the option belongs.
            product_option: The CCAPI product option object.

        Kwargs:
            shop_option: True if this product is a Variation Option.
        """
        self.product_range = product_range
        self.id = product_option.id
        self.name = product_option.name.replace(" (Master)", "")
        if shop_option is not None:
            self._selected = True
            self._variable = shop_option.is_web_shop_select
        else:
            self._selected = False
            self._variable = False

    def __repr__(self):
        return self.name

    @property
    def selected(self):
        """Return True if this Product Option is in use by the Range."""
        return self._selected

    @selected.setter
    def selected(self, selected):
        """
        Set weather this Product Option is selected.

        Args:
            selected(bool): If True product option will be seleced.
        """
        value = bool(selected)
        if value:
            CCAPI.add_option_to_product(
                range_id=self.product_range.id, option_id=self.id
            )
        else:
            CCAPI.remove_option_from_product(
                range_id=self.product_range.id, option_id=self.id
            )
        for product in self.product_range:
            product._options = None
        self._selected = value

    @property
    def variable(self):
        """Return True if this Product Option is a Variation Option."""
        return self._variable

    @variable.setter
    def variable(self, value):
        """
        Set weather this Product Option is a Variation Option.

        Args:
            selected(bool): If True product option will be set as a Variation
                Option.
        """
        value = bool(value)
        if value == self._variable:
            return
        CCAPI.set_range_option_drop_down(
            range_id=self.product_range.id, option_id=self.id, drop_down=value
        )
        self._variable = value
