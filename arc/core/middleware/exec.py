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
from arc.core.middleware.middleware import Middleware

if t.TYPE_CHECKING:
    from arc.core.param.param_tree import ParamTree
    from arc.core import Command


class ContextInjectorMiddleware(Middleware):
    """Utility middleware that injects the [`Context`][arc.context.Context] object into the enviroment,
    which is what is passed to other parts of `arc` when they need access to the
    enviroment, but with a bit cleaner of an interface

    # Env Dependancies
    None

    # Env Additions
    - `arc.ctx`

    """

    def __call__(self, env: at.ExecEnv):
        env["arc.ctx"] = arc.Context(env)
        return self.app(env)


class ExitStackMiddleware(Middleware):
    """Utility middleware that adds an instance of `contextlib.ExitStack` to the enviroment.
    This can be used to open resources (like IO objects) that need to be closed when the program is exiting.

    # Env Dependancies
    None

    # Env Additions
    - `arc.exitstack`
    """

    def __call__(self, env: at.ExecEnv):
        with contextlib.ExitStack() as stack:
            env["arc.exitstack"] = stack
            return self.app(env)


class SetupParamMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv) -> t.Any:
        command: Command = env["arc.command"]
        param_instance = command.param_def.create_instance()
        env["arc.args.tree"] = param_instance
        env["arc.args.origins"] = {}
        return self.app(env)


class ParamProcessor(Middleware):
    env: at.ExecEnv
    param_tree: ParamTree
    config: Config
    ctx: Context | None
    origins: dict[str, ValueOrigin]

    __IGNORE = object()

    def __call__(self, env: at.ExecEnv):
        self.env = env
        self.param_tree: ParamTree = env["arc.args.tree"]
        self.config = env["arc.config"]
        self.ctx = env.get("arc.ctx")
        self.origins = env["arc.args.origins"]

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

        # print(type(self).__name__, self.instance.compile())
        return self.app(env)

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

    def __call__(self, env: at.ExecEnv):
        if env.get("arc.args") is not None:
            return self.app(env)

        self.res = env["arc.parse.result"]

        return super().__call__(env)

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
        stack: contextlib.ExitStack = self.env["arc.exitstack"]
        return stack.enter_context(resource)


class MissingParamsCheckerMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv) -> t.Any:
        tree: ParamTree = env["arc.args.tree"]
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

        return self.app(env)


class CompileParamsMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv) -> t.Any:
        instance: ParamTree = env["arc.args.tree"]
        env["arc.args"] = instance.compile()
        return self.app(env)


class DecoratorStackMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv):
        command: Command = env["arc.command"]
        ctx = env.get("arc.ctx")

        decostack = command.decorators()
        decostack.start(ctx)

        try:
            res = self.app(env)
        except Exception as e:
            res = None
            decostack.throw(e)
        else:
            decostack.close()

        return res


class ExecutionHandler(Middleware):
    def __call__(self, env: at.ExecEnv):
        command: Command = env["arc.command"]
        args: dict = env["arc.args"]

        res = command.callback(**args)

        return res
