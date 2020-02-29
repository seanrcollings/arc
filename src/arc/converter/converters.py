# Allow it to be recursive?? - <array:<int:number>>
# TODO: Swap all converters to raise a Conversion exception if they will fail

import sys
from arc.converter.base_converter import BaseConverter
from arc.converter import ConversionError


class StringConverter(BaseConverter):
    convert_to = "string"
    convert = str


class IntConverter(BaseConverter):
    convert_to = "integer"

    @classmethod
    def convert(cls, value):
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, "Value must be a whole number integer")


class FloatConverter(BaseConverter):
    convert_to = "float"

    @classmethod
    def convert(cls, value):
        try:
            return float(value)
        except ValueError:
            raise ConversionError(value,
                                  "Value must be a number (1.3, 4, 1.7)")


class ByteConverter(BaseConverter):
    convert_to = "byte"

    @classmethod
    def convert(cls, value):
        return value.encode()


class BoolConverter(BaseConverter):
    convert_to = "boolean"
    convert = bool


class StringBoolConverter(BaseConverter):
    '''Converts a string to a boolean
    True / true - True
    False / false - False
    '''
    convert_to = "boolean"

    @classmethod
    def convert(cls, value):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False

        raise ConversionError(value, "sbool only accepts true or false")


class IntBoolConverter(BaseConverter):
    '''Converts an int to a boolean.
    0 - False
    All other ints / floats - True
    '''
    convert_to = "boolean"

    @classmethod
    def convert(cls, value):
        if value.isnumeric():
            value = int(value)
            return value != 0
        raise ConversionError(value,
                              "ibool only accepts whole number integers")


class ListConverter(BaseConverter):
    '''Converts arguement into an array
    argument: my_list=1,2,3,4,5,6
    return : ["1", "2", "3", "4", "5", "6"
    '''
    convert_to = "list"

    @classmethod
    def convert(cls, value):
        return value.replace(" ", "").split(",")


# Dictionary Conversion... etc....
