from __future__ import annotations
import argparse
import enum
from functools import cached_property
import os
import typing as t

from arc import errors, utils
from arc import constants
from arc.autocompletions import CompletionInfo, get_completions
from arc.color import colorize, effects, fg
from arc.prompt.prompts import input_prompt
from arc.types.helpers import convert_type, iscontextmanager
from arc.types.type_info import TypeInfo
import arc.typing as at
from arc.constants import MISSING, MissingType

if t.TYPE_CHECKING:
    from arc.context import Context


T = t.TypeVar("T")


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
    INJECTED = "injected"
    GETTER = "getter"


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
    action: Action | t.Type[argparse.Action]
    """argparse action associated with this param"""
    expose: bool
    """If a param is 'exposed' it will be passed to the command's callback.
    If it's not 'exposed' then it will not be passed to the command's callback.
    This is useful when the parameter's side effects are desired, but the value
    doesn't matter. This is used to implment the `--version` and `--help` flags"""
    comp_func: at.CompletionFunc | None
    """Function that can provide shell completions for the parameter"""
    getter_func: at.GetterFunc | None
    """Function that can retrieve a value not provided on the command line"""

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
        action: Action | t.Type[argparse.Action] | None = None,
        expose: bool = True,
        comp_func: at.CompletionFunc | None = None,
        getter_func: at.GetterFunc | None = None,
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
        self.comp_func = comp_func
        self.getter_func = getter_func

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

    def __completions__(self, info: CompletionInfo, *args, **kwargs):
        if self.comp_func:
            return self.comp_func(info, self)

        if hasattr(self.type.resolved_type, "__completions__"):
            return get_completions(self.type.resolved_type, info, self)

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
            return self.prompt + colorize(f" ({self.default})", fg.GREY)
        return self.prompt

    @property
    def cli_name(self):
        return self.param_name

    @property
    def parser_default(self):
        return MISSING

    @cached_property
    def nargs(self) -> at.NArgs:
        if (
            utils.safe_issubclass(self.type.origin, tuple)
            and self.type.sub_types
            and self.type.sub_types[-1].origin is not Ellipsis
        ):
            return len(self.type.sub_types)  # Consume a specific number
        elif utils.safe_issubclass(self.type.origin, constants.COLLECTION_TYPES):
            return "*"  # Consume one or more

        return "?"  # Optional

    def process_parsed_result(
        self, res: at.ParseResult, ctx: Context
    ) -> T | MissingType:
        value, origin = self.get_value(res, ctx)

        ctx.arg_origins[self.argument_name] = origin

        if self.is_required and value is None:
            raise errors.MissingArgError(
                f"argument {colorize(self.cli_name, fg.YELLOW)} expected 1 argument",
                ctx,
            )

        if value not in (None, MISSING, True, False) and self.type.origin not in (
            bool,
            t.Any,
        ):
            value = self.convert(value, ctx)

        if value not in (None, MISSING):
            value = self.run_middleware(value, ctx)

        if self.callback and value is not MISSING and origin is not ValueOrigin.DEFAULT:
            value = self.callback(value, ctx, self) or value

        if iscontextmanager(value) and not value is ctx:
            value = ctx.resource(value)  # type: ignore

        return value

    def get_value(
        self, res: at.ParseResult, ctx: Context
    ) -> tuple[t.Any | MissingType, ValueOrigin]:
        value: t.Any = res.pop(self.argument_name, MISSING)
        origin = ValueOrigin.CLI

        if value is MISSING:
            if self.envvar and (env := self.get_env_value(ctx)):
                value = env
                origin = ValueOrigin.ENV
            elif self.prompt and (prompt := self.get_prompt_value(ctx)) != MISSING:
                value = prompt
                origin = ValueOrigin.PROMPT
            elif (
                self.getter_func and (gotten := self.getter_func(ctx, self)) != MISSING
            ):
                value = gotten
                origin = ValueOrigin.GETTER
            else:
                value = self.default
                origin = ValueOrigin.DEFAULT

        return (value, origin)

    def convert(self, value: t.Any, ctx: Context) -> T:
        try:
            return convert_type(self.type.resolved_type, value, self.type, ctx)
        except errors.ConversionError as e:
            message = self._fmt_error(e)
            if e.details:
                message += colorize(f" ({e.details})", fg.GREY)
            raise errors.InvalidArgValue(message, ctx) from e

    def run_middleware(self, value: t.Any, ctx: Context):
        for middleware in self.type.middleware:
            try:
                value = utils.dispatch_args(middleware, value, ctx, self)
            except errors.ValidationError as e:
                message = self._fmt_error(e)
                raise errors.InvalidArgValue(message, ctx) from e

        return value

    def get_env_value(self, ctx: Context):
        return os.getenv(f"{ctx.config.env_prefix}{self.envvar}")

    def get_prompt_value(self, ctx: Context):
        if hasattr(self.type.resolved_type, "__prompt__"):
            return self.type.resolved_type.__prompt__(ctx, self)  # type: ignore

        return input_prompt(ctx, self)

    def get_param_names(self) -> list[str]:
        return []

    def _fmt_error(self, error: errors.ArcError):
        return (
            f"invalid value for {colorize(self.cli_name, fg.YELLOW)}: "
            f"{colorize(str(error), effects.BOLD)}"
        )


class ArgumentParam(
    Param[t.Any],
    members=["argument_name", "type"],
):
    @property
    def is_argument(self):
        return True

    # @property
    # def nargs(self):
    #     if utils.safe_issubclass(self.type.origin, (tuple, list, set)):
    #         return "*"  # Consume one or more

    #     return "?"  # Optional

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.type.origin in constants.COLLECTION_TYPES:
            self.action = Action.APPEND

    @property
    def is_option(self):
        return True

    @property
    def parser_default(self):
        if self.action is Action.APPEND:
            return None
        return MISSING


class FlagParam(KeywordParam[bool]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A default of false is always assumed with flags, so they
        # are always optional
        if self.default is MISSING:
            self.default = False

        # Explictly checks for bools because Count()
        # users a differnt action
        if self.action == Action.STORE:
            if self.default is True:
                self.action = Action.STORE_FALSE
            elif self.default is False:
                self.action = Action.STORE_TRUE

    @property
    def is_flag(self):
        return True

    @property
    def parser_default(self):
        if self.action is Action.COUNT:
            return 0
        return MISSING


class InjectedParam(Param):
    """Injected Params are params whose values do
    not come from the command line, but from a dependancy injection.
    Used to get access to things like the arc Context and State
    """

    callback: t.Callable

    def get_injected_value(self, ctx: Context) -> t.Any:
        value = self.callback(ctx) if self.callback else None
        ctx.arg_origins[self.argument_name] = ValueOrigin.INJECTED

        value = self.run_middleware(value, ctx)

        if iscontextmanager(value) and not value is ctx:
            value = ctx.resource(value)

        return value

    @property
    def is_injected(self):
        return True
