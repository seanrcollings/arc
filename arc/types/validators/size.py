from __future__ import annotations
import typing as t

from arc import errors


class SupportsLen(t.Protocol):
    def __len__(self) -> int:
        ...


class Len:
    """Validator for the length of a value.

    - `Len(4)` - Value must be length 4
    - `Len(1, 4)` - Value must be from length 1 to 4

    ## Type Constraints
    - Supports `len()`
    """

    def __init__(self, min: int, max: int | None = None):
        self.min = min
        self.max = max

    def __call__(self, value: SupportsLen):
        length = len(value)

        if self.max:
            if length < self.min:
                raise errors.ValidationError(
                    f"must have a length between {self.min} and {self.max}"
                )
            if length > self.max:
                raise errors.ValidationError(
                    f"must have a length between {self.min} and {self.max}"
                )
        else:
            if length != self.min:
                raise errors.ValidationError(f"must have a length equal to {self.min}")

        return value


class SupportsComparison(t.Protocol):
    def __gt__(self, other: SupportsComparison) -> bool:
        ...

    def __lt__(self, other: SupportsComparison) -> bool:
        ...

    def __le__(self, other: SupportsComparison) -> bool:
        ...

    def __ge__(self, other: SupportsComparison) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...


class GreaterThan:
    """Validator to limit the maximum size of a value

    ## Type Constraints
    - Supports Comparison (<, >, ==)
    """

    def __init__(self, smallest: SupportsComparison):
        self.smallest = smallest

    def __call__(self, value: SupportsComparison):
        if value <= self.smallest:
            raise errors.ValidationError(f"must be greater than {self.smallest}")

        return value


class LessThan:
    """Validator to limit the minimum size of a value

    ## Type Constraints
    - Supports Comparison (<, >, ==)
    """

    def __init__(self, largest: SupportsComparison):
        self.largest = largest

    def __call__(self, value: SupportsComparison):
        if value >= self.largest:
            raise errors.ValidationError(f"must be less than {self.largest}")

        return value


class Between:
    """Validator to ensure that a value falls within a particular range

    ## Type Constraints
    - Supports Comparison (<, >, ==)
    """

    def __init__(self, lower: SupportsComparison, upper: SupportsComparison):
        self.lower = lower
        self.upper = upper

    def __call__(self, value: SupportsComparison):
        if value <= self.lower or value >= self.upper:
            raise errors.ValidationError(
                f"must be between {self.lower} and {self.upper}"
            )

        return value
