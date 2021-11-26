from __future__ import annotations

from dataclasses import asdict
from typing import Any, Callable, Optional

from arc import errors, utils
from arc.color import colorize, fg
from arc.config import config
from arc.execution_state import ExecutionState
from arc.result import Result
from arc.types import aliases
from arc.types.helpers import TypeInfo

# Represents a missing value
# Used to represent an argument
# with no default value
MISSING = utils.symbol("MISSING")


class Param:
    def __init__(
        self,
        arg_name: str,
        annotation: type,
        arg_alias: str = None,
        short: str = None,
        default: Any = MISSING,
        description: str = None,
    ):

        self.type_info = TypeInfo.analyze(annotation)
        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.short: Optional[str] = short
        self.default: Any = default
        self.description: Optional[str] = description

        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Argument {self.arg_name}'s shortened name is longer than 1 character"
            )

    def __repr__(self):
        type_name = getattr(self.type_info.origin, "__name__", self.type_info.origin)

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

    def schema(self) -> dict[str, Any]:
        return {
            "arg_name": self.arg_name,
            "arg_alias": self.arg_alias,
            "type_info": asdict(self.type_info),
            "short": self.short,
            "default": self.default,
            "description": self.description,
            "arg_type": self.__class__.__name__,
            "optional": self.optional,
        }

    def pre_run(self, state: ExecutionState) -> Any:
        """Hook that is ran before the command is executed. Should
        return the value of the param.
        """
        value = Selectors.select_value(self, state)
        converted = self.convert(value, state)

        return converted

    def convert(self, value: Any, state):

        type_class: type[aliases.TypeProtocol] = aliases.Alias.resolve(self.type_info)
        if value is MISSING:
            raise errors.MissingArgError(
                "No value provided for required argument "
                + colorize(self.cli_rep(), fg.YELLOW)
            )

        try:
            converted = utils.dispatch_args(
                type_class.__convert__, value, self.type_info, state
            )
        except errors.ConversionError as e:
            message = e.message
            if e.source:
                message += f" ({e.source})"

            raise errors.InvalidParamaterError(message, self, state) from e

        return converted

    def cli_rep(self) -> str:
        """Provides the representation that
        would be seen on the command line"""
        return self.arg_alias


class PositionalParam(Param):
    ...


class KeywordParam(Param):
    def cli_rep(self) -> str:
        return f"{config.flag_prefix}{self.arg_alias}"


class FlagParam(Param):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.default not in {True, False, MISSING}:
            raise errors.ArgumentError(
                "The default for a FlagParam must be True, False, or not specified."
            )

        if self.default is MISSING:
            self.default = False

    def cli_rep(self) -> str:
        return f"{config.flag_prefix}{self.arg_alias}"


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
