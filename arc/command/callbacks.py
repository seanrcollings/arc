import functools
from typing import Literal
from .command import Command

CallbackTime = Literal["before", "around", "after"]


def register_wrapper(when: CallbackTime, func, **kwargs):
    def register(command: Command):
        command.executor.register_callback(when, func, **kwargs)
        return command

    return register


def callback(when: CallbackTime, **options):
    def wrapper(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            if isinstance(args[0], Command):
                return register_wrapper(when, func, **options)(args[0])

            inner = func(*args, **kwargs)
            return register_wrapper(when, inner, **options)

        return handle_args

    return wrapper


def callback_helper(when: CallbackTime, func=None, *, inherit=True):
    """Acts as an intermediary between the actual
    `callback` function and the other callback helpers.
    Allows the decorators to be called in either of these two ways
    ```py
    @before
    def foo(): ...

    @before()
    def bar(): ...
    ```
    """
    wrapped = callback(when, inherit=inherit)
    if func:
        return wrapped(func)
    return wrapped


def before(*args, **kwargs):
    return callback_helper("before", *args, **kwargs)


def after(*args, **kwargs):
    return callback_helper("after", *args, **kwargs)


def around(*args, **kwargs):
    return callback_helper("around", *args, **kwargs)


def skip(*skip_callbacks):
    def wrapper(command: Command):
        unwrapped = {c.__wrapped__ for c in skip_callbacks}
        callbacks: set
        for callbacks in command.executor.callbacks.values():
            intersect = callbacks.intersection(unwrapped)
            for to_skip in intersect:
                callbacks.remove(to_skip)

        return command

    return wrapper
