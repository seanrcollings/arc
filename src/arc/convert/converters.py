from arc.convert.base_converter import BaseConverter
from arc.convert import ConversionError


class StringConverter(BaseConverter):
    convert_to = str


class IntConverter(BaseConverter):
    convert_to = int

    def convert(self, value):
        if value.isnumeric():
            return int(value)
        raise ConversionError(value, "Value must be a whole number integer")


class FloatConverter(BaseConverter):
    convert_to = float

    def convert(self, value):
        try:
            return float(value)
        except ValueError:
            raise ConversionError(value, "Value must be a number (1.3, 4, 1.7)")


class BytesConverter(BaseConverter):
    convert_to = bytes

    def convert(self, value):
        return value.encode()


# !! DEPRECATED !!
# Honestly, I don't think these will ever get called
# Since bool annotations get matched with flags and not options
class BoolConverter(BaseConverter):
    convert_to = bool


class StringBoolConverter(BaseConverter):
    """Converts a string to a boolean
    True / true - True
    False / false - False
    """

    convert_to = bool

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

    convert_to = bool

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

    convert_to = list

    def convert(self, value):
        if "," in value:
            return value.replace(" ", "").split(",")
        raise ConversionError(
            value, "ListConverter only accepts comma seperated strings"
        )


# Dictionary Conversion... etc....
