from __future__ import annotations

import re
import typing as t

from arc import errors

if t.TYPE_CHECKING:
    from arc.define.param.param import Param
    from arc.runtime.context import Context


class Matches:
    """Validator to match a regular expression.

    ## Type Constraints
    - Matches against `str(value)`, so the type must have a sensible string representation
    """

    def __init__(self, pattern: str | re.Pattern[str], flags: int = 0):
        self.pattern = pattern
        self.flags = flags

    def __call__(self, value: t.Any) -> t.Any:
        if not re.match(self.pattern, str(value), self.flags):
            raise errors.ValidationError(
                f"does not match expected format: {self.pattern}"
            )

        return value


class SupportsLen(t.Protocol):
    def __len__(self) -> int:
        ...


class Len:
    """Validator for the length of a value.

    - `Len(4)` - Value must be length 4
    - `Len(1, 4)` - Value must be from length 1 to 4

    ## Type Constraints
    - Supports `len()`

    **Note**: If you find yourself doing something similar to `Annotated[list[int], Len(2)]`,
    it's generally going to be a bettter idea to do: `tuple[int, int]`
    """

    def __init__(self, min: int, max: int | None = None):
        self.min = min
        self.max = max

    def __call__(
        self,
        value: SupportsLen,
        ctx: Context | None = None,
        param: Param[t.Any] | None = None,
    ) -> SupportsLen:
        length = len(value)

        if self.max:
            if length < self.min or length > self.max:
                if param and param.type.is_collection_type:
                    raise errors.ValidationError(
                        f"expects between {self.min} and {self.max} arguments"
                    )

                raise errors.ValidationError(
                    f"must have a length between {self.min} and {self.max}"
                )
        elif length != self.min:
            if param and param.type.is_collection_type:
                raise errors.ValidationError(f"expects {self.min} arguments")

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

    def __call__(self, value: SupportsComparison) -> SupportsComparison:
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

    def __call__(self, value: SupportsComparison) -> SupportsComparison:
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

    def __call__(self, value: SupportsComparison) -> SupportsComparison:
        if value <= self.lower or value >= self.upper:
            raise errors.ValidationError(
                f"must be between {self.lower} and {self.upper}"
            )

        return value
