from typing import Callable, Optional, TypeVar, Generic, Union
import sys
import tty
import termios
import threading
from arc.color import fg, colorize


T = TypeVar("T")


def ctrl(char: str):
    """Converts a letter into it's CTRL + <letter> escape sequence"""
    return chr(ord(char.upper()) - 64)


class HotKey(Generic[T]):
    """`HotKey` provides a simple interface for a CLI app to listen
    for user input and respond to it accordingly. To do so, define handlers for
    specific keys with the `HotKey.handle` decorator, then execute with
    `HotKey.run`

    ### Example
    ```py
    from arc.prompt.hotkey import HotKey, ctrl

    handler = HotKey()

    @handler.handle('r')
    def reload():
        '''Reloads the application'''
        # ^ Docstrings are used for helper text!
        print("Reloading app...")

    @handler.handle(ctrl('r'))
    def reload_hard():
        '''Reloads the application, and rebuilds native extensions'''
        print("Hard Reloading app...")

    handler.run()

    ```
    """

    def __init__(self, quit_key: str = ctrl("q"), help_key: str = "?"):
        """Creates a `HotKey` handler

        Args:
            quit_key (str, optional): Key(s) to press to quit the program. Defaults to Ctrl + Q.
            help_key (str, optional): Key(s) to press to display a list of all available hotkeys.
                Defaults to "?".
        """

        self.handlers: dict[str, Callable] = {
            quit_key: self._quit,
            help_key: self._default_help,
        }
        self.quit_key = quit_key
        self.help_key = help_key
        self._onstart: Optional[Callable] = self._default_on_start
        self._onquit: Optional[Callable[[], Optional[T]]] = None
        self.running = True

    def handle(self, char: str) -> Callable:
        """Registers a function as a handler for `char`"""

        def inner(f: Callable) -> Callable:
            self.handlers[char] = f
            return f

        return inner

    def onstart(self, f: Callable) -> Callable:
        """Register a function to execute when the program starts up"""
        self._onstart = f
        return f

    def onquit(self, f: Callable[[], Optional[T]]) -> Callable[[], Optional[T]]:
        """Registers a function to execute when the program exits"""
        self._onquit = f
        return f

    def run(self, blocking: bool = True) -> Union[Optional[T], threading.Thread]:
        if blocking:
            return self._run()
        else:
            thread = threading.Thread(target=self._run)
            thread.start()
            return thread

    def _run(self) -> Optional[T]:
        """Runs the central loop"""
        if self._onstart:
            self._onstart()

        while self.running:
            char = getch()
            if char in self.handlers:
                self.handlers[char]()

        if self._onquit:
            return self._onquit()

        return None

    def _quit(self):
        """Quit the program"""
        self.running = False

    def _default_on_start(self):
        print(
            "Waiting for input. "
            f"{colorize(human_readable_key(self.quit_key), fg.YELLOW)} to quit. "
            f"{colorize(human_readable_key(self.help_key), fg.YELLOW)} for all hotkeys"
        )

    def _default_help(self):
        """Displays the help information"""
        for char, handler in self.handlers.items():
            print(
                f"  - {colorize(format(human_readable_key(char), '<20'), fg.ARC_BLUE)}"
                f" {handler.__doc__ if handler.__doc__ else ''}"
            )


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


def human_readable_key(char: str) -> str:
    if ord(char) in range(1, 26):
        return f"Ctrl + {chr(ord(char) + 64)}"
    return char
