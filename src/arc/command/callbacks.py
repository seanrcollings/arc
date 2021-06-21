import functools
from typing import Literal
from .command import Command


def callback(when: Literal["before", "around", "after"]):
    def wrapper(func):
        @functools.wraps(func)
        def register(command: Command):
            command.executor.register_callback(when, func)
            return command

        return register

    return wrapper


def before(func):
    return callback("before")(func)


def around(func):
    return callback("around")(func)


def after(func):
    return callback("after")(func)


def skip(*remove_callbacks):
    def wrapper(command: Command):
        unwrapped = {c.__wrapped__ for c in remove_callbacks}
        callbacks: set
        for callbacks in command.executor.callbacks.values():  # type: ignore
            intersect = callbacks.intersection(unwrapped)
            for to_skip in intersect:
                callbacks.remove(to_skip)

        return command

    return wrapper
