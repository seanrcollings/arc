from __future__ import annotations

import shlex
import sys
import typing as t

from arc import errors
from arc import typing as at
from arc.parser import Parser
from arc.runtime import Context
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    Middleware,
    MiddlewareBase,
)

if t.TYPE_CHECKING:
    from arc.define import Command
    from arc.config import Config


class PerformDevChecksMiddleware(MiddlewareBase):
    """A utility middleware that performs some development checks.
    Will be disabled in production mode.

    # Context Dependencies
    - `arc.root` - Root Command object to start checks from
    - `arc.concig` - Checks Configuration for enviroment

    # Context Additions
    None

    """

    def __call__(self, ctx: Context) -> t.Any:
        if ctx.config.environment == "development":
            ctx.logger.debug("Performing dev checks...")
            ctx.logger.debug("  Checking all command parameters")

            for command in ctx.root:
                if "param_def" not in command.__dict__:
                    command.param_def
                    del command.param_def


class AddUsageErrorInfoMiddleware(MiddlewareBase):
    """A utility middleware that catches `UsageError`s and adds information so they can generate a usage error

    # Context Dependencies
    - `arc.command` (optional): Usage information comes from the current
    executing [`Command`][arc.define.command.Command] object

    # Context Additions
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

    # Context Dependencies
    - `arc.input` (optional): Only exists if input was provided in the call to the command

    # Context Additions
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

    # Context Dependencies
    - `arc.config`
    - `arc.command`
    - `arc.parse.extra` (optional)

    # Context Additions
    """

    def __call__(self, ctx: Context):
        config: Config = ctx["arc.config"]
        extra: list[str] | None = ctx.get("arc.parse.extra")
        command: Command = ctx["arc.command"]

        if extra and not config.allow_unrecognized_args:
            raise errors.UnrecognizedArgError(extra)


class InitMiddleware(DefaultMiddlewareNamespace):
    """Namespace for all the default init middlewares"""

    PerformDevChecks = PerformDevChecksMiddleware()
    AddUsageErrorInfo = AddUsageErrorInfoMiddleware()
    NormalizeInput = NormalizeInputMiddleware()
    CommandFinder = CommandFinderMiddleware()
    Parser = ArgParseMiddleware()
    CheckParseResult = CheckParseReulstMiddleware()

    _list: list[Middleware] = [
        PerformDevChecks,
        AddUsageErrorInfo,
        NormalizeInput,
        CommandFinder,
        Parser,
        CheckParseResult,
    ]
