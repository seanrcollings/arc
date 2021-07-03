from typing import Literal, Union, Optional
import re
import shutil

from arc import color
from .data import justifications, Justification

border_styles = {
    "regular": {
        "horizontal": "\u2500",
        "vertical": "\u2502",
        "corners": {
            "top-left": "\u256D",
            "top-right": "\u256E",
            "bot-left": "\u2570",
            "bot-right": "\u256F",
        },
    },
    "heavy": {
        "horizontal": "\u2501",
        "vertical": "\u2503",
        "corners": {
            "top-left": "\u250F",
            "top-right": "\u2513",
            "bot-left": "\u2517",
            "bot-right": "\u251B",
        },
    },
}


def _clean(string):
    """Gets rid of escape sequences"""
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


Border = Union[Literal["regular"], Literal["heavy"]]


class Box:
    """Presenter for creating a Box around provided text

    Examples:
    ```
        print(Box('some cool text', padding=2, justify='center')) ->

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
        border: Border = "regular",
        padding: Union[int, dict[str, int]] = 0,
        justify: Justification = "left",
        color: color.Color = color.fg.WHITE,
    ):
        """
        Args:
            string: String to surround with a box - May be colored
            border: Border style, either 'regular' or 'heavy' defaults to 'regular
            padding: Dictionary containing the padding of each side of the string
                    defaults to: `{"top": 0, "left": 0, "bottom": 0, "right": 0}`
                    If all sides are going to have the same padding, can just pass
                    in that integer, rather than the entire dictionary
            justify: how to justify the text (left, center, right). Defaults to left
            color: What color the border should be. Defaults to white.
                    Use `arc.color.fg` constants
        """
        self.string = string
        self.__border = border_styles[border]
        self.__justify = justifications[justify]
        self.__padding = self.__get_padding(padding)
        self.__color = color

    def __str__(self):
        cleaned = list(
            self.pad_line(_clean(string)) for string in self.string.split("\n")
        )
        width = len(max(cleaned, key=len)) + 4
        term_width, _ = shutil.get_terminal_size()
        width = min(width, term_width)

        pad_top = "".join(
            self.format_line("", width) for _ in range(0, self.__padding["top"])
        )
        content = "".join(
            self.format_line(line, width, clean_line)
            for line, clean_line in zip(self.string.split("\n"), cleaned)
        )
        pad_btm = "".join(
            self.format_line("", width) for _ in range(0, self.__padding["bottom"])
        )

        content = f"{pad_top}{content}{pad_btm}"

        top = self.horizontal_border(width, "top")
        bottom = self.horizontal_border(width, "bot")
        return f"{top}\n{content}{bottom}"

    @property
    def border(self):
        """Dictionary containting the border stylings"""
        return self.__border

    @border.setter
    def border(self, value):
        self.__border = border_styles[value]

    # Utils

    def horizontal_border(self, width, side: str):
        return "".join(
            (
                self.__color,
                self.border["corners"][f"{side}-left"],
                self.border["horizontal"] * (width - 2),
                self.border["corners"][f"{side}-right"],
                color.effects.CLEAR,
            )
        )

    def format_line(
        self,
        line: str,
        width: int,
        cleaned: Optional[str] = None,
    ):
        cleaned = cleaned or line
        formatted = (
            f"{self.__color}{self.border['vertical']}{color.effects.CLEAR}"
            f"{cleaned:{self.__justify}{width - 2}}"
            f"{self.__color}{self.border['vertical']}{color.effects.CLEAR}\n"
        )

        if line == "":
            return formatted

        # Uses the clean string for calculating the necessary
        # amount of padding on the right, but we want the color, so
        # just re.sub it back in after
        regex = re.compile(cleaned)
        formatted = regex.sub(self.pad_line(line), formatted)
        return formatted

    def pad_line(self, line: str):
        return " " * self.__padding["left"] + line + " " * self.__padding["right"]

    @staticmethod
    def __get_padding(padding: Union[int, dict[str, int]]) -> dict[str, int]:
        default_padding = {"top": 0, "left": 0, "bottom": 0, "right": 0}
        if isinstance(padding, int):
            return dict.fromkeys(default_padding, padding)
        if isinstance(padding, dict):
            return default_padding | padding

        return default_padding
