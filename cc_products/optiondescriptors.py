"""Descriptors for Product Options."""

import datetime

from . import exceptions


class OptionDescriptor:
    """Descriptor class for Product Options."""

    def __init__(self, option_name):
        """Set Product Option name."""
        self.option_name = option_name

    def __get__(self, instance, owner):
        return self.to_python(instance, owner)

    def __set__(self, instance, value):
        instance.options[self.option_name] = self.clean(value)

    def __delete__(self, instance):
        self.__set__(instance, "")

    def to_python(self, instance, owner):
        """Return Product Option value in the correct type for python."""
        if self.option_name not in instance.options:
            return None
        value = instance.options[self.option_name]
        return value

    def clean(self, value):
        """Format value for storage as a Product Option in Cloud Commerce."""
        return str(value)


class PackageTypeOption(OptionDescriptor):
    """Product Option Descriptor for the Package Type Product Option."""

    def __init__(self):
        """Set product option name."""
        super().__init__("Package Type")

    def __set__(self, instance, value):
        value = value.strip()
        non_large_letter_values = (
            instance.PACKET,
            instance.HEAVY_AND_LARGE,
            instance.COURIER,
        )
        if value in (instance.LARGE_LETTER, instance.LARGE_LETTER_SINGLE):
            super().__set__(instance, value)
            instance.large_letter_compatible = True
        elif value in non_large_letter_values:
            super().__set__(instance, value)
            instance.large_letter_compatible = False
        else:
            raise ValueError('"{}" is not a valid package type'.format(value))


class GenderOption(OptionDescriptor):
    """Product Option Descriptor for Gender."""

    def __init__(self):
        """Set product option name."""
        super().__init__("Gender")

    def __set__(self, isinstance, value):
        value = value.strip()
        valid_values = (
            isinstance.MENS,
            isinstance.GIRLS,
            isinstance.WOMENS,
            isinstance.BOYS,
            isinstance.BABY_BOYS,
            isinstance.BABY_GIRLS,
            isinstance.UNISEX_BABY,
        )
        if value in valid_values:
            super().__set__(value)
        else:
            raise ValueError('"{}" is not a valid gender'.format(value))


class DateOption(OptionDescriptor):
    """Product Option Descriptor for Product Options containing dates."""

    def to_python(self, *args, **kwargs):
        """Return Product Option value as datetime.datetime."""
        value = super().to_python(*args, **kwargs)
        if value is None:
            return None
        year, month, day = value.split("-")
        return datetime.date(year=int(year), month=int(month), day=int(day))

    def clean(self, value):
        """Return value as a string containting a formatted date."""
        return super().clean(value.strftime("%Y-%m-%d"))


class FloatOption(OptionDescriptor):
    """Product Option Descriptor for Product Options containing floats."""

    def to_python(self, *args, **kwargs):
        """Return Product Option value as a float."""
        value = super().to_python(*args, **kwargs)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


class BoolOption(OptionDescriptor):
    """Product Option Descriptor for boolean product options."""

    def __init__(self, option_name, true=None, false=None):
        """
        Set true, false and option name attributes.

        Args:
            option_name: Name of the Product Option.
            true: Value to return if Product Option Value is True.
            false: Value to return if Product Option Value is False.
        """
        self.true = true
        self.false = false
        super().__init__(option_name)

    def to_python(self, *args, **kwargs):
        """Return Product Option value as a bool."""
        value = super().to_python(*args, **kwargs)
        if value is None or value == self.false:
            return False
        if value == self.true:
            return True
        raise exceptions.OptionValueNotRecognised(value)

    def clean(self, value):
        """Return self.true if value is True, else False."""
        if value is True:
            return self.true
        return super().clean(self.false)


class ListOption(OptionDescriptor):
    """
    Product Option Descriptor for product options containing multiple values.

    Args:
        option_name: The name of the Product Option.
        delimiter: Character used to delimit listed values. Default: '|'.
    """

    def __init__(self, option_name, delimiter="|"):
        """Set delimiter."""
        self.delimiter = delimiter
        super().__init__(option_name)

    def to_python(self, *args, **kwargs):
        """Return list containing Product Option values."""
        value = super().to_python(*args, **kwargs)
        if value is None:
            return []
        return value.split(self.delimiter)

    def clean(self, value):
        """Return values as a delimited string."""
        return super().clean(self.delimiter.join([str(v) for v in value]))
