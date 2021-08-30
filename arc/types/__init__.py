"""
.. include:: ../../wiki/Data-Types.md
"""

from arc import errors
from arc.color import fg, effects as ef
from .converters import *
from .helpers import *
from .type_store import register, type_store
from .params import (
    ParamType,
    Meta,
    meta,
    VarPositional,
    VarKeyword,
)


def convert(value, kind, name: str = ""):
    """Converts the provided string to the provided type
    Args:
        value: value to convert
        kind: type to attempt the convertion to
        name: optional descriptive name of the argument
    """

    converter_cls = type_store.get_converter(kind)
    converter = converter_cls(kind)

    try:
        value = converter.convert(value)
    except errors.ConversionError as e:
        raise errors.ArgumentError(
            f"Argument {fg.BLUE}{name}{ef.CLEAR} expected {e.expected}, but was "
            f"{fg.YELLOW}{value}{ef.CLEAR}. {e.helper_text}"
        ) from e

    return value
