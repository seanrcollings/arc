from typing import Literal
import sys
import tty
import termios

PREVIOUS_LINE = "\033[F"


def clear_line(amount: Literal["all", "before", "after"] = "all"):
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
    def pos(x: int, y: int):
        sys.stdout.write(f"\x1b[{y};{x}H")

    @staticmethod
    def show():
        sys.stdout.write("\x1b[?25h")

    class __HideContextManager:
        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc_val, _exc_tb):
            Cursor.show()

    _hidectx = __HideContextManager()

    @staticmethod
    def hide():
        sys.stdout.write("\x1b[?25l")
        return Cursor._hidectx


class State:
    public_name: str
    private_name: str

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if instance.should_update(getattr(instance, self.private_name, None), value):
            setattr(instance, self.private_name, value)
            instance.queue_update(self)
        else:
            setattr(instance, self.private_name, value)


ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"
ESCAPE = "\x1b"
CTRL_C = "\x03"
