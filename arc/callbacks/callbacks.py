from __future__ import annotations
from typing import Literal, Callable, Any, Generator, TypeVar, Union, TYPE_CHECKING
import functools

from arc.result import Result

if TYPE_CHECKING:
    from arc.command import Command

CallbackTime = Literal["before", "around", "after"]


def register_wrapper(when: CallbackTime, func, **kwargs):
    def register(command: Command):
        command.executable.callback_store.register_callback(when, func, **kwargs)
        return command

    return register


def callback(when: CallbackTime, **options):
    """Wraps a function so it can be used as
    a command callback

    Args:
        when (CallbackTime): When the callback should fire (before, after, or around)
    """

    def wrapper(func):
        @functools.wraps(func)
        def handle_args(*args, **kwargs):
            from arc.command import Command

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


T = TypeVar("T")
Callback = Union[T, Callable[..., T]]

Before = Callable[[dict[str, Any]], None]
After = Callable[[Result], None]
Around = Callable[[dict[str, Any]], Generator[None, Result, None]]


def before(func: Callback[Before] = None, *, inherit=True) -> Callable[..., Command]:
    return callback_helper("before", func=func, inherit=inherit)


def after(func: Callback[After] = None, *, inherit=True) -> Callable[..., Command]:
    return callback_helper("after", func=func, inherit=inherit)


def around(func: Callback[Around] = None, *, inherit=True) -> Callable[..., Command]:
    return callback_helper("around", func=func, inherit=inherit)


def skip(*skip_callbacks):
    """Removes callbacks from command"""

    def wrapper(command: Command):
        unwrapped = {c.__wrapped__ for c in skip_callbacks}
        callbacks: set
        for callbacks in command.executable.callback_store.callbacks.values():
            intersect = callbacks.intersection(unwrapped)
            for to_skip in intersect:
                callbacks.remove(to_skip)

        return command

    return wrapper
