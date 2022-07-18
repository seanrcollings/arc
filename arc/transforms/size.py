from __future__ import annotations
import typing as t


class SupportsSlice(t.Protocol):
    def __getitem__(self, slice: slice) -> SupportsSlice:
        ...


class Truncate:
    """Type transformation to truncate a value to `length`

    ### Type Restrictions
    - Support list-like slice access

    ```
    @arc.command()
    def command(val: Annotated[str, Truncate(6)])
        print(val)
    ```

    >>> command('string longer than 6 chars')
    string
    """

    def __init__(self, length: int):
        self.length = length

    def __call__(self, value: SupportsSlice) -> SupportsSlice:
        return value[0 : self.length]


class PadProtocol(t.Protocol):
    def __add__(self, other) -> PadProtocol:
        ...

    def __len__(self) -> int:
        ...


class Pad:
    """Type transformation to pad a value to `length` with `padding`.
    Ensures that value will be at least `length` long. `padding`
    should be the same type as value, so the concatenation functions properly

    ### Type Constraints
    - Support `len()`
    - Support `+` for concatenation (like `str` or `list`)

    ```
    @arc.command()
    def command(val: Annotated[str, Pad(6, 'b')])
        print(val)
    ```

    >>> command('a')
    'abbbbbb'
    """

    def __init__(self, length: int, padding: t.Any = None):
        self.length = length
        self.padding = padding

    def __call__(self, value: PadProtocol):
        while len(value) < self.length:
            value += self.padding

        return value
