from typing import Union


def _rgb(val: int, red: int = 0, green: int = 0, blue: int = 0) -> str:
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
    BLACK          = "\033[30m"
    """Ansi escape code: `\\033[30m`"""
    RED            = "\033[31m"
    """Ansi escape code: `\\033[31m`"""
    GREEN          = "\033[32m"
    """Ansi escape code: `\\033[32m`"""
    YELLOW         = "\033[33m"
    """Ansi escape code: `\\033[33m`"""
    BLUE           = "\033[34m"
    """Ansi escape code: `\\033[34m`"""
    MAGENTA        = "\033[35m"
    """Ansi escape code: `\\033[35m`"""
    CYAN           = "\033[36m"
    """Ansi escape code: `\\033[36m`"""
    WHITE          = "\033[37m"
    """Ansi escape code: `\\033[37m`"""
    GREY           = "\033[90m"
    """Ansi escape code: `\\033[90m`"""
    BRIGHT_RED     = "\033[91m"
    """Ansi escape code: `\\033[91m`"""
    BRIGHT_GREEN   = "\033[92m"
    """Ansi escape code: `\\033[92m`"""
    BRIGHT_YELLOW  = "\033[93m"
    """Ansi escape code: `\\033[93m`"""
    BRIGHT_BLUE    = "\033[94m"
    """Ansi escape code: `\\033[94m`"""
    BRIGHT_MAGENTA = "\033[95m"
    """Ansi escape code: `\\033[95m`"""
    BRIGHT_CYAN    = "\033[96m"
    """Ansi escape code: `\\033[96m`"""
    BRIGHT_WHITE   = "\033[97m"
    """Ansi escape code: `\\033[97m`"""
    ARC_BLUE       = "\033[38;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **foreground** escape
        sequence for the provided rgb values"""
        return _rgb(38, red, green, blue)

    @staticmethod
    def hex(hex_code: Union[str, int]):
        """Returns the **foreground** escape
        sequence for the provided hex values"""
        return _rgb(38, *_hex_to_rgb(hex_code))


class bg:
    """Background colors"""
    BLACK          = "\033[40m"
    """Ansi escape code: `\\033[40m`"""
    RED            = "\033[41m"
    """Ansi escape code: `\\033[41m`"""
    GREEN          = "\033[42m"
    """Ansi escape code: `\\033[42m`"""
    YELLOW         = "\033[43m"
    """Ansi escape code: `\\033[43m`"""
    BLUE           = "\033[44m"
    """Ansi escape code: `\\033[44m`"""
    MAGENTA        = "\033[45m"
    """Ansi escape code: `\\033[45m`"""
    CYAN           = "\033[46m"
    """Ansi escape code: `\\033[46m`"""
    WHITE          = "\033[47m"
    """Ansi escape code: `\\033[47m`"""
    GREY           = "\033[100m"
    """Ansi escape code: `\\033[100m`"""
    BRIGHT_RED     = "\033[101m"
    """Ansi escape code: `\\033[101m`"""
    BRIGHT_GREEN   = "\033[102m"
    """Ansi escape code: `\\033[102m`"""
    BRIGHT_YELLOW  = "\033[103m"
    """Ansi escape code: `\\033[103m`"""
    BRIGHT_BLUE    = "\033[104m"
    """Ansi escape code: `\\033[104m`"""
    BRIGHT_MAGENTA = "\033[105m"
    """Ansi escape code: `\\033[105m`"""
    BRIGHT_CYAN    = "\033[106m"
    """Ansi escape code: `\\033[106m`"""
    BRIGHT_WHITE   = "\033[107m"
    """Ansi escape code: `\\033[107m`"""
    ARC_BLUE       = "\033[48;2;59;192;240m"
    """The blue used in arc branding"""

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        """Returns the **background** escape
        sequence for the provided rgb values"""
        return _rgb(48, red, green, blue)

    @staticmethod
    def hex(hex_code: Union[str, int]):
        """Returns the **background** escape
        sequence for the provided hex value"""
        return _rgb(48, *_hex_to_rgb(hex_code))


class effects:
    """Other effects. Support from terminal to terminal may vary"""
    CLEAR         = "\033[0m"
    """Remove any effects applied with escape codes"""
    BOLD          = "\033[1m"
    """Bold the text"""
    ITALIC        = "\033[3m"
    """Italicize the text"""
    UNDERLINE     = "\033[4m"
    """Underline the text"""
    STRIKETHROUGH = "\033[9m"
    """Strikethrough the text"""

# fmt: on


def colorize(string: str, *codes: str, clear: bool = True):
    """Applies colors / effects to an entire string

    Args:
        string (str): String to colorize
        *codes (str): colors / effects to apply to the strin
        clear (bool): Whether or not to append `effects.CLEAR`
            to the end of the string which will prevent any
            subsequent strings from recieving the styles. Defaults
            to True

    Returns:
        str: The colorized string
    """
    return f"{''.join(str(code) for code in codes)}{string}{effects.CLEAR if clear else ''}"
