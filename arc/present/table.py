from typing import TypedDict, Union, cast, Any, Sequence
from arc.errors import ArcError
from arc.color import fg, effects
from .data import justifications, Justification


class ColumnBase(TypedDict):  # pylint: disable=inherit-non-class
    """ColumnBase Type"""

    name: str


class Column(ColumnBase, total=False):  # pylint: disable=inherit-non-class
    """Column Type"""

    justify: Justification
    width: int


DEFAULT_COLUMN: Column = {
    "name": "NAME",
    "justify": "left",
    "width": 20,
}


def _format_column(column: Column, column_index):
    return Table.formatter(
        string=column["name"],
        align=justifications[column["justify"]],
        width=column["width"],
        tcolor=fg.YELLOW,
        style=effects.UNDERLINE,
    )


def _format_cell(content, column: Column, row_idx, column_idx):
    return (
        Table.formatter(
            string=content,
            width=column["width"],
            align=justifications[column["justify"]],
        )
        + " "
    )


ColumnInput = list[Union[str, Column]]
RowInput = Sequence[Union[Sequence[Any], dict[str, Any]]]


class Table:
    """Present data in a table-like format"""

    def __init__(
        self,
        columns: ColumnInput,
        rows: RowInput,
        format_column=_format_column,
        format_cell=_format_cell,
    ):
        self.__columns = self.__resolve_columns(columns)
        self.__rows: list[dict[str, Any]] = self.__resolve_rows(rows)
        self.format_column = format_column
        self.format_cell = format_cell

    def __str__(self):

        table = "\n"
        table += " ".join(
            [
                self.format_column(column, idx)
                for idx, column in enumerate(self.__columns.values())
            ]
        )

        table += "\n"

        for row_idx, row in enumerate(self.__rows):
            for col_idx, column in enumerate(self.__columns.values()):
                table += self.format_cell(
                    str(row[column["name"]]),
                    column,
                    row_idx,
                    col_idx,
                )

            table += "\n"

        return table

    @staticmethod
    def formatter(
        string,
        width=20,
        align="<",
        tcolor=fg.GREEN,
        bcolor="",
        style=effects.BOLD,
    ):
        return f"{tcolor}{bcolor}{style}{string:{align}{width}}{effects.CLEAR}"

    def resize_columns(self, pad: int = 0):
        for row in self.__rows:
            for column, data in row.items():
                if len(str(data)) > self.__columns[column]["width"]:
                    self.__columns[column]["width"] = len(str(data)) + pad

    def __resolve_rows(self, rows: RowInput):
        resolved: list[dict[str, Any]] = []
        column_names = self.__columns.keys()
        for row in rows:
            if isinstance(row, list):
                if len(row) == len(self.__columns):
                    resolved.append(
                        {key: row[idx] for idx, key in enumerate(column_names)}
                    )
                else:
                    raise ArcError(
                        f"{row} has too few or too many items "
                        f"for {len(self.__columns)} columns"
                    )
            elif isinstance(row, dict):
                if all(name in row for name in column_names):
                    resolved.append(row)
                else:
                    raise ArcError(f"{row} does not match column schema {column_names}")
            else:
                raise ArcError(
                    "Each row must either be a list of strings or a dictionary"
                )

        return resolved

    @staticmethod
    def __resolve_columns(columns: ColumnInput) -> dict[str, Column]:
        resolved: dict[str, Column] = {}
        for column in columns:
            copy = DEFAULT_COLUMN.copy()

            if isinstance(column, str):
                copy.update({"name": column})

            elif isinstance(column, dict):
                column = cast(Column, column)
                copy.update(column)  # type: ignore
            else:
                raise ArcError("Columns must either be a string or a dictionary")

            resolved[copy["name"]] = copy

        return resolved
