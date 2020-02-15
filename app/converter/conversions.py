from app.converter.base_converter import BaseConverter
from app.converter import ConversionError

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
    convert_to = "boolean"

    @classmethod
    def convert(cls, value):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise ConversionError(
                f"Error: string {value} coult not be converted to a boolean")

# Array conversion, Dictionary Conversion... etc....
