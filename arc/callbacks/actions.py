"""Callbacks that perform some action on a type, should be treated with caution"""
import os
from arc.color import fg, effects
from arc import errors

from .callbacks import before, around, after


@around(inherit=False)
def open_file(argument: str, mode="r", *args, **kwargs):
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
