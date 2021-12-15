from __future__ import annotations

from dataclasses import asdict

import typing as t

from arc import errors, utils
from arc.color import colorize, fg, colored
from arc.config import config

if t.TYPE_CHECKING:
    from arc.context import Context

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
        default: t.Any = MISSING,
        description: str = None,
        callback: t.Callable[[t.Any, Context, Param], t.Any] = None,
        expose: bool = True,
    ):

        self.type_info = TypeInfo.analyze(annotation)
        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.short: t.Optional[str] = short
        self.default: t.Any = default
        self.description: t.Optional[str] = description
        self.callback = callback
        self.expose = expose

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

    def schema(self) -> dict[str, t.Any]:
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

    def process_parse_result(self, ctx: Context, args: dict):
        value = self.consume_value(ctx, args)

        if value is MISSING:
            if self.is_flag:
                value = not self.default
            else:
                raise errors.MissingArgError(
                    "No value provided for required argument "
                    + colorize(self.cli_rep(), fg.YELLOW),
                    ctx,
                )

        value = self.convert(value, ctx)
        if self.callback:
            value = self.callback(value, ctx, self)

        if utils.iscontextmanager(value) and not value is ctx:
            value = ctx.resource(value)

        return value

    ## TODO:
    ## Add other possible sources  if absent on the command line
    ## Env, config, prompt, ...
    def consume_value(self, _ctx: Context, args: dict):
        value = args.get(self.arg_name)
        if value is not None:
            args.pop(self.arg_name)
        else:
            value = self.default

        return value

    def convert(self, value: t.Any, ctx: Context):
        type_class: type[aliases.TypeProtocol] = aliases.Alias.resolve(self.type_info)

        try:
            converted = convert(type_class, value, self.type_info, ctx)
        except errors.ConversionError as e:
            message = str(e)
            if e.source:
                message += f" ({e.source})"

            raise errors.InvalidParamaterError(message, self, ctx) from e

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


from arc.types.helpers import TypeInfo, convert
from arc.types import aliases
