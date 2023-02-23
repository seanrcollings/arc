import typing as t
from arc import present


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


class effects:
    """Other effects. Support from terminal to terminal may vary"""
    CLEAR         = "\033[0m"
    BOLD          = "\033[1m"
    ITALIC        = "\033[3m"
    UNDERLINE     = "\033[4m"
    STRIKETHROUGH = "\033[9m"

# fmt: on


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
    return f"{''.join(str(code) for code in codes)}{string}{effects.CLEAR if clear else ''}"


ColorLevel = t.Union[t.Type[bg], t.Type[fg]]


class Styled:
    def __init__(self, join_char: str = ""):
        self.__styled_contents: list[tuple[str, list[str]]] = []
        self.__current_content: str = ""
        self.__current_styles: list[str] = []
        self.__join_char = join_char

    def __str__(self) -> str:
        self.content("")

        return present.Joiner.join(
            (
                colorize(str(content), *styles, clear=True)
                for content, styles in self.__styled_contents
            ),
            self.__join_char,
        )

    def __len__(self) -> int:
        return sum(len(con) for con, _ in self.__styled_contents)

    def content(self, content: str):
        self.__current_content = content
        self.__current_styles = []
        self.__styled_contents.append((self.__current_content, self.__current_styles))
        return self

    def strip(self, chars: str):
        self.__current_content = self.__current_content.strip(chars)
        self.__styled_contents[-1] = (
            self.__current_content,
            self.__styled_contents[-1][1],
        )
        return self

    def style(self, style: str):
        self.__current_styles.append(style)
        return self

    def bold(self):
        return self.style(effects.BOLD)

    def italic(self):
        return self.style(effects.ITALIC)

    def underline(self):
        return self.style(effects.UNDERLINE)

    def striketrough(self):
        return self.style(effects.STRIKETHROUGH)

    def rgb(self, red: int = 0, green: int = 0, blue: int = 0, level: ColorLevel = fg):
        return self.style(level.rgb(red, green, blue))

    def hex(self, hexcode: str | int, level: ColorLevel = fg):
        return self.style(level.hex(hexcode))

    def _add_predefined_color(self, color: str, level: ColorLevel):
        return self.style(getattr(level, color))

    def black(self, level: ColorLevel = fg):
        return self._add_predefined_color("BLACK", level)

    def red(self, level: ColorLevel = fg):
        return self._add_predefined_color("RED", level)

    def green(self, level: ColorLevel = fg):
        return self._add_predefined_color("GREEN", level)

    def yellow(self, level: ColorLevel = fg):
        return self._add_predefined_color("YELLOW", level)

    def blue(self, level: ColorLevel = fg):
        return self._add_predefined_color("BLUE", level)

    def magenta(self, level: ColorLevel = fg):
        return self._add_predefined_color("MAGENTA", level)

    def cyan(self, level: ColorLevel = fg):
        return self._add_predefined_color("CYAN", level)

    def white(self, level: ColorLevel = fg):
        return self._add_predefined_color("WHITE", level)

    def grey(self, level: ColorLevel = fg):
        return self._add_predefined_color("GREY", level)

    def bright_red(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_RED", level)

    def bright_green(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_GREEN", level)

    def bright_yellow(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_YELLOW", level)

    def bright_blue(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_BLUE", level)

    def bright_magenta(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_MAGENTA", level)

    def bright_cyan(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_CYAN", level)

    def bright_white(self, level: ColorLevel = fg):
        return self._add_predefined_color("BRIGHT_WHITE", level)

    def arc_blue(self, level: ColorLevel = fg):
        return self._add_predefined_color("ARC_BLUE", level)
