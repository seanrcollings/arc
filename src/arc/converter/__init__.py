__all__ = [
    "StringConverter",
    "ByteConverter",
    "IntConverter",
    "FloatConverter",
    "BoolConverter",
    "StringBoolConverter",
    "IntBoolConverter",
    "ListConverter",
]

import re
from typing import Tuple
from arc.errors import ConversionError
from arc.converter.base_converter import BaseConverter
from arc.converter.converters import *


def is_converter(string) -> bool:
    """Regex that matches to "<convertername:varname>"
    returns True if it does match, returns false otherwise
    """
    return re.match(r"<[^<>:]+:[^<>:]+>$", string) is not None


def parse_converter(string) -> Tuple[str, str]:
    """ Extracts the option name and the converter name
    from the provided string. Uses a similar regex as above.
    Ideally, check if it is a converter with is_conveter before
    calling this function

    :param string: converter string to be parsed. Should match this syntax: '<type:name>'

    :returns: tuple(name, converter)
    """

    regex = re.compile(r"<([^<>:]+):([^<>:]+)>$")
    matches = regex.match(string)

    if not matches:
        raise ValueError(f"{string} does not contain valid converter syntax")

    return matches.group(2), matches.group(1)
