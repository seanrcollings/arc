import typing as t


class Round:
    """Type Tranformation to round given input to `ndigits`

    ## Type Contraints
    - Reports `round()`

    ## Example
    ```py
    import arc
    from arc.transforms import Round

    @arc.command()
    def command(val: Annotated[float, Round(2)])
        arc.print(val)

    command()
    ```

    ```console
    $ python example.py 1.123456789
    1.23
    ```
    """

    __slots__ = ("ndigits",)

    def __init__(self, ndigits: int) -> None:
        self.ndigits = ndigits

    def __call__(self, value: t.SupportsRound) -> t.SupportsRound:
        return round(value, self.ndigits)
