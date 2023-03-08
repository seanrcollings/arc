"""This module contains various functions that get exposed to the external interface.
Notabally, the things in here should only be here if there is no better location for them to exist"""
from __future__ import annotations
import typing as t
from arc import errors
from arc.types.type_info import TypeInfo
from arc.types.helpers import convert_type
from arc import utils
import arc.typing as at


def convert(value: str, type: type):
    info = TypeInfo.analyze(type)
    converted = convert_type(info.resolved_type, value, info)

    for middleware in info.middleware:
        converted = utils.dispatch_args(middleware, converted, None)

    return converted


def exit(code: int = 0, message: str | None = None) -> t.NoReturn:
    """Exits the application with `code`.
    Optionally recieves a `message` that will be written
    to stderr before exiting"""
    raise errors.Exit(code, message)
