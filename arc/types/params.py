from __future__ import annotations
from typing import Annotated, Optional, Any, Sequence, Callable, TypeVar
import enum
from dataclasses import dataclass, field
from arc.execution_state import ExecutionState

from arc.utils import symbol
from arc.types.helpers import UnwrapHelper

# Represents a missing value
# Used to represent an arguments
# with no default value
MISSING = symbol("MISSING")


@dataclass
class Meta:
    """Represents meta-data about an argument

    Args:
    name (str): The name that will be used on the command line for this argument
    type (ParamType): The type of the argument. `ParamType.POS` or `ParamType.KEY`
        are the most common
    short (str): The single-character short name to refer to this argument
        on the command line
    hidden (bool): whether or not this paramater is exposed to the command line
    default (Any): Value to pass if no value is given on the command line
    """

    name: Optional[str] = None
    type: Optional[ParamType] = None
    short: Optional[str] = None
    hidden: bool = False
    default: Any = MISSING
    hooks: Sequence[Callable[[Any, ExecutionState], Any]] = field(default_factory=list)


def meta(**kwargs):
    """Wraps a given type with Meta data. Any
    refernce to that type will carry the same
    meta-data

    ```py
    @meta(short="s")
    class Shoe:
        ...

    # Both of these commands will have the short-name of "s"
    @cli.subcommand()
    def command(shoe: Shoe):
        ...

    @cli.subcommand()
    def other_command(shoe: Shoe):
        ...
    ```
    """

    def inner(cls: type):
        return Annotated[cls, Meta(**kwargs)]

    return inner


class ParamType(enum.Enum):
    POS = "positional"
    KEY = "keyword"
    FLAG = "flag"
    SPECIAL = "special"


T = TypeVar("T")
V = TypeVar("V")


class VarPositional(list[T], UnwrapHelper):
    ...


WrappedVarPositional = Annotated[
    VarPositional[T], Meta(hidden=True, type=ParamType.SPECIAL)
]


class VarKeyword(dict[str, V], UnwrapHelper):
    ...


WrappedVarKeyword = Annotated[VarKeyword[V], Meta(hidden=True, type=ParamType.SPECIAL)]
