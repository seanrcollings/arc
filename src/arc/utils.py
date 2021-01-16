import logging
import os
import time
import functools
from typing import Dict
from abc import ABC, abstractmethod

from arc.color import fg, effects
from arc import config


class MyFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelno
        message = record.getMessage()
        if level == logging.DEBUG:
            return decorate_text(message, tcolor=fg.YELLOW)
        elif level == logging.INFO:
            return decorate_text(message, tcolor=fg.GREEN)

        return decorate_text(message, tcolor=fg.WHITE)


logger = logging.getLogger("arc_logger")
handler = logging.StreamHandler()
formatter = MyFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


def decorate_text(string, tcolor=fg.GREEN, bcolor=None, style=effects.BOLD):
    if config.decorate_text:
        return (
            f"{tcolor}"
            f"{bcolor if bcolor else ''}"
            f"{style}"
            f"{string}"
            f"{effects.CLEAR}"
        )
    return string


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
