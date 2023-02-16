from __future__ import annotations
import typing as t
import contextlib
import os

import arc
from arc import constants
from arc import errors
from arc import typing as at
from arc import utils
from arc.config import Config
from arc.context import Context
from arc.present import Joiner
from arc.color import fg, colorize
from arc.prompt.prompts import input_prompt
from arc.types.helpers import iscontextmanager

from arc.core.param.param import InjectedParam, Param, ValueOrigin
from arc.core.middleware.middleware import MiddlewareBase

if t.TYPE_CHECKING:
    from arc.core.param.param_tree import ParamTree
    from arc.core import Command


class ExitStackMiddleware(MiddlewareBase):
    """Utility middleware that adds an instance of `contextlib.ExitStack` to the context.
    This can be used to open resources (like IO objects) that need to be closed when the program is exiting.

    # Context Dependancies
    None

    # Context Additions
    - `arc.exitstack`
    """

    def __call__(self, ctx: Context):
        with contextlib.ExitStack() as stack:
            ctx["arc.exitstack"] = stack
            yield


class SetupParamMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        command: Command = ctx["arc.command"]
        param_instance = command.param_def.create_instance()
        ctx["arc.args.tree"] = param_instance
        ctx["arc.args.origins"] = {}


class ParamProcessor(MiddlewareBase):
    ctx: Context
    param_tree: ParamTree
    config: Config
    origins: dict[str, ValueOrigin]

    __IGNORE = object()

    def __call__(self, ctx: Context):
        self.ctx = ctx
        self.param_tree: ParamTree = ctx["arc.args.tree"]
        self.config = ctx["arc.config"]
        self.origins = ctx["arc.args.origins"]

        for param_value in self.param_tree.values():
            if not self.skip(param_value.param, param_value.value):
                updated = self.process(param_value.param, param_value.value)

                if updated is not self.__IGNORE:
                    param_value.value = updated

                if param_value.value is constants.MISSING:
                    updated = self.process_missing(param_value.param)
                else:
                    updated = self.process_not_missing(
                        param_value.param, param_value.value
                    )

                if updated is not self.__IGNORE:
                    param_value.value = updated

    def process(self, param: Param, value: t.Any) -> t.Any:
        return self.__IGNORE

    def process_missing(self, param: Param) -> t.Any:
        return self.__IGNORE

    def process_not_missing(self, param: Param, value: t.Any) -> t.Any:
        return self.__IGNORE

    def skip(self, param: Param, value: t.Any) -> bool:
        return param.is_injected or not param.expose

    def set_origin(self, param: Param, origin: ValueOrigin) -> None:
        self.origins[param.argument_name] = origin


class ApplyParseResultMiddleware(ParamProcessor):
    res: at.ParseResult

    def __call__(self, ctx: Context):
        self.res = ctx["arc.parse.result"]
        return super().__call__(ctx)

    def process_missing(self, param: Param):
        value: t.Any = self.res.pop(param.argument_name, constants.MISSING)
        self.set_origin(param, ValueOrigin.CLI)

        # This is dependant on the fact that the current parser
        # adds a None to the result when you input a keyword, but
        # with no value
        if param.is_required and value is None:
            raise errors.MissingArgError(
                f"argument {colorize(param.cli_name, fg.YELLOW)} expected 1 argument",
            )

        return value


class GetEnvValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param) -> t.Any:
        value = self.get_env_value(param)
        self.set_origin(param, ValueOrigin.ENV)
        return value

    def get_env_value(self, param: Param) -> str | constants.MissingType:
        if not param.envvar:
            return constants.MISSING

        return os.getenv(f"{self.config.env_prefix}{param.envvar}", constants.MISSING)


class GetPromptValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param) -> t.Any:
        value = self.get_prompt_value(param)
        self.set_origin(param, ValueOrigin.PROMPT)
        return value

    def get_prompt_value(self, param: Param) -> str | constants.MissingType:
        if not param.prompt:
            return constants.MISSING

        if hasattr(param.type.resolved_type, "__prompt__"):
            return utils.dispatch_args(
                param.type.resolved_type.__prompt__, param, self.ctx  # type: ignore
            )

        return input_prompt(self.config.prompt, param)


class GetterValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param) -> t.Any:
        value = self.get_getter_value(param)
        self.set_origin(param, ValueOrigin.GETTER)
        return value

    def get_getter_value(self, param: Param) -> t.Any | constants.MissingType:
        getter = param.getter_func
        if not getter:
            return constants.MISSING

        return utils.dispatch_args(getter, param, self.ctx)


class ConvertValuesMiddleware(ParamProcessor):
    def process_not_missing(self, param: Param, value: t.Any):
        if value not in (
            None,
            constants.MISSING,
            True,
            False,
        ) and param.type.origin not in (
            bool,
            t.Any,
        ):
            value = param.convert(value)

        return value


class DefaultValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param):
        self.set_origin(param, ValueOrigin.DEFAULT)
        return param.default


class DependancyInjectorMiddleware(ParamProcessor):
    def process(self, param: Param, value: t.Any) -> t.Any:
        param = t.cast(InjectedParam, param)
        injected = param.get_injected_value(self.ctx)
        self.set_origin(param, ValueOrigin.INJECTED)
        return injected

    def skip(self, param: Param, _value: t.Any) -> bool:
        return not param.is_injected


class RunTypeMiddlewareMiddleware(ParamProcessor):
    def process(self, param: Param, value: t.Any) -> t.Any:
        if value not in (None, constants.MISSING):
            value = param.run_middleware(value, self.ctx)

        return value

    def skip(self, _param: Param, _value: t.Any) -> bool:
        return False  # Don't want to skip any of the params


class OpenResourceMiddleware(ParamProcessor):
    def process(self, _param: Param, value: t.Any) -> t.Any:
        if iscontextmanager(value):
            value = self.open_resource(value)

        return value

    def open_resource(self, resource: t.ContextManager) -> t.Any:
        stack: contextlib.ExitStack = self.ctx["arc.exitstack"]
        return stack.enter_context(resource)


class MissingParamsCheckerMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        tree: ParamTree = ctx["arc.args.tree"]
        missing = [
            value.param
            for value in tree.values()
            if value.value is constants.MISSING and value.param.expose
        ]

        if missing:
            params = Joiner.with_comma(
                (param.cli_name for param in missing), style=fg.YELLOW
            )
            raise arc.errors.MissingArgError(
                f"The following arguments are required: {params}"
            )


class CompileParamsMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        instance: ParamTree = ctx["arc.args.tree"]
        ctx["arc.args"] = instance.compile()


DEFAULT_EXEC_MIDDLEWARES = [
    ExitStackMiddleware(),
    SetupParamMiddleware(),
    ApplyParseResultMiddleware(),
    GetEnvValueMiddleware(),
    GetPromptValueMiddleware(),
    GetterValueMiddleware(),
    ConvertValuesMiddleware(),
    DefaultValueMiddleware(),
    DependancyInjectorMiddleware(),
    RunTypeMiddlewareMiddleware(),
    OpenResourceMiddleware(),
    MissingParamsCheckerMiddleware(),
    CompileParamsMiddleware(),
]
