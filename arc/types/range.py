import math
import typing as t


class Range(int):
    def __new__(cls, value: int, _lower: t.Any = ..., _upper: t.Any = ...):
        obj = int.__new__(Range, value)
        return obj

    def __init__(self, _value: int, lower: t.Any = ..., upper: t.Any = ...):
        super().__init__()
        self.lower = lower if isinstance(lower, int) else float("-inf")
        self.upper = upper if isinstance(upper, int) else float("inf")

        assert self.lower <= self <= self.upper, "Value must between lower and upper"

    def range(self, step: int = 1):
        """Returns the result of `range(lower, upper + 1, step)"""
        if math.isinf(self.lower) or math.isinf(self.upper):
            raise ValueError("Cannot obtain a range when lower or upper is unbounded")

        return range(self.lower, self.upper + 1, step)  # type: ignore

    def range_with_picked(
        self, step: int = 1
    ) -> t.Generator[tuple[int, bool], None, None]:
        """Iterator that returns each integer in the specified range, along
        with whether or not it was the value picked"""
        for i in self.range(step):
            yield i, i == self
