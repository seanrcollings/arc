from typing import Callable, Optional
import sys
import tty
import termios


def getch():
    """Get a single character from stdin, Unix version"""

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())  # Raw read
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def ctrl(char: str):
    """Converts a letter into it's CTRL + <letter> escape sequence"""
    return chr(ord(char.upper()) - 64)


def alt(char: str):
    return chr(ord(char.upper()) - 38)


class HotKeyHandler:
    def __init__(self, quit_key: str = ctrl("q")):
        self.handlers: dict[str, Callable] = {}
        self.quit_key = quit_key
        self._onstart: Optional[Callable] = None
        self._onquit: Optional[Callable] = None

    def handle(self, char: str):
        def inner(f: Callable):
            self.handlers[char] = f
            return f

        return inner

    def onstart(self, f: Callable):
        self._onstart = f
        return f

    def onquit(self, f: Callable):
        self._onquit = f
        return f

    def run(self):
        if self._onstart:
            self._onstart()

        while True:
            char = getch()
            if char == self.quit_key:
                if self._onquit:
                    self._onquit()

                break

            if char in self.handlers:
                self.handlers[char]()
