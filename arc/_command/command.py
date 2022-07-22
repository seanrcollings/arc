from __future__ import annotations
import inspect
import sys
import typing as t
import shlex

import arc
from arc import errors, utils
from arc._command import classful
from arc._command.autoload import Autoload
from arc._command.decorators import CommandDecorator, DecoratorStack
from arc._command.documentation import Documentation
from arc.color import colorize, fg
from arc.config import config
from arc.parser import Parser
from arc.present.helpers import Joiner
from .param import ParamMixin
from arc.context import Context

import arc.typing as at
from arc.autocompletions import CompletionInfo, get_completions, Completion

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
    members=["name"],
):
    callback: at.CommandCallback
    name: str
    parent: Command | None
    subcommands: SubcommandsDict[str, Command]
    param_groups: list[ParamGroup]
    doc: Documentation
    explicit_name: bool
    decorators: DecoratorStack
    __autoload__: bool

    def __init__(
        self,
        callback: at.CommandCallback,
        name: str | None = None,
        description: str | None = None,
        parent: Command | None = None,
        explicit_name: bool = True,
        autoload: bool = False,
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
        self.__autoload__ = autoload

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
                arc.print(e)
                raise errors.Exit(1)

            raise
        except Exception as e:
            if config.report_bug:
                raise errors.InternalError(
                    f"{self.name} has encountered a critical error. "
                    f"Please file a bug report with the maintainer: {colorize(config.report_bug, fg.YELLOW)}"
                ) from e

            raise

    def __completions__(self, info: CompletionInfo, *_args, **_kwargs):
        # TODO: it does not take into
        # account that collection types can include more than 1 positional
        # argument.
        global_args, command, command_args = self.split_args(info.words)

        if command is self:
            args = global_args
        else:
            args = command_args

        if not args and command.subcommands:
            return command.__complete_subcommands(info)
        elif info.current.startswith("-"):
            return command.__complete_option(info)
        elif len(args) >= 1 and args[-1].startswith("-"):
            return command.__complete_param_value(info, args[-1].lstrip("-"))
        elif len(args) >= 2 and args[-2].startswith("-"):
            return command.__complete_param_value(info, args[-2].lstrip("-"))
        else:
            if command.is_root and command.subcommands:
                return command.__complete_subcommands(info)
            else:
                return command.__complete_positional_value(info, args)

    def __complete_subcommands(self, info: CompletionInfo):
        return [Completion(command.name) for command in self.subcommands.values()]

    def __complete_option(self, info: CompletionInfo):
        return [Completion(param.cli_name) for param in self.key_params]

    def __complete_param_value(self, info: CompletionInfo, param_name: str):
        param = self.get_param(param_name)
        if not param:
            return []

        return get_completions(param, info)

    def __complete_positional_value(self, info: CompletionInfo, args: list[str]):
        # TODO: This approach does not take into consideration positonal
        # arguments that are peppered in between options. It only counts ones
        # at the end of the command line.
        pos_arg_count = 0
        for word in reversed(args):
            if word.startswith("-") and word != "--":
                break
            pos_arg_count += 1

        if info.current != "" and pos_arg_count > 0:
            pos_arg_count -= 1

        arg_params = list(self.argument_params)
        if pos_arg_count < len(arg_params):
            param = arg_params[pos_arg_count]
            return get_completions(param, info)

        return []

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

    def inherit_decorators(self, command: Command):
        decos, command.decorators = command.decorators, DecoratorStack()

        for deco in self.decorators:
            if deco.inherit:
                command.decorators.add(deco)
        for deco in decos:
            command.decorators.add(deco)

    # Execution ------------------------------------------------------------------

    def __main(self, args: list[str]):
        global_args, command, command_args = self.split_args(args)

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
                return commandctx.run(command_args)

    def parse_args(
        self, args: list[str], ctx: Context
    ) -> tuple[at.ParseResult, list[str]]:
        parser = self.create_parser()
        try:
            return parser.parse_known_intermixed_args(args)
        except errors.ParserError as e:
            e.ctx = ctx
            raise

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

    # Argument Handling ---------------------------------------------------------

    def get_args(self, args: at.InputArgs) -> list[str]:
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        return list(args)

    def split_args(self, args: list[str]) -> tuple[list[str], Command, list[str]]:
        """Seperates out a sequence of args into:
        - global arguments
        - a subcommand object
        - command arguments
        """
        index = 0
        global_args: list[str] = []
        while index < len(args) and args[index] not in self.subcommands:
            global_args.append(args[index])
            index += 1

        command: Command = self

        for idx, value in enumerate(args):
            if value in command.subcommands:
                index = idx
                command = command.subcommands.get(value)

        command_args: list[str] = args[index + 1 :]

        return global_args, command, command_args

    def create_parser(self) -> Parser:
        parser = Parser(add_help=False)
        for param in self.cli_params:
            parser.add_param(param, self)

        return parser

    # Helpers --------------------------------------------------------------------

    def complete(self, param_name: str):
        param = self.get_param(param_name)
        if param:

            def inner(func: at.CompletionFunc):
                param.comp_func = func  # type: ignore
                return func

            return inner

        raise errors.ParamError(f"No parameter with name: {param_name}")

    def autoload(self, *paths: str):
        Autoload(paths, self).load()

    def create_ctx(self, **kwargs) -> Context:
        return Context(self, **kwargs)

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
            autoload=True,
        )

    return inner


def namespace_callback(ctx: Context):
    arc.print(ctx.command.doc.usage())
    command = colorize(
        f"{ctx.command.root.name} {Joiner.with_space(ctx.command.doc.fullname)} --help",
        fg.YELLOW,
    )
    arc.print(f"{command} for more information")


def namespace(name: str, description: str | None = None):
    return Command(
        callback=namespace_callback,
        name=name,
        description=description,
        parent=None,
        autoload=True,
    )
