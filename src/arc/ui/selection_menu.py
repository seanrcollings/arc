from typing import List
from arc.color import effects, fg

from . import UIBase, state
from . import keys


class SelectionMenu(UIBase):
    selected_index = state(0)

    def __init__(
        self,
        options: List[str],
        format_str="({index}) {string}",
        selected_format_str=fg.RED
        + effects.BOLD
        + "({index}) {string}"
        + effects.CLEAR,
    ):
        self.options: list = options
        self.format_str: str = format_str
        self.selected_format_str: str = selected_format_str

        super().__init__()

    def update(self, key):
        if key in keys.NUMBERS:
            value = int(chr(key))
            if value < len(self.options):
                self.selected_index = value

        elif key in keys.ENTER_TUP:
            self.done((self.selected_index, self.options[self.selected_index]))

        elif key in (keys.w, keys.k, keys.UP) and self.selected_index > 0:
            self.selected_index -= 1

        elif (
            key in (keys.s, keys.j, keys.DOWN)
            and self.selected_index < len(self.options) - 1
        ):
            self.selected_index += 1

    def render(self):
        print(f"Press {fg.YELLOW}q{effects.CLEAR} to quit")
        for index, string in enumerate(self.options):
            if index == self.selected_index:
                print(self.selected_format_str.format(index=index, string=string))
            else:
                print(self.format_str.format(index=index, string=string))
