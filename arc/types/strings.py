import typing as t
from arc.types import aliases

__all__ = ["strictstr", "Char"]


def strictstr(
    max_length: t.Optional[int] = None,
    min_length: t.Optional[int] = None,
    length: t.Optional[int] = None,
    matches: t.Optional[str] = None,
) -> type[str]:
    return type(
        "StrictStr",
        (aliases.StringAlias,),
        {
            "max_length": max_length,
            "min_length": min_length,
            "length": length,
            "matches": matches,
        },
    )


Char = strictstr(min_length=1, max_length=1)
"""String than can only be length 1"""
