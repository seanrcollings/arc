from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional

from arc import errors, utils
from arc.color import colorize, fg, colored
from arc.config import config
from arc.execution_state import ExecutionState
from arc.command.argument import Argument

# Represents a missing value
# Used to represent an argument
# with no default value
MISSING = utils.symbol("MISSING")


class Param:
    """Represents both the Python function paramater,
    and it's equivalent on the command line. `Argument`
    represents the actual value that a paramater is given.
    """

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
            f": {type_name} = {self.default}>"
        )

    def __format__(self, spec: str):
        if spec == "usage":
            return self._format_usage()
        elif spec == "arguments":
            return self._format_arguments()
        else:
            raise ValueError(
                "Invalid value for format spec, must be usage or arguments"
            )

    def _format_usage(self):
        return ""

    def _format_arguments(self):
        return ""

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

    def process_parse_result(self, ctx, args: dict, extra: list):
        value = self.consume_value(ctx, args)

        if value is MISSING:
            if self.is_flag:
                value = not self.default
            else:
                raise errors.MissingArgError(
                    f"No Value provided for argument {self.arg_alias} :("
                )

        return self.convert(value, None), extra

    ## TODO:
    ## Add other possible sources  if absent on the command line
    ## Env, config, prompt, ...
    def consume_value(self, _ctx, args: dict):
        value = args.get(self.arg_name)
        if value is not None:
            args.pop(self.arg_name)
        else:
            value = self.default

        return value

    def get_arg(self, state: ExecutionState) -> Argument:
        value = Selectors.select_value(self, state)
        converted = self.convert(value, state)

        return Argument(converted, self)

    def convert(self, value: Any, state):
        type_class: type[aliases.TypeProtocol] = aliases.Alias.resolve(self.type_info)

        try:
            converted = convert(type_class, value, self.type_info, state)
        except errors.ConversionError as e:
            message = e.message
            if e.source:
                message += f" ({e.source})"

            raise errors.InvalidParamaterError(message, self, state) from e

        return converted

    def cli_rep(self, _short=False) -> str:
        """Provides the representation that
        would be seen on the command line"""
        return self.arg_alias


class PositionalParam(Param):
    def _format_usage(self):
        if self.optional:
            return f"[{self.arg_alias}]"

        return f"<{self.arg_alias}>"

    def _format_arguments(self):
        return colored(colorize(f"<{self.arg_alias}>", config.brand_color))

    def cli_rep(self, short=False) -> str:
        return f"<{self.arg_alias}>"


class _KeywordFlagShared(Param):
    def _format_usage(self):
        string = f"{config.flag_prefix}{self.arg_alias}"
        if self.is_keyword:
            string += " <...>"

        if self.optional:
            string = f"[{string}]"

        return string

    def _format_arguments(self):
        string = colorize(f"{config.flag_prefix}{self.arg_alias}", config.brand_color)
        if self.short:
            string += colorize(f" ({config.short_flag_prefix}{self.short})", fg.GREY)

        return colored(string)


class KeywordParam(_KeywordFlagShared):
    def cli_rep(self, short=False) -> str:
        return (config.short_flag_prefix if short else config.flag_prefix) + (
            self.short if short and self.short else self.arg_alias
        )


class FlagParam(_KeywordFlagShared):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.default not in {True, False, MISSING}:
            raise errors.ArgumentError(
                "The default for a flag must be True, False, or not specified."
            )

        if self.default is MISSING:
            self.default = False

    def cli_rep(self, short=False) -> str:
        return (config.short_flag_prefix if short else config.flag_prefix) + (
            self.short if short and self.short else self.arg_alias
        )


class SpecialParam(Param):
    ...


class Selectors:
    @staticmethod
    def select_value(param: Param, state: ExecutionState):
        default = param.default

        if param.is_special:
            value = default
        elif param.is_positional:
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


from arc.types.helpers import TypeInfo, convert
from arc.types import aliases
