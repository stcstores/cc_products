from ccapi import CCAPI


class OptionList:

    def has_option(self, option_name):
        if option_name in self.names:
            return True
        return False

    @property
    def names(self):
        return [o.name for o in self.options]

    def __contains__(self, key): return key in self.names

    def __len__(self): return len(self.names)


class VariationOptions(OptionList):

    def __init__(self, product, product_range):
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
        CCAPI.set_product_option_value([self.product.id], option.id, value_id)
        self._options = None

    def __repr__(self):
        return self.names.__repr__()

    def product_has_option(self, key):
        return key in self.names

    @property
    def options(self):
        if self._options is None:
            options = CCAPI.get_options_for_product(self.product.id)
            self._options = [VariationOption(o) for o in options]
        return self._options

    @property
    def names(self):
        return {o.name: o for o in self.options}


class VariationOption:

    def __init__(self, option):
        self.id = option.id
        self.name = option.option_name
        if option.value is None:
            self.value = None
        else:
            self.value = option.value.value

    def __repr__(self):
        return '{}: {}'.format(self.name, self.value)


class RangeOptions(OptionList):

    def __init__(self, product_range):
        self.product_range = product_range
        option_data = CCAPI.get_product_range_options(self.product_range.id)
        options = {o.id: o for o in option_data.options}
        self.options = [
            RangeOption(self.product_range, o, options.get(o.id)) for o in
            option_data.shop_options]

    def __getitem__(self, key):
        return self.names[key]

    def __repr__(self):
        return self.selected_options.__repr__()

    @property
    def variation_options(self):
        return [o.name for o in self.options if o.selected]

    @property
    def names(self):
        return {o.name: o for o in self.options}

    @property
    def ids(self):
        return {o.id: o for o in self.options}

    @property
    def selected_options(self):
        return [o for o in self.options if o.selected]

    @property
    def variable_options(self):
        return [o for o in self.options if o.variable]


class RangeOption:

    def __init__(self, product_range, product_option, shop_option=None):
        self.product_range = product_range
        self.id = product_option.id
        self.name = product_option.name.replace(' (Master)', '')
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
        return self._selected

    @selected.setter
    def selected(self, selected):
        value = bool(selected)
        if value:
            CCAPI.add_option_to_product(self.product_range.id, self.id)
        else:
            CCAPI.remove_option_from_product(self.product_range.id, self.id)
        for product in self.product_range:
            product._options = None
        self._selected = value

    @property
    def variable(self):
        return self._variable

    @variable.setter
    def variable(self, value):
        value = bool(value)
        if value == self._variable:
            return
        CCAPI.set_range_option_drop_down(self.product_range.id, self.id, value)
        self._variable = value
