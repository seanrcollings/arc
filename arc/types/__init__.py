"""
.. include:: ../../wiki/Data-Types.md
"""

from arc.errors import ConversionError, CommandError
from arc.color import fg, effects as ef
from .converters import *
from .helpers import *
from .type_store import register, type_store


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
    except ConversionError as e:
        raise CommandError(
            f"Argument {fg.BLUE}{name}{ef.CLEAR} expected {e.expected}, but was "
            f"{fg.YELLOW}{value}{ef.CLEAR}. {e.helper_text}"
        ) from e

    return value
