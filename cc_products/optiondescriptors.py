"""Descriptors for Product Options."""


import datetime

from . import exceptions


class OptionDescriptor:

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
        return value

    def clean(self, value):
        return str(value)


class PackageTypeOption(OptionDescriptor):

    def __init__(self):
        super().__init__('Package Type')

    def __set__(self, instance, value):
        value = value.strip()
        non_large_letter_values = (
            instance.PACKET, instance.HEAVY_AND_LARGE, instance.COURIER)
        if value == instance.LARGE_LETTER:
            super().__set__(instance, instance.LARGE_LETTER)
            instance.large_letter_compatible = True
        elif value in non_large_letter_values:
            super().__set__(instance, value)
            instance.large_letter_compatible = False
        else:
            raise ValueError('"{}" is not a valid package type'.format(value))


class DateOption(OptionDescriptor):

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value is None:
            return None
        year, month, day = value.split('-')
        return datetime.date(
            year=int(year), month=int(month), day=int(day))

    def clean(self, value):
        return super().clean(value.strftime('%Y-%m-%d'))


class FloatOption(OptionDescriptor):

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if not value:
            return float(value)


class BoolOption(OptionDescriptor):

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


class ListOption(OptionDescriptor):

    def __init__(self, option_name, delimiter='|'):
        self.delimiter = delimiter
        super().__init__(option_name)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value is None:
            return []
        return value.split(self.delimiter)

    def clean(self, value):
        return super().clean(self.delimiter.join([str(v) for v in value]))
