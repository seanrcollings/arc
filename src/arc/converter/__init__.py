import re
from arc.errors import ConversionError
from arc.converter.base_converter import BaseConverter
from arc.converter.converters import *

__all__ = [
    "StringConverter", "ByteConverter", "IntConverter", "FloatConverter",
    "BoolConverter", "StringBoolConverter", "IntBoolConverter", "ListConverter"
]


def is_converter(string) -> bool:
    '''Regex that matches to "<convertername:varname>"
    returns True if it does match, returns false otherwise
    '''
    return re.match(r"<[^<>:]+:[^<>:]+>$", string) is not None
