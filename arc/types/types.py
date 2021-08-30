from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")


class VarPositional(list[T]):
    ...


class VarKeyword(dict[str, V]):
    ...
