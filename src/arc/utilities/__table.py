from arc._utils import decorate_text


class Table:
    def __init__(self, headers: list, rows: dict, column_width: int = 20):
        self.headers = headers
        self.rows = rows
        self.column_width = column_width

    def print_table(self):
        print("")
        format_headers = [
            self.formatter("name".upper(), align="^", tcolor="33", style="4")
        ]

        format_headers += [
            self.formatter(header.upper(), align="^", tcolor="33", style="4")
            for header in self.headers
        ]

        print(*format_headers)

        for key, value in self.rows.items():
            formatted_string = self.formatter(
                key,
                align="<",
            )
            print(formatted_string, end="")
            for item in value:
                print(" ", end="")
                formatted_string = self.formatter(
                    str(item),
                    align=">",
                )
                print(formatted_string, end="")
            print()

        print()

    def formatter(self,
                  string,
                  align="<",
                  type_of="s",
                  tcolor="32",
                  bcolor="40",
                  style="1"):
        formatted = format(string, f"{align}{self.column_width}{type_of}")
        return decorate_text(formatted, tcolor, bcolor, style)
