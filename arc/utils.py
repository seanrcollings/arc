import functools
import io
import re
import sys
import time
from types import MethodType
import typing as t
import os

from arc import logging, typing as at
from arc.color import fg, effects, colorize

logger = logging.getArcLogger("util")


IDENT = r"[a-zA-Z-_0-9]+"


def indent(string: str, distance="\t", split="\n"):
    """Indents the block of text provided by the distance"""
    return f"{distance}" + f"{split}{distance}".join(string.split(split))


def header(contents: str):
    logger.debug(colorize(f"{contents:^35}", effects.UNDERLINE, effects.BOLD, fg.BLUE))


ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")


@functools.cache
def ansi_clean(string: str):
    """Gets rid of escape sequences"""
    return ansi_escape.sub("", string)


@functools.cache
def ansi_len(string: str):
    return len(ansi_clean(string))


FuncT = t.TypeVar("FuncT", bound=t.Callable[..., t.Any])


def timer(name):
    """Decorator for timing functions
    will only time if config.debug is set to True
    """

    def wrapper(func: FuncT) -> FuncT:
        @functools.wraps(func)
        def decorator(*args, **kwargs):

            start_time = time.time()
            try:

                return_value = func(*args, **kwargs)
            except BaseException as e:
                raise
            finally:
                end_time = time.time()
                logger.info(
                    "%sCompleted %s in %ss%s",
                    fg.GREEN,
                    name,
                    round(end_time - start_time, 5),
                    effects.CLEAR,
                )
            return return_value

        return t.cast(FuncT, decorator)

    return wrapper


# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(s1: str, s2: str):
    if len(s1) < len(s2):
        # pylint: disable=arguments-out-of-order
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = (
                previous_row[j + 1] + 1
            )  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row  # type: ignore

    return previous_row[-1]


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


def partition(item: t.Any, n: int):
    """Partion `item` into a list of elements `n` long"""
    return [item[index : index + n] for index in range(0, len(item), n)]


def discover_name():
    name = sys.argv[0]
    return os.path.basename(name)


class IoWrapper(io.StringIO):
    """Wraps an IO object to handle colored text.
    If the output looks to be a terminal, ansi-escape sequences will be allowed.
    If it does not look like a terminal,  ansi-escape sequences will be removed.
    """

    def __init__(self, wrapped: t.TextIO):
        self.wrapped = wrapped

    def write(self, message: str):
        if not self.wrapped.isatty():
            message = ansi_clean(message)

        self.wrapped.write(message)

    def flush(self):
        self.wrapped.flush()

    def __getattr__(self, attr: str):
        return getattr(self.wrapped, attr)
