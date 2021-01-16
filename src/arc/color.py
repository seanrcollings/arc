class Ansi(str):
    __escape = "\u001b["

    def __new__(cls, content, extra="m"):
        obj = str.__new__(cls, f"{cls.__escape}{content}{extra}")  # type: ignore
        obj.__init__(content)
        return obj

    def __init__(self, code, *_args):
        super().__init__()
        self.code = code

    @property
    def bright(self):
        return Ansi(self.code + 60)

    @property
    def background(self):
        if self.code >= 30 and self.code < 39:
            return Ansi(self.code + 10)

        raise AttributeError(f"{self.code} does not have attribute 'background'")


# pylint: disable=bad-whitespace
# fmt: off
class fg:
    BLACK   = Ansi(30)
    RED     = Ansi(31)
    GREEN   = Ansi(32)
    YELLOW  = Ansi(33)
    BLUE    = Ansi(34)
    MAGENTA = Ansi(35)
    CYAN    = Ansi(36)
    WHITE   = Ansi(37)

class bg:
    BLACK   = Ansi(30).background
    RED     = Ansi(31).background
    GREEN   = Ansi(32).background
    YELLOW  = Ansi(33).background
    BLUE    = Ansi(34).background
    MAGENTA = Ansi(35).background
    CYAN    = Ansi(36).background
    WHITE   = Ansi(37).background


class effects:
    CLEAR         = Ansi(0)
    BOLD          = Ansi(1)
    ITALIC        = Ansi(3)
    UNDERLINE     = Ansi(4)
    STRIKETHROUGH = Ansi(9)

# fmt: on
