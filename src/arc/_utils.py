import logging
import os
import time
import functools
from typing import Dict
from arc import Config


class MyFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelno
        message = record.getMessage()
        if level == logging.DEBUG:
            return decorate_text(message, tcolor=33)
        elif level == logging.INFO:
            return decorate_text(message, tcolor=32)

        return decorate_text(message, tcolor=31)


logger = logging.getLogger("arc_logger")
handler = logging.StreamHandler()
formatter = MyFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)


def decorate_text(string, tcolor="32", bcolor="40", style="1"):
    if Config.decorate_text:
        return f"\033[{style};{tcolor}m{string}\033[00m"
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
    will only time if Config.debug is set to True
    """

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Completed in {end_time - start_time:.2f}s")

    return decorator


class symbol:
    __symbols__: Dict[str, object] = {}
    # use object to get rid of mypy error, will actually be of type symbol

    def __new__(cls, name, *args, **kwargs):
        if name in cls.__symbols__:
            return cls.__symbols__[name]

        obj = super().__new__(cls, *args, **kwargs)
        cls.__symbols__[name] = obj
        return obj

    def __init__(self, name):
        self.__name = name

    def __str__(self):
        return self.__name

    def __hash__(self):
        return hash(self.__name)

    def __eq__(self, other):
        return self.__name == other
