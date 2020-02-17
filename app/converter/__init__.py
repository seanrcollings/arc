__all__ = [
    "StringConverter", "ByteConverter", "IntConverter", "FloatConverter",
    "BoolConverter", "StringBoolConverter", "IntBoolConverter"
]


class ConversionError(Exception):
    '''Generalized Conversion error if a conversion failes for some reason'''
    pass


from app.converter.base_converter import BaseConverter
from app.converter.converters import *
