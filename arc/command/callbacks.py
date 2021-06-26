from typing import Literal
from .command import Command


def callback(when: Literal["before", "around", "after"]):
    def wrapper(func):
        def register_wrapper(register_func):
            def register(command: Command):
                command.executor.register_callback(when, register_func)
                return command

            return register

        def handle_args(*args):
            if isinstance(args[0], Command):
                return register_wrapper(func)(args[0])
            else:
                inner = func(*args)
                return register_wrapper(inner)

        return handle_args

    return wrapper


def before(func):
    return callback("before")(func)


def around(func):
    return callback("around")(func)


def after(func):
    return callback("after")(func)


def skip(*skip_callbacks):
    def wrapper(command: Command):
        unwrapped = {c.__wrapped__ for c in skip_callbacks}
        callbacks: set
        for callbacks in command.executor.callbacks.values():  # type: ignore
            intersect = callbacks.intersection(unwrapped)
            for to_skip in intersect:
                callbacks.remove(to_skip)

        return command

    return wrapper
