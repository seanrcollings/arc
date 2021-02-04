class Color(str):
    ESCAPE = "\033["

    def __new__(cls, content, extra="m"):
        obj = str.__new__(cls, f"{cls.ESCAPE}{content}{extra}")  # type: ignore
        obj.__init__(content)
        return obj

    def __init__(self, code, *_args):
        super().__init__()
        self.code = code

    @property
    def bright(self):
        return Color(self.code + 60)


# pylint: disable=bad-whitespace
# fmt: off
class fg:
    BLACK   = Color(30)
    RED     = Color(31)
    GREEN   = Color(32)
    YELLOW  = Color(33)
    BLUE    = Color(34)
    MAGENTA = Color(35)
    CYAN    = Color(36)
    WHITE   = Color(37)

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        '''Returns the **foreground** ansi escape
        sequence for the provided rgb values'''
        return f"\033[38;2;{red};{green};{blue}m"


class bg:
    BLACK   = Color(40)
    RED     = Color(41)
    GREEN   = Color(42)
    YELLOW  = Color(43)
    BLUE    = Color(44)
    MAGENTA = Color(45)
    CYAN    = Color(46)
    WHITE   = Color(47)

    @staticmethod
    def rgb(red: int = 0, green: int = 0, blue: int = 0):
        '''Returns the **background** ansi escape
        sequence for the provided rgb values'''
        return f"\033[48;2;{red};{green};{blue}m"


class effects:
    CLEAR         = Color(0)
    BOLD          = Color(1)
    ITALIC        = Color(3)
    UNDERLINE     = Color(4)
    STRIKETHROUGH = Color(9)

# fmt: on
