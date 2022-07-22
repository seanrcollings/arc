import typing as t
from arc.prompt.prompts import password_prompt
from arc.types.validators import Len

__all__ = ["Char", "Password"]


Char = t.Annotated[str, Len(1)]
"""String than can only be length 1"""


class Password(str):
    """For Secret Strings.

    When prompted for input, the user's input will not be echoed to the screen.
    """

    __prompt__ = password_prompt

    @classmethod
    def __convert__(cls, value):
        return cls(value)
