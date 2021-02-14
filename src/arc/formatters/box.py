import re
import shutil
import textwrap


def clean(string):
    """Gets rid of escape sequences"""
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


styles = {
    "regular": {
        "horizontal": "\u2500",
        "vertical": "\u2502",
        "corners": {
            "top-left": "\u256D",
            "top-right": "\u256E",
            "bot-left": "\u2570",
            "bot-right": "\u256F",
        },
    }
}

justifications = {
    "left": "<",
    "center": "^",
    "right": ">",
}


class Box:
    def __init__(self, string: str, style: str = "regular", justify: str = "left"):
        self.string = string
        self.__style = styles[style]
        self.__justify = justifications[justify]

    def __str__(self):
        cleaned = (clean(string) for string in self.string.split("\n"))
        width = len(max(cleaned, key=len)) + 4
        term_width, _ = shutil.get_terminal_size()
        width = min(width, term_width)

        content = "".join(
            self.format_line(line, width) for line in self.string.split("\n")
        )

        top = self.horizontal_line(width, "top")
        bottom = self.horizontal_line(width, "bot")
        return f"{top}\n{content}{bottom}"

    @property
    def style(self):
        return self.__style

    @style.setter  # type: ignore
    def style_setter(self, value):
        self.__style = styles[value]

    def horizontal_line(self, width, side: str):
        return "".join(
            (
                self.style["corners"][f"{side}-left"],
                self.style["horizontal"] * width,
                self.style["corners"][f"{side}-right"],
            )
        )

    def format_line(self, line: str, width: int):
        # Uses the clean string for calculating the nessecary
        # amount of padding on the right, but we want the color, so
        # just re.sub it back in after
        clean_line = clean(line)
        formatted = (
            f"{self.style['vertical']}"
            f"{clean_line:{self.__justify}{width}}{self.style['vertical']}\n"
        )
        regex = re.compile(clean_line)
        formatted = regex.sub(line, formatted)
        return formatted
