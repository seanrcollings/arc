from __future__ import annotations
import itertools
import typing as t
from arc.errors import ArcError

from arc.color import fg, effects
from . import drawing


class ColumnBase(t.TypedDict):  # pylint: disable=inherit-non-class
    """ColumnBase Type"""

    name: str


class Column(ColumnBase, total=False):  # pylint: disable=inherit-non-class
    """Column Type"""

    justify: drawing.Justification
    width: int
    default: t.Any


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


ColumnInput = list[t.Union[str, Column]]
Row = dict[str, t.Any]
RowInput = t.Union[t.Sequence[t.Any], Row]

T = t.TypeVar("T")


def has_next(seq: t.Sequence[T]) -> t.Generator[tuple[T, bool], None, None]:
    length = len(seq)
    for idx, val in enumerate(seq):
        yield val, idx < length - 1


class Table:
    def __init__(
        self, columns: ColumnInput, border: str = "light", head_border: str = "heavy"
    ) -> None:
        self.__columns: list[Column] = self.__resolve_columns(columns)
        self.__rows: list[Row] = []
        self._border = drawing.borders[border]
        self._head_border = BORDER_HEAVY_TRANS
        self._type_formatters: dict[type, t.Callable[[t.Any], str]] = {}

    def __str__(self):

        table = ""
        table += self._fmt_header()
        table += "\n"

        for row, has_next_row in has_next(self.__rows):
            table += self._fmt_row(row, has_next_row)
            if has_next_row:
                table += "\n"

        return table

    def _fmt_header(self) -> str:
        border = self._head_border
        header = ""

        header += border["corner"]["top_left"]
        for idx, col in enumerate(self.__columns):
            header += border["horizontal"] * (len(col["name"]) + 2)
            if idx < len(self.__columns) - 1:
                header += border["intersect"]["hori_top"]
            else:
                header += border["corner"]["top_right"]

        header += "\n"
        header += border["vertical"]
        for col in self.__columns:
            header += " "
            header += col["name"]
            header += " "
            header += border["vertical"]

        header += "\n"
        header += border["intersect"]["vert_left"]
        for col, has_next_column in has_next(self.__columns):
            header += border["horizontal"] * (len(col["name"]) + 2)
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
            formatted_cell = str(cell)

            if type(cell) in self._type_formatters:
                formatted_cell = self._type_formatters[type(cell)](formatted_cell)

            fmt += format(formatted_cell, f"<{len(col['name']) + 2}")
            fmt += border["vertical"]

        if not next_row:
            fmt += "\n"
            fmt += border["corner"]["bot_left"]
            for col, has_next_column in has_next(self.__columns):
                fmt += border["horizontal"] * (len(col["name"]) + 2)
                if has_next_column:
                    fmt += border["intersect"]["hori_bot"]
                else:
                    fmt += border["corner"]["bot_right"]

        return fmt

    def add_row(self, row: RowInput):
        if len(row) > len(self.__columns):
            raise ArcError("Too many values")

        if isinstance(row, dict):
            self.__rows.append(row)
        else:
            resolved = {}
            for col, value in itertools.zip_longest(self.__columns, row, fillvalue=""):
                resolved[col["name"]] = value

            self.__rows.append(resolved)

    def fmt_type(self, cls: type):
        def inner(func: t.Callable[[t.Any], str]):
            self._type_formatters[cls] = func
            return func

        return inner

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
