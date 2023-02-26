"""Module contains code relavent to ANSI escape codes"""
import typing as t
import re
import functools


class Ansi:
    """Utility methods for ANSI color codes"""

    def __init__(self, content: t.Any):
        self.__content = content

    def __str__(self):
        return f"\033[{self.__content}"

    @classmethod
    def clean(cls, string: str):
        """Gets rid of escape sequences"""
        return cls.__ansi_escape().sub("", string)

    @classmethod
    def len(cls, string: str) -> int:
        """Length of a string, not including escape sequences"""
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

    @classmethod
    @functools.cache
    def __ansi_escape(self):
        return re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")


# fmt: off
class fg:
    """Foreground colors"""
    BLACK          = "\033[30m"
    RED            = "\033[31m"
    GREEN          = "\033[32m"
    YELLOW         = "\033[33m"
    BLUE           = "\033[34m"
    MAGENTA        = "\033[35m"
    CYAN           = "\033[36m"
    WHITE          = "\033[37m"
    GREY           = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"
    ARC_BLUE       = "\033[38;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **foreground** escape
        sequence for the provided rgb values"""
        return _rgb(38, red, green, blue)

    @staticmethod
    def hex(hex_code: str | int):
        """Returns the **foreground** escape
        sequence for the provided hex values"""
        return _rgb(38, *_hex_to_rgb(hex_code))


class bg:
    """Background colors"""
    BLACK          = "\033[40m"
    RED            = "\033[41m"
    GREEN          = "\033[42m"
    YELLOW         = "\033[43m"
    BLUE           = "\033[44m"
    MAGENTA        = "\033[45m"
    CYAN           = "\033[46m"
    WHITE          = "\033[47m"
    GREY           = "\033[100m"
    BRIGHT_RED     = "\033[101m"
    BRIGHT_GREEN   = "\033[102m"
    BRIGHT_YELLOW  = "\033[103m"
    BRIGHT_BLUE    = "\033[104m"
    BRIGHT_MAGENTA = "\033[105m"
    BRIGHT_CYAN    = "\033[106m"
    BRIGHT_WHITE   = "\033[107m"
    ARC_BLUE       = "\033[48;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **background** escape
        sequence for the provided rgb values"""
        return _rgb(48, red, green, blue)

    @staticmethod
    def hex(hex_code: str | int):
        """Returns the **background** escape
        sequence for the provided hex value"""
        return _rgb(48, *_hex_to_rgb(hex_code))


class fx:
    """Other effects like `CLEAR` or `BOLD`.
    Support from terminal to terminal may vary"""
    CLEAR         = "\033[0m"
    BOLD          = "\033[1m"
    ITALIC        = "\033[3m"
    UNDERLINE     = "\033[4m"
    STRIKETHROUGH = "\033[9m"

# fmt: on


def _rgb(val: int, red: int = 0, green: int = 0, blue: int = 0) -> str:
    return f"\033[{val};2;{red};{green};{blue}m"


def _hex_to_rgb(hex_rep: str | int):
    def pull_apart(hex_string: str):
        return (
            int(hex_string[0:2], 16),
            int(hex_string[2:4], 16),
            int(hex_string[4:6], 16),
        )

    if isinstance(hex_rep, int):
        return pull_apart(hex(hex_rep).strip("0x"))
    elif isinstance(hex_rep, str):
        hex_rep = hex_rep.lstrip("#")
        if len(hex_rep) == 3:
            hex_rep = hex_rep + hex_rep[0:]
        return pull_apart(hex_rep)
    else:
        raise TypeError(f"type of hex_rep must be int or str, got: {type(hex_rep)}")


def colorize(string: str, *codes: str, clear: bool = True) -> str:
    """Applies colors / effects to an entire string

    Args:
        string (str): String to colorize
        *codes (str): colors / effects to apply to the strin
        clear (bool): Whether or not to append `effects.CLEAR`
            to the end of the string which will prevent any
            subsequent strings from recieving the styles. Defaults
            to True

    Returns:
        string: The colorized string
    """
    return f"{''.join(str(code) for code in codes)}{string}{fx.CLEAR if clear else ''}"
