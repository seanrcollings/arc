import sys
import typing as t
import sys, tty, termios
import contextlib

from arc.color import effects, fg

# TODO:
# - Move a lot of thos code into a helper module
# - More effecient rendering
# - Add a way to select multiple options


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())
    ch = sys.stdin.read(1)
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


class SupportsStr(t.Protocol):
    def __str__(self) -> str:
        ...


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

    @staticmethod
    @contextlib.contextmanager
    def hide():
        sys.stdout.write("\x1b[?25l")
        yield
        Cursor.show()


class State:
    public_name: str
    private_name: str

    def __init__(self) -> None:
        self.initial_set = True

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not self.initial_set and instance.update(
            getattr(instance, self.private_name), value
        ):
            setattr(instance, self.private_name, value)
            instance.render()
        else:
            setattr(instance, self.private_name, value)

        self.initial_set = False


ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"
ESCAPE = "\x1b"


class SelectionMenu:
    selected = State()

    def __init__(
        self,
        items: list[SupportsStr],
        char: str = "❯",
        highlight_color: str = fg.ARC_BLUE,
    ):
        self.items = items
        self.char = char
        self.highlight_color = highlight_color
        self.selected = 0
        self._first_render = True

    def __call__(self) -> tuple[int, SupportsStr]:
        with Cursor.hide():
            self.render()
            return self.run()

    def run(self):
        while True:
            seq = getch()
            if seq == "\r":
                break

            if seq == ESCAPE:
                seq += getch()  # [
                seq += getch()  # Some Character
                self.check_sequence(seq)
                seq = ""
            else:
                seq = ""

        return self.selected, self.items[self.selected]

    def check_sequence(self, seq: str):
        if seq == ARROW_UP:
            self.selected = max(0, self.selected - 1)
        elif seq == ARROW_DOWN:
            self.selected = min(len(self.items) - 1, self.selected + 1)

    def update(self, new, old):
        return new != old

    def render(self):
        if not self._first_render:
            Cursor.up(len(self.items))

        for idx, item in enumerate(self.items):
            if idx == self.selected:
                print(f"{self.highlight_color} {self.char} {item}{effects.CLEAR}")
            else:
                print(f"{fg.GREY}   {item}{effects.CLEAR}")

        if self._first_render:
            self._first_render = False
