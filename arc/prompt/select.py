import typing as t
from arc.color import effects, fg
from arc.prompt.helpers import ARROW_DOWN, ARROW_UP, ESCAPE, Cursor, State, getch
import arc.typing as at

# TODO:
# - More effecient rendering
# - Add a way to select multiple options


class SelectionMenu:
    selected = State()

    def __init__(
        self,
        items: list[at.SupportsStr],
        char: str = "❯",
        highlight_color: str = fg.ARC_BLUE,
    ):
        self.items = items
        self.char = char
        self.highlight_color = highlight_color
        self.selected = 0
        self._first_render = True

    def __call__(self) -> t.Optional[tuple[int, at.SupportsStr]]:
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
            if seq == "q":
                return None
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
            Cursor.up(len(self.items) + 1)

        for idx, item in enumerate(self.items):
            if idx == self.selected:
                print(f"{self.highlight_color} {self.char} {item}{effects.CLEAR}")
            else:
                print(f"{fg.GREY}   {item}{effects.CLEAR}")
        print("press q to quit")

        if self._first_render:
            self._first_render = False
