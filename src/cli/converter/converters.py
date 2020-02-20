# Allow it to be recursive?? - <array:<int:number>>

import sys
from cli.converter.base_converter import BaseConverter
from cli.converter import ConversionError


class StringConverter(BaseConverter):
    convert_to = "string"
    convert = str


class IntConverter(BaseConverter):
    convert_to = "integer"
    convert = int


class FloatConverter(BaseConverter):
    convert_to = "float"
    convert = float


class ByteConverter(BaseConverter):
    convert_to = "byte"
    convert = str.encode


class BoolConverter(BaseConverter):
    convert = bool
    convert_to = "boolean"


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
        else:
            raise ConversionError(
                f"String '{value}' could not be converted to a 'boolean'")


class IntBoolConverter(BaseConverter):
    '''
        Converts an int to a boolean.
        0 - False
        All other ints / floats - True
    '''
    convert_to = "boolean"

    @classmethod
    def convert(cls, value):
        try:
            value = int(value)
        except ValueError:
            raise ConversionError(
                f"The string '{value}' could not be converted to an 'int'")
        return value != 0


class ListConverter(BaseConverter):
    '''
        Converts arguement into an array
        argument: my_list=1,2,3,4,5,6
        return : ["1", "2", "3", "4", "5", "6"
    '''
    @classmethod
    def convert(cls, value):
        return value.replace(" ", "").split(",")


# Dictionary Conversion... etc....
