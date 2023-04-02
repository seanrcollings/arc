"""Module contains code relavent to ANSI escape codes"""
import functools
import re
import typing as t


class Ansi:
    """Utility methods for ANSI color codes"""

    def __init__(self, content: t.Any):
        self.__content = content

    def __str__(self) -> str:
        return f"\033[{self.__content}"

    @classmethod
    def clean(cls, string: str) -> str:
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
    def __ansi_escape(self) -> re.Pattern[str]:
        return re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")


class fg:
    """Foreground colors"""

    BLACK = "\033[30m"
    """Escape code for foreground ANSI black"""
    RED = "\033[31m"
    """Escape code for foreground ANSI red"""
    GREEN = "\033[32m"
    """Escape code for foreground ANSI green"""
    YELLOW = "\033[33m"
    """Escape code for foreground ANSI yellow"""
    BLUE = "\033[34m"
    """Escape code for foreground ANSI blue"""
    MAGENTA = "\033[35m"
    """Escape code for foreground ANSI magenta"""
    CYAN = "\033[36m"
    """Escape code for foreground ANSI cyan"""
    WHITE = "\033[37m"
    """Escape code for foreground ANSI white"""
    GREY = "\033[90m"
    """Escape code for foreground ANSI grey"""
    BRIGHT_RED = "\033[91m"
    """Escape code for foreground ANSI bright red"""
    BRIGHT_GREEN = "\033[92m"
    """Escape code for foreground ANSI bright green"""
    BRIGHT_YELLOW = "\033[93m"
    """Escape code for foreground ANSI bright yellow"""
    BRIGHT_BLUE = "\033[94m"
    """Escape code for foreground ANSI brightblue"""
    BRIGHT_MAGENTA = "\033[95m"
    """Escape code for foreground ANSI bright magenta"""
    BRIGHT_CYAN = "\033[96m"
    """Escape code for foreground ANSI bright cyan"""
    BRIGHT_WHITE = "\033[97m"
    """Escape code for foreground ANSI bright white"""
    ARC_BLUE = "\033[38;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0) -> str:
        """Returns the **foreground** escape
        sequence for the provided rgb values"""
        return _rgb(38, red, green, blue)

    @staticmethod
    def hex(hex_code: str | int) -> str:
        """Returns the **foreground** escape
        sequence for the provided hex values"""
        return _rgb(38, *_hex_to_rgb(hex_code))


class bg:
    """Background colors"""

    BLACK = "\033[40m"
    """Escape code for background ANIS black"""
    RED = "\033[41m"
    """Escape code for background ANIS red"""
    GREEN = "\033[42m"
    """Escape code for background ANIS green"""
    YELLOW = "\033[43m"
    """Escape code for background ANIS yellow"""
    BLUE = "\033[44m"
    """Escape code for background ANIS blue"""
    MAGENTA = "\033[45m"
    """Escape code for background ANIS magenta"""
    CYAN = "\033[46m"
    """Escape code for background ANIS cyan"""
    WHITE = "\033[47m"
    """Escape code for background ANIS white"""
    GREY = "\033[100m"
    """Escape code for background ANIS grey"""
    BRIGHT_RED = "\033[101m"
    """Escape code for background ANIS bright red"""
    BRIGHT_GREEN = "\033[102m"
    """Escape code for background ANIS bright green"""
    BRIGHT_YELLOW = "\033[103m"
    """Escape code for background ANIS bright yellow"""
    BRIGHT_BLUE = "\033[104m"
    """Escape code for background ANIS bright blue"""
    BRIGHT_MAGENTA = "\033[105m"
    """Escape code for background ANIS bright magenta"""
    BRIGHT_CYAN = "\033[106m"
    """Escape code for background ANIS bright cyan"""
    BRIGHT_WHITE = "\033[107m"
    """Escape code for background ANIS bright white"""
    ARC_BLUE = "\033[48;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0) -> str:
        """Returns the **background** escape
        sequence for the provided rgb values"""
        return _rgb(48, red, green, blue)

    @staticmethod
    def hex(hex_code: str | int) -> str:
        """Returns the **background** escape
        sequence for the provided hex value"""
        return _rgb(48, *_hex_to_rgb(hex_code))


class fx:
    """Other effects like `CLEAR` or `BOLD`.
    Support from terminal to terminal may vary"""

    CLEAR = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"


def _rgb(val: int, red: int = 0, green: int = 0, blue: int = 0) -> str:
    return f"\033[{val};2;{red};{green};{blue}m"


def _hex_to_rgb(hex_rep: str | int) -> tuple[int, int, int]:
    def pull_apart(hex_string: str) -> tuple[int, int, int]:
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
