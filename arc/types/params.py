"""Defines types relevant to Param Definition / Creation"""
from __future__ import annotations
from typing import (
    Annotated,
    Optional,
    Any,
    MutableSequence,
    Callable,
    TextIO,
    TypeVar,
    get_args,
    TYPE_CHECKING,
)
import enum
from dataclasses import dataclass, field
from arc.execution_state import ExecutionState

from arc.utils import symbol
from arc.types.type_store import convert

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
        hooks (Callable): sequence of callable objects

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
    hooks: MutableSequence[Callable[[Any, Param, ExecutionState], Any]] = field(
        default_factory=list
    )


def meta(**kwargs):
    """Wraps a given type with meta-data. Any
    refernce to that type will carry the same
    meta-data

    ```py
    @meta(short="s")
    class Shoe:
        ...

    # Both of these command's 'shoe' argument will have the short-name of "s"
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
    """All the types that a Paramater can be

    - `POS` is given to regular arguments to a function
    - `KEY` is given to keyword-only arguments of a function
    - `FLAG` is given to arguments with a `bool` annotation
    - `SPECIAL` isn't given to any arguments by default, but
        can be used to explicitly mark a a special type. Internally,
        arc uses this to mark `Context`, `VarPositional `, and `VarKeyword`
    """

    POS = "positional"
    KEY = "keyword"
    FLAG = "flag"
    SPECIAL = "special"


class _VarPositional(list[T]):
    @staticmethod
    def positional_hook(_default: list, param: Param, state: ExecutionState):
        assert state.parsed
        values = state.parsed["pos_args"]
        state.parsed["pos_args"] = []

        if (args := get_args(param.annotation)) and not isinstance(args[0], TypeVar):
            values = [convert(value, args[0], param.arg_alias) for value in values]

        return values


class _VarKeyword(dict[str, T]):
    @staticmethod
    def keyword_hook(_default: dict, param: Param, state: ExecutionState):
        assert state.parsed
        values = state.parsed["options"]
        state.parsed["options"] = {}

        if (args := get_args(param.annotation)) and not isinstance(args[0], TypeVar):
            values = {key: convert(val, args[0], key) for key, val in values.items()}

        return values


VarPositional = Annotated[
    _VarPositional[T],
    Meta(
        hidden=True,
        type=ParamType.SPECIAL,
        default=[],
        hooks=[_VarPositional.positional_hook],
    ),
]


VarKeyword = Annotated[
    _VarKeyword[T],
    Meta(
        hidden=True,
        type=ParamType.SPECIAL,
        default={},
        hooks=[_VarKeyword.keyword_hook],
    ),
]


def _open_file(mode: str):
    def inner(val, _param, _state):
        with open(val, mode) as file:
            yield file

    return inner


class File:
    Read = Annotated[TextIO, Meta(hooks=[_open_file("r")])]
    Write = Annotated[TextIO, Meta(hooks=[_open_file("w")])]
    Append = Annotated[TextIO, Meta(hooks=[_open_file("a")])]
    ReadWrite = Annotated[TextIO, Meta(hooks=[_open_file("r+")])]
