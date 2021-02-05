import sys
import termios
import tty


def getch(val: int = 1):
    # I have no idea how this works lol
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(val)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def send(string):
    sys.stdout.write(string)
    sys.stdout.flush()


def getpos():
    send("\033[6n")
    getch(2)
    chars = ""
    while (char := getch()) != "R":
        chars += char

    return tuple(int(val) for val in chars.split(";"))


def pos(row, column):
    send(f"\033[{row};{column}f")


def save_pos():
    send("\u001b[s")


def restore_pos():
    send("\u001b[u")


def clear():
    send("\u001b[2J")


def home_pos():
    send("\u001b[H")


def hide_cursor():
    send("\x1b[?25l")


def show_cursor():
    print("\x1b[?25h")


class Move:
    @classmethod
    def up(cls, val: int):
        send(f"\u001b[{val}A")

    @classmethod
    def down(cls, val: int):
        send(f"\u001b[{val}B")

    @classmethod
    def right(cls, val: int):
        send(f"\u001b[{val}C")

    @classmethod
    def left(cls, val: int):
        send(f"\u001b[{val}D")
