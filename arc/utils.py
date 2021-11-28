import functools
import re
import time
from types import MethodType
from typing import Callable

from arc import logging, typing as at
from arc.color import fg, effects, colorize

logger = logging.getArcLogger("util")


IDENT = r"[a-zA-Z-_0-9]+"


def indent(string: str, distance="\t", split="\n"):
    """Indents the block of text provided by the distance"""
    return f"{distance}" + f"{split}{distance}".join(string.split(split))


def header(contents: str):
    logger.debug(colorize(f"{contents:^35}", effects.UNDERLINE, effects.BOLD, fg.BLUE))


def clean(string):
    """Gets rid of escape sequences"""
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


def timer(name):
    """Decorator for timing functions
    will only time if config.debug is set to True
    """

    def wrapper(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):

            start_time = time.time()
            return_value = func(*args, **kwargs)
            end_time = time.time()
            logger.info(
                "%sCompleted %s in %ss%s",
                fg.GREEN,
                name,
                round(end_time - start_time, 5),
                effects.CLEAR,
            )
            return return_value

        return decorator

    return wrapper


# TODO: get rid of this
class symbol:
    __symbols__: dict[str, "symbol"] = {}

    def __new__(cls, name, *args, **kwargs):
        if name in cls.__symbols__:
            return cls.__symbols__[name]

        obj = super().__new__(cls, *args, **kwargs)  # type: ignore
        cls.__symbols__[name] = obj
        return obj

    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

    def __repr__(self):
        return f"<symbol : {self.__name}>"

    def __hash__(self):
        return hash(self.__name)

    def __eq__(self, other):
        return self is other

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    @property
    def name(self):
        return self.__name


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


def dispatch_args(func: Callable, *args):
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
