from __future__ import annotations
import functools
import itertools
import typing as t
from arc.errors import ArcError

from arc.color import colorize, effects, fg
from arc.utils import ansi_len
from . import drawing


class ColumnBase(t.TypedDict):  # pylint: disable=inherit-non-class
    """ColumnBase Type"""

    name: str


class Column(ColumnBase, total=False):  # pylint: disable=inherit-non-class
    """Column Type"""

    justify: drawing.Justification
    width: int


NO_DEFAULT = object()
DEFAULT_COLUMN: Column = {
    "name": "NAME",
    "justify": "left",
}

BORDER_HEAVY_TRANS: drawing.Border = {
    "horizontal": "━",
    "vertical": "┃",
    "corner": {
        "top_left": "┏",
        "top_right": "┓",
        "bot_left": "┗",
        "bot_right": "┛",
    },
    "intersect": {
        "cross": "╇",
        "vert_left": "┡",
        "vert_right": "┩",
        "hori_top": "┳",
        "hori_bot": "┻",
    },
}


ColumnInput = t.Sequence[t.Union[str, Column]]
Row = dict[str, t.Any]
TableFormatter = t.Callable[[t.Any], str]

T = t.TypeVar("T")


def has_next(seq: t.Sequence[T]) -> t.Generator[tuple[T, bool], None, None]:
    length = len(seq)
    for idx, val in enumerate(seq):
        yield val, idx < length - 1


def _format_cell(value: t.Any):
    return str(value)


def _format_header_cell(value: t.Any):
    return colorize(str(value), effects.BOLD)


def _format_bool(val: bool):
    return colorize(str(val), fg.GREEN if val else fg.RED)


def _format_int(val: int):
    return colorize(str(val), fg.BLUE)


_DEFAULT_TYPE_FORMATTERS: dict[type, TableFormatter] = {
    bool: _format_bool,
    int: _format_int,
}


class Table:
    """Display information in a table

    ```py
    from arc.color import colorize, fg
    from arc.present.table import Table

    t = Table(["Name", "Age", "Stand"])
    t.add_row(["Jonathen Joestar", 20, "-"])
    t.add_row(["Joseph Joestar", 18, "Hermit Purple (in Part 3)"])
    t.add_row(["Jotaro Kujo", 18, "Star Platinum"])
    t.add_row(["Josuke Higashikata", 16, "Crazy Diamon"])
    t.add_row(["Giorno Giovanna", 15, "Gold Experience"])
    t.add_row(["Joylene Kujo", 19, "Stone Free"])


    print(t)
    ```

    Will yield:
    ```console
    ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Name               ┃ Age ┃ Stand                     ┃
    ┡━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ Jonathen Joestar   │ 20  │ -                         │
    │ Joseph Joestar     │ 18  │ Hermit Purple (in Part 3) │
    │ Jotaro Kujo        │ 18  │ Star Platinum             │
    │ Josuke Higashikata │ 16  │ Crazy Diamon              │
    │ Giorno Giovanna    │ 15  │ Gold Experience           │
    │ Joylene Kujo       │ 19  │ Stone Free                │
    └────────────────────┴─────┴───────────────────────────┘
    ```
    """

    def __init__(self, columns: ColumnInput, default_formatting: bool = True) -> None:
        self.__columns: t.Sequence[Column] = self.__resolve_columns(columns)
        self.__rows: list[Row] = []
        self._border = drawing.borders["light"]
        self._head_border = BORDER_HEAVY_TRANS
        self._header_cell_formatter: TableFormatter = (
            _format_header_cell if default_formatting else _format_cell
        )
        self._cell_formatter: TableFormatter = _format_cell
        self._type_formatters: dict[type, TableFormatter] = (
            _DEFAULT_TYPE_FORMATTERS if default_formatting else {}
        )

    def __str__(self):
        for col in self.__columns:
            cells = [row[col["name"]] for row in self.__rows]
            cells.append(col["name"])

            col["width"] = max(
                ansi_len(self._fmt_cell_contents(cell)) + 2 for cell in cells
            )

        table = ""
        table += self._fmt_header()
        table += "\n"

        for row, has_next_row in has_next(self.__rows):
            table += self._fmt_row(row, has_next_row)
            if has_next_row:
                table += "\n"

        return table

    def add_row(self, row: t.Sequence[t.Any]):
        if len(row) > len(self.__columns):
            raise ArcError("Too many values")

        resolved = {}
        for col, value in itertools.zip_longest(self.__columns, row, fillvalue=""):
            resolved[col["name"]] = value

        self.__rows.append(resolved)

    def fmt_header_cell(self, func: TableFormatter | None = None):
        def inner(func: TableFormatter):
            self._cell_formatter = func
            return func

        if func:
            return inner(func)

        return inner

    def fmt_cell(self, func: TableFormatter | None = None):
        """Formats any cell that does not already have a formatter applied"""

        def inner(func: TableFormatter):
            self._cell_formatter = func
            return func

        if func:
            return inner(func)

        return inner

    def fmt_type(self, cls: type):
        def inner(func: t.Callable[[t.Any], str]):
            self._type_formatters[cls] = func
            return func

        return inner

    def _fmt_header(self) -> str:
        border = self._head_border
        header = ""

        header += border["corner"]["top_left"]
        for idx, col in enumerate(self.__columns):
            header += border["horizontal"] * col["width"]
            if idx < len(self.__columns) - 1:
                header += border["intersect"]["hori_top"]
            else:
                header += border["corner"]["top_right"]

        header += "\n"
        header += border["vertical"]
        for col in self.__columns:
            header += self._fmt_cell(
                col["name"],
                col["width"],
                col["justify"],
                header=True,
            )
            header += border["vertical"]

        header += "\n"
        header += border["intersect"]["vert_left"]
        for col, has_next_column in has_next(self.__columns):
            header += border["horizontal"] * col["width"]
            if has_next_column:
                header += border["intersect"]["cross"]
            else:
                header += border["intersect"]["vert_right"]

        return header

    def _fmt_row(self, row: Row, next_row: bool):
        border = self._border
        fmt = ""

        fmt += border["vertical"]

        for col in self.__columns:
            cell = row.get(col["name"], "")
            fmt += self._fmt_cell(cell, col["width"], col["justify"])
            fmt += border["vertical"]

        if not next_row:
            fmt += "\n"
            fmt += border["corner"]["bot_left"]
            for col, has_next_column in has_next(self.__columns):
                fmt += border["horizontal"] * col["width"]
                if has_next_column:
                    fmt += border["intersect"]["hori_bot"]
                else:
                    fmt += border["corner"]["bot_right"]

        return fmt

    def _fmt_cell(
        self,
        cell: t.Any,
        width: int,
        justify: drawing.Justification,
        header: bool = False,
    ):
        formatted_cell = self._fmt_cell_contents(cell, header)
        width = width - 2
        padding = " " * (width - ansi_len(formatted_cell))

        if justify == "left":
            return " " + formatted_cell + padding + " "
        elif justify == "right":
            return " " + padding + formatted_cell + " "
        elif justify == "center":
            padding_width, remainder = divmod(width - ansi_len(formatted_cell), 2)
            padding = " " * padding_width
            return (
                " " + padding + formatted_cell + padding + ("  " if remainder else " ")
            )

    @functools.cache
    def _fmt_cell_contents(self, cell: t.Any, header: bool = False):
        if header:
            return self._header_cell_formatter(cell)
        if type(cell) in self._type_formatters:
            return self._type_formatters[type(cell)](cell)
        else:
            return self._cell_formatter(cell)

    @staticmethod
    def __resolve_columns(columns: ColumnInput) -> list[Column]:
        resolved: list[Column] = []

        for column in columns:
            copy = DEFAULT_COLUMN.copy()

            if isinstance(column, str):
                copy.update({"name": column})

            elif isinstance(column, dict):
                column = t.cast(Column, column)
                copy.update(column)  # type: ignore
            else:
                raise ArcError("Columns must either be a string or a dictionary")

            resolved.append(copy)

        return resolved
