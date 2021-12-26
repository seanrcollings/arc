from __future__ import annotations

from dataclasses import asdict
import enum

import typing as t

from arc import errors, constants
from arc.color import colorize, fg, colored
from arc.config import config
from arc.typing import CollectionTypes


if t.TYPE_CHECKING:
    from arc.context import Context

# Represents a missing value
# Used to represent an argument
# with no default value


NO_CONVERT = (None, t.Any)


class ParamAction(enum.Enum):
    STORE = enum.auto()
    APPEND = enum.auto()
    COUNT = enum.auto()


class Param:
    def __init__(
        self,
        arg_name: str,
        annotation: type,
        arg_alias: str = None,
        short: str = None,
        default: t.Any = constants.MISSING,
        description: str = None,
        callback: t.Callable[[t.Any, Context, Param], t.Any] = None,
        expose: bool = True,
        action: ParamAction = None,
        nargs: int = None,
    ):

        self.type_info = helpers.TypeInfo.analyze(annotation)
        self.default: t.Any = default

        if self.type_info.is_optional_type():
            self.type_info = self.type_info.sub_types[0]
            if self.default is constants.MISSING:
                self.default = None

        self.arg_name: str = arg_name
        self.arg_alias: str = arg_alias if arg_alias else arg_name
        self.short: t.Optional[str] = short
        self.description: t.Optional[str] = description
        self.callback: t.Optional[t.Callable] = callback
        self.expose: bool = expose
        self.nargs: t.Optional[int] = nargs or self._discover_nargs()
        self.action: ParamAction = action or self._discover_action()

        if self.short and len(self.short) > 1:
            raise errors.ArgumentError(
                f"Parameter {self.arg_name}'s shortened name is longer than 1 character"
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
                "Invalid value for format spec, must be: usage or arguments"
            )

    def _format_usage(self):
        return ""

    def _format_arguments(self):
        return ""

    def _discover_action(self) -> ParamAction:
        action = ParamAction.STORE

        if helpers.safe_issubclass(self.type_info.origin, CollectionTypes):
            action = ParamAction.APPEND

        return action

    def _discover_nargs(self) -> t.Optional[int]:
        if (
            helpers.safe_issubclass(self.type_info.origin, tuple)
            and self.type_info.sub_types
            and self.type_info.sub_types[-1].origin is not Ellipsis
        ):
            return len(self.type_info.sub_types)
        return None

    @property
    def optional(self):
        return self.default is not constants.MISSING

    @property
    def is_keyword(self):
        return isinstance(self, Option)

    @property
    def is_positional(self):
        return isinstance(self, Argument)

    @property
    def is_flag(self):
        return isinstance(self, Flag)

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

        if value is constants.MISSING:
            if self.is_flag:
                value = not self.default
            else:
                raise errors.MissingArgError(
                    "No value provided for required argument "
                    + colorize(self.cli_rep(), fg.YELLOW),
                    ctx,
                )

        if value not in NO_CONVERT and self.type_info.origin not in NO_CONVERT:
            value = self.convert(value, ctx)

        if self.callback:
            value = self.callback(value, ctx, self)

        if helpers.iscontextmanager(value) and not value is ctx:
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
        if value is constants.MISSING:
            return None

        type_class: type[aliases.TypeProtocol] = aliases.Alias.resolve(self.type_info)

        try:
            converted = helpers.convert(type_class, value, self.type_info, ctx)
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


class Argument(Param):
    def _format_usage(self):
        if self.action is ParamAction.APPEND:
            if self.nargs is None:
                string = f"<{self.arg_alias}...>"
            elif self.nargs > 1:
                string = f"<{self.arg_alias}1> ... <{self.arg_alias}{self.nargs}>"
            else:
                string = self.arg_alias
        else:
            string = self.arg_alias

        if self.optional:
            return f"[{string}]"

        return string

    def _format_arguments(self):
        return colored(colorize(f"{self.arg_alias}", config.brand_color))

    def cli_rep(self, short=False) -> str:
        return f"{self.arg_alias}"


class _KeywordParam(Param):
    def _format_usage(self):
        string = f"{constants.FLAG_PREFIX}{self.arg_alias}"
        if self.is_keyword:
            string += " <...>"

        if self.optional:
            string = f"[{string}]"

        return string

    def _format_arguments(self):
        string = colorize(
            f"{constants.FLAG_PREFIX}{self.arg_alias}", config.brand_color
        )
        if self.short:
            string += colorize(f" ({constants.SHORT_FLAG_PREFIX}{self.short})", fg.GREY)

        return colored(string)

    def cli_rep(self, short=False) -> str:
        return (constants.SHORT_FLAG_PREFIX if short else constants.FLAG_PREFIX) + (
            self.short if short and self.short else self.arg_alias
        )


class Option(_KeywordParam):
    ...


class Flag(_KeywordParam):
    def __init__(self, arg_name: str, annotation: type = bool, **kwargs):

        super().__init__(arg_name, annotation, **kwargs)

        # if self.default not in {True, False, MISSING}:
        #     raise errors.ArgumentError(
        #         "The default for a flag must be True, False, or not specified."
        #     )

        if self.default is constants.MISSING:
            self.default = False


class SpecialParam(Param):
    ...


from arc.types import aliases, helpers
