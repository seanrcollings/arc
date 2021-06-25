from typing import Dict, Type, _GenericAlias as GenericAlias  # type: ignore
from contextlib import contextmanager
import traceback
import functools
import logging
import time
import sys

from arc.errors import NoOpError
from arc.color import fg, effects

IDENT = r"[a-zA-Z-_0-9]+"


def no_op():
    raise NoOpError()


def timer(name):
    """Decorator for timing functions
    will only time if config.debug is set to True
    """

    def wrapper(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            # pylint: disable=import-outside-toplevel
            from arc import logger

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


class symbol:
    __symbols__: Dict[str, "symbol"] = {}

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
        return self.__name == other

    @property
    def name(self):
        return self.__name


def indent(string: str, distance="\t", split="\n"):
    """Indents the block of text provided by the distance"""
    return f"{distance}" + f"{split}{distance}".join(string.split(split))


@contextmanager
def handle(*exceptions: Type[Exception], exit_code=1, handle=True):
    # pylint: disable=import-outside-toplevel
    from arc import config

    if handle:
        try:
            yield
        except exceptions as e:
            if config.loglevel == logging.DEBUG:
                raise e
            else:
                print(f"{effects.BOLD}{fg.RED}ERROR{effects.CLEAR}:", e)
                sys.exit(exit_code)
    else:
        yield


def format_exception(e: BaseException):
    return "".join(
        traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    )


def unwrap_type(annotation) -> type:
    """Handles unwrapping `GenericTypes`, `SpecialForms`, etc...
    To retrive the inner origin type.

    For Example:

    - `list[int] -> list`
    - `Union[int, str] -> Union`
    - `File[File.Read] -> File`
    - `list -> list`
    """
    if origin := getattr(annotation, "__origin__", None):
        return origin
    else:
        return annotation


def is_alias(alias):
    return isinstance(alias, GenericAlias) or getattr(alias, "__origin__", False)
