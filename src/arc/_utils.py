import sys
import os
import time
import functools
from typing import Dict
from arc import Config


def logger(*messages, state="info", sep=" ", end="\n"):
    """Arc logger utility. Logs various dev info.
    Can be turned on by setting Config.log or Config.debug to True
    """

    if Config.log or Config.debug:
        if state == "ok":
            print(*decorate_text_gen(*messages, tcolor="32"), sep=sep, end=end)
        elif state == "error":
            print(*decorate_text_gen(*messages, tcolor="31"), sep=sep, end=end)
        elif state == "debug" and Config.debug:
            print(*decorate_text_gen(*messages, tcolor="33"), sep=sep, end=end)
        elif state == "info":
            print(*decorate_text_gen(*messages, tcolor="37"), sep=sep, end=end)
        else:
            print(*messages, sep=sep, end=end)


def decorate_text_gen(*strings, tcolor="32", bcolor="40", style="1"):
    """Generator that colors a series of strings"""
    for string in strings:
        if not Config.decorate_text:
            yield string
        else:
            yield decorate_text(string, tcolor, bcolor, style)


def decorate_text(string, tcolor="32", bcolor="40", style="1"):
    return f"\033[{style};{tcolor}m{string}\033[00m"


def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    """Exception handler to overide the default one
    supresses traceback messages
    will be used if debug is set to False
    """
    if Config.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}: {exception}")


# sys.excepthook = exception_handler


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
        logger(f"Completed in {end_time - start_time:.2f}s", state="ok")

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
