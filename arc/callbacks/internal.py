from typing import Callable
from arc.command.argument import NO_DEFAULT
from arc.callbacks.callbacks import CallbackTime
from arc import errors, color


def verify_args_filled(arguments: dict):
    for key, value in arguments.items():
        if value is NO_DEFAULT:
            raise errors.ValidationError(
                f"No value provided for argument: {color.colorize(key, color.fg.YELLOW)}",
            )


INTERNAL_CALLBACKS: dict[CallbackTime, set[Callable]] = {
    "before": {verify_args_filled},
    "after": set(),
    "around": set(),
}
