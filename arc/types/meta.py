from __future__ import annotations
from typing import Annotated, Optional, Any, Sequence, Callable
from dataclasses import dataclass, field
from arc.command.param import ParamType, NO_DEFAULT
from arc.execution_state import ExecutionState


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
    default: Any = NO_DEFAULT
    hooks: Sequence[Callable[[Any, ExecutionState], Any]] = field(default_factory=list)


def meta(**kwargs):
    """Wraps a given type with Meta data. Any
    refernce to that type will carry the same
    meta-data

    ```py
    @meta(hidden=True, short="s")
    class Shoe:
        ...

    @cli.subcommand()
    def command(shoe: Shoe):
        ...
    ```
    """

    def inner(cls: type):
        return Annotated[cls, Meta(**kwargs)]

    return inner
