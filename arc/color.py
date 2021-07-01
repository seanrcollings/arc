from typing import Union


class Color(str):
    """Color class, extends str"""

    ESCAPE = "\033["

    def __new__(cls, content, extra="m"):

        obj = str.__new__(cls, f"{cls.ESCAPE}{content}{extra}")  # type: ignore
        return obj

    def __init__(self, code, *_args):
        super().__init__()
        self.code = code

    @property
    def bright(self):
        return Color(self.code + 60)


def _rgb(val: int, red: int = 0, green: int = 0, blue: int = 0):
    return f"\033[{val};2;{red};{green};{blue}m"


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
    BLACK    = Color(30)
    RED      = Color(31)
    GREEN    = Color(32)
    YELLOW   = Color(33)
    BLUE     = Color(34)
    MAGENTA  = Color(35)
    CYAN     = Color(36)
    WHITE    = Color(37)
    GREY     = BLACK.bright
    ARC_BLUE = '\x1b[38;2;59;192;240m'

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
    BLACK    = Color(40)
    RED      = Color(41)
    GREEN    = Color(42)
    YELLOW   = Color(43)
    BLUE     = Color(44)
    MAGENTA  = Color(45)
    CYAN     = Color(46)
    WHITE    = Color(47)
    GREY     = BLACK.bright
    ARC_BLUE = '\x1b[38;2;59;192;240m'

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
    CLEAR         = Color(0)
    BOLD          = Color(1)
    ITALIC        = Color(3)
    UNDERLINE     = Color(4)
    STRIKETHROUGH = Color(9)

# fmt: on
