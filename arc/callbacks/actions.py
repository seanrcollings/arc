"""Callbacks that perform some action on a type, should be treated with caution"""
import os
from arc.color import fg, effects
from arc import errors

from .callbacks import around


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
