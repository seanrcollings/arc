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

    By default, `str(Password())` will emit only asterisks to prevent you from emitting it to places you don't intend.
    If you need the actual string representation you can use `repr(Password())`. Alternatively you can disable this using
    an  annotated type argument:

    ```py
    from typing import Annotated
    import arc
    from arc.types import Password

    @arc.command
    def command(password: Annotated[Password, Password.Args(obscure=False)]):
        print(password)
    ```
    """

    def __init__(self, seq: object, obscure: bool = True) -> None:
        super().__init__(seq)
        self.__obscure = obscure

    def __str__(self) -> str:
        if self.__obscure:
            return "*" * len(self)

        return super().__str__()

    def __repr__(self) -> str:
        return super().__str__()

    @classmethod
    def __prompt__(cls, param: Param[str], ctx: Context) -> str:
        return input_prompt(param, ctx, echo=False)

    @classmethod
    def __convert__(cls, value: str, info: TypeInfo[str]) -> Password:
        args = info.type_arg or cls.Args()
        return cls(value, **args.dict())

    class Args(TypeArg):
        __slots__ = ("obscure",)

        def __init__(self, obscure: bool = Default(True)) -> None:
            self.obscure = obscure
