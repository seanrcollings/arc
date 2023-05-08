"""Contains all of the middlewares used during initialization of a command"""
from __future__ import annotations
import typing as t
from datetime import datetime
import shlex
import sys

from arc import autocompletions, errors
from arc import typing as at
from arc.define.param.param import FlagParam, OptionParam
from arc.parser import CustomAutocompleteAction, CustomVersionAction, Parser
from arc.runtime import Context
from arc.runtime.middleware import (
    DefaultMiddlewareNamespace,
    Middleware,
    MiddlewareBase,
)
from arc.types.type_info import TypeInfo

if t.TYPE_CHECKING:
    from arc.define import Command
    from arc.define.param import ParamDefinition


class StartTimeMiddleware(MiddlewareBase):
    """Utility Middleware that tracks how long execution takes

    # Context Dependencies
    None

    #  Context Additions
    - `arc.debug.start` - datetime representing the start of execution
    - `arc.debug.end`  - datetime representing the end of execution.
    """

    def __call__(self, ctx: Context) -> t.Any:
        start = datetime.now()
        ctx["arc.debug.start"] = start
        try:
            yield
        finally:
            end = datetime.now()
            ctx["arc.debug.end"] = end
            diff = end - start
            ctx.logger.debug(f"Execution took: {diff.total_seconds():.4f}s")


class LoadPluginsMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        ctx.logger.debug("Loading plugins...")
        app = ctx.app
        app.plugins.paths(*ctx.config.plugins.paths)
        app.plugins.groups(*ctx.config.plugins.groups)
        app.plugins.entrypoints(*ctx.config.plugins.entrypoints)

        if app.plugins:
            ctx.logger.debug("Plugins loaded: %s", ", ".join(app.plugins))
            ctx.logger.debug("Calling plugin hooks...")
            for name, p in app.plugins.items():
                ctx.logger.debug("  Calling plugin hook: %s", name)
                p(ctx)


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


class AddRuntimeParmsMiddleware(MiddlewareBase):
    """Adds runtime-params to the root Command object

    # Context Dependencies
    - `arc.root`

    # Context Additions
    None

    # Added Parameters
    - `--version / -v`: If there is a version set in the configuration
    - `--autocomplete`: If shell completions are enabled
    """

    def __call__(self, ctx: Context) -> t.Any:

        if ctx.config.version:
            self.__add_version_param(ctx.root.param_def)

        if ctx.config.autocomplete:
            self.__add_autocomplete_param(ctx.root.param_def)

    def __add_version_param(self, group: ParamDefinition) -> None:
        group.insert(
            1,
            FlagParam(
                "version",
                short_name="v",
                type=TypeInfo.analyze(bool),
                description="Displays the app's version number",
                default=False,
                action=CustomVersionAction,
                expose=False,
            ),
        )

    def __add_autocomplete_param(self, group: ParamDefinition) -> None:
        annotation = t.Literal[1]
        annotation.__args__ = tuple(autocompletions.ShellCompletion.shells.keys())  # type: ignore
        group.insert(
            1,
            OptionParam(
                "autocomplete",
                type=TypeInfo.analyze(annotation),
                description="Shell completion support",
                action=CustomAutocompleteAction,
                default=None,
                expose=False,
            ),
        )


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
    def __call__(self, ctx: Context) -> t.Any:
        args: list[str] = ctx["arc.input"]
        command, command_args = ctx.root.find_command(args)
        ctx["arc.command"] = command
        ctx["arc.input"] = command_args


class ArgParseMiddleware(MiddlewareBase):
    def __call__(self, ctx: Context) -> t.Any:
        args: list[str] = ctx["arc.input"]

        result, extra = self.parse_args(ctx.command, args)
        ctx["arc.parse.result"] = result
        ctx["arc.parse.extra"] = extra

    def parse_args(
        self, command: Command, args: list[str]
    ) -> tuple[at.ParseResult, list[str]]:
        parser = self.create_parser(command)
        return parser.parse_known_intermixed_args(args)

    def create_parser(self, command: Command) -> Parser:
        parser = Parser(add_help=False)
        for param in command.cli_params:
            parser.add_param(param, command)

        return parser


class CheckParseResultsMiddleware(MiddlewareBase):
    """Checks the results of the input parsing against configutation options.
    Generates error messages for unrecognized arguments

    # Context Dependencies
    - `arc.config`
    - `arc.parse.extra` (optional)

    # Context Additions
    """

    def __call__(self, ctx: Context) -> t.Any:
        extra: list[str] | None = ctx.get("arc.parse.extra")

        if extra and not ctx.config.allow_unrecognized_args:
            raise errors.UnrecognizedArgError(extra)


class InitMiddleware(DefaultMiddlewareNamespace):
    """Namespace for all the default init middlewares

    Use it to reference a default init middleware when adding your own custom middlewares

    ```py
    import arc

    @arc.command
    def command():
        arc.print("hello there")

    # To add your own init middlewares, you need to
    # create the App object explicitly
    app = arc.App(command)

    @app.use(before=arc.InitMiddleware.Parse)
    def before_parse(ctx: arc.Context):
        # Will run before the middleware that performs the parsing operation
        ...

    app()
    ```

    """

    StartTime = StartTimeMiddleware()
    LoadPlugins = LoadPluginsMiddleware()
    PerformDevChecks = PerformDevChecksMiddleware()
    AddRuntimeParms = AddRuntimeParmsMiddleware()
    AddUsageErrorInfo = AddUsageErrorInfoMiddleware()
    NormalizeInput = NormalizeInputMiddleware()
    CommandFinder = CommandFinderMiddleware()
    Parser = ArgParseMiddleware()
    CheckParseResult = CheckParseResultsMiddleware()

    _list: list[Middleware] = [
        StartTime,
        LoadPlugins,
        PerformDevChecks,
        AddRuntimeParms,
        AddUsageErrorInfo,
        NormalizeInput,
        CommandFinder,
        Parser,
        CheckParseResult,
    ]
