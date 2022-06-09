from abc import ABC, abstractmethod
import typing as t
import sys

from arc.color import colorize, fg
from arc.present.formatters import TextFormatter
from arc.prompt.helpers import (
    ARROW_DOWN,
    ARROW_UP,
    CTRL_C,
    ESCAPE,
    Cursor,
    State,
    getch,
)
import arc.typing as at

# Could the prompt be expanded to accept something like SelectMenu for Question type?


class Widget(ABC):
    hide_cursor = False

    def __init__(self):
        self.update_queued = True
        self.should_exit = False
        self.return_value = None
        self._initial = True
        self._prev_buffer = []
        self._buffer = []

    def __call__(self):
        if self.hide_cursor:
            Cursor.hide()

        while not self.should_exit:
            self.handle_render()
            self.run()

        Cursor.show()
        return self.return_value

    def queue_update(self, _requester):
        self.update_queued = True

    def should_update(self, new, old):
        return new != old

    def handle_render(self):
        if not self.update_queued:
            return

        self.render()
        self.update_queued = False

        if not self._initial:
            Cursor.up(len(self._prev_buffer))
        else:
            self._initial = False

        for line in self._buffer:
            sys.stdout.write(line + "\n")

        self._prev_buffer = self._buffer
        self._buffer = []

    def exit(self, return_value=None):
        self.should_exit = True
        self.return_value = return_value

    @abstractmethod
    def run(self):
        ...

    @abstractmethod
    def render(self):
        ...


class SelectionMenu(Widget):
    hide_cursor = True
    tab_distance = "   "
    selected = State()

    def __init__(
        self,
        items: t.Sequence[t.Any],
        char: str = "❯",
        highlight_color: str = fg.ARC_BLUE,
    ):
        super().__init__()
        self.items = items
        self.char = char
        self.highlight_color = highlight_color
        self.selected = 0
        self._first_render = True

    def run(self):
        seq = getch()
        if seq == ESCAPE:
            seq += getch()  # [
            seq += getch()  # Some Character
            self.check_sequence(seq)
            seq = ""
        elif seq == "\r":
            self.exit((self.selected, self.items[self.selected]))
        elif seq == CTRL_C:
            self.exit()
        elif seq.isnumeric():
            val = int(seq) - 1
            if 0 <= val < len(self.items):
                self.selected = val
        else:
            seq = ""

    def check_sequence(self, seq: str):
        if seq == ARROW_UP:
            self.selected = max(0, self.selected - 1)
        elif seq == ARROW_DOWN:
            self.selected = min(len(self.items) - 1, self.selected + 1)

    def write(self, text: t.Any):
        text = str(text).replace("\n", f"\n{self.tab_distance}").split("\n")
        self._buffer.extend(text)

    def render(self):
        for idx, item in enumerate(self.items):
            if idx == self.selected:
                # self.write(f" {self.char} {item}")
                self.write(colorize(f" {self.char} {item}", self.highlight_color))
            else:
                # self.write(f"{self.tab_distance}{item}")
                self.write(colorize(f"{self.tab_distance}{item}", fg.GREY))


T = t.TypeVar("T")


def select(
    items: t.Sequence[T],
    char: str = "❯",
    highlight_color: str = fg.ARC_BLUE,
) -> t.Optional[tuple[int, T]]:
    """Prompt the user to select an item from a list of `items`. The list
    is navigable using the up and down arrow keys, along with the number keys.
    A slection is made by pressing the enter key.

    Args:
        items (t.Sequence[T]): A list of items to select from
        char (str, optional): Character that denotes the currently selected item.
            Defaults to "❯".
        highlight_color (str, optional): Color to highlight the currently selected item.
            Defaults to `fg.ARC_BLUE`.

    Returns:
        t.Optional[tuple[int, T]]: A tuple of the index of the selected item and the item itself.
            If the user exits the prompt, `None` is returned.
    """
    return SelectionMenu(items, char, highlight_color)()
