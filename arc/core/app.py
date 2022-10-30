import itertools
import os
import shlex
import sys
import typing as t
import arc
from arc import constants
from arc import errors
from arc import typing as at
from arc.core.param.param import InjectedParam, Param, ValueOrigin
from arc.parser import Parser
from arc.config import config, Config
from arc.present import Joiner
from arc.color import fg, colorize
from arc import utils
from arc.prompt.prompts import input_prompt
from arc.core.param.param_group import ParamGroup
from arc.core import Command


Env = dict[str, t.Any]


class Middleware:
    def __init__(self, app: t.Callable[[Env], t.Any]):
        self.app = app

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.app)})"

    def __call__(self, env: Env):
        return self.app(env)


class InputMiddleware(Middleware):
    def __call__(self, env):
        args: at.InputArgs = env.get("arc.input")
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        args = list(args)
        env["arc.input"] = args

        return self.app(env)


class CommandFinderMiddleware(Middleware):
    def __call__(self, env: Env):
        args: list[str] = env["arc.input"]
        root: Command = env["arc.root"]
        global_args, command, command_args = root.split_args(args)
        env["arc.command"] = command
        env["arc.input"] = global_args if command is root else command_args
        return self.app(env)


class ArgParseMiddleware(Middleware):
    def __call__(self, env: Env):
        command: Command = env["arc.command"]
        args: list[str] = env["arc.input"]

        parser = Parser(add_help=False)
        for param in command.cli_params:
            parser.add_param(param, command)

        result, extra = parser.parse_known_intermixed_args(args)
        env["arc.parse.result"] = result
        env["arc.parse.extra"] = extra

        return self.app(env)


class ParseResultCheckerMiddleware(Middleware):
    def __call__(self, env: Env):
        config: Config = env["arc.config"]
        extra: list[str] | None = env.get("arc.parse.extra")
        command: Command = env["arc.command"]

        if extra and not config.allow_unrecognized_args:
            message = (
                f"Unrecognized arguments: {Joiner.with_space(extra, style=fg.YELLOW)}"
            )
            message += self.__get_suggestions(extra, config, command)
            env["arc.errors"].append(message)
            return None

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


class ContextCreationMiddleware(Middleware):
    def __call__(self, env: Env) -> t.Any:
        command: Command = env["arc.command"]
        parent: arc.Context | None = env.get("arc.ctx")
        ctx = arc.Context(command=command, parent=parent)
        env["arc.ctx"] = ctx

        with ctx:
            return self.app(env)


class ProcessParseResultMiddleware(Middleware):
    config: Config

    def __call__(self, env: Env) -> t.Any:
        command: Command = env["arc.command"]
        result: dict = env["arc.parse.result"]
        self.config = env["arc.config"]
        processed: dict[str, t.Any] = {}
        missing: list[tuple[tuple[str, ...], Param]] = []

        for group in command.param_groups:
            group_processed, group_missing = self.process_param_group(
                group, result, tuple()
            )
            missing.extend(group_missing)

            if group.is_default:
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
        # env["arc.args.missing"] = missing
        return self.app(env)

    def process_param_group(
        self, group: ParamGroup, res: at.ParseResult, path: tuple[str, ...]
    ) -> tuple[t.Any | dict, list[tuple[tuple[str, ...], Param]]]:
        processed = {}
        missing: list[tuple[tuple[str, ...], Param]] = []

        param: Param
        for param in group:
            if param.is_injected:
                continue

            value, origin = self.process_param(param, res)
            if value is constants.MISSING:
                missing.append(((*path, param.argument_name), param))
            if param.expose:
                processed[param.argument_name] = value

        for sub in group.sub_groups:
            processed[sub.name], sub_missing = self.process_param_group(
                group, res, (*path, sub.name)
            )
            missing.extend(sub_missing)

        if group.cls:
            inst = group.cls()
            for key, value in processed.items():
                setattr(inst, key, value)

            return (inst, missing)

        return processed, missing

    def process_param(self, param: Param, res: at.ParseResult):
        value, origin = self.get_param_value(param, res)

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
            value = param.run_middleware(value)

        if (
            param.callback
            and value is not constants.MISSING
            and origin is not ValueOrigin.DEFAULT
        ):
            value = param.callback(value, param) or value

        # if iscontextmanager(value) and not value is ctx:
        #     value = ctx.resource(value)  # type: ignore

        return value, origin

    def get_param_value(
        self, param: Param, res: at.ParseResult
    ) -> tuple[t.Any | constants.MissingType, ValueOrigin]:
        value: t.Any = res.pop(param.argument_name, constants.MISSING)
        origin = ValueOrigin.CLI

        if value is constants.MISSING:
            if param.envvar and (env := self.get_env_value(param)):
                value = env
                origin = ValueOrigin.ENV
            elif (
                param.prompt
                and (prompt := self.get_prompt_value(param)) != constants.MISSING
            ):
                value = prompt
                origin = ValueOrigin.PROMPT
            # elif param.getter_func and (gotten := param.getter_func(param)) != MISSING:
            #     value = gotten
            #     origin = ValueOrigin.GETTER
            else:
                value = param.default
                origin = ValueOrigin.DEFAULT

        return (value, origin)

    def get_env_value(self, param: Param) -> str | None:
        return os.getenv(f"{self.config.env_prefix}{param.envvar}")

    def get_prompt_value(self, param: Param) -> str | constants.MissingType:
        if hasattr(param.type.resolved_type, "__prompt__"):
            return param.type.resolved_type.__prompt__(param)  # type: ignore

        return input_prompt(self.config.prompt, param)


class DependancyInjectorMiddleware(Middleware):
    def __call__(self, env: Env):
        command: Command = env["arc.command"]
        args: dict = env["arc.args"]

        for group in command.param_groups:
            self.inject_dependancies(group, args)

        return self.app(env)

    def inject_dependancies(self, group: ParamGroup, args: dict):
        injected = {}

        for param in group:
            if not param.is_injected:
                continue

            param = t.cast(InjectedParam, param)

            value = param.get_injected_value()
            injected[param.argument_name] = value

        if group.sub_groups:
            inst = args[group.name]
            for sub in group.sub_groups:
                self.inject_dependancies(sub, {sub.name: getattr(inst, sub.name)})

        if group.cls:
            inst = args[group.name]
            for key, value in injected.items():
                setattr(inst, key, value)
        else:
            args.update(injected)


# def nested_update(dct: dict, path: t.Sequence[str], value: t.Any):
#     for p in path[0:-1]:
#         dct = dct[p]

#     dct[path[-1]] = value


# class EnvArgFillerMiddleware(Middleware):
#     def __call__(self, env: Env):
#         args: dict = env["arc.args"]
#         config: Config = env["arc.config"]
#         missing: list[tuple[tuple[str, ...], Param]] = env["arc.args.missing"]
#         next_missing = []

#         for path, param in missing:
#             if param.envvar:
#                 value = os.getenv(f"{config.env_prefix}{param.envvar}")
#                 if value:
#                     nested_update(args, path, value)
#                 else:
#                     next_missing.append((path, param))

#         env["arc.args.missing"] = next_missing
#         return self.app(env)


class DecoratorStackMiddleware(Middleware):
    def __call__(self, env: Env):
        command: Command = env["arc.command"]

        decostack = command.decorators()
        decostack.start()

        try:
            res = self.app(env)
        except Exception as e:
            res = None
            decostack.throw(e)
        else:
            decostack.close()

        return res


class ExecutionHandler(Middleware):
    def __call__(self, env: Env):
        command: Command = env["arc.command"]
        args: dict = env["arc.args"]

        res = command.callback(**args)

        return res


class Arc:
    DEFAULT_INIT_MIDDLEWARES = [
        InputMiddleware,
        CommandFinderMiddleware,
        ArgParseMiddleware,
        ParseResultCheckerMiddleware,
    ]

    DEFAULT_EXEC_MIDDLEWARES = [
        ProcessParseResultMiddleware,
        DependancyInjectorMiddleware,
        DecoratorStackMiddleware,
        ExecutionHandler,
    ]

    def __init__(
        self,
        root: Command,
        init_middlewares: list[type[Middleware]] | None = None,
        exec_middlewares: list[type[Middleware]] | None = None,
        input: at.InputArgs = None,
        env: Env | None = None,
    ) -> None:
        self.root: Command = root
        self.init_middleware_types: list[type[Middleware]] = (
            init_middlewares or self.DEFAULT_INIT_MIDDLEWARES
        )
        self.exec_middleware_types: list[type[Middleware]] = (
            exec_middlewares or self.DEFAULT_EXEC_MIDDLEWARES
        )
        self.provided_env: Env = env or {}
        self.input: at.InputArgs = input
        self.env: Env = self.create_env()

    def __call__(self) -> t.Any:
        self.init()
        return self.execute()

    def init(self) -> t.Any:
        first = self.build_middleware_stack(self.init_middleware_types)
        return first(self.env)

    def execute(self) -> t.Any:
        first = self.build_middleware_stack(self.exec_middleware_types)
        return first(self.env)

    def subexecute(self, command: t.Optional[Command] = None) -> t.Any:
        print(f"Excute: {command}")

    def build_middleware_stack(
        self, middlewares: t.Sequence[type[Middleware]]
    ) -> Middleware:
        first: Middleware | None = None

        for middleware_type in reversed(middlewares):
            if first is None:
                first = middleware_type(lambda env: env)
            else:
                first = middleware_type(first)

        assert first is not None

        return first

    def create_env(self) -> Env:
        return {
            "arc.root": self.root,
            "arc.input": self.input,
            "arc.config": config,
            "arc.errors": [],
            "arc.app": self,
        } | self.provided_env
