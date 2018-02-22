import datetime

from ccapi import CCAPI

from . import exceptions


class ProductOptions:

    def has_option(self, option_name):
        if option_name in self.names:
            return True
        return False

    def __contains__(self, key): return key in self.names

    def __len__(self): return len(self.names)


class VariationOptions(ProductOptions):

    def __init__(self, options, product, product_range):
        self.options = options
        self.product = product
        self.product_range = product_range

    def __getitem__(self, key):
        if self.product_has_option(key):
            return self.options[key].value
        return None

    def __setitem__(self, key, value):
        if self.product_has_option(key):
            self.product.product.set_option_value(key, str(value), create=True)
            self.options[key].value.value = str(value)
        raise exceptions.ProductOptionNotSetForProduct(key)

    @property
    def names(self):
        return list(self.options.option_names.keys())


class RangeOptions(ProductOptions):

    def __init__(self, product_range):
        self.product_range = product_range
        option_data = CCAPI.get_product_range_options(self.product_range.id)
        options = {o.id: o for o in option_data.options}
        self.options = [
            RangeOption(self, o, options.get(o.id)) for o in
            option_data.shop_options]

    def __getitem__(self, key):
        return self.options[key]

    @property
    def variation_options(self):
        return [o.name for o in self.options if o.selected]

    @property
    def names(self):
        return {o.name: o for o in self.options}

    @property
    def ids(self):
        return {o.id: o for o in self.options}


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

    @property
    def selected(self):
        return self._selected


class Option:

    def __init__(self, option_name):
        self.option_name = option_name

    def __get__(self, instance, owner):
        return self.to_python(instance, owner)

    def __set__(self, instance, value):
        instance.options[self.option_name] = self.clean(value)

    def __delete__(self, instance):
        self.__set__(instance, '')

    def to_python(self, instance, owner):
        if self.option_name not in instance.options:
            return None
        value = instance.options[self.option_name]
        if value.value is not None:
            return value.value
        return None

    def clean(self, value):
        return str(value)


class DateOption(Option):

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value is None:
            return None
        year, month, day = value.split('-')
        return datetime.date(
            year=int(year), month=int(month), day=int(day))

    def clean(self, value):
        return super().clean('-'.join(
            [str(value.year), str(value.month), str(value.day)]))


class FloatOption(Option):

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        return float(value)


class BoolOption(Option):

    def __init__(self, option_name, true=None, false=None):
        self.true = true
        self.false = false
        super().__init__(option_name)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value is None or value == self.false:
            return False
        if value == self.true:
            return True
        raise exceptions.OptionValueNotRecognised(value)

    def clean(self, value):
        if value is True:
            return self.true
        return super().clean(self.false)


class ListOption(Option):

    def __init__(self, option_name, delimiter='|'):
        self.delimiter = delimiter
        super().__init__(option_name)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        return value.split(self.delimiter)

    def clean(self, value):
        return super().clean(self.delimiter.join([str(v) for v in value]))
