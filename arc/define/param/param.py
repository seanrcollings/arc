from __future__ import annotations

import argparse
import enum
import typing as t
from functools import cached_property

import arc.typing as at
from arc import api, constants, errors, safe
from arc.autocompletions import CompletionInfo, get_completions
from arc.color import colorize, fg
from arc.constants import MISSING, Constant
from arc.types.convert import convert_type
from arc.types.type_info import TypeInfo

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


class Param(t.Generic[T]):
    argument_name: str
    """The cannonical name of the function's argument"""
    param_name: str
    """The names used on the command line / for parsing"""
    short_name: str | None
    """Optional single-character name alternabive for keyword params"""
    type: TypeInfo[T]
    """Information on the type of the argument"""
    default: T | Constant | None
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
    getter_func: at.ParamGetter | None
    """Function that can retrieve a value not provided on the command line"""
    data: dict[str, t.Any]
    """Dictionary of any other key values passed to the constructors"""

    def __init__(
        self,
        argument_name: str,
        type: TypeInfo[T],
        default: T | None | Constant = MISSING,
        param_name: str | None = None,
        short_name: str | None = None,
        description: str | None = None,
        callback: at.ParamCallback | None = None,
        envvar: str | None = None,
        prompt: str | None = None,
        action: Action | t.Type[argparse.Action] | None = None,
        expose: bool = True,
        comp_func: at.CompletionFunc | None = None,
        getter_func: at.ParamGetter | None = None,
        data: dict[str, t.Any] = None,
    ):
        self.argument_name = argument_name
        self.param_name = param_name or argument_name
        self.type = type
        self.short_name = short_name
        self.default = default
        self.description = description
        self.callback = callback
        self.envvar = envvar
        self.prompt = prompt
        self.action = action or Action.STORE
        self.expose = expose
        self.comp_func = comp_func
        self.getter_func = getter_func
        self.data = data or {}

        if self.type.is_optional_type and self.default is MISSING:
            self.default = None

    __repr__ = api.display("argument_name", "type")

    def __completions__(
        self, info: CompletionInfo, *args: t.Any, **kwargs: t.Any
    ) -> at.CompletionReturn:
        if self.comp_func:
            return self.comp_func(info, self)

        if hasattr(self.type.resolved_type, "__completions__"):
            return get_completions(self.type.resolved_type, info, self)  # type: ignore

        return None

    @property
    def schema(self) -> dict[str, t.Any]:
        return {
            "argument_name": self.argument_name,
            "type": self.type,
            "param_name": self.param_name,
            "short_name": self.short_name,
            "default": self.default,
        }

    @property
    def is_argument(self) -> bool:
        return False

    @property
    def is_keyword(self) -> bool:
        return False

    @property
    def is_option(self) -> bool:
        return False

    @property
    def is_flag(self) -> bool:
        return False

    @property
    def is_injected(self) -> bool:
        return False

    @property
    def is_optional(self) -> bool:
        return self.type.is_optional_type or self.default is not MISSING

    @property
    def is_required(self) -> bool:
        return not self.is_optional

    @property
    def prompt_string(self) -> str:
        assert isinstance(self.prompt, str), "No prompt string provided"

        if self.default is not MISSING:
            return self.prompt + colorize(f" ({self.default}) ", fg.GREY)
        return self.prompt

    @property
    def cli_name(self) -> str:
        return self.param_name

    @property
    def parser_default(self) -> t.Any:
        return MISSING

    @cached_property
    def nargs(self) -> at.NArgs:
        if (
            safe.issubclass(self.type.origin, tuple)
            and self.type.sub_types
            and self.type.sub_types[-1].origin is not Ellipsis
        ):
            return len(self.type.sub_types)  # Consume a specific number
        elif self.type.is_collection_type:
            return "*"  # Consume one or more

        return "?"  # Optional

    def convert(self, value: t.Any) -> T:
        return convert_type(self.type.resolved_type, value, self.type)

    def run_middleware(self, value: t.Any, ctx: t.Any) -> t.Any:
        for middleware in self.type.middleware:
            value = api.dispatch_args(middleware, value, ctx, self)

        return value

    def get_param_names(self) -> list[str]:
        return []


class ArgumentParam(Param[T]):
    @property
    def is_argument(self) -> bool:
        return True

    # @property
    # def nargs(self):
    #     if safe.issubclass(self.type.origin, (tuple, list, set)):
    #         return "*"  # Consume one or more

    #     return "?"  # Optional

    def get_param_names(self) -> list[str]:
        return [self.argument_name]


class KeywordParam(Param[T]):
    @property
    def is_keyword(self) -> bool:
        return True

    @property
    def cli_name(self) -> str:
        return f"--{self.param_name}"

    def get_param_names(self) -> list[str]:
        if self.short_name:
            return [f"-{self.short_name}", f"--{self.param_name}"]

        return [f"--{self.param_name}"]


class OptionParam(KeywordParam[T]):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)

        if self.type.is_collection_type:
            self.action = Action.APPEND

    @property
    def is_option(self) -> bool:
        return True

    @property
    def parser_default(self) -> t.Any:
        if self.action is Action.APPEND:
            return None
        return MISSING


class FlagParam(KeywordParam[bool]):
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
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
    def is_flag(self) -> bool:
        return True

    @property
    def parser_default(self) -> t.Any:
        if self.action is Action.COUNT:
            return 0
        return MISSING


class InjectedParam(Param[T]):
    """Injected Params are params whose values do
    not come from the command line, but from a dependancy injection.
    Used to get access to things like the arc Context and State
    """

    callback: at.ParamGetter  # type: ignore[assignment]

    def get_injected_value(self, ctx: t.Any) -> t.Any:
        value = api.dispatch_args(self.callback, ctx, self)
        return value

    @property
    def is_injected(self) -> bool:
        return True
