# Allow it to be recursive?? - <array:<int:number>>

import re
from arc.converter.base_converter import BaseConverter
from arc.converter import ConversionError


class StringConverter(BaseConverter):
    convert_to = "string"
    convert = str


class IntConverter(BaseConverter):
    convert_to = "integer"

    def convert(self, value):
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, "Value must be a whole number integer")


class FloatConverter(BaseConverter):
    convert_to = "float"

    def convert(self, value):
        try:
            return float(value)
        except ValueError:
            raise ConversionError(value, "Value must be a number (1.3, 4, 1.7)")


class ByteConverter(BaseConverter):
    convert_to = "byte"

    def convert(self, value):
        return value.encode()


class BoolConverter(BaseConverter):
    convert_to = "boolean"
    convert = bool


class StringBoolConverter(BaseConverter):
    """Converts a string to a boolean
    True / true - True
    False / false - False
    """

    convert_to = "boolean"

    def convert(self, value):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False

        raise ConversionError(value, "sbool only accepts true or false")


class IntBoolConverter(BaseConverter):
    """Converts an int to a boolean.
    0 - False
    All other ints / floats - True
    """

    convert_to = "boolean"

    def convert(self, value):
        if value.isnumeric():
            value = int(value)
            return value != 0
        raise ConversionError(value, "ibool only accepts whole number integers")


class ListConverter(BaseConverter):
    """Converts arguement into an array
    argument: my_list=1,2,3,4,5,6
    return : ["1", "2", "3", "4", "5", "6"]
    """

    convert_to = "list"

    def convert(self, value):
        if "," in value:
            return value.replace(" ", "").split(",")
        raise ConversionError(
            value, "ListConverter only accepts comma seperated strings"
        )


# Dictionary Conversion... etc....
