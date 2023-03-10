from __future__ import annotations
import typing as t
import shlex
import sys

from arc import errors
from arc import typing as at
from arc.context import Context
from arc.parser import Parser
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    Middleware,
    MiddlewareBase,
)
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
            if not command:
                ctx.logger.debug("UsageError raised, but no command is set in context")

            if e.command:
                ctx.logger.debug(
                    "UsageError was raised, but a command is already attached"
                )
            else:
                e.command = command

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
            raise errors.UnrecognizedArgError(extra)


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
