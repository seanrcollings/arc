import sys
from arc.color import fg, effects
from arc.errors import ConversionError, ArcError

from .converters import *
from .converters import get_converter


__all__ = [
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
    # pylint: disable=import-outside-toplevel
    from arc.utils import logger, format_exception

    converter_cls = get_converter(kind)
    converter = converter_cls(kind)

    try:
        value = converter.convert(value)

    except ConversionError as e:
        if name:
            error_message = (
                f"{fg.RED}ERROR{effects.CLEAR}: Argument "
                f"{fg.YELLOW}{name}{effects.CLEAR} expected {e.expected}"
            )
        else:
            error_message = (
                f"Value: {e.value} could not be"
                f" converted to '{converter.annotation}'"
            )

        if e.helper_text:
            error_message += f"\n{fg.YELLOW}{e.helper_text}{effects.CLEAR}"

        logger.debug(format_exception(e))
        logger.error(error_message)
        raise e

    return value
