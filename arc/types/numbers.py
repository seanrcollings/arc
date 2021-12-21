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
    name: str = None,
) -> type[aliases.IntAlias]:
    return type(
        name or "StrictInteger",
        (aliases.IntAlias,),
        {
            "base": base,
            "greater_than": greater_than,
            "less_than": less_than,
            "matches": matches,
        },
    )


Binary = strictint(base=2, name="Binary")
Oct = strictint(base=8, name="Oct")
Hex = strictint(base=16, name="Hex")
PositiveInt = strictint(greater_than=0, name="PositiveInt")
NegativeInt = strictint(less_than=0, name="NegativeInt")

# Floats -------------------------------------------------------------------
def strictfloat(
    greater_than: t.Union[int, float] = float("-inf"),
    less_than: t.Union[int, float] = float("inf"),
    matches: str = None,
    min_precision: t.Optional[int] = None,
    max_precision: t.Optional[int] = None,
    precision: t.Optional[int] = None,
    name: str = None,
) -> type[aliases.FloatAlias]:
    return type(
        name or "StrictFloat",
        (aliases.FloatAlias,),
        {
            "greater_than": greater_than,
            "less_than": less_than,
            "min_precision": min_precision,
            "max_precision": max_precision,
            "precision": precision,
            "matches": matches,
        },
    )


PositiveFloat = strictfloat(greater_than=0, name="PositiveFloat")
NegativeFloat = strictfloat(less_than=0, name="NegativeFloat")


AnyNumber = t.Union[float, Hex, Oct, Binary, int]
