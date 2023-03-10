from __future__ import annotations

import inspect
import typing as t
from types import MethodType

import arc.typing as at

if t.TYPE_CHECKING:
    from arc.define import Command


def display(*members: str):
    def __repr__(self):
        values = ", ".join(
            [f"{member}={repr(getattr(self, member))}" for member in members]
        )
        return f"{type(self).__name__}({values})"

    return __repr__


def dispatch_args(func: t.Callable, *args):
    """Calls the given `func` with the maximum
    slice of `*args` that it can accept. Handles
    function and method types

    For example:
    ```py
    def foo(bar, baz): # only accepts 2 args
        arc.print(bar, baz)

    # Will call the provided function with the first
    # two arguments
    dispatch_args(foo, 1, 2, 3, 4)
    # 1 2
    ```
    """
    # TODO: I haven't tested if this will capture
    # all callables, but it should hopefully.
    if isinstance(func, MethodType):
        arg_count = func.__func__.__code__.co_argcount - 1
    elif inspect.isfunction(func):
        arg_count = func.__code__.co_argcount
    else:
        arg_count = func.__call__.__func__.__code__.co_argcount - 1  # type: ignore

    args = args[0:arg_count]
    return func(*args)
