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
from arc.present import Join
from arc.color import fg, fx, colorize
from arc.prompt.prompts import input_prompt
from arc.types.helpers import iscontextmanager
from arc.define.param.param import InjectedParam, Param, ValueOrigin
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    MiddlewareBase,
    Middleware,
)

if t.TYPE_CHECKING:
    from arc.define.param.param_tree import ParamTree
    from arc.define import Command


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
            if length := len(stack._exit_callbacks):  # type: ignore
                ctx.logger.debug("Closing %d resource(s)", length)


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

    def get_env_value(self, param: Param) -> str | constants.Constant:
        if not param.envvar:
            return constants.MISSING

        return os.getenv(f"{self.config.env_prefix}{param.envvar}", constants.MISSING)


class GetPromptValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param) -> t.Any:
        value = self.get_prompt_value(param)
        self.set_origin(param, ValueOrigin.PROMPT)
        return value

    def get_prompt_value(self, param: Param) -> str | constants.Constant:
        if not param.prompt:
            return constants.MISSING

        prompter = getattr(param.type.resolved_type, "__prompt__", input_prompt)
        return utils.dispatch_args(prompter, param, self.ctx)


class GetterValueMiddleware(ParamProcessor):
    def process_missing(self, param: Param) -> t.Any:
        value = self.get_getter_value(param)
        self.set_origin(param, ValueOrigin.GETTER)
        return value

    def get_getter_value(self, param: Param) -> t.Any | constants.Constant:
        getter = param.getter_func
        if not getter:
            return constants.MISSING

        return utils.dispatch_args(getter, param, self.ctx)


def fmt_error(ctx: Context, param: Param, error: errors.ArcError):
    return f"invalid value for {colorize(param.cli_name, ctx.config.color.highlight)}: {error}"


class ConvertValuesMiddleware(ParamProcessor):
    def process_not_missing(self, param: Param, value: t.Any):
        if value in (None, constants.MISSING, True, False,) and param.type.origin in (
            bool,
            t.Any,
        ):
            return value

        try:
            return param.convert(value)
        except errors.ConversionError as e:
            message = fmt_error(self.ctx, param, e)
            if e.details:
                message += colorize(f" ({e.details})", self.ctx.config.color.subtle)
            raise errors.InvalidArgValue(message) from e


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
            try:
                value = param.run_middleware(value, self.ctx)
            except errors.ValidationError as e:
                message = fmt_error(self.ctx, param, e)
                raise errors.InvalidArgValue(message) from e
        return value

    def skip(self, _param: Param, _value: t.Any) -> bool:
        return False  # Don't want to skip any of the params


class MissingParamsCheckerMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        tree: ParamTree = ctx["arc.args.tree"]
        missing = [
            value.param
            for value in tree.values()
            if value.value is constants.MISSING and value.param.expose
        ]

        if missing:
            params = Join.with_comma(
                (param.cli_name for param in missing), style=ctx.config.color.highlight
            )
            raise arc.errors.MissingArgError(
                f"The following arguments are required: {params}"
            )


class CompileParamsMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        instance: ParamTree = ctx["arc.args.tree"]
        ctx["arc.args"] = instance.compile()


class OpenResourceMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        stack: contextlib.ExitStack | None = ctx.get("arc.exitstack")
        if not stack:
            return

        args: dict[str, t.Any] = ctx["arc.args"]

        for key, val in args.items():
            if iscontextmanager(val):
                args[key] = stack.enter_context(val)


class ExecMiddleware(DefaultMiddlewareNamespace):
    """Container for all default execution middleware"""

    ExitStack = ExitStackMiddleware()
    SetupParam = SetupParamMiddleware()
    AopplyParseResult = ApplyParseResultMiddleware()
    GetEnvValue = GetEnvValueMiddleware()
    GetPromptValue = GetPromptValueMiddleware()
    GetterValue = GetterValueMiddleware()
    ConvertValues = ConvertValuesMiddleware()
    DefaultValue = DefaultValueMiddleware()
    DependancyInjector = DependancyInjectorMiddleware()
    RunTypeMiddleware = RunTypeMiddlewareMiddleware()
    MissingParamsChecker = MissingParamsCheckerMiddleware()
    CompileParams = CompileParamsMiddleware()
    OpenResource = OpenResourceMiddleware()

    _list: list[Middleware] = [
        ExitStack,
        SetupParam,
        AopplyParseResult,
        GetEnvValue,
        GetPromptValue,
        GetterValue,
        ConvertValues,
        DefaultValue,
        DependancyInjector,
        RunTypeMiddleware,
        MissingParamsChecker,
        CompileParams,
        OpenResource,
    ]
