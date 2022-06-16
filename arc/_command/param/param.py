from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import cached_property
import os
import typing as t
from unittest.mock import DEFAULT

from arc import errors, utils
from arc.color import colorize, effects, fg
from arc.prompt.prompts import input_prompt
from arc.types.helpers import convert, iscontextmanager
from arc.types.type_info import TypeInfo
import arc.typing as at
from arc.types import aliases
from arc.constants import MISSING, MissingType

if t.TYPE_CHECKING:
    from arc.context import Context


T = t.TypeVar("T")

NO_CONVERT = {None, bool, t.Any, MISSING}


class Action(enum.Enum):
    STORE = "store"
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    APPEND = "append"
    COUNT = "count"


class ValueOrigin(enum.Enum):
    CLI = "cli"
    ENV = "env"
    PROMPT = "prompt"
    DEFAULT = "default"


class Param(
    t.Generic[T],
    utils.Display,
    members=["argument_name", "type"],
):
    argument_name: str
    """The cannonical name of the function's argument"""
    param_name: str
    """The names used on the command line / for parsing"""
    short_name: str | None
    """Optional single-character name alternabive for keyword params"""
    type: TypeInfo
    """Information on the type of the argument"""
    default: T | MissingType | None
    """Default value for this Param, will be used if no
    other source provides a value. A value `MISSING` indicates
    that the parameter is required. Otherwise, the parameter is optional"""
    description: str | None
    """Documentation for this parameter. If none is provided explicitly,
    it may also originate from the command's docstring"""
    envvar: str | None
    """Optional Enviroment variable to pull the value from
    if there is no value provided on the CLI"""
    prompt: str | None
    """Optional input prompt text to pull the value from
    stdin with when no valus is provided on the CLI"""
    action: Action
    """argparse action associated with this param"""
    expose: bool
    """If a param is 'exposed' it will be passed to the command's callback.
    If it's not 'exposed' then it will not be passed to the command's callback.
    This is useful when the parameter's side effects are desired, but the value
    doesn't matter. This is used to implment the `--version` and `--help` flags"""

    def __init__(
        self,
        argument_name: str,
        annotation: at.Annotation,
        default: T | None | MissingType = MISSING,
        param_name: str | None = None,
        short_name: str | None = None,
        description: str | None = None,
        callback: t.Callable | None = None,
        envvar: str | None = None,
        prompt: str | None = None,
        action: Action | None = None,
        expose: bool = True,
    ):
        self.argument_name = argument_name
        self.param_name = param_name or argument_name
        self.short_name = short_name
        self.default = default
        self.description = description
        self.callback = callback
        self.envvar = envvar
        self.prompt = prompt
        self.action = action or Action.STORE
        self.type = TypeInfo.analyze(annotation)
        self.expose = expose

        if self.type.is_union_type:
            for sub in self.type.sub_types:
                if utils.safe_issubclass(sub.origin, (set, tuple, list)):
                    raise errors.ParamError(
                        f"{self.type.original_type} is not a valid type. "
                        f"lists, sets, and tuples cannot be members of a Union / Optional type"
                    )

        if self.type.is_optional_type and self.default is MISSING:
            self.default = None

        if self.short_name and len(self.short_name) > 1:
            raise errors.ParamError(
                f"Parameter {self.param_name}'s shortened name is longer than 1 character",
                self,
            )

    @property
    def schema(self):
        return {
            "argument_name": self.argument_name,
            "type": self.type,
            "param_name": self.param_name,
            "short_name": self.short_name,
            "default": self.default,
        }

    @property
    def is_argument(self):
        return False

    @property
    def is_keyword(self):
        return False

    @property
    def is_option(self):
        return False

    @property
    def is_flag(self):
        return False

    @property
    def is_injected(self):
        return False

    @property
    def is_optional(self):
        return self.type.is_optional_type or self.default is not MISSING

    @property
    def is_required(self):
        return not self.is_optional

    @property
    def prompt_string(self):
        if self.default is not MISSING:
            return self.prompt + colorize(f"({self.default})", fg.GREY)
        return self.prompt

    @property
    def cli_name(self):
        return self.param_name

    @cached_property
    def nargs(self) -> at.NArgs:
        if (
            utils.safe_issubclass(self.type.origin, tuple)
            and self.type.sub_types
            and self.type.sub_types[-1].origin is not Ellipsis
        ):
            return len(self.type.sub_types)
        elif utils.safe_issubclass(self.type.origin, (tuple, list, set)):
            return "*"

        return None

    def process_parsed_result(
        self, res: at.ParseResult, ctx: Context
    ) -> T | MissingType:
        value, origin = self.get_value(res, ctx)

        if value not in (None, MISSING, True, False) and self.type.origin not in (
            bool,
            t.Any,
        ):
            value = self.convert(value, ctx)

        if self.callback and value is not MISSING and origin is not ValueOrigin.DEFAULT:
            value = self.callback(value, ctx, self) or value

        if iscontextmanager(value) and not value is ctx:
            value = ctx.resource(value)  # type: ignore

        return value

    def convert(self, value: t.Any, ctx: Context) -> T:
        try:
            return convert(self.type.resolved_type, value, self.type, ctx)
        except errors.ConversionError as e:
            message = (
                f"invalid value for {colorize(self.cli_name, fg.YELLOW)}: "
                f"{colorize(str(e), effects.BOLD)}"
            )
            if e.details:
                message += colorize(f" ({e.details})", fg.GREY)
            raise errors.InvalidArgValue(message, ctx) from e

    def get_value(
        self, res: at.ParseResult, ctx: Context
    ) -> tuple[t.Any | MissingType, ValueOrigin]:
        value: t.Any = res.pop(self.argument_name, MISSING)
        origin = ValueOrigin.CLI

        if value is MISSING:
            if self.envvar and (env := self.get_env_value(ctx)):
                value = env
                origin = ValueOrigin.ENV
            elif self.prompt and (prompt := self.get_prompt_value(ctx)):
                value = prompt
                origin = ValueOrigin.PROMPT
            else:
                value = self.default
                origin = ValueOrigin.DEFAULT

        return (value, origin)

    def get_env_value(self, ctx: Context):
        return os.getenv(f"{ctx.config.env_prefix}{self.envvar}")

    def get_prompt_value(self, ctx: Context):
        if hasattr(self.type.resolved_type, "__prompt__"):
            return type_class.__prompt__(ctx, self)  # type: ignore

        return input_prompt(ctx, self)

    def get_param_names(self) -> list[str]:
        return []


class ArgumentParam(
    Param[t.Any],
    members=["argument_name", "type"],
):
    @property
    def is_argument(self):
        return True

    @cached_property
    def nargs(self):
        return "?"

    def get_param_names(self) -> list[str]:
        return [self.argument_name]


class KeywordParam(Param[T]):
    @property
    def is_keyword(self):
        return True

    @property
    def cli_name(self):
        return f"--{self.param_name}"

    def get_param_names(self) -> list[str]:
        if self.short_name:
            return [f"-{self.short_name}", f"--{self.param_name}"]

        return [f"--{self.param_name}"]


class OptionParam(KeywordParam[t.Any]):
    @property
    def is_option(self):
        return True


class FlagParam(KeywordParam[bool]):
    @property
    def is_flag(self):
        return True


class InjectedParam(Param):
    """Injected Params are params whose values do
    not come from the command line, but from a dependancy injection.
    Used to get access to things like the arc Context and State
    """

    callback: t.Callable

    def is_injected(self):
        return True
