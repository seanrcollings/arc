from __future__ import annotations
import re
import typing as t

from arc import errors


T = t.TypeVar("T")


class StrictType(t.Generic[T]):
    def __new__(cls, value: str):
        return cls.validate(value)

    @classmethod
    def validate(cls, value: str) -> T:
        ...


V = t.TypeVar("V", contravariant=True)


class Comparable(t.Protocol[V]):
    def __gt__(self, other: V) -> bool:
        ...

    def __lt__(self, other: V) -> bool:
        ...

    def __ge__(self, other: V) -> bool:
        ...

    def __le__(self, other: V) -> bool:
        ...


class ComparisonValidator(t.Generic[T]):
    greater_than: t.ClassVar[Comparable[T] | None]
    less_than: t.ClassVar[Comparable[T] | None]

    @classmethod
    def compare(cls, value: Comparable[T]):
        if cls.less_than and value >= cls.less_than:
            raise errors.ConversionError(value, f"must be less than {cls.less_than}")
        if cls.greater_than and value <= cls.greater_than:
            raise errors.ConversionError(
                value, f"must be greater than {cls.greater_than}"
            )


class RegexValidator:
    matches: t.ClassVar[str | re.Pattern | None]

    @classmethod
    def _match(cls, value: str):
        if cls.matches and not re.match(cls.matches, value):
            raise errors.ConversionError(
                value, f"does not follow required format: {cls.matches}"
            )
