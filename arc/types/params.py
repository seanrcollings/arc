from typing import TypeVar
import enum

from arc.utils import symbol


NO_DEFAULT = symbol("NO_DEFAULT")


T = TypeVar("T")
V = TypeVar("V")


class VarPositional(list[T]):
    ...


class VarKeyword(dict[str, V]):
    ...


class ParamType(enum.Enum):
    POS = "positional"
    KEY = "keyword"
    FLAG = "flag"
    SPECIAL = "special"
