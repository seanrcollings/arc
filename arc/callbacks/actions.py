"""Callbacks that perform some action on a type, should be treated with caution"""
from typing import TextIO
import os
import sys
from arc.color import fg, effects
from arc import errors
from arc.types.params import MISSING

from .callbacks import around, before


@around(inherit=False)
def open_file(argument: str, mode="r", *args, **kwargs):
    """Attempts to open the file given as the provided argument.
    Is not inherited by subcommands

    Args:
        argument (str): Name of the argument to attempt to open as a file
        mode (str, optional): Mode to open the file in. Defaults to "r" (read).

    All other arguments are passed to the `open()` call

    Raises:
        ActionError: If the provided path is not a file

    """

    def inner(arguments: dict):
        filepath = arguments[argument]
        if not os.path.isfile(filepath):
            raise errors.ActionError(
                f"{fg.YELLOW}{filepath}{effects.CLEAR} does not exist, or is not a file"
            )

        with open(filepath, mode, *args, **kwargs) as file:
            arguments[argument] = file
            yield

    return inner


def _input_stream(
    stream: TextIO, arguments: dict, argument: str, take_precedence: bool
):
    arg_value = arguments[argument]
    arg_exists = arg_value and arg_value is not MISSING
    if not arg_exists or take_precedence:
        arguments[argument] = stream.read()


@before(inherit=False)
def stdin(argument: str, take_precedence: bool = False):
    def inner(arguments: dict):
        _input_stream(sys.stdin, arguments, argument, take_precedence)

    return inner


@before(inherit=False)
def stderr(argument: str, take_precedence: bool = False):
    def inner(arguments: dict):
        _input_stream(sys.stderr, arguments, argument, take_precedence)

    return inner
