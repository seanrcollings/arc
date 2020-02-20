__all__ = [
    "StringConverter", "ByteConverter", "IntConverter", "FloatConverter",
    "BoolConverter", "StringBoolConverter", "IntBoolConverter", "ListConverter"
]


class ConversionError(Exception):
    '''Generalized Conversion error if a conversion failes for some reason'''
    pass


from arc.converter.base_converter import BaseConverter
from arc.converter.converters import *
