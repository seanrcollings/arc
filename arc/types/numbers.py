from __future__ import annotations
import typing as t

from arc.types.default import Default
from arc.types.type_arg import TypeArg
from arc.types.validators import GreaterThan, LessThan


__all__ = [
    "Hex",
    "Oct",
    "Binary",
    "PositiveInt",
    "NegativeInt",
    "PositiveFloat",
    "NegativeFloat",
    "AnyNumber",
]


class IntArgs(TypeArg):
    __slots__: tuple[str, ...] = ("base",)

    def __init__(self, base: int = Default(10)) -> None:
        self.base = base


Binary = t.Annotated[int, IntArgs(base=2)]
Oct = t.Annotated[int, IntArgs(base=8)]
Hex = t.Annotated[int, IntArgs(base=16)]
PositiveInt = t.Annotated[int, GreaterThan(0)]
NegativeInt = t.Annotated[int, LessThan(0)]
PositiveFloat = t.Annotated[float, GreaterThan(0)]
NegativeFloat = t.Annotated[float, LessThan(0)]
AnyNumber = t.Union[float, Hex, Oct, Binary, int]
