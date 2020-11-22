from typing import Dict, Type, Optional, Union
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
]

converter_mapping: Dict[str, Type[BaseConverter]] = {
    "str": StringConverter,
    "int": IntConverter,
    "float": FloatConverter,
    "bytes": BytesConverter,
    "bool": BoolConverter,
    "sbool": StringBoolConverter,
    "ibool": IntBoolConverter,
    "list": ListConverter,
}


def get_converter(key: Union[str, type]) -> Optional[Type[BaseConverter]]:
    if isinstance(key, type):
        key = key.__name__
    return converter_mapping.get(key)
