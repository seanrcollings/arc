import sys
from typing import cast

from arc.types import ArcGeneric
from arc.errors import ConversionError

from .base_converter import BaseConverter
from .converters import *

__all__ = [
    "StringConverter",
    "BytesConverter",
    "IntConverter",
    "FloatConverter",
    "BoolConverter",
    "ListConverter",
    "FileConverter",
    "AliasConverter",
]


def convert(value, kind):
    name = __get_converter_name(kind)
    converter_cls = get_converter(name)

    if converter_cls is not None:
        converter = converter_cls(kind)

    try:
        value = converter.convert(value)

    except ConversionError as e:
        print(f"Value: {e.value} could not be converted to '{converter.convert_to}'")
        if e.helper_text is not None:
            print(e.helper_text)
        sys.exit(1)

    return value


def __get_converter_name(annotation) -> str:
    """Returns the converter name for
    the provided type annotation
    """

    if is_alias(annotation):
        if issubclass(annotation.__origin__, ArcGeneric):  # type: ignore
            return annotation.__origin__.__name__.lower()  # type: ignore
        return "alias"
    return annotation.__name__
