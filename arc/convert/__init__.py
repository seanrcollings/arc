from arc.errors import ConversionError, CommandError
from arc.color import fg, effects as ef

from .converters import *
from .converters import get_converter, BaseConverter


def convert(value, kind, name: str = ""):
    """Converts the provided string to the provided type

    :param value: value to convert
    :param kind: type to attempt the convertion to
    :param name: optional descrive name of the argument
    """
    # pylint: disable=import-outside-toplevel
    from arc.utils import handle

    converter_cls = get_converter(kind)
    converter = converter_cls(kind)

    with handle(CommandError):
        try:
            value = converter.convert(value)
        except ConversionError as e:
            raise CommandError(
                f"Argument {fg.BLUE}{name}{ef.CLEAR} expected {e.expected}, but was "
                f"{fg.YELLOW}{value}{ef.CLEAR}. {e.helper_text}"
            ) from e

    return value
