import sys

from arc.types import ArcType
from arc.color import fg, effects
from arc.errors import ConversionError, ArcError

from .converters import *
from .converters import get_converter, is_alias, is_enum

__all__ = [
    "StringConverter",
    "BytesConverter",
    "IntConverter",
    "FloatConverter",
    "BoolConverter",
    "ListConverter",
    "FileConverter",
    "AliasConverter",
    "EnumConverter",
    "RangeConverter",
]


def convert(value, kind, name: Optional[str] = None):
    """Converts the provided string to the provided type

    :param value: value to convert
    :param kind: type to attempt the convertion to
    :param name: optional descrive name of the argument
    """
    converter_name = __get_converter_name(kind)
    converter_cls = get_converter(converter_name)

    if converter_cls is not None:
        converter = converter_cls(kind)
    else:
        raise ArcError(f"No converter found for type: {kind}")

    try:
        value = converter.convert(value)

    except ConversionError as e:
        if name:
            error_message = (
                f"Argument {fg.YELLOW}{name}={value}{effects.CLEAR} could not "
                f"be converted to type {fg.YELLOW}{converter.annotation}{effects.CLEAR}"
            )
        else:
            error_message = (
                f"Value: {e.value} could not be"
                f" converted to '{converter.annotation}'"
            )

        print(error_message)
        if e.helper_text is not None:
            print(e.helper_text)
        sys.exit(1)

    return value


def __get_converter_name(annotation) -> str:
    """Returns the converter name for
    the provided type annotation
    """

    if is_alias(annotation):
        if issubclass(annotation.__origin__, ArcType):  # type: ignore
            return annotation.__origin__.__name__.lower()  # type: ignore
        return "alias"
    elif is_enum(annotation):
        return "enum"

    return annotation.__name__
