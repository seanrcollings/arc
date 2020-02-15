class ConversionError(Exception):
    pass


from app.converter.base_converter import BaseConverter
from app.converter.conversions import *

__all__ = ["StringConverter", "ByteConverter", "IntConverter", "FloatConverter", "BoolConverter"]