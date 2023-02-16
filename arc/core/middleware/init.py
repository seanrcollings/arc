from __future__ import annotations
import typing as t
import shlex
import sys
import itertools

import arc
from arc import errors, utils
from arc import typing as at
from arc.color import colorize, fg
from arc.context import Context
from arc.parser import Parser
from arc.core.middleware.middleware import MiddlewareBase
from arc.present import Joiner
from arc.config import Config

if t.TYPE_CHECKING:
    from arc.core import Command


class InitChecksMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context):
        root: Command = ctx["arc.root"]

        if root.subcommands and len(list(root.argument_params)) != 0:
            raise errors.CommandError(
                "Top-level command with subcommands cannot "
                "have argument / positional parameters"
            )


class AddUsageErrorInfoMiddleware(MiddlewareBase):
    """A utility middleware that catches `UsageError`s and adds information so they can generate a usage error

    # ctx Dependancies
    - `arc.command` (optional): Usage information comes from the current executing [`Command`][arc.core.command.Command] object
    # ctx Additions
    None
    """

    def __call__(self, ctx: Context) -> t.Any:
        try:
            yield
        except errors.UsageError as e:
            e.command = ctx.get("arc.command")
            raise


class InputMiddleware(MiddlewareBase):
    """Middleware that normalizes different input sources. If input is provided when
    command is called, it will be normalized to an list. If input is not provided,
    `sys.argv` is used.

    # ctx Dependancies
    - `arc.input` (optional): Only exists if input was provided in the call to the command

    # ctx Additions
    - `arc.input`: Adds it if it's not already there, normalizes it if it is there
    """

    def __call__(self, ctx) -> t.Any:
        args: at.InputArgs = ctx.get("arc.input")
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        args = list(args)
        ctx["arc.input"] = args


class CommandFinderMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context):
        args: list[str] = ctx["arc.input"]
        root: Command = ctx["arc.root"]
        global_args, command, command_args = root.split_args(args)
        ctx["arc.input.global"] = global_args
        ctx["arc.command"] = command
        ctx["arc.input"] = command_args
        ctx["arc.mode"] = self.get_mode(root, command)

    def get_mode(self, root: Command, command: Command) -> at.ExecMode:
        if root is command:
            return "root"
        else:
            return "subcommand"


class ArgParseMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context):
        command: Command = ctx["arc.command"]
        args: list[str] = ctx["arc.input"]
        global_args: list[str] = ctx["arc.input.global"]
        mode: at.ExecMode = ctx["arc.mode"]

        if mode == "root":
            self.run_parse(command, global_args, ctx)
        elif mode == "subcommand":
            self.run_parse(command, args, ctx)

    def run_parse(self, command: Command, args: list[str], ctx: Context):
        result, extra = self.parse_args(command, args)

        ctx["arc.parse.result"] = result
        ctx["arc.parse.extra"] = extra

    def parse_args(self, command: Command, args: list[str]) -> tuple[dict, list[str]]:
        parser = self.create_parser(command)
        return parser.parse_known_intermixed_args(args)

    def create_parser(self, command: Command) -> Parser:
        parser = Parser(add_help=False)
        for param in command.cli_params:
            parser.add_param(param, command)

        return parser


class ParseResultCheckerMiddleware(MiddlewareBase):
    """Checks the results of the input parsing against configutation options.
    Generates error messages for unrecognized arguments

    # ctx Dependancies
    - `arc.config`
    - `arc.command`
    - `arc.parse.extra` (optional)

    # ctx Additions
    """

    def __call__(self, ctx: Context):
        config: Config = ctx["arc.config"]
        extra: list[str] | None = ctx.get("arc.parse.extra")
        command: Command = ctx["arc.command"]

        if extra and not config.allow_unrecognized_args:
            message = (
                f"Unrecognized arguments: {Joiner.with_space(extra, style=fg.YELLOW)}"
            )
            message += self.__get_suggestions(extra, config, command)
            raise errors.UnrecognizedArgError(message)

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


DEFAULT_INIT_MIDDLEWARES = [
    AddUsageErrorInfoMiddleware(),
    InitChecksMiddleware(),
    InputMiddleware(),
    CommandFinderMiddleware(),
    ArgParseMiddleware(),
    ParseResultCheckerMiddleware(),
]
