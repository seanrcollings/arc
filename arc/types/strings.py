import typing as t
from arc import errors
from arc.types import aliases
from arc.prompt.prompts import password_prompt
from arc.types.strict import RegexValidator, StrictType

__all__ = ["Char", "Password"]


class StrictStr(StrictType[str], RegexValidator, str):
    max_length: t.ClassVar[t.Optional[int]] = None
    min_length: t.ClassVar[t.Optional[int]] = None
    length: t.ClassVar[t.Optional[int]] = None
    matches: t.ClassVar[t.Optional[str]] = None

    @classmethod
    def validate(cls, value: str) -> str:
        length = len(value)

        if cls.max_length and length > cls.max_length:
            raise ValueError(f"maximum length is {cls.max_length}")

        if cls.min_length and length < cls.min_length:
            raise ValueError(f"minimum length is {cls.min_length}")

        if cls.length and length != cls.length:
            raise ValueError(f"must be {cls.length} characters long")

        cls._match(value)

        return value


class Char(StrictStr):
    """String than can only be length 1"""

    length: t.ClassVar[t.Optional[int]] = 1


class Password(str):
    """For Secret Strings.

    When prompted for input, the user's input will not be echoed to the screen.
    """

    __prompt__ = password_prompt

    @classmethod
    def __convert__(cls, value):
        return cls(value)
