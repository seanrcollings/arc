from __future__ import annotations
import re
import sys
import typing as t
from contextlib import contextmanager

T = t.TypeVar("T")


def clear_line(amount: t.Literal["all", "before", "after"] = "all") -> str:
    if amount == "all":
        num = 2
    elif amount == "before":
        num = 1
    else:
        num = 0

    return f"\033[{num}K"


class RawTerminal:
    __raw: bool = False
    __old_settings: list[t.Any]

    def __init__(self) -> None:
        # Moved into here to support pyodide
        import termios
        import tty

        self.termios = termios
        self.tty = tty

    def __enter__(self) -> RawTerminal:
        fd = sys.stdin.fileno()
        self.__old_settings = self.termios.tcgetattr(fd)
        self.tty.setraw(sys.stdin.fileno())
        self.__raw = True
        return self

    def __exit__(self, *args: t.Any) -> None:
        fd = sys.stdin.fileno()
        self.__raw = False
        self.termios.tcsetattr(fd, self.termios.TCSADRAIN, self.__old_settings)

    def getch(self) -> str:
        assert self.__raw, "Cannot getch() when not in raw mode"
        return sys.stdin.read(1)


class Cursor:
    @staticmethod
    def up(val: int = 1) -> None:
        sys.stdout.write(f"\x1b[{val}A")

    @staticmethod
    def down(val: int = 1) -> None:
        sys.stdout.write(f"\x1b[{val}B")

    @staticmethod
    def right(val: int = 1) -> None:
        sys.stdout.write(f"\x1b[{val}C")

    @staticmethod
    def left(val: int = 1) -> None:
        sys.stdout.write(f"\x1b[{val}D")

    @staticmethod
    def nextline(val: int = 1) -> None:
        sys.stdout.write(f"\x1b[{val}E")

    @staticmethod
    def prevline(val: int = 1) -> None:
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
    def setpos(row: int, col: int) -> None:
        sys.stdout.write(f"\x1b[{row};{col}H")

    @staticmethod
    def save() -> None:
        sys.stdout.write(f"\033[s")
        sys.stdout.flush()

    @staticmethod
    def restore() -> None:
        sys.stdout.write(f"\033[u")
        sys.stdout.flush()

    @staticmethod
    def show() -> None:
        sys.stdout.write("\x1b[?25h")

    @contextmanager
    @staticmethod
    def hide() -> t.Generator[None, None, None]:
        try:
            sys.stdout.write("\x1b[?25l")
            sys.stdout.flush()
            yield
        finally:
            Cursor.show()


class State(t.Generic[T]):
    public_name: str
    private_name: str

    def __init__(self, initial_value: T | None = None) -> None:
        self._initial_value: T | None = initial_value

    def __set_name__(self, _owner: t.Any, name: str) -> None:
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, instance: t.Any, _owner: t.Any) -> T:
        return getattr(instance, self.private_name, self._initial_value)  # type: ignore

    def __set__(self, instance: t.Any, value: T) -> None:
        prev = getattr(instance, self.private_name, self._initial_value)
        if prev != value:
            setattr(instance, self.private_name, value)
            setattr(instance, "update_occured", True)


ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"
ESCAPE = "\x1b"
CTRL_C = "\x03"
BACKSPACE = "\x7f"
PREVIOUS_LINE = "\033[F"
