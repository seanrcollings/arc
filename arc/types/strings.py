from __future__ import annotations

import typing as t
from collections import UserString

from arc.prompt.prompts import input_prompt
from arc.types.default import Default
from arc.types.type_arg import TypeArg
from arc.types.type_info import TypeInfo
from arc.types.middleware import Len

if t.TYPE_CHECKING:
    from arc.define import Param
    from arc.runtime import Context

__all__ = ["Char", "Password"]


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
