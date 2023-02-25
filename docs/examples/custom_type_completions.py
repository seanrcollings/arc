import arc
from arc import autocompletions as ac


class CustomType:
    def __init__(self, val: int):
        self.val = val

    def __str__(self):
        return f"CustomType(val={self.val})"

    @classmethod
    def __convert__(cls, value: str):
        if value.isnumeric():
            return cls(int(value))
        else:
            raise arc.ConversionError(value, "must be an integer")

    @classmethod
    def __completions__(self, info: ac.CompletionInfo, param):
        return [
            ac.Completion("1"),
            ac.Completion("2"),
        ]


@arc.command
def main(foo: CustomType):
    arc.print(foo)


main()
