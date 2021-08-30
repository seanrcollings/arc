from __future__ import annotations
from typing import (
    Annotated,
    Optional,
    Any,
    Sequence,
    Callable,
    TypeVar,
    get_args,
    TYPE_CHECKING,
)
import enum
from dataclasses import dataclass, field
from arc.execution_state import ExecutionState

from arc.utils import symbol

from . import types

if TYPE_CHECKING:
    from arc.command.param import Param

# Represents a missing value
# Used to represent an arguments
# with no default value
MISSING = symbol("MISSING")
T = TypeVar("T")


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

    Usage:

    ```py
    @cli.subcommand()
    def command(val: Annotated[int, Meta(short='v')]):
        ...
    ```
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


def _positional_args(default: list, param: Param, state: ExecutionState):
    from . import convert

    assert state.parsed
    assert state.executable
    vals = state.parsed["pos_args"]
    exe = state.executable

    values = vals[len(exe.pos_params) :]

    state.parsed["pos_args"] = []
    if (args := get_args(param.annotation)) and not isinstance(args[0], TypeVar):
        values = [convert(value, args[0], param.arg_alias) for value in values]

    return values


def _keyword_args(default: dict, param: Param, state: ExecutionState):
    from . import convert

    assert state.parsed
    assert state.executable
    vals = state.parsed["options"]
    exe = state.executable

    values = {key: val for key, val in vals.items() if key not in exe.key_params}
    state.parsed["options"] = {}
    if (args := get_args(param.annotation)) and not isinstance(args[0], TypeVar):
        values = {key: convert(val, args[0], key) for key, val in values.items()}

    return values


VarPositional = Annotated[
    types.VarPositional[T],
    Meta(hidden=True, type=ParamType.SPECIAL, default=[], hooks=[_positional_args]),
]


VarKeyword = Annotated[
    types.VarKeyword[T],
    Meta(hidden=True, type=ParamType.SPECIAL, default={}, hooks=[_keyword_args]),
]
