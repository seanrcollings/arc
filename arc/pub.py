"""This module contains various functions that get exposed to the external interface.
They could be placed along with the stuff they interact with, but this felt more convenient"""
from __future__ import annotations
import builtins
import sys
import typing as t
from arc import errors
from arc.color import colorize, fg
from arc.define.command import Command, namespace_callback
from arc.runtime import ExecMiddleware
from arc.present import Joiner, Ansi
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


def print(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    file: t.IO | None = None,
    flush: bool = False,
):
    """A wrapper around `print()` that handles removing escape
    codes when the output is not a TTY"""
    file = file or sys.stdout

    if file and not file.isatty():
        values = tuple(Ansi.clean(str(v)) for v in values)

    builtins.print(*values, sep=sep, end=end, file=file, flush=flush)


def err(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
):
    """Wrapper around `print()` that emits to stderr instead of stdout"""
    print(*values, sep=sep, end=end, file=sys.stderr, flush=flush)


def info(
    *values: object,
    sep: str | None = None,
    end: str | None = None,
    flush: bool = False,
):
    """Wrapper around `print()` that emits to stderr instead of stdout"""
    print(*values, sep=sep, end=end, file=sys.stderr, flush=flush)


def exit(code: int = 0, message: str | None = None) -> t.NoReturn:
    """Exits the application with `code`.
    Optionally recieves a `message` that will be written
    to stderr before exiting"""
    raise errors.Exit(code, message)


def usage(command: Command, help_prompt: bool = True):
    info(command.doc.usage())

    if help_prompt:
        help_call = colorize(
            f"{command.root.name} {Joiner.with_space(command.doc.fullname)} --help",
            fg.YELLOW,
        )
        info(f"{help_call} for more information")
