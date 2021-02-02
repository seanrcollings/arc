from arc.color import fg, effects


class Table:
    def __init__(self, headers: list, rows: list, column_width: int = 20):
        self.__headers = headers
        self.__rows = rows
        self.__column_width = column_width

    def __str__(self):

        table = "\n"
        table += " ".join(
            [
                self.__formatter(
                    header.upper(),
                    align="^",
                    tcolor=fg.YELLOW,
                    style=effects.UNDERLINE,
                )
                for header in self.__headers
            ]
        )

        table += "\n"

        for row in self.__rows:
            for item in row:
                formatted_string = self.__formatter(str(item), align=">",)
                table += formatted_string + " "
            table += "\n"

        return table

    def __formatter(
        self,
        string,
        align="<",
        type_of="s",
        tcolor=fg.GREEN,
        bcolor="",
        style=effects.BOLD,
    ):
        formatted = format(string, f"{align}{self.__column_width}{type_of}")
        return f"{tcolor}{bcolor}{style}{formatted}{effects.CLEAR}"
