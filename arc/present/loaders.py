from __future__ import annotations
from arc.color import fg, effects

RGB = tuple[int, int, int]


class Styler:
    """Base Class for Stylers"""

    def style_full(self, string: str, index: int, loader: Loader):
        return string

    def style_empty(self, string: str, index: int, loader: Loader):
        return string


default = Styler()


class Transiton(Styler):
    def __init__(self, from_c: RGB, to_c: RGB):
        self.from_color = from_c
        self.to_color = to_c

    def style_full(self, string: str, index: int, loader: Loader):
        # https://stackoverflow.com/questions/21835739/smooth-color-transition-algorithm
        p = index / float(loader.segments - 1)
        r1, g1, b1 = self.from_color
        r2, g2, b2 = self.to_color
        r = int((1.0 - p) * r1 + p * r2 + 0.5)
        g = int((1.0 - p) * g1 + p * g2 + 0.5)
        b = int((1.0 - p) * b1 + p * b2 + 0.5)
        return f"{fg.rgb(r, g, b)}{string}{effects.CLEAR}"


class Loader:
    def __init__(
        self,
        start: float = 0.0,
        segments: int = 100,
        format_str="{bar}",
        styler: Styler = default,
    ):
        self.progress: float = start
        self.segments: int = segments
        self.format_str: str = format_str
        self.styler: Styler = styler

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, trace):
        self.clear()

    def __str__(self):
        return "[" + self.render() + "]"

    @property
    def done(self):
        return self.progress >= 1

    @property
    def percent(self) -> int:
        return int(self.progress * 100)

    def render(self):
        return ""

    def update(self, value):
        if not self.done:
            self.progress = value
            self.print()

    def print(self):
        print(
            f"\r{self.format_str.format(bar=str(self), percent=self.percent)}",
            flush=True,
            end="",
        )

    def clear(self):
        print("\u001b[2K")


class BarLoader(Loader):
    FULL = "\u2588"
    EMPTY = "."

    def __init__(
        self,
        full=None,
        empty=None,
        *args,
        **kwargs,
    ):
        self.full = full or self.FULL
        self.empty = empty or self.EMPTY
        super().__init__(*args, **kwargs)

    def render(self):
        return "".join(
            self.styler.style_full(self.full, i, self)
            for i in range(int(self.progress * self.segments))
        ) + "".join(
            self.styler.style_empty(self.empty, i, self)
            for i in range(int(self.segments - self.progress * self.segments))
        )


class SlantLoader(BarLoader):
    FULL = "▰"
    EMPTY = "▱"


class RectangleLoader(BarLoader):
    FULL = "▮"
    EMPTY = "▯"


class Pacman(Loader):
    FULL = "-"
    EMPTY = f"{fg.BLACK.bright} o {effects.CLEAR}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouth_open = False

    def __str__(self):
        return (
            self.EMPTY * int(self.segments / 3)
            + "]\r"
            + "["
            + (self.FULL * int(self.progress * self.segments - 2))
            + self.pacman()
        )

    def pacman(self):
        return (
            f"{fg.YELLOW}{effects.BOLD}"
            f"{'C' if self.mouth_open else 'c'}{effects.CLEAR}"
        )

    def update(self, value):
        self.mouth_open = not self.mouth_open
        super().update(value)
