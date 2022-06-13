from __future__ import annotations
import sys
import typing as t
import shlex

from arc import utils
from arc.config import config
from arc.parser import Parser
from .param import ParamMixin
from arc.context import Context

import arc.typing as at

if t.TYPE_CHECKING:
    from .param import Param, ParamGroup


class Command(
    ParamMixin,
    utils.Display,
    members=["name", "callback", "params", "subcommands"],
):
    parent: Command | None
    name: str
    subcommands: dict[str, Command]
    param_groups: list[ParamGroup]
    callback: at.CommandCallback

    def __init__(
        self,
        callback: at.CommandCallback,
        name: str | None = None,
        parent: Command | None = None,
    ):
        self.callback = callback
        self.name = name or callback.__name__
        self.parent = parent
        self.subcommands = {}

        if config.environment == "development":
            self.param_groups

    def __call__(self, user_args: str | list[str] | None = None, state: dict = None):
        args = self.get_args(user_args)

        if state:
            Context.state = state

        global_args = []
        while len(args) > 0 and args[0] not in self.subcommands:
            global_args.append(args.pop(0))

        command: Command = self

        index = 0
        for idx, value in enumerate(args):
            if value in command.subcommands:
                index = idx
                command = command.subcommands[value]

        with self.create_ctx() as ctx:
            global_res = ctx.run(global_args)

            if command is self:
                return global_res

            with command.create_ctx(parent=ctx) as commandctx:
                command_args = args[index + 1 :]
                return commandctx.run(command_args)

    @property
    def schema(self):
        return {
            "name": self.name,
            "params": [param.schema for param in self.params],
            "subcommands": [com.schema for com in self.subcommands.values()],
        }

    # Subcommands ----------------------------------------------------------------

    def subcommand(self, name: str | None = None):
        def inner(callback: at.CommandCallback):
            command_name = name
            if not command_name:
                command_name = callback.__name__
            if config.transform_snake_case:
                command_name = command_name.replace("_", "-")

            command = Command(callback=callback, name=name, parent=self)
            self.subcommands[command.name] = command
            return command

        return inner

    # Execution ------------------------------------------------------------------

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

    def get_args(self, args: str | list[str] | None):
        if args is None:
            args = sys.argv[1:]

        if isinstance(args, str):
            args = shlex.split(args)

        return args


def command(name: str | None = None):
    name = name or utils.discover_name()

    def inner(callback: at.CommandCallback):
        return Command(callback=callback, name=name, parent=None)

    return inner
