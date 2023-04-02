from __future__ import annotations

import typing as t


class Round:
    """Type Tranformation to round given input to `ndigits`

    ## Type Contraints
    - Supports `round()`

    ## Example
    ```py
    import arc
    from arc.types.middleware import Round

    @arc.command
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

    def __call__(self, value: t.SupportsRound[t.Any]) -> t.SupportsRound[t.Any]:
        return round(value, self.ndigits)


class SupportsSlice(t.Protocol):
    def __getitem__(self, slice: slice) -> SupportsSlice:
        ...


class Truncate:
    """Type transformation to truncate a value to `length`

    ## Type Constraints
    - Support list-like slice access

    ## Example
    ```py
    import arc
    from arc.types.middleware import Truncate

    @arc.command
    def command(val: Annotated[str, Truncate(6)])
        arc.print(val)

    command()
    ```

    ```console
    $ python example.py 'string longer than 6 chars'
    string
    ```
    """

    def __init__(self, length: int):
        self.length = length

    def __call__(self, value: SupportsSlice) -> SupportsSlice:
        return value[0 : self.length]


class PadProtocol(t.Protocol):
    def __add__(self, other: t.Any) -> PadProtocol:
        ...

    def __len__(self) -> int:
        ...


class Pad:
    """Type transformation to pad a value to `length` with `padding`.
    Ensures that value will be at least `length` long. `padding`
    should be the same type as value, so the concatenation functions properly

    ## Type Constraints
    - Support `len()`
    - Support `+` for concatenation (like `str` or `list`)

    ## Example
    ```py
    import arc
    from arc.types.middleware import Pad

    @arc.command
    def command(val: Annotated[str, Pad(6, 'b')])
        arc.print(val)

    command()
    ```

    ```console
    $ python example.py a
    abbbbbb
    ```
    """

    def __init__(
        self, length: int, padding: t.Any, side: t.Literal["left", "right"] = "right"
    ):
        self.length = length
        self.padding = padding
        self.side = side

    def __call__(self, value: PadProtocol) -> PadProtocol:
        if self.side == "right":
            while len(value) < self.length:
                value += self.padding
        else:
            while len(value) < self.length:
                value = self.padding + value

        return value
