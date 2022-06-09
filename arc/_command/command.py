from __future__ import annotations
from functools import cached_property
import sys
import typing as t
import shlex

from arc import utils
from arc.context import Context
from arc.parser import Parser
from .param import ParamGroup, ParamMixin

import arc.typing as at


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
        args = args or sys.argv
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

    def process_parsed_result(self, res: at.ParseResult, ctx: Context):
        processed: dict[str, t.Any] = {}
        for group in self.param_groups:
            if group.is_default:
                processed |= group.process_parsed_result(res, ctx)
            else:
                processed[group.name] = group.process_parsed_result(res, ctx)

        return processed

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
