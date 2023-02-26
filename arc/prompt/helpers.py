import typing as t
from contextlib import contextmanager
import re
import sys
import tty
import termios

T = t.TypeVar("T")


def clear_line(amount: t.Literal["all", "before", "after"] = "all"):
    if amount == "all":
        num = 2
    elif amount == "before":
        num = 1
    else:
        num = 0

    return f"\033[{num}K"


def write(string: str):
    sys.stdout.write(string)


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class RawTerminal:
    __raw: bool = False
    __old_settings: list

    def __enter__(self):
        fd = sys.stdin.fileno()
        self.__old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        self.__raw = True
        return self

    def __exit__(self, *args):
        fd = sys.stdin.fileno()
        self.__raw = False
        termios.tcsetattr(fd, termios.TCSADRAIN, self.__old_settings)

    def getch(self):
        assert self.__raw, "Cannot getch() when not in raw mode"
        return sys.stdin.read(1)


class Cursor:
    @staticmethod
    def up(val: int = 1):
        sys.stdout.write(f"\x1b[{val}A")

    @staticmethod
    def down(val: int = 1):
        sys.stdout.write(f"\x1b[{val}B")

    @staticmethod
    def right(val: int = 1):
        sys.stdout.write(f"\x1b[{val}C")

    @staticmethod
    def left(val: int = 1):
        sys.stdout.write(f"\x1b[{val}D")

    @staticmethod
    def nextline(val: int = 1):
        sys.stdout.write(f"\x1b[{val}E")

    @staticmethod
    def prevline(val: int = 1):
        sys.stdout.write(f"\x1b[{val}F")

    @staticmethod
    def getpos() -> tuple[int, int]:
        sys.stdout.write(f"\x1b[6n")
        sys.stdout.flush()
        with RawTerminal() as term:
            seq = term.getch()
            while seq[-1] != "R":
                seq += term.getch()

        match = re.match(r"\x1b\[(\d+);(\d+)R", seq)
        if not match:
            raise RuntimeError("Could not match position string returned")
        return t.cast(tuple[int, int], tuple(int(v) for v in match.groups()))

    @staticmethod
    def setpos(row: int, col: int):
        sys.stdout.write(f"\x1b[{row};{col}H")

    @staticmethod
    def save():
        sys.stdout.write(f"\033[s")
        sys.stdout.flush()

    @staticmethod
    def restore():
        sys.stdout.write(f"\033[u")
        sys.stdout.flush()

    @staticmethod
    def show():
        sys.stdout.write("\x1b[?25h")

    # class __HideContextManager:
    #     def __enter__(self):
    #         return self

    #     def __exit__(self, _exc_type, _exc_val, _exc_tb):
    #         Cursor.show()

    # _hidectx = __HideContextManager()

    @contextmanager
    @staticmethod
    def hide():
        try:
            sys.stdout.write("\x1b[?25l")
            yield
        finally:
            Cursor.show()


class State(t.Generic[T]):
    public_name: str
    private_name: str

    def __init__(self, initial_value: T | None = None) -> None:
        self._initial_value: T | None = initial_value

    def __set_name__(self, _owner, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, instance, _owner) -> T:
        return getattr(instance, self.private_name, self._initial_value)

    def __set__(self, instance, value: T):
        setattr(instance, self.private_name, value)
        setattr(instance, "update_occured", True)


ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"
ESCAPE = "\x1b"
CTRL_C = "\x03"
BACKSPACE = "\x7f"
PREVIOUS_LINE = "\033[F"
