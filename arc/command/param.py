from __future__ import annotations
from typing import Any, Callable, Optional

from arc import errors
from arc.config import config
from arc.execution_state import ExecutionState
from arc.result import Result
from arc.utils.other import symbol

# Represents a missing value
# Used to represent an arguments
# with no default value
MISSING = symbol("MISSING")


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
        short (str): the single-character shortened name for the
            argument on the command line
    """

    def __init__(
        self,
        arg_name: str,
        annotation: type,
        arg_alias: str = None,
        short: str = None,
        default: Any = MISSING,
    ):
        from arc.types.param_types import ParamType

        self.annotation = annotation
        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.short: Optional[str] = short
        self.default: Any = default
        self.param_type: ParamType = ParamType.get_param_type(self.annotation)
        self._cleanup_funcs: set[Callable] = set()

        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Argument {self.arg_name}'s shortened name is longer than 1 character"
            )

    def __repr__(self):
        type_name = getattr(self.annotation, "__name__", self.annotation)

        return (
            f"<{self.__class__.__name__} {self.arg_name}"
            f"({self.__class__.__name__}): {type_name} = {self.default}>"
        )

    def __format__(self, spec: str):
        modifiers = spec.split("|")
        name = self.arg_alias

        if self.is_positional:
            formatted = f"<{name}>"
        else:
            if "short" in modifiers:
                assert self.short
                name = self.short
                denoter = config.short_flag_prefix
            else:
                denoter = config.flag_prefix

            formatted = f"{denoter}{name}"

            if "usage" in modifiers:
                if self.is_keyword:
                    formatted += " <...>"

                if self.optional:
                    formatted = f"[{formatted}]"

        return formatted

    def pre_run(self, state: ExecutionState) -> Any:
        """Hook that is ran before the command is executed. Should
        return the value of the param.
        """
        value = Selectors.select_value(self, state)
        return self.convert(value, state)

    def post_run(self, res: Result):
        """Hook that runs after the command is excuted."""
        self.cleanup()

    def convert(self, value: str, state):
        return self.param_type(value, self, state)

    def cleanup(self):
        for func in self._cleanup_funcs:
            func()

    @property
    def optional(self):
        return self.default is not MISSING

    @property
    def is_keyword(self):
        return isinstance(self, KeywordParam)

    @property
    def is_positional(self):
        return isinstance(self, PositionalParam)

    @property
    def is_flag(self):
        return isinstance(self, FlagParam)

    @property
    def is_special(self):
        return isinstance(self, SpecialParam)

    @property
    def hidden(self):
        return self.is_special


class PositionalParam(Param):
    ...


class KeywordParam(Param):
    ...


class FlagParam(Param):
    ...


class SpecialParam(Param):
    ...


class Selectors:
    @staticmethod
    def select_value(param: Param, state: ExecutionState):
        default = param.default

        if param.is_special:
            return default

        if param.is_positional:
            value = Selectors.select_positional_value(default, param, state)
        elif param.is_keyword:
            value = Selectors.select_keyword_value(default, param, state)
        elif param.is_flag:
            value = Selectors.select_flag_value(default, param, state)

        return value

    @staticmethod
    def select_positional_value(default: Any, _param: Param, state: ExecutionState):
        assert state.parsed
        pos_args = state.parsed["pos_values"]
        return default if len(pos_args) == 0 else pos_args.pop(0)

    @staticmethod
    def select_keyword_value(default: Any, param: Param, state: ExecutionState):
        assert state.parsed

        options = state.parsed["key_values"]
        if value := options.get(param.arg_alias):
            options.pop(param.arg_alias)
        elif value := options.get(param.short):  # type: ignore
            options.pop(param.short)  # type: ignore
        else:
            value = default

        return value

    @staticmethod
    def select_flag_value(default: bool, param: Param, state: ExecutionState):
        assert state.parsed

        flags = state.parsed["key_values"]
        if param.arg_alias in flags:
            flags.pop(param.arg_alias)
            return not default
        elif param.short in flags:
            flags.pop(param.short)
            return not default
        else:
            return default
