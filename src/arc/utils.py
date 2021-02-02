import sys
import functools
import logging
import os
import time
import traceback
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Dict, Type

from arc import config


logger = logging.getLogger("arc_logger")
handler = logging.StreamHandler()
formatter = logging.Formatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


def clear():
    """Executes a clear screen command
    will work on any OS. Used in the CLI's
    interactive mode
    """
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def timer(func):
    """Decorator for timing functions
    will only time if config.debug is set to True
    """

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        logger.info("Completed in %ss", round(end_time - start_time, 2))

    return decorator


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


def indent(string: str, distance="\t", split="\n"):
    """Indents the block of text provided by the distance"""
    return f"{distance}" + f"{split}{distance}".join(string.split(split))


class Helpful(ABC):
    @abstractmethod
    def helper(self):
        ...


@contextmanager
def handle(*exceptions: Type[Exception], exit_code=1):
    try:
        yield
    except exceptions as e:
        if config.loglevel == logging.DEBUG:
            logger.debug(
                "".join(
                    traceback.format_exception(
                        etype=type(e), value=e, tb=e.__traceback__
                    )
                )
            )
        else:
            print(e)
        sys.exit(exit_code)
