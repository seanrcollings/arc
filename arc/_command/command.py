from __future__ import annotations
from ast import alias
import inspect
import sys
import typing as t
import shlex

from arc import errors, utils
from arc._command import classful
from arc._command.decorators import CommandDecorator, DecoratorStack
from arc._command.documentation import Documentation
from arc.color import colorize, fg
from arc.config import config
from arc.parser import Parser
from arc.present.helpers import Joiner
from .param import ParamMixin
from arc.context import Context

import arc.typing as at

if t.TYPE_CHECKING:
    from .param import Param, ParamGroup

K = t.TypeVar("K")
V = t.TypeVar("V")


class SubcommandsDict(dict[K, V]):
    aliases: dict[K, K]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aliases = {}

    def get(self, key: K, default=None):
        if super().__contains__(key):
            return self[key]
        if key in self.aliases:
            return self[self.aliases[key]]

        return default

    def __contains__(self, key: object):
        return super().__contains__(key) or key in self.aliases

    def add_alias(self, key: K, alias: K):
        self.aliases[alias] = key

    def add_aliases(self, key: K, *aliases: K):
        for alias in aliases:
            self.add_alias(key, alias)

    def aliases_for(self, key: K) -> list[K]:
        return [alias for alias, val in self.aliases.items() if val == key]


class Command(
    ParamMixin,
    utils.Display,
    members=["name", "callback", "params", "subcommands"],
):
    callback: at.CommandCallback
    name: str
    parent: Command | None
    subcommands: SubcommandsDict[str, Command]
    param_groups: list[ParamGroup]
    doc: Documentation
    explicit_name: bool
    decorators: DecoratorStack

    def __init__(
        self,
        callback: at.CommandCallback,
        name: str | None = None,
        description: str | None = None,
        parent: Command | None = None,
        explicit_name: bool = True,
    ):
        if inspect.isclass(callback):
            self.callback = classful.wrap_class_callback(
                t.cast(type[at.ClassCallback], callback)
            )
        else:
            self.callback = callback

        self.name = name or callback.__name__
        self.parent = parent
        self.subcommands = SubcommandsDict()
        self.doc = Documentation(self, description)
        self.explicit_name = explicit_name
        self.decorators = DecoratorStack()

        if config.environment == "development":
            self.param_groups

    def __call__(self, input_args: at.InputArgs = None, state: dict = None):
        if not self.explicit_name:
            self.name = utils.discover_name()
        args = self.get_args(input_args)

        if self.is_root and self.subcommands and len(list(self.argument_params)) != 0:
            raise errors.CommandError(
                "Top-level command with subcommands cannot "
                "have argument / positional parameters"
            )

        Context.state.data = state or {}

        try:
            return self.__main(args)
        except errors.ExternalError as e:
            if config.environment == "production":
                print(e)
                raise errors.Exit(1)

            raise
        except Exception as e:
            if config.report_bug:
                raise errors.InternalError(
                    f"{self.name} has encountered a critical error. "
                    f"Please file a bug report with the maintainer: {colorize(config.report_bug, fg.YELLOW)}"
                ) from e

            raise

    @property
    def schema(self):
        return {
            "name": self.name,
            "params": [param.schema for param in self.params],
            "subcommands": [com.schema for com in self.subcommands.values()],
        }

    @property
    def is_namespace(self):
        return self.callback is namespace_callback

    @property
    def is_root(self):
        return self.parent is None

    @property
    def root(self):
        command = self
        while command.parent:
            command = command.parent

        return command

    # Subcommands ----------------------------------------------------------------

    def subcommand(self, name: at.CommandName = None, description: str | None = None):
        def inner(callback: at.CommandCallback):
            command_name, aliases = self.get_command_name(callback, name)
            command = Command(
                callback=callback,
                name=command_name,
                description=description,
                parent=self,
            )
            self.add_command(command, aliases)
            return command

        return inner

    def add_command(self, command: Command, aliases: t.Sequence[str] | None = None):
        self.subcommands[command.name] = command
        command.parent = self
        self.inherit_decorators(command)
        if aliases:
            self.subcommands.add_aliases(command.name, *aliases)

        return command

    def add_commands(self, *commands: Command):
        return [self.add_command(command) for command in commands]

    # Execution ------------------------------------------------------------------

    def __main(self, args: list[str]):
        global_args = []
        while len(args) > 0 and args[0] not in self.subcommands:
            global_args.append(args.pop(0))

        command: Command = self

        index = 0
        for idx, value in enumerate(args):
            if value in command.subcommands:
                index = idx
                command = command.subcommands.get(value)

        with self.create_ctx() as ctx:
            if (
                global_args
                or command is self
                or config.global_callback_execution == "always"
            ):
                global_res = ctx.run(global_args)

                if command is self:
                    return global_res

            with command.create_ctx(parent=ctx) as commandctx:
                command_args = args[index + 1 :]
                return commandctx.run(command_args)

    def process_parsed_result(
        self, res: at.ParseResult, ctx: Context
    ) -> tuple[dict[str, t.Any], list[Param]]:
        processed: dict[str, t.Any] = {}
        missing: list[Param] = []

        for group in self.param_groups:
            group_processed, group_missing = group.process_parsed_result(res, ctx)
            missing.extend(group_missing)

            if group.is_default:
                processed.update(group_processed)
            else:
                processed[group.name] = group_processed

        return processed, missing

    def inject_dependancies(self, args: dict[str, t.Any], ctx: Context):
        for group in self.param_groups:
            group.inject_dependancies(args, ctx)

    # Helpers --------------------------------------------------------------------

    def create_parser(self):
        parser = Parser(add_help=False)
        for param in self.cli_params:
            parser.add_param(param)

        return parser

    def create_ctx(self, **kwargs):
        return Context(self, **kwargs)

    def get_args(self, args: at.InputArgs):
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        return args

    def inherit_decorators(self, command: Command):
        decos, command.decorators = command.decorators, DecoratorStack()

        for deco in self.decorators:
            command.decorators.add(deco)
        for deco in decos:
            command.decorators.add(deco)

    @staticmethod
    def get_command_name(
        callback: at.CommandCallback, names: at.CommandName
    ) -> tuple[str, tuple[str, ...]]:
        if names is None:
            name = callback.__name__

            if config.transform_snake_case:
                name = name.replace("_", "-")

            return name, tuple()

        if isinstance(names, str):
            return names, tuple()

        return names[0], tuple(names[1:])


def command(name: str | None = None, description: str | None = None):
    def inner(callback: at.CommandCallback):
        return Command(
            callback=callback,
            name=Command.get_command_name(callback, name)[0],
            description=description,
            parent=None,
            explicit_name=bool(name),
        )

    return inner


def namespace_callback(ctx: Context):
    print(ctx.command.doc.usage())
    command = colorize(
        f"{ctx.command.root.name} {Joiner.with_space(ctx.command.doc.fullname)} --help",
        fg.YELLOW,
    )
    print(f"{command} for more information")


def namespace(name: str, description: str | None = None):
    return Command(
        callback=namespace_callback,
        name=name,
        description=description,
        parent=None,
    )
