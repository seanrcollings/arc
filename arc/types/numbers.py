from __future__ import annotations
import typing as t
from arc import errors
from arc.types.strict import RegexValidator, StrictType, ComparisonValidator

if t.TYPE_CHECKING:
    import re

__all__ = [
    "Hex",
    "Oct",
    "Binary",
    "PositiveInt",
    "NegativeInt",
    "PositiveFloat",
    "NegativeFloat",
    "AnyNumber",
    "StrictInt",
    "StrictFloat",
]


# Integers ----------------------------------------------------------------
class StrictInt(StrictType[int], ComparisonValidator[int], RegexValidator, int):
    base: t.ClassVar[int] = 10
    greater_than: t.ClassVar[int | None] = None
    less_than: t.ClassVar[int | None] = None
    matches: t.ClassVar[str | re.Pattern | None] = None

    @classmethod
    def validate(cls, value) -> int:
        cls._match(value)
        value = int(value, base=cls.base)
        cls.compare(value)

        return value


class Binary(StrictInt):
    base = 2


class Oct(StrictInt):
    base = 8


class Hex(StrictInt):
    base = 16


class PositiveInt(StrictInt):
    greater_than = 0


class NegativeInt(StrictInt):
    less_than = 0


# Floats -------------------------------------------------------------------


class StrictFloat(StrictType[float], ComparisonValidator[float], float):
    greater_than: t.ClassVar[float | int | None] = None
    less_than: t.ClassVar[float | int | None] = None
    matches: t.ClassVar[int | None] = None
    min_precision: t.ClassVar[int | None] = None
    max_precision: t.ClassVar[int | None] = None
    precision: t.ClassVar[int | None] = None

    @classmethod
    def validate(cls, value: str) -> float:
        _natural, fractional = value.split(".")

        if cls.min_precision and cls.min_precision > len(fractional):
            raise errors.ConversionError(
                value, f"minimum decimal precision allowed is {cls.min_precision}"
            )

        if cls.max_precision and cls.max_precision < len(fractional):
            raise errors.ConversionError(
                value, f"maximum decimal precision allowed is {cls.max_precision}"
            )

        if cls.precision and cls.precision != len(fractional):
            raise errors.ConversionError(
                value, f"decimal precision must be {cls.precision}"
            )

        number = float(value)
        cls.compare(number)

        return number


class PositiveFloat(StrictFloat):
    greater_than: t.ClassVar[float | int | None] = 0


class NegativeFloat(StrictFloat):
    less_than: t.ClassVar[float | int | None] = 0


AnyNumber = t.Union[float, Hex, Oct, Binary, int]
