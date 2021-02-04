from typing import List
from arc.color import effects, fg

from . import UIBase
from . import keys


class SelectionMenu(UIBase):
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
        self.selected_index = 0

        super().__init__()

    async def update(self, key):
        if key in keys.NUMBERS:
            value = int(chr(key))
            if value < len(self.options):
                self.selected_index = value
                return True

        elif key in keys.ENTER_TUP:
            self.done((self.selected_index, self.options[self.selected_index]))
            return False

        elif key in (keys.w, keys.k) and self.selected_index > 0:
            self.selected_index -= 1
            return True

        elif key in (keys.s, keys.j) and self.selected_index < len(self.options) - 1:
            self.selected_index += 1
            return True

        return False

    async def render(self):
        print(f"Press {fg.YELLOW}q{effects.CLEAR} to quit")
        for index, string in enumerate(self.options):
            if index == self.selected_index:
                print(self.selected_format_str.format(index=index, string=string))
            else:
                print(self.format_str.format(index=index, string=string))
