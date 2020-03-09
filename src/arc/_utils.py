import sys
import os
from arc import Config


def logger(*messages, state="ok", level=3, sep=" ", end="\n"):
    '''Arc logger utility. Logs various dev info.
    Can be turned on by setting Config.log or Config.debug to True
    '''
    if level > Config.logger_level:
        return

    if Config.log or Config.debug:
        if state == "ok":
            print(*decorate_text_gen(*messages), sep=sep, end=end)
        elif state == "error":
            print(*decorate_text_gen(*messages, tcolor="31"), sep=sep, end=end)
        else:
            print(*decorate_text_gen(*messages, tcolor="33"), sep=sep, end=end)


def decorate_text_gen(*strings, tcolor="32", bcolor="40", style="1"):
    '''Generator that colors a series of strings'''
    for string in strings:
        if not Config.decorate_text:
            yield string
        else:
            yield decorate_text(string, tcolor, bcolor, style)


def decorate_text(string, tcolor="32", bcolor="40", style="1"):
    return f"\033[{style};{tcolor};{bcolor}m{string}\033[00m"


def exception_handler(exception_type,
                      exception,
                      traceback,
                      debug_hook=sys.excepthook):
    '''Exception handler to overide the default one
    supresses traceback messages
    will be used if debug is set to False
    '''
    if Config.debug:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}: {exception}")


sys.excepthook = exception_handler


def clear():
    '''Executes a clear screen command
    will work on any OS. Used in the CLI's
    interactive mode
    '''
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
