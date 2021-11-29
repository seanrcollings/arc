import typing as t
from arc.types import aliases

__all__ = [
    "Hex",
    "Oct",
    "Binary",
    "PositiveInt",
    "NegativeInt",
    "PositiveFloat",
    "NegativeFloat",
    "AnyNumber",
    "strictint",
    "strictfloat",
]
# Integers ----------------------------------------------------------------
def strictint(
    base: int = 10,
    greater_than: t.Union[int, float] = float("-inf"),
    less_than: t.Union[int, float] = float("inf"),
    matches: str = None,
) -> type[int]:
    return type(
        "StrictInteger",
        (aliases.IntAlias,),
        {
            "base": base,
            "greater_than": greater_than,
            "less_than": less_than,
            "matches": matches,
        },
    )


Binary = strictint(base=2)
Oct = strictint(base=8)
Hex = strictint(base=16)
PositiveInt = strictint(greater_than=0)
NegativeInt = strictint(less_than=0)

# Floats -------------------------------------------------------------------
def strictfloat(
    greater_than: t.Union[int, float] = float("-inf"),
    less_than: t.Union[int, float] = float("inf"),
    matches: str = None,
) -> type[int]:
    return type(
        "StrictFloat",
        (aliases.FloatAlias,),
        {
            "greater_than": greater_than,
            "less_than": less_than,
            "matches": matches,
        },
    )


PositiveFloat = strictfloat(greater_than=0)
NegativeFloat = strictfloat(less_than=0)


AnyNumber = t.Union[float, Hex, Oct, Binary, int]
