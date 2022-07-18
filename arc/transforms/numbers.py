import typing as t


class Round:
    """Type Tranformation to round given input to `ndigits`

    ```
    @arc.command()
    def command(val: Annotated[float, Round(2)])
        print(val)
    ```

    >>> command('1.123456789')
    1.23
    """

    __slots__ = ("ndigits",)

    def __init__(self, ndigits: int) -> None:
        self.ndigits = ndigits

    def __call__(self, value: t.SupportsRound) -> t.SupportsRound:
        return round(value, self.ndigits)
