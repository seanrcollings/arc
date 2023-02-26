from __future__ import annotations
import typing as t
import shlex
import sys
import itertools

from arc import errors, utils
from arc import typing as at
from arc.color import colorize, fg
from arc.context import Context
from arc.parser import Parser
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    Middleware,
    MiddlewareBase,
)
from arc.present import Joiner
from arc.config import Config

if t.TYPE_CHECKING:
    from arc.define import Command


class AddUsageErrorInfoMiddleware(MiddlewareBase):
    """A utility middleware that catches `UsageError`s and adds information so they can generate a usage error

    # ctx Dependancies
    - `arc.command` (optional): Usage information comes from the current
    executing [`Command`][arc.define.command.Command] object
    # ctx Additions
    None
    """

    def __call__(self, ctx: Context) -> t.Any:
        try:
            yield
        except errors.UsageError as e:
            command = ctx.get("arc.command")
            e.command = command
            if not command:
                ctx.logger.debug("UsageError rasied, but no command is set in context")
            raise


class NormalizeInputMiddleware(MiddlewareBase):
    """Middleware that normalizes different input sources. If input is provided when
    command is called, it will be normalized to an list. If input is not provided,
    `sys.argv` is used.

    # ctx Dependancies
    - `arc.input` (optional): Only exists if input was provided in the call to the command

    # ctx Additions
    - `arc.input`: Adds it if it's not already there, normalizes it if it is there
    """

    def __call__(self, ctx: Context) -> t.Any:
        args: at.InputArgs = ctx.get("arc.input")
        if args is None:
            ctx.logger.debug("Using sys.argv as input: %s", sys.argv[1:])
            args = sys.argv[1:]
        elif isinstance(args, str):
            args = shlex.split(args)
            ctx.logger.debug("Using provided string as input. Shlex output: %s", args)
        else:
            ctx.logger.debug("Using provided iterable as input: %s", args)

        args = list(args)
        ctx["arc.input"] = args


class CommandFinderMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context):
        args: list[str] = ctx["arc.input"]
        root: Command = ctx["arc.root"]
        command, command_args = self.split_args(root, args)
        ctx["arc.command"] = command
        ctx["arc.input"] = command_args

    def split_args(self, root: Command, args: list[str]) -> tuple[Command, list[str]]:
        """Seperates out a sequence of args into:
        - a subcommand object
        - command arguments
        """
        index = 0
        command: Command = root

        for value in args:
            if value in command.subcommands:
                index += 1
                command = command.subcommands.get(value)
            else:
                break

        command_args: list[str] = args[index:]

        return command, command_args


class ArgParseMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context):
        command: Command = ctx["arc.command"]
        args: list[str] = ctx["arc.input"]

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


class CheckParseReulstMiddleware(MiddlewareBase):
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


class InitMiddleware(DefaultMiddlewareNamespace):
    """Namespace for all the default init middlewares"""

    AddUsageErrorInfo = AddUsageErrorInfoMiddleware()
    NormalizeInput = NormalizeInputMiddleware()
    CommandFinder = CommandFinderMiddleware()
    Parser = ArgParseMiddleware()
    CheckParseResult = CheckParseReulstMiddleware()

    _list: list[Middleware] = [
        AddUsageErrorInfo,
        NormalizeInput,
        CommandFinder,
        Parser,
        CheckParseResult,
    ]
