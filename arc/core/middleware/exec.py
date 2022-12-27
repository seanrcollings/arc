from __future__ import annotations
import typing as t
import contextlib
import itertools
import os

import arc
from arc import constants
from arc import errors
from arc import typing as at
from arc import utils
from arc.config import Config
from arc.present import Joiner
from arc.color import fg, colorize
from arc.prompt.prompts import input_prompt
from arc.types.helpers import iscontextmanager

from arc.core.param.param import InjectedParam, Param, ValueOrigin
from arc.core.middleware.middleware import Middleware

if t.TYPE_CHECKING:
    from arc.core.param.param_group import ParamDefinition
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


class ParseResultCheckerMiddleware(Middleware):
    """Checks the results of the input parsing against configutation options.
    Generates error messages for unrecognized arguments

    # Env Dependancies
    - `arc.config`
    - `arc.command`
    - `arc.parse.extra` (optional)

    # Env Additions
    """

    def __call__(self, env: at.ExecEnv):
        config: Config = env["arc.config"]
        extra: list[str] | None = env.get("arc.parse.extra")
        command: Command = env["arc.command"]

        if extra and not config.allow_unrecognized_args:
            message = (
                f"Unrecognized arguments: {Joiner.with_space(extra, style=fg.YELLOW)}"
            )
            message += self.__get_suggestions(extra, config, command)
            raise errors.UnrecognizedArgError(message)

        return self.app(env)

    def __get_suggestions(
        self,
        extra: list[str],
        config: Config,
        command: Command,
    ) -> str:
        message = ""

        if config.suggestions["suggest_commands"]:

            message += self.__fmt_suggestions(
                extra[0:1],
                itertools.chain(
                    *[com.all_names for com in command.subcommands.values()]
                ),
                "subcommand",
                config,
            )

        if config.suggestions["suggest_params"]:
            message += self.__fmt_suggestions(
                extra,
                itertools.chain(
                    *[param.get_param_names() for param in command.key_params]
                ),
                "argument",
                config,
            )

        return message

    def __fmt_suggestions(
        self,
        rest: t.Iterable[str],
        possibilities: t.Iterable[str],
        kind: str,
        config: Config,
    ) -> str:
        message = ""

        suggestions = utils.string_suggestions(
            rest, possibilities, config.suggestions["distance"]
        )

        for param_name, param_sug in suggestions.items():
            if param_sug:
                message += (
                    f"\nUnrecognized {kind} {colorize(param_name, fg.YELLOW)}, "
                    f"did you mean: {Joiner.with_or(param_sug, style=fg.YELLOW)}"
                )

        return message


class Thing(Middleware):
    ...


class ProcessParseResultMiddleware(Middleware):
    config: Config
    exit_stack: contextlib.ExitStack | None

    def __call__(self, env: at.ExecEnv) -> t.Any:
        self.origins: dict[str, ValueOrigin] = {}
        env["arc.args.origins"] = self.origins

        if env.get("arc.args") is not None:
            return self.app(env)

        command: Command = env["arc.command"]
        result: dict = env["arc.parse.result"]
        self.config = env["arc.config"]

        self.exit_stack = env.get("arc.exitstack")
        self.ctx = env.get("arc.ctx")

        processed: dict[str, t.Any] = {}
        missing: list[tuple[tuple[str, ...], Param]] = []

        for group in command.param_def:
            group_processed, group_missing = self.process_param_group(
                group, result, tuple()
            )
            missing.extend(group_missing)

            if group.is_base:
                processed.update(group_processed)
            else:
                processed[group.name] = group_processed

        if missing:
            params = Joiner.with_comma(
                (param.cli_name for (_, param) in missing), style=fg.YELLOW
            )
            raise arc.errors.MissingArgError(
                f"The following arguments are required: {params}"
            )

        env["arc.args"] = processed

        return self.app(env)

    def process_param_group(
        self, group: ParamDefinition, res: at.ParseResult, path: tuple[str, ...]
    ) -> tuple[t.Any | dict, list[tuple[tuple[str, ...], Param]]]:
        processed = {}
        missing: list[tuple[tuple[str, ...], Param]] = []

        param: Param
        for param in group:
            if param.is_injected:
                continue

            value = self.process_param(param, res)

            if value is constants.MISSING:
                missing.append(((*path, param.argument_name), param))
            if param.expose:
                processed[param.argument_name] = value

        for sub in group.children:
            processed[sub.name], sub_missing = self.process_param_group(
                sub, res, (*path, sub.name)
            )
            missing.extend(sub_missing)

        if group.cls:
            inst = group.cls()
            for key, value in processed.items():
                setattr(inst, key, value)

            return inst, missing

        return processed, missing

    def process_param(self, param: Param, res: at.ParseResult):
        value, origin = self.get_param_value(param, res)
        self.origins[param.argument_name] = origin

        if param.is_required and value is None:
            raise errors.MissingArgError(
                f"argument {colorize(param.cli_name, fg.YELLOW)} expected 1 argument",
            )

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

        if value not in (None, constants.MISSING):
            value = param.run_middleware(value, self.ctx)

        if (
            param.callback
            and value is not constants.MISSING
            and origin is not ValueOrigin.DEFAULT
        ):
            value = param.callback(value, param) or value

        if self.exit_stack and iscontextmanager(value):
            value = self.exit_stack.enter_context(value)  # type: ignore

        return value

    def get_param_value(
        self, param: Param, res: at.ParseResult
    ) -> tuple[t.Any | constants.MissingType, ValueOrigin]:
        value: t.Any = res.pop(param.argument_name, constants.MISSING)
        origin = ValueOrigin.CLI

        if value is constants.MISSING:
            if (env := self.get_env_value(param)) != constants.MISSING:
                value = env
                origin = ValueOrigin.ENV
            elif (prompt := self.get_prompt_value(param)) != constants.MISSING:
                value = prompt
                origin = ValueOrigin.PROMPT
            elif (gotten := self.get_getter_value(param)) != constants.MISSING:
                value = gotten
                origin = ValueOrigin.GETTER
            else:
                value = param.default
                origin = ValueOrigin.DEFAULT

        return (value, origin)

    def get_env_value(self, param: Param) -> str | constants.MissingType:
        if not param.envvar:
            return constants.MISSING

        return os.getenv(f"{self.config.env_prefix}{param.envvar}", constants.MISSING)

    def get_prompt_value(self, param: Param) -> str | constants.MissingType:
        if not param.prompt:
            return constants.MISSING

        if hasattr(param.type.resolved_type, "__prompt__"):
            return utils.dispatch_args(
                param.type.resolved_type.__prompt__, param, self.ctx  # type: ignore
            )

        return input_prompt(self.config.prompt, param)

    def get_getter_value(self, param: Param) -> t.Any | constants.MissingType:
        getter = param.getter_func
        if not getter:
            return constants.MISSING

        return utils.dispatch_args(getter, param, self.ctx)


class DependancyInjectorMiddleware(Middleware):
    def __call__(self, env: at.ExecEnv):
        command: Command = env["arc.command"]
        args: dict = env["arc.args"]

        for group in command.param_def:
            self.inject_dependancies(group, args, env)

        return self.app(env)

    def inject_dependancies(self, group: ParamDefinition, args: dict, env: at.ExecEnv):
        injected = {}
        exit_stack: contextlib.ExitStack | None = env.get("arc.exitstack")
        ctx = env.get("arc.ctx")

        for param in group:
            if not param.is_injected:
                continue

            param = t.cast(InjectedParam, param)

            env["arc.args.origins"][param.argument_name] = ValueOrigin.INJECTED
            value = param.get_injected_value(ctx)

            if exit_stack and iscontextmanager(value):
                value = exit_stack.enter_context(value)

            injected[param.argument_name] = value

        if group.children:
            inst = args[group.name]
            for sub in group.children:
                self.inject_dependancies(sub, {sub.name: getattr(inst, sub.name)}, env)

        if group.cls:
            inst = args[group.name]
            for key, value in injected.items():
                setattr(inst, key, value)
        else:
            args.update(injected)


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
