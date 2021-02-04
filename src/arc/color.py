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

    @property
    def background(self):
        if (self.code >= 30 and self.code < 38) or (
            self.code >= 90 and self.code < 108
        ):
            return Color(self.code + 10)

        raise AttributeError(f"{self} does not have attribute 'background'")


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
    BLACK   = Color(30).background
    RED     = Color(31).background
    GREEN   = Color(32).background
    YELLOW  = Color(33).background
    BLUE    = Color(34).background
    MAGENTA = Color(35).background
    CYAN    = Color(36).background
    WHITE   = Color(37).background

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
