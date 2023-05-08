"""Contains all of the middlewares used during execution of a command"""
from __future__ import annotations

import contextlib
import os
import typing as t

import arc
from arc import api, constants, errors
from arc import typing as at
from arc.config import Config
from arc.define.param.param import InjectedParam, Param, ValueOrigin
from arc.prompt.prompts import input_prompt
from arc.runtime import Context
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    Middleware,
    MiddlewareBase,
)

if t.TYPE_CHECKING:
    from arc.define import Command
    from arc.define.param.param_tree import ParamTree


class ExitStackMiddleware(MiddlewareBase):
    """Utility middleware that adds an instance of `contextlib.ExitStack` to the context.
    This can be used to open resources (like IO objects) that need to be closed when the program is exiting.

    # Context Dependencies
    None

    # Context Additions
    - `arc.exitstack`
    """

    def __call__(self, ctx: Context) -> t.Any:
        with contextlib.ExitStack() as stack:
            ctx["arc.exitstack"] = stack
            yield
            if length := len(stack._exit_callbacks):  # type: ignore
                ctx.logger.debug("Closing %d resource(s)", length)


class SetupParamMiddleware(MiddlewareBase):
    """Performs parameter setup for the given command

    # Context Dependencies
    - `arc.command`

    # Context Additions
    `arc.args.tree` - Tree representing the command's parameters and their realized values
    `arc.args.origins` - Dictionary that stores where each parameter value comes from. See `Context.get_origin()`
    """

    def __call__(self, ctx: Context) -> t.Any:
        command: Command = ctx["arc.command"]
        param_instance = command.param_def.create_instance()
        ctx["arc.args.tree"] = param_instance
        ctx["arc.args.origins"] = {}


class ParamProcessor(MiddlewareBase):
    ctx: Context
    param_tree: ParamTree[type[dict[str, t.Any]]]
    config: Config
    origins: dict[str, ValueOrigin]

    __IGNORE = object()

    def __call__(self, ctx: Context) -> t.Any:
        self.ctx = ctx
        self.param_tree: ParamTree[type[dict[str, t.Any]]] = ctx["arc.args.tree"]
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

    def process(self, param: Param[t.Any], value: t.Any) -> t.Any:
        return self.__IGNORE

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        return self.__IGNORE

    def process_not_missing(self, param: Param[t.Any], value: t.Any) -> t.Any:
        return self.__IGNORE

    def skip(self, param: Param[t.Any], value: t.Any) -> bool:
        return param.is_injected or not param.expose

    def set_origin(self, param: Param[t.Any], origin: ValueOrigin) -> None:
        self.origins[param.argument_name] = origin


class ApplyParseResultMiddleware(ParamProcessor):
    """Update the parameter values with the values found from parsing the input

    # Context Dependencies
    - `arc.parse.result`
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    res: at.ParseResult

    def __call__(self, ctx: Context) -> t.Any:
        self.res = ctx["arc.parse.result"]
        return super().__call__(ctx)

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        value: t.Any = self.res.pop(param.argument_name, constants.MISSING)
        self.set_origin(param, ValueOrigin.CLI)

        # This is dependent on the fact that the current parser
        # adds a None to the result when you input a keyword, but
        # with no value
        if param.is_required and value is None:
            raise errors.MissingOptionValueError(param)

        return value


class GetEnvValueMiddleware(ParamProcessor):
    """Retrieves parameter values from enviroment variables

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        value = self.get_env_value(param)
        self.set_origin(param, ValueOrigin.ENV)
        return value

    def get_env_value(self, param: Param[t.Any]) -> str | constants.Constant:
        if not param.envvar:
            return constants.MISSING

        return os.getenv(f"{self.config.env_prefix}{param.envvar}", constants.MISSING)


class GetPromptValueMiddleware(ParamProcessor):
    """Retrieves parameter values from user input

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        value = self.get_prompt_value(param)
        self.set_origin(param, ValueOrigin.PROMPT)
        return value

    def get_prompt_value(self, param: Param[t.Any]) -> str | constants.Constant:
        if not param.prompt:
            return constants.MISSING

        prompter = getattr(param.type.resolved_type, "__prompt__", input_prompt)
        return api.dispatch_args(prompter, param, self.ctx)


class GetterValueMiddleware(ParamProcessor):
    """Retrieves parameter values from the parameter getter function

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        value = self.get_getter_value(param)
        self.set_origin(param, ValueOrigin.GETTER)
        return value

    def get_getter_value(self, param: Param[t.Any]) -> t.Any | constants.Constant:
        getter = param.getter_func
        if not getter:
            return constants.MISSING

        return api.dispatch_args(getter, param, self.ctx)


class ConvertValuesMiddleware(ParamProcessor):
    """Performs type conversion on retrieved parameter values

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process_not_missing(self, param: Param[t.Any], value: t.Any) -> t.Any:
        if value in (None, constants.MISSING, True, False,) and param.type.origin in (
            bool,
            t.Any,
        ):
            return value

        try:
            return param.convert(value)
        except errors.ConversionError as e:
            raise errors.InvalidParamValueError(str(e), param, e.details) from e


class DefaultValueMiddleware(ParamProcessor):
    """Retrieves parameter values from the defaults for each parameter

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process_missing(self, param: Param[t.Any]) -> t.Any:
        self.set_origin(param, ValueOrigin.DEFAULT)
        return param.default


class DependancyInjectorMiddleware(ParamProcessor):
    """Performs dependcy injection for relavent parameters

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process(self, param: Param[t.Any], value: t.Any) -> t.Any:
        param = t.cast(InjectedParam[t.Any], param)
        injected = param.get_injected_value(self.ctx)
        self.set_origin(param, ValueOrigin.INJECTED)
        return injected

    def skip(self, param: Param[t.Any], _value: t.Any) -> bool:
        return not param.is_injected


class RunTypeMiddlewareMiddleware(ParamProcessor):
    """Execute the registered type middleware for each parameter

    # Context Dependencies
    - `arc.args.tree`
    - `arc.config`
    - `arc.args.origins`

    # Context Additions
    None
    """

    def process(self, param: Param[t.Any], value: t.Any) -> t.Any:
        if value not in (None, constants.MISSING):
            try:
                value = param.run_middleware(value, self.ctx)
            except errors.ValidationError as e:
                raise errors.InvalidParamValueError(str(e), param) from e
        return value

    def skip(self, _param: Param[t.Any], _value: t.Any) -> bool:
        return False  # Don't want to skip any of the params


class RunCallbacksMiddleware(ParamProcessor):
    def process(self, param: Param[t.Any], value: t.Any) -> t.Any:
        if not param.callback:
            return value

        return api.dispatch_args(param.callback, value, param, self.ctx)


class MissingParamsCheckerMiddleware(MiddlewareBase):
    """Checks to ensure that all params have been given a value

    # Context Dependencies
    - `arc.args.tree`

    # Context Additions
    None
    """

    def __call__(self, ctx: Context) -> t.Any:
        tree: ParamTree[t.Any] = ctx["arc.args.tree"]
        missing = [
            value.param
            for value in tree.values()
            if value.value is constants.MISSING and value.param.expose
        ]

        if missing:
            raise arc.errors.MissingArgValueError(missing)


class CompileParamsMiddleware(MiddlewareBase):
    """Compile the parameter tree into dictionary that can be used
    to call the command callback.

    # Context Dependencies
    - `arc.args.tree`

    # Context Additions
    - `arc.args` - Dictionary to pass into command callback

    """

    def __call__(self, ctx: Context) -> t.Any:
        instance: ParamTree[t.Any] = ctx["arc.args.tree"]
        ctx["arc.args"] = instance.compile()


def iscontextmanager(obj: t.Any) -> bool:
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")


class OpenResourceMiddleware(MiddlewareBase):
    """Opens any parameter that is a context manager

    # Context Dependencies
    - `arc.args`
    - `arc.exitstack`

    # Context Additions
    None
    """

    def __call__(self, ctx: Context) -> t.Any:
        stack: contextlib.ExitStack | None = ctx.get("arc.exitstack")
        if not stack:
            return

        args: dict[str, t.Any] = ctx["arc.args"]

        for key, val in args.items():
            if isinstance(val, constants.COLLECTION_TYPES):
                cls = type(val)
                args[key] = cls(
                    item if not iscontextmanager(item) else stack.enter_context(item)
                    for item in val
                )

            if iscontextmanager(val):
                args[key] = stack.enter_context(val)


class ExecMiddleware(DefaultMiddlewareNamespace):
    """Container for all default execution middlewares

    Use it to reference a default exec middleware when adding your own custom middlewares

    ```py
    import arc

    @arc.command
    def command():
        arc.print("hello there")

    @command.use(after=arc.ExecMiddleware.ConverValues)
    def after_convert(ctx: arc.Context):
        # Runs after type conversion occurs
        ...
    ```
    """

    ExitStack = ExitStackMiddleware()
    SetupParam = SetupParamMiddleware()
    ApplyParseResult = ApplyParseResultMiddleware()
    GetEnvValue = GetEnvValueMiddleware()
    GetPromptValue = GetPromptValueMiddleware()
    GetterValue = GetterValueMiddleware()
    ConvertValues = ConvertValuesMiddleware()
    DefaultValue = DefaultValueMiddleware()
    DependancyInjector = DependancyInjectorMiddleware()
    RunTypeMiddleware = RunTypeMiddlewareMiddleware()
    RunCallbacks = RunCallbacksMiddleware()
    MissingParamsChecker = MissingParamsCheckerMiddleware()
    CompileParams = CompileParamsMiddleware()
    OpenResource = OpenResourceMiddleware()

    _list: list[Middleware] = [
        ExitStack,
        SetupParam,
        ApplyParseResult,
        GetEnvValue,
        GetPromptValue,
        GetterValue,
        ConvertValues,
        DefaultValue,
        DependancyInjector,
        RunTypeMiddleware,
        RunCallbacks,
        MissingParamsChecker,
        CompileParams,
        OpenResource,
    ]
