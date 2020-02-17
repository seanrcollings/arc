__all__ = [
    "StringConverter", "ByteConverter", "IntConverter", "FloatConverter",
    "BoolConverter", "StringBoolConverter", "IntBoolConverter"
]


class ConversionError(Exception):
    '''Generalized Conversion error if a conversion failes for some reason'''
    pass


from cli.converter.base_converter import BaseConverter
from cli.converter.converters import *
