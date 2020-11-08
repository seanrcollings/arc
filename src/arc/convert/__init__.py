from typing import _GenericAlias as GenericAlias  # type: ignore
from arc.errors import ConversionError
from arc.convert.base_converter import BaseConverter
from arc.convert.converters import *

__all__ = [
    "StringConverter",
    "BytesConverter",
    "IntConverter",
    "FloatConverter",
    "BoolConverter",
    "StringBoolConverter",
    "IntBoolConverter",
    "ListConverter",
    "FileConverter",
]


def is_alias(alias):
    return isinstance(alias, GenericAlias)
