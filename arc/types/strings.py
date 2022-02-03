import typing as t
from arc.types import aliases
from arc.types.helpers import password_prompt

__all__ = ["strictstr", "Char", "Password"]


def strictstr(
    *,
    max_length: t.Optional[int] = None,
    min_length: t.Optional[int] = None,
    length: t.Optional[int] = None,
    matches: t.Optional[str] = None,
    name: t.Optional[str] = None,
) -> type[str]:
    return type(
        name or "StrictStr",
        (aliases.StringAlias,),
        {
            "max_length": max_length,
            "min_length": min_length,
            "length": length,
            "matches": matches,
        },
    )


Char = strictstr(name="Char", min_length=1, max_length=1)
"""String than can only be length 1"""


class Password(str):
    """For Secret Strings.
    Prints a * for each character in place of the actual string.

    When prompted for input, the user's input will not be echoed to the screen.
    """

    __prompt__ = password_prompt

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "*" * len(self)

    @classmethod
    def __convert__(cls, value):
        return cls(value)
