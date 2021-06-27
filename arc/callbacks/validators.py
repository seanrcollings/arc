"""Callbacks that check the validitiy of some type. Upon fail, should raise a ValidationError"""
from arc.color import fg, effects
from arc import errors

from .callbacks import before, around, after


@before
def in_range(arg: str, smallest: int, largest: int):
    def inner(arguments):
        value = arguments[arg]
        if value < smallest or value > largest:
            raise errors.ValidationError(
                f"Argument {fg.BLUE}{arg}{effects.CLEAR} must be within range "
                f"{fg.YELLOW}{smallest}-{largest}{effects.CLEAR}"
            )

    return inner
