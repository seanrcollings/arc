from __future__ import annotations
import functools
import os
import re
import sys
from types import MethodType
import typing as t
import arc.typing as at


def safe_issubclass(typ, classes: type | tuple[type, ...]) -> bool:
    try:
        return issubclass(typ, classes)
    except TypeError:
        return False


class Display:
    __display_members: list[str]

    def __init_subclass__(cls, members: list[str] | None = None) -> None:
        if members:
            cls.__display_members = members

    def __repr__(self):
        values = ", ".join(
            [
                f"{member}={repr(getattr(self, member))}"
                for member in self.__display_members
            ]
        )
        return f"{type(self).__name__}({values})"


def isgroup(cls: type):
    return getattr(cls, "__arc_group__", False)


noop = lambda: ...


def cbreakpoint(cond: bool):
    return breakpoint if cond else noop


def isdunder(string: str, double_dunder: bool = False):
    if double_dunder:
        return string.startswith("__") and string.endswith("__")

    return string.startswith("__")


def dispatch_args(func: t.Callable, *args):
    """Calls the given `func` with the maximum
    slice of `*args` that it can accept. Handles
    function and method types

    For example:
    ```py
    def foo(bar, baz): # only accepts 2 args
        print(bar, baz)

    # Will call the provided function with the first
    # two arguments
    dispatch_args(foo, 1, 2, 3, 4)
    # 1 2
    ```
    """
    if isinstance(func, MethodType):
        unwrapped = func.__func__
    else:
        unwrapped = func  # type: ignore

    arg_count = unwrapped.__code__.co_argcount
    args = args[0 : arg_count - 1]
    return func(*args)


def discover_name():
    name = sys.argv[0]
    return os.path.basename(name)


def cmp(a, b) -> at.CompareReturn:
    """Compare two values

    Args:
        a (Any): First value
        b (Any): Second value

    Returns:
        - `a < b  => -1`
        - `a == b =>  0`
        - `a > b  =>  1`
    """
    return (a > b) - (a < b)


ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")


@functools.cache
def ansi_clean(string: str):
    """Gets rid of escape sequences"""
    return ansi_escape.sub("", string)


def ansi_len(string: str):
    length = 0
    in_escape_code = False

    for char in string:
        if in_escape_code and char == "m":
            in_escape_code = False
        elif char == "\x1b" or in_escape_code:
            in_escape_code = True
        else:
            length += 1

    return length
