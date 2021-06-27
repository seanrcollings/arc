"""Callbacks that check the validitiy of some type. Upon fail, should raise a ValidationError"""
import os
from typing import Union
from pathlib import Path
from arc.color import fg, effects
from arc import errors

from .callbacks import before


@before(inherit=False)
def in_range(arg: str, smallest: int, largest: int):
    def inner(arguments):
        value = arguments[arg]
        if value < smallest or value > largest:
            raise errors.ValidationError(
                f"Argument {fg.BLUE}{arg}{effects.CLEAR} must be within range "
                f"{fg.YELLOW}{smallest}-{largest}{effects.CLEAR}"
            )

    return inner


@before(inherit=False)
def valid_path(arg: str):
    def inner(arguments):
        path: Union[str, Path] = arguments[arg]
        if not os.path.exists(str(path)):
            raise errors.ValidationError(
                f"Path {fg.YELLOW}{path}{effects.CLEAR} doest not exist"
            )

    return inner
