"""Converters for basic builtin types
This module does not include the converters for things like `list` or `tuple`
because those converters also handle their generic form (`list[int]`) and are
placed in `generic_convertrs.py`
"""
from arc.errors import ConversionError
from .base_converter import BaseConverter


class StringConverter(BaseConverter[str]):
    def convert(self, value: str) -> str:
        return str(value)


class IntConverter(BaseConverter[int]):
    def convert(self, value: str) -> int:
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, expected="a whole number integer")


class FloatConverter(BaseConverter[float]):
    def convert(self, value):
        try:
            return float(value)
        except ValueError as e:
            raise ConversionError(value, expected="a float (1.3, 4, 1.7)") from e


class BytesConverter(BaseConverter):
    def convert(self, value: str):
        return value.encode()


class BoolConverter(BaseConverter[bool]):
    """Converts a string to a boolean
    True / true - True
    False / false - False
    """

    def convert(self, value: str):
        if value.isnumeric():
            return bool(int(value))

        value = value.lower()
        if value in ("true", "t"):
            return True
        elif value in ("false", "f"):
            return False

        raise ConversionError(value, "'(t)rue' or '(f)alse' or a valid integer")


class IntBoolConverter(BaseConverter[bool]):
    """Converts an int to a boolean.
    0 - False
    All other ints / floats - True
    """

    def convert(self, value: str):
        if value.isnumeric():
            return int(value) != 0
        raise ConversionError(value, "ibool only accepts whole number integers")
