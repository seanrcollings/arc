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
        raise ConversionError(value, cls.convert_to)


class FloatConverter(BaseConverter):
    convert_to = "float"
    convert = float


class ByteConverter(BaseConverter):
    convert_to = "byte"
    convert = str.encode


class BoolConverter(BaseConverter):
    convert_to = "boolean"
    convert = bool


class StringBoolConverter(BaseConverter):
    '''
        Converts a string to a boolean
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

        raise ConversionError(value, cls.convert_to)


class IntBoolConverter(BaseConverter):
    '''
        Converts an int to a boolean.
        0 - False
        All other ints / floats - True
    '''
    convert_to = "boolean"

    @classmethod
    def convert(cls, value):
        if value.isnumeric():
            value = int(value)
            return value != 0
        raise ConversionError(value, cls.convert_to)


class ListConverter(BaseConverter):
    '''
        Converts arguement into an array
        argument: my_list=1,2,3,4,5,6
        return : ["1", "2", "3", "4", "5", "6"
    '''
    convert_to = "list"

    @classmethod
    def convert(cls, value):
        return value.replace(" ", "").split(",")


# Dictionary Conversion... etc....
