import re
import shutil
from typing import Literal, Optional, Union

from arc.present.ansi import bg, fg, fx
from arc.present.joiner import Join

from .ansi import Ansi
from .data import Justification, justifications
from .drawing import Border, borders


class Box:
    """Presenter for creating a Box around provided text

    Examples:
    ```
        arc.print(Box('some cool text', padding=2, justify='center')) ->

        ╭────────────────────╮
        │                    │
        │                    │
        │   some cool text   │
        │                    │
        │                    │
        ╰────────────────────╯
    ```
    Will accept colorized strings
    """

    def __init__(
        self,
        string: str,
        border: str = "rounded",
        padding: Union[int, dict[str, int]] = 0,
        justify: Justification = "center",
        color: str = fg.WHITE,
    ):
        """
        Args:
            string: String to surround with a box - May be colored
            border: Border style, either 'light' or 'heavy' defaults to 'light'
            padding: Dictionary containing the padding of each side of the string
                    defaults to: `{"top": 0, "left": 0, "bottom": 0, "right": 0}`
                    If all sides are going to have the same padding, can just pass
                    in that integer, rather than the entire dictionary
            justify: how to justify the text (left, center, right). Defaults to left
            color: What color the border should be. Defaults to white.
                    Use `arc.color.fg` constants
        """
        self.string = string
        self.__border: Border = borders[border]
        self.__justify = justifications[justify]
        self.__padding = self.__get_padding(padding)
        self.__color = color

    def __str__(self) -> str:
        cleaned = list(
            self.pad_line(Ansi.clean(string)) for string in self.string.split("\n")
        )
        width = len(max(cleaned, key=len)) + 4
        term_width, _ = shutil.get_terminal_size()
        width = min(width, term_width)

        pad_top = Join.together(
            self.format_line("", width) for _ in range(0, self.__padding["top"])
        )
        content = Join.together(
            self.format_line(line, width, clean_line)
            for line, clean_line in zip(self.string.split("\n"), cleaned)
        )
        pad_btm = Join.together(
            self.format_line("", width) for _ in range(0, self.__padding["bottom"])
        )

        content = f"{pad_top}{content}{pad_btm}"

        top = self.horizontal_border(width, "top")
        bottom = self.horizontal_border(width, "bot")
        return f"{top}\n{content}{bottom}"

    @property
    def border(self) -> Border:
        """Dictionary containting the border stylings"""
        return self.__border

    @border.setter
    def border(self, value: str) -> None:
        self.__border = borders[value]

    # Utils

    def horizontal_border(self, width: int, side: str) -> str:
        return Join.together(
            (
                self.border["corner"][f"{side}_left"],  # type: ignore
                self.border["horizontal"] * (width - 2),
                self.border["corner"][f"{side}_right"],  # type: ignore
            ),
            style=self.__color,
        )

    def format_line(
        self,
        line: str,
        width: int,
        cleaned: Optional[str] = None,
    ) -> str:
        cleaned = cleaned or line
        formatted = (
            f"{self.__color}{self.border['vertical']}{fx.CLEAR}"
            f"{cleaned:{self.__justify}{width - 2}}"
            f"{self.__color}{self.border['vertical']}{fx.CLEAR}\n"
        )

        if line == "":
            return formatted

        # Uses the clean string for calculating the necessary
        # amount of padding on the right, but we want the color, so
        # just re.sub it back in after
        regex = re.compile(cleaned)
        formatted = regex.sub(self.pad_line(line), formatted)
        return formatted

    def pad_line(self, line: str) -> str:
        return " " * self.__padding["left"] + line + " " * self.__padding["right"]

    @staticmethod
    def __get_padding(padding: Union[int, dict[str, int]]) -> dict[str, int]:
        default_padding = {"top": 0, "left": 0, "bottom": 0, "right": 0}
        if isinstance(padding, int):
            return dict.fromkeys(default_padding, padding)
        if isinstance(padding, dict):
            return default_padding | padding

        return default_padding
