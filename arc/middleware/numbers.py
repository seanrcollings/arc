import typing as t


class Round:
    __slots__ = ("ndigits",)

    def __init__(self, ndigits: int) -> None:
        self.ndigits = ndigits

    def __call__(self, value: t.SupportsRound) -> t.SupportsRound:
        return round(value, self.ndigits)
