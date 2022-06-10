from __future__ import annotations
import sys
import typing as t
import shlex

from arc import utils
from arc.parser import Parser
from .param import ParamMixin
from arc.context import Context

import arc.typing as at

if t.TYPE_CHECKING:
    from .param import Param, ParamGroup


class Command(
    ParamMixin,
    utils.Display,
    members=["name", "parent", "callback", "params", "subcommands"],
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

    def __call__(self, args: str | list[str] | None = None):
        args = args or sys.argv[1:]
        if isinstance(args, str):
            args = shlex.split(args)

        with self.create_ctx() as ctx:
            ctx.run(args)

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
        parser = Parser()
        for param in self.cli_params:
            parser.add_param(param)

        return parser

    def create_ctx(self):
        return Context(self)


def command(name: str | None = None):
    def inner(callback: at.CommandCallback):
        return Command(callback=callback, name=name, parent=None)

    return inner
