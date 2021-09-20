from __future__ import annotations
from typing import Any, Callable, Optional, TYPE_CHECKING, Sequence

from arc import errors
from arc.color import colorize, fg
from arc.config import config
from arc.execution_state import ExecutionState
from arc.types.params import MISSING, ParamType
from arc.types import convert

if TYPE_CHECKING:
    from arc.types import Meta

Hooks = Sequence[Callable[[Any, "Param", ExecutionState], Any]]


class BuiltinHooks:
    @staticmethod
    def pre_run(default: Any, param: Param, state: ExecutionState):
        if param.type is ParamType.SPECIAL:
            return default

        if param.type is ParamType.POS:
            value = BuiltinHooks.handle_postional(default, param, state)
        elif param.type is ParamType.KEY:
            value = BuiltinHooks.handle_keyword(default, param, state)
        elif param.type is ParamType.FLAG:
            value = BuiltinHooks.handle_flag(default, param, state)

        if isinstance(value, str):
            value = BuiltinHooks.convert_value(value, param, state)

        return value

    @staticmethod
    def handle_postional(default: Any, _param: Param, state: ExecutionState):
        assert state.parsed
        pos_args = state.parsed["pos_args"]
        return default if len(pos_args) == 0 else pos_args.pop(0)

    @staticmethod
    def handle_keyword(default: Any, param: Param, state: ExecutionState):
        assert state.parsed

        options = state.parsed["options"]
        if value := options.get(param.arg_alias):
            options.pop(param.arg_alias)
        elif value := options.get(param.short):  # type: ignore
            options.pop(param.short)  # type: ignore
        else:
            value = default

        return value

    @staticmethod
    def handle_flag(default: bool, param: Param, state: ExecutionState):
        assert state.parsed

        flags = state.parsed["flags"]
        if param.arg_alias in flags:
            flags.remove(param.arg_alias)
            return not default
        elif param.short in flags:
            flags.remove(param.short)
            return not default
        else:
            return default

    @staticmethod
    def convert_value(value: str, param: Param, _state: ExecutionState):
        return convert(value, param.annotation, param.arg_alias)

    @staticmethod
    def post_run(value: Any, param: Param, state: ExecutionState):
        value = BuiltinHooks.missing_check(value, param, state)
        return value

    @staticmethod
    def missing_check(value: Any, param: Param, _state: ExecutionState):
        if value is MISSING:
            raise errors.ArgumentError(
                "No value provided for required positional argument: "
                + colorize(param.arg_alias, fg.YELLOW)
            )
        return value


class Param:
    """Represents a single command-line parameter.

    Instance Variables:
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
        hooks (list[Callable]): list of callables that will recieve the
            provided data-type at runtime and return a modified value
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
        hooks: Hooks = None,
    ):
        self.annotation = annotation
        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.type: ParamType = type
        self.short: Optional[str] = short
        self.hidden: bool = hidden
        self.default: Any = default
        self.hooks: Hooks = [BuiltinHooks.pre_run]
        if hooks:
            self.hooks.extend(hooks)
        self.hooks.append(BuiltinHooks.post_run)

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
