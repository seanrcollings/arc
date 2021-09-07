from __future__ import annotations
import inspect
from typing import Any, Callable, Optional, TYPE_CHECKING, Sequence

from arc import errors
from arc.color import fg, colorize
from arc.config import config
from arc.execution_state import ExecutionState
from arc.types.params import MISSING, ParamType

if TYPE_CHECKING:
    from arc.types import Meta


class Param:
    """Represents a single command-line parameter.

    Instance Variables:
        paramater (inspect.Paramater): The Paramater object generated
            for the associated function argument. Usually not needed as
            the other values should provide all context needed. But we
            store it off just in case.
        arg_name (str): The actual name of the argument of the function.
            can be used to pass some value to said function
        arg_alias (str): The name to be used to pass a value to
            the argument from the command line. Will default to the
            `arg_name` if no other value is provided
        annotation (type): The type of the argument
        default (Any): Default value for the argument
        hidden (bool): Whether or not the value is visible to the
            command  line. Usually used to hide `Context` arguments
        short (str): the single-character shortened name for the
            argument on the command line
    """

    def __init__(
        self,
        arg_name: str,
        annotation: type,
        arg_alias: str = None,
        type: ParamType = ParamType.POS,
        short: str = None,
        hidden: bool = False,
        default: Any = MISSING,
        hooks: Sequence[Callable[[Any, Param, ExecutionState], Any]] = None,
    ):
        self.annotation = annotation
        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.type: ParamType = type
        self.short: Optional[str] = short
        self.hidden: bool = hidden
        self.default: Any = default
        self.hooks = hooks if hooks else []

        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Argument {self.arg_name}'s shortened name is longer than 1 character"
            )

    def run_hooks(self, val: Any, state: ExecutionState):
        for hook in self.hooks:
            val = hook(val, self, state)
        return val

    def __repr__(self):
        type_name = getattr(self.annotation, "__name__", self.annotation)

        return f"<Param {self.arg_name}({self.type}): {type_name} = {self.default}>"

    def __format__(self, spec: str):
        modifiers = spec.split("|")
        name = self.arg_alias

        if self.is_positional:
            formatted = f"<{name}>"
        else:
            if "short" in modifiers:
                assert self.short
                name = self.short
                denoter = config.short_flag_denoter
            else:
                denoter = config.flag_denoter

            formatted = f"{denoter}{name}"

            if "usage" in modifiers:
                if self.is_keyword:
                    formatted += " <...>"

        if self.optional:
            formatted = f"[{formatted}]"

        return formatted

    @property
    def optional(self):
        return self.default is not MISSING

    @property
    def is_keyword(self):
        return self.type is ParamType.KEY

    @property
    def is_positional(self):
        return self.type is ParamType.POS

    @property
    def is_flag(self):
        return self.type is ParamType.FLAG

    @property
    def is_special(self):
        return self.type is ParamType.SPECIAL
