from functools import cached_property
from typing import Union


class Ansi(str):
    """Color class, extends str"""

    ESCAPE = "\033["

    def __new__(cls, content):
        obj = str.__new__(cls, f"{cls.ESCAPE}{content}m")
        return obj

    def __init__(self, code, *_args):
        super().__init__()
        self.code = code


def _rgb(val: int, red: int = 0, green: int = 0, blue: int = 0) -> Ansi:
    return Ansi(f"{val};2;{red};{green};{blue}")


def _hex_to_rgb(hex_rep: Union[str, int]):
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


# fmt: off
class fg:
    """Foreground colors"""
    BLACK          = Ansi(30)
    RED            = Ansi(31)
    GREEN          = Ansi(32)
    YELLOW         = Ansi(33)
    BLUE           = Ansi(34)
    MAGENTA        = Ansi(35)
    CYAN           = Ansi(36)
    WHITE          = Ansi(37)
    GREY           = Ansi(90)
    BRIGHT_RED     = Ansi(91)
    BRIGHT_GREEN   = Ansi(92)
    BRIGHT_YELLOW  = Ansi(93)
    BRIGHT_BLUE    = Ansi(94)
    BRIGHT_MAGENTA = Ansi(95)
    BRIGHT_CYAN    = Ansi(96)
    BRIGHT_WHITE   = Ansi(97)
    ARC_BLUE       = Ansi('38;2;59;192;240')

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **foreground** ansi escape
        sequence for the provided rgb values"""
        return _rgb(38, red, green, blue)

    @staticmethod
    def hex(hex_code: Union[str, int]):
        """Returns the **foreground** ansi escape
        sequence for the provided hex values"""
        return _rgb(38, *_hex_to_rgb(hex_code))


class bg:
    """Background colors"""
    BLACK          = Ansi(40)
    RED            = Ansi(41)
    GREEN          = Ansi(42)
    YELLOW         = Ansi(43)
    BLUE           = Ansi(44)
    MAGENTA        = Ansi(45)
    CYAN           = Ansi(46)
    WHITE          = Ansi(47)
    GREY           = Ansi(100)
    BRIGHT_RED     = Ansi(101)
    BRIGHT_GREEN   = Ansi(102)
    BRIGHT_YELLOW  = Ansi(103)
    BRIGHT_BLUE    = Ansi(104)
    BRIGHT_MAGENTA = Ansi(105)
    BRIGHT_CYAN    = Ansi(106)
    BRIGHT_WHITE   = Ansi(107)
    ARC_BLUE       = Ansi('48;2;59;192;240')

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **background** ansi escape
        sequence for the provided rgb values"""
        return _rgb(48, red, green, blue)

    @staticmethod
    def hex(hex_code: Union[str, int]):
        """Returns the **"background"** ansi escape
        sequence for the provided hex value"""
        return _rgb(48, *_hex_to_rgb(hex_code))


class effects:
    """Other effects"""
    CLEAR         = Ansi(0)
    BOLD          = Ansi(1)
    ITALIC        = Ansi(3)
    UNDERLINE     = Ansi(4)
    STRIKETHROUGH = Ansi(9)

# fmt: on


class colored(str):
    """`str` subclass that does not consider escape
    characters in things like length and formatting"""

    @cached_property
    def _cleaned(self):
        from arc import utils

        return utils.ansi_clean(self)

    def __format__(self, spec: str):
        formatted = format(self._cleaned, spec)
        return formatted.replace(self._cleaned, self)

    def split(self, *args, **kwargs):
        return [colored(s) for s in super().split(*args, **kwargs)]


def colorize(string: str, *codes: str, clear: bool = True):
    """Applies colors / effects to an entire string

    Args:
        string (str): String to colorize
        *codes (Ansi): colors / effects to apply to the string
        clear (bool): Whether or not to append `effects.CLEAR`
            to the end of the string which will prevent any
            subsequent strings from recieving the styles. Defaults
            to True

    Returns:
        str: The colorized string
    """
    return f"{''.join(str(code) for code in codes)}{string}{effects.CLEAR if clear else ''}"
