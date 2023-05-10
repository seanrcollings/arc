from __future__ import annotations
import re

import typing as t
from collections import UserString

from arc.prompt.prompts import input_prompt
from arc.types.middleware import Len, Matches

if t.TYPE_CHECKING:
    from arc.define import Param
    from arc.runtime import Context

__all__ = ["Char", "Password", "Email"]


Char = t.Annotated[str, Len(1)]
"""String than can only be length 1"""


class Password(UserString):
    """For Secret Strings.

    When prompted for input, the user's input will not be echoed to the screen.

    Additionally, the string will be obscured when printed. For example:

    ```py
    from typing import Annotated
    import arc
    from arc.types import Password

    @arc.command
    def command(password: Password):
        print(password) # This would be obscured
        print(password.data) # This would be the actual password
    ```
    """

    def __str__(self) -> str:
        return "*" * len(self)

    def __repr__(self) -> str:
        return "Password()"

    @classmethod
    def __prompt__(cls, param: Param[str], ctx: Context) -> str:
        return input_prompt(param, ctx, echo=False)

    @classmethod
    def __convert__(cls, value: str) -> Password:
        return cls(value)


# https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression

email_regex = re.compile(
    r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
)

Email = t.Annotated[str, Matches(email_regex, message="is not a valid email address")]
"""String type with email validation"""
